using System;
using System.IO;
using System.IO.Compression;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using Microsoft.Win32;

public class PatchFile {
 public string path, sourceSha256, targetSha256, patch, patchSha256;
 public long sourceBytes, targetBytes;
}
public class PatchManifest { public string version, steamBuild; public PatchFile[] files; }
public class BackupManifest { public string version, gameRoot, state; public PatchFile[] files; public int completed; }
public static class BRZHInstaller {
 static JavaScriptSerializer json;
 static string package=AppDomain.CurrentDomain.BaseDirectory;
 static StreamWriter log;
 static string logPath="";
 static void Trace(string text) { if(log!=null) {log.WriteLine(DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff")+" "+text);log.Flush();} }
 static void Say(string text) { Trace(text);Console.WriteLine(text); }
 static void OpenLog() {
  Exception last=null;
  foreach(string parent in new [] {Path.Combine(package,"logs"),Path.Combine(Path.GetTempPath(),"BRZH-logs")}) {
   try { Directory.CreateDirectory(parent);string p=Path.Combine(parent,"BRZH-v0.95-r1-"+DateTime.Now.ToString("yyyyMMdd-HHmmss")+"-"+Guid.NewGuid().ToString("N").Substring(0,8)+".log");log=new StreamWriter(new FileStream(p,FileMode.CreateNew,FileAccess.Write,FileShare.Read),new UTF8Encoding(true));log.AutoFlush=true;logPath=p;return; }
   catch(Exception e) {last=e;}
  }
  throw new IOException("无法创建安装日志，尚未操作游戏。请把完整安装包解压到可写的普通文件夹后重试。",last);
 }
 static string NormalizeRoot(string input) {
  string value=(input??"").Trim();
  if(value.Length>=2&&((value[0]=='"'&&value[value.Length-1]=='"')||(value[0]=='“'&&value[value.Length-1]=='”')))value=value.Substring(1,value.Length-2).Trim();
  if(String.IsNullOrEmpty(value)||!Path.IsPathRooted(value))throw new Exception("请填写完整的游戏根目录路径。可在 Steam 中右键 Battle Realms → 管理 → 浏览本地文件取得；不要选 Data 或 Interface 子目录。");
  return Path.GetFullPath(value);
 }
 static string Input(string label) { Say(label);string value=Console.ReadLine();if(value==null)throw new EndOfStreamException("输入已关闭，操作停止。");return value; }
 static void WaitForExit(string message) {
  Console.WriteLine(message);
  while(Console.KeyAvailable)Console.ReadKey(true);
  while(Console.ReadKey(true).Key!=ConsoleKey.Escape) { }
 }
 static string Sha(string p) { using(var f=File.OpenRead(p)) using(var h=SHA256.Create()) return BitConverter.ToString(h.ComputeHash(f)).Replace("-",""); }
 static string Child(string root,string rel) {
  if(String.IsNullOrEmpty(rel)||Path.IsPathRooted(rel))throw new Exception("清单路径无效。");
  string p=Path.GetFullPath(Path.Combine(root,rel)), prefix=Path.GetFullPath(root).TrimEnd('\\','/')+Path.DirectorySeparatorChar;
  if(!p.StartsWith(prefix,StringComparison.OrdinalIgnoreCase))throw new Exception("清单路径超出目录。");
  string dir=Path.GetDirectoryName(p);
  while(dir.Length>=prefix.Length) {
   if(Directory.Exists(dir)&&(File.GetAttributes(dir)&FileAttributes.ReparsePoint)!=0)throw new Exception("目标路径含目录链接，已停止。");
   dir=Path.GetDirectoryName(dir);
  }
  if(File.Exists(p)&&(File.GetAttributes(p)&FileAttributes.ReparsePoint)!=0)throw new Exception("目标文件是链接，已停止。");
  return p;
 }
 static void Guard(string root) {
  string prefix=Path.GetFullPath(root).TrimEnd('\\','/')+Path.DirectorySeparatorChar;
  foreach(var p in Process.GetProcesses()) using(p) {
   if(p.Id==Process.GetCurrentProcess().Id)continue;
   try { string name=p.MainModule.FileName; if(name.StartsWith(prefix,StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException("游戏目录中有程序正在运行，请先正常退出游戏。不会强行关闭任何进程。"); }
   catch(InvalidOperationException e) { if(e.Message.StartsWith("游戏目录"))throw; }
   catch(System.ComponentModel.Win32Exception) { }
  }
 }
 static void BuildGuard(string root,string build) {
  if(!Directory.Exists(root))throw new Exception("游戏目录不存在。");
  string steamapps=Directory.GetParent(Directory.GetParent(root).FullName).FullName;
  string path=Path.Combine(steamapps,"appmanifest_1025600.acf");
  if(!File.Exists(path))throw new Exception("没有找到此安装对应的Steam清单，请选择steamapps/common/Battle Realms目录。");
  string text=File.ReadAllText(path);
  if(!Regex.IsMatch(text,"\"appid\"\\s+\"1025600\"")||!Regex.IsMatch(text,"\"buildid\"\\s+\""+Regex.Escape(build)+"\""))throw new Exception("仅适用Steam build "+build+"。当前版本不匹配，未覆盖文件。");
 }
 static void CopyExactly(Stream input,Stream output,long bytes) {
  if(bytes<0)throw new Exception("补丁长度无效。"); byte[] buf=new byte[1024*1024];
  while(bytes>0) { int n=input.Read(buf,0,(int)Math.Min(bytes,buf.Length)); if(n==0)throw new EndOfStreamException("补丁或原文件不完整。");output.Write(buf,0,n);bytes-=n; }
 }
 static void Apply(string source,string patch,string target,PatchFile f) {
  using(var src=File.OpenRead(source)) using(var inp=File.OpenRead(patch)) using(var gz=new GZipStream(inp,CompressionMode.Decompress)) using(var rd=new BinaryReader(gz)) using(var dst=new FileStream(target,FileMode.CreateNew,FileAccess.Write)) {
   if(Encoding.ASCII.GetString(rd.ReadBytes(8))!="BRZHDP1\0")throw new Exception("补丁格式无效。");
   while(true) { int tag=rd.ReadByte();if(tag==255)break;long count;
    if(tag==0) { long off=rd.ReadInt64();count=rd.ReadInt64();if(off<0||count<0||off>src.Length-count)throw new Exception("补丁复制范围无效。");if(dst.Position>f.targetBytes-count)throw new Exception("补丁超出目标范围。");src.Position=off;CopyExactly(src,dst,count); }
    else if(tag==1) { count=rd.ReadInt64();if(count<0||dst.Position>f.targetBytes-count)throw new Exception("补丁数据范围无效。");CopyExactly(gz,dst,count); }
    else throw new Exception("补丁操作无效。");
   }
   if(gz.ReadByte()!=-1||dst.Length!=f.targetBytes)throw new Exception("补丁目标长度无效。");
  }
  if(Sha(target)!=f.targetSha256)throw new Exception("生成资源校验失败，原文件未更改。");
 }
 static void WriteJournal(string backup,BackupManifest j) { File.WriteAllText(Path.Combine(backup,"backup.json"),json.Serialize(j),new UTF8Encoding(false)); }
 static PatchManifest Manifest() {
  var m=json.Deserialize<PatchManifest>(File.ReadAllText(Path.Combine(package,"patch-manifest.json"),Encoding.UTF8));
  if(m.version!="v0.95"||m.steamBuild!="25733254"||m.files==null||m.files.Length!=37)throw new Exception("安装清单不符合此版本。");
  if(m.files.Select(f=>f.path.ToLowerInvariant()).Distinct().Count()!=m.files.Length)throw new Exception("清单含重复文件。");
  foreach(var f in m.files) {
   Child(package,f.patch);
   string p=f.path.Replace('/','\\');
   if(!(p.StartsWith("AIProfiles\\")&&p.EndsWith(".ini")||p=="Interface\\Interface.H2O"||p=="Interface\\Interface_Text.H2O"||p=="Levels\\Levels_Multi.H2O"||p.StartsWith("Sound\\Dialogue\\")&&p.EndsWith(".H2O")))throw new Exception("清单含非汉化资源。");
  }
  return m;
 }
 static void CheckSources(string root,PatchManifest m) {
  Trace("预检游戏版本、进程和全部37项资源："+root);
  BuildGuard(root,m.steamBuild);Guard(root);
  foreach(var f in m.files) {
   string source=Child(root,f.path),patch=Child(package,f.patch);
   if(!File.Exists(source)||Sha(source)!=f.sourceSha256)throw new Exception("原版资源不匹配："+f.path+"。保留现有文件，请先还原原版；不会覆盖其他MOD。");
   if(!File.Exists(patch)||Sha(patch)!=f.patchSha256)throw new Exception("安装包损坏："+f.patch);
  }
 }
 static void Install(string root) {
  var m=Manifest();CheckSources(root,m);
  string backup=Path.Combine(root,"BRZH-backups","v0.95-"+DateTime.Now.ToString("yyyyMMdd-HHmmss")+"-"+Guid.NewGuid().ToString("N").Substring(0,6));
  Directory.CreateDirectory(backup);Trace("备份目录："+backup);string stage=Path.Combine(backup,"stage");Directory.CreateDirectory(stage);
  var j=new BackupManifest {version=m.version,gameRoot=Path.GetFullPath(root),state="preparing",files=m.files,completed=0};WriteJournal(backup,j);
  foreach(var f in m.files) {
   string copy=Child(backup,f.path);Directory.CreateDirectory(Path.GetDirectoryName(copy));File.Copy(Child(root,f.path),copy,false);
   if(Sha(copy)!=f.sourceSha256)throw new Exception("备份校验失败，未覆盖游戏。");
   string next=Child(stage,f.path);Directory.CreateDirectory(Path.GetDirectoryName(next));Apply(copy,Child(package,f.patch),next,f);
  }
  CheckSources(root,m);j.state="installing";WriteJournal(backup,j);
  try {
   foreach(var f in m.files) { Guard(root);Trace("安装资源："+f.path);File.Replace(Child(stage,f.path),Child(root,f.path),null);j.completed++;WriteJournal(backup,j); }
   foreach(var f in m.files)if(Sha(Child(root,f.path))!=f.targetSha256)throw new Exception("安装后校验失败。");
   j.state="installed";WriteJournal(backup,j);Say("安装完成，37项资源校验通过。尚未进行全流程实机验证。\n还原备份："+backup);
  } catch {
   Guard(root);
   foreach(var f in m.files.Take(j.completed)) { Guard(root);string temp=Child(root,f.path)+".brzh-rollback";if(File.Exists(temp))throw new Exception("回滚暂存文件已存在，请保留备份后联系维护者。");File.Copy(Child(backup,f.path),temp);File.Replace(temp,Child(root,f.path),null); }
   j.state="rolled_back_after_error";WriteJournal(backup,j);throw;
  }
 }
 static void Restore(string root) {
  var m=Manifest();BuildGuard(root,m.steamBuild);Guard(root);
  string parent=Path.Combine(root,"BRZH-backups");
  if(!Directory.Exists(parent))throw new Exception("未找到此安装器生成的备份。");
  string backup=Directory.GetDirectories(parent,"v0.95-*").OrderByDescending(s=>s).FirstOrDefault(s=>File.Exists(Path.Combine(s,"backup.json")));
  if(backup==null)throw new Exception("没有可用备份。");
  var j=json.Deserialize<BackupManifest>(File.ReadAllText(Path.Combine(backup,"backup.json")));
  if(j.version!=m.version||!String.Equals(Path.GetFullPath(root),j.gameRoot,StringComparison.OrdinalIgnoreCase))throw new Exception("备份属于其他安装。");
  foreach(var f in m.files) {
   string saved=Child(backup,f.path),current=Child(root,f.path);
   if(!File.Exists(saved)||Sha(saved)!=f.sourceSha256)throw new Exception("备份损坏："+f.path);
   if(!File.Exists(current))throw new Exception("当前资源缺失："+f.path);
   string h=Sha(current);if(h!=f.targetSha256&&h!=f.sourceSha256)throw new Exception("资源已被其他MOD改变，已停止还原："+f.path);
  }
  foreach(var f in m.files) {
   Guard(root);string current=Child(root,f.path);if(Sha(current)==f.sourceSha256)continue;
   string temp=current+".brzh-restore";if(File.Exists(temp))throw new Exception("还原暂存文件已存在。");File.Copy(Child(backup,f.path),temp);if(Sha(temp)!=f.sourceSha256)throw new Exception("还原暂存校验失败。");File.Replace(temp,current,null);
  }
  foreach(var f in m.files)if(Sha(Child(root,f.path))!=f.sourceSha256)throw new Exception("还原后校验失败。");
  j.state="restored";WriteJournal(backup,j);Say("已还原安装前37项原版资源。备份仍保留，其他文件未修改。");
 }
 static string FindRoot() {
  var steam=Registry.CurrentUser.OpenSubKey(@"Software\Valve\Steam");string path=steam==null?null:steam.GetValue("SteamPath")as string;
  if(path==null)return "";var libraries=new List<string>{path};string vdf=Path.Combine(path,"steamapps","libraryfolders.vdf");
  if(File.Exists(vdf))foreach(Match match in Regex.Matches(File.ReadAllText(vdf),"\"path\"\\s+\"([^\"]+)\""))libraries.Add(match.Groups[1].Value.Replace("\\\\","\\"));
  return libraries.Select(p=>Path.Combine(p,"steamapps","common","Battle Realms")).FirstOrDefault(Directory.Exists)??"";
 }
 public static int Main(string[] args) {
  bool interactive=args.Length==0;int result=1;string completion="操作失败，按 Esc 退出";
  try {
   OpenLog();Console.OutputEncoding=Encoding.UTF8;Console.InputEncoding=Encoding.UTF8;
   json=new JavaScriptSerializer { MaxJsonLength=8000000 };
   Trace("BRZH v0.95 installer r1；交互="+interactive+"；安装包="+package+"；工作目录="+Environment.CurrentDirectory);
   string action,root;
   if(interactive) {
    Say("Battle Realms Steam 中文补丁 v0.95（安装器 r1）\n请先正常退出游戏。\n日志："+logPath);
    root="";try{root=FindRoot();}catch(Exception e){Trace("自动检测目录失败，可手动输入："+e);}
    string choice=null;
    string input=Input("请先粘贴游戏根目录完整路径（可带双引号）。直接回车采用检测结果：\n"+(String.IsNullOrEmpty(root)?"未检测到，请手动填写。":root));
    // Accept the previous menu-first workflow too.
    if(input.Trim()=="1"||input.Trim()=="2") {choice=input.Trim();input=Input("请输入游戏根目录；直接回车采用检测结果：\n"+root);}
    else if(input.Trim()=="3") {Say("已取消，未操作游戏。");completion="已取消，按 Esc 退出";result=0;return result;}
    if(!String.IsNullOrWhiteSpace(input))root=input;
    root=NormalizeRoot(root);Say("已选择游戏根目录："+root);
    if(choice==null) {
     while(true) {choice=Input("1 安装汉化\n2 还原安装前资源\n3 退出\n请输入 1、2 或 3：").Trim();if(choice=="1"||choice=="2"||choice=="3")break;Say("输入无效，请重新输入 1、2 或 3。尚未操作游戏。");}
    }
    if(choice=="3") {Say("已取消，未操作游戏。");completion="已取消，按 Esc 退出";result=0;return result;}
    action=choice=="1"?"--install":"--restore";
   }
   else { if(args.Length!=2)throw new Exception("用法：--check / --install / --restore 加游戏目录。");action=args[0];root=args[1]; }
   root=NormalizeRoot(root);Trace("操作="+action+"；游戏根目录="+root);
   if(action=="--check") {CheckSources(root,Manifest());Say("版本、进程和37项原版资源校验通过。未修改游戏。");}
   else if(action=="--install")Install(root);else if(action=="--restore")Restore(root);else throw new Exception("未知操作。");
   completion=action=="--install"?"安装完成，按 Esc 退出":action=="--restore"?"还原完成，按 Esc 退出":"检查完成，按 Esc 退出";
   result=0;Say("操作成功。日志："+logPath);return result;
  } catch(Exception e) {
   try {Trace("操作失败，退出码 1。完整异常："+e);Console.Error.WriteLine("操作失败（退出码 1）："+e.Message+"\n日志："+(String.IsNullOrEmpty(logPath)?"未能创建日志。":logPath));}catch{}
   return 1;
  }
  finally {
   if(interactive) {try{WaitForExit(completion);}catch{}}
   if(log!=null) {try{Trace("程序退出，代码="+result);log.Dispose();}catch{}}
  }
 }
}
