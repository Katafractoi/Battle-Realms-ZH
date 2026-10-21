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
using System.Threading;

public class PatchFile {
 public string path, sourceSha256, targetSha256, patch, patchSha256;
 public long sourceBytes, targetBytes;
}
public class PatchManifest { public string version, steamBuild; public PatchFile[] files; }
public class BackupManifest { public string version, gameRoot, state, steamBuild, installerRevision, operation; public PatchFile[] files; public int completed; public Dictionary<string,string> before; }
public class SourceProfile { public string id, sourcePackageSha256, manifestSha256; public PatchFile[] files; }
public class CompatibilityManifest { public string version, steamBuild; public SourceProfile[] profiles; }
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
   try { Directory.CreateDirectory(parent);string p=Path.Combine(parent,"BRZH-v0.95-r2-"+DateTime.Now.ToString("yyyyMMdd-HHmmss")+"-"+Guid.NewGuid().ToString("N").Substring(0,8)+".log");log=new StreamWriter(new FileStream(p,FileMode.CreateNew,FileAccess.Write,FileShare.Read),new UTF8Encoding(true));log.AutoFlush=true;logPath=p;return; }
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
  NoLink(root);
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
  if(!Directory.Exists(root))throw new Exception("游戏根目录不存在。");
  var common=Directory.GetParent(root);var apps=common==null?null:common.Parent;
  string path=apps==null?"":Path.Combine(apps.FullName,"appmanifest_1025600.acf");
  if(!File.Exists(path))throw new Exception("未找到 Steam AppID 1025600 清单。请从 Steam 管理菜单浏览本地文件并选择游戏根目录。");
  string text=File.ReadAllText(path);var actual=Regex.Match(text,"\"buildid\"\\s+\"([^\"]+)\"");
  if(!Regex.IsMatch(text,"\"appid\"\\s+\"1025600\"")||!actual.Success||actual.Groups[1].Value!=build)throw new Exception("版本不兼容：仅验证 Steam Build ID "+build+"；检测到 "+(actual.Success?actual.Groups[1].Value:"未知")+"。未覆盖资源，请使用匹配版本的安装包。");
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
 static PatchManifest Manifest() {
  if(Sha(Child(package,"patch-manifest.json"))!=ManifestDigest)throw new Exception("资源清单校验失败，请完整解压正确的汉化0.95测试版安装包。");
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
 // Trusted profiles are package-authenticated, never learned from backup.json.
 const string InstallerRevision="r2";
 const string ManifestDigest="28A57FEA068E4CECFE31C29A2DC6982ED17F0FADF7AA82E6D643EF3B84A72258";
 const string CompatibilityDigest="E2F333EEB13B455879C146EA5FD608D83BE89D6C957BDD4F542D1CB756B1E540";
 static void NoLink(string path) {
  if((File.Exists(path)||Directory.Exists(path))&&(File.GetAttributes(path)&FileAttributes.ReparsePoint)!=0)throw new Exception("路径含链接，已停止："+path);
 }
 static Mutex TakeLock(string root) {
  string id;using(var h=SHA256.Create())id=BitConverter.ToString(h.ComputeHash(Encoding.UTF8.GetBytes(root.ToUpperInvariant()))).Replace("-","");
  var m=new Mutex(false,"Local\\BRZH-r2-"+id);bool owned=false;
  try {try{owned=m.WaitOne(0);}catch(AbandonedMutexException){owned=true;}if(!owned)throw new Exception("此游戏目录已有安装或还原操作，请先等待该操作结束。");return m;}
  catch {m.Dispose();throw;}
 }
 static bool Same(string a,string b) {return String.Equals(a,b,StringComparison.OrdinalIgnoreCase);}
 static void FileSet(PatchFile[] files,PatchManifest m) {
  if(files==null||files.Length!=37||files.Any(f=>f==null||String.IsNullOrEmpty(f.path))||files.Select(f=>f.path).Distinct(StringComparer.OrdinalIgnoreCase).Count()!=37)throw new Exception("备份或兼容清单必须恰有37项且没有重复路径。");
  var expected=m.files.ToDictionary(f=>f.path,StringComparer.OrdinalIgnoreCase);
  foreach(var f in files) {
   PatchFile original;if(!expected.TryGetValue(f.path,out original)||!Same(f.sourceSha256,original.sourceSha256)||f.sourceBytes!=original.sourceBytes)throw new Exception("路径或原版哈希不属于已验证的 Steam Build ID 25733254。");
   if(f.targetSha256==null||!Regex.IsMatch(f.targetSha256,"^[0-9A-Fa-f]{64}$")||f.targetBytes<0)throw new Exception("目标哈希或长度无效。");
  }
 }
 static SourceProfile[] Profiles(PatchManifest m) {
  string path=Child(package,"compatibility.json");
  if(!File.Exists(path)||Sha(path)!=CompatibilityDigest)throw new Exception("兼容清单缺失或校验失败，请完整解压本安装包。");
  var c=json.Deserialize<CompatibilityManifest>(File.ReadAllText(path,Encoding.UTF8));
  if(c.version!=m.version||c.steamBuild!=m.steamBuild||c.profiles==null||c.profiles.Length!=1)throw new Exception("兼容清单版本不匹配。");
  foreach(var p in c.profiles)FileSet(p.files,m);
  return new [] {new SourceProfile {id="current-v0.95",files=m.files}}.Concat(c.profiles).ToArray();
 }
 static Dictionary<string,string> Snapshot(string root,PatchManifest m,SourceProfile[] profiles) {
  BuildGuard(root,m.steamBuild);Guard(root);NoLink(root);var result=new Dictionary<string,string>(StringComparer.OrdinalIgnoreCase);
  foreach(var f in m.files) {
   string p=Child(root,f.path);if(!File.Exists(p))throw new Exception("资源缺失，未覆盖任何文件："+f.path+"。请使用 Steam 验证游戏文件完整性。");
   string h=Sha(p);
   if(!Same(h,f.sourceSha256)&&!profiles.Any(v=>v.files.Any(x=>Same(x.path,f.path)&&Same(x.targetSha256,h))))throw new Exception("未知修改或其他 MOD，已停止："+f.path+"\n实际 SHA256："+h+"\n保留现有文件。需要原版时可通过 Steam 验证游戏文件完整性。");
   result[f.path]=h;
  }
  return result;
 }
 static bool MatchProfile(PatchFile[] files,SourceProfile profile) {
  var by=profile.files.ToDictionary(f=>f.path,StringComparer.OrdinalIgnoreCase);
  return files.All(f=>by.ContainsKey(f.path)&&Same(f.targetSha256,by[f.path].targetSha256)&&f.targetBytes==by[f.path].targetBytes);
 }
 static string FindBackup(string root,PatchManifest m,SourceProfile[] profiles) {
  string parent=Path.Combine(root,"BRZH-backups");NoLink(parent);
  if(File.Exists(parent))throw new Exception("BRZH-backups 被文件占用，未修改资源。");
  if(!Directory.Exists(parent))return null;
  foreach(string dir in Directory.GetDirectories(parent,"v0.95-*").OrderByDescending(s=>s)) {
   try {
    NoLink(dir);string path=Child(dir,"backup.json");if(!File.Exists(path))throw new Exception("缺少 backup.json");
    var j=json.Deserialize<BackupManifest>(File.ReadAllText(path,Encoding.UTF8));
    if(j==null||j.version!=m.version||String.IsNullOrEmpty(j.gameRoot)||!Same(Path.GetFullPath(j.gameRoot).TrimEnd('\\','/'),root.TrimEnd('\\','/'))||j.completed<0||j.completed>37)throw new Exception("备份目录或版本记录不匹配");
    if(!String.IsNullOrEmpty(j.steamBuild)&&j.steamBuild!=m.steamBuild)throw new Exception("备份 Build ID 不匹配");
    FileSet(j.files,m);if(!profiles.Any(p=>MatchProfile(j.files,p)))throw new Exception("备份目标不属于认证发行版本");
    foreach(var f in m.files) {string p=Child(dir,f.path);if(!File.Exists(p)||new FileInfo(p).Length!=f.sourceBytes||!Same(Sha(p),f.sourceSha256))throw new Exception("原版备份不完整或损坏："+f.path);}
    Say("已选择完整原版备份："+dir);return dir;
   } catch(Exception e) {Trace("跳过不可用备份："+dir+"；原因："+e.Message);}
  }
  return null;
 }
 static void CheckPatches(PatchManifest m) {
  foreach(var f in m.files) {string p=Child(package,f.patch);if(!File.Exists(p)||!Same(Sha(p),f.patchSha256))throw new Exception("安装包差分损坏，未修改资源："+f.patch);}
 }
 static void CheckSources(string root,PatchManifest m) {
  var profiles=Profiles(m);var before=Snapshot(root,m,profiles);
  if(before.Any(p=>!Same(p.Value,m.files.First(f=>Same(f.path,p.Key)).sourceSha256))&&FindBackup(root,m,profiles)==null)throw new Exception("已识别认证汉化，但未找到完整可信的原版备份。请保留现有文件，并使用 Steam 验证修复官方文件。");
  Say("Steam Build ID 25733254 与37项认证资源校验通过；未修改游戏。");
 }
 static void WritableAndReserved(string root,PatchManifest m) {
  foreach(var f in m.files) {
   string p=Child(root,f.path);if((File.GetAttributes(p)&FileAttributes.ReadOnly)!=0)throw new Exception("资源为只读，未改变权限或覆盖文件："+f.path);
   foreach(string suffix in new [] {".brzh-restore",".brzh-rollback",".brzh-r2-next",".brzh-r2-undo"}) {
    string q=Child(root,f.path+suffix);if(File.Exists(q)||Directory.Exists(q))throw new Exception("存在先前暂存文件，已在替换前停止："+q+"。请保留该文件与备份后联系维护者。");
   }
  }
 }
 static void CopyChecked(string source,string target,string expected) {
  Directory.CreateDirectory(Path.GetDirectoryName(target));File.Copy(source,target,false);
  if(!Same(Sha(target),expected))throw new Exception("副本校验失败，尚未开始资源替换："+target);
 }
 static void WriteJournal(string backup,BackupManifest j) {
  string path=Child(backup,"backup.json"),next=Child(backup,"backup.json.new");
  using(var f=new FileStream(next,FileMode.CreateNew,FileAccess.Write,FileShare.None))using(var w=new StreamWriter(f,new UTF8Encoding(false)))w.Write(json.Serialize(j));
  if(File.Exists(path))File.Replace(next,path,null);else File.Move(next,path);
 }
 static void AssertSnapshot(string root,PatchManifest m,Dictionary<string,string> expected) {
  Guard(root);foreach(var f in m.files)if(!Same(Sha(Child(root,f.path)),expected[f.path]))throw new Exception("操作期间资源发生变化，已停止："+f.path);
 }
 static void Install(string root) {Change(root,true);}
 static void Restore(string root) {Change(root,false);}
 static void Change(string root,bool install) {
  var m=Manifest();var profiles=Profiles(m);var before=Snapshot(root,m,profiles);
  bool original=m.files.All(f=>Same(before[f.path],f.sourceSha256));
  if(!install&&original) {Say("当前37项已经是已验证原版，未改动文件或旧备份。");return;}
  string saved=original?null:FindBackup(root,m,profiles);
  if(!original&&saved==null)throw new Exception("未找到37项齐全且校验通过的可信原版备份，未覆盖资源。可在 Steam 库中右键游戏 → 属性 → 已安装文件 → 验证游戏文件的完整性。");
  if(install)CheckPatches(m);
  if(install&&m.files.All(f=>Same(before[f.path],f.targetSha256))) {Say("本版37项资源已安装且有可信原版备份，未重复覆盖。");return;}
  WritableAndReserved(root,m);
  string parent=Path.Combine(root,"BRZH-backups");NoLink(parent);if(File.Exists(parent))throw new Exception("备份目录被文件占用。");
  string work=Path.Combine(parent,"v0.95-r2-"+DateTime.Now.ToString("yyyyMMdd-HHmmss")+"-"+Guid.NewGuid().ToString("N"));
  if(Directory.Exists(work)||File.Exists(work))throw new Exception("事务目录已存在，未覆盖任何文件。");
  foreach(var f in m.files)foreach(string prefix in new [] {"","before/","stage/","undo/"}) {string p=Child(work,prefix+f.path);if(File.Exists(p)||Directory.Exists(p))throw new Exception("暂存路径冲突，未覆盖资源。");}
  long needed=m.files.Sum(f=>f.sourceBytes+(install?f.targetBytes:f.sourceBytes)+2*new FileInfo(Child(root,f.path)).Length)+67108864;
  if(new DriveInfo(Path.GetPathRoot(root)).AvailableFreeSpace<needed)throw new Exception("没有足够空间保存完整原版、操作前副本和回退暂存，未修改资源。");
  Guard(root);Directory.CreateDirectory(work);
  var j=new BackupManifest {version=m.version,steamBuild=m.steamBuild,installerRevision=InstallerRevision,operation=install?"install":"restore",gameRoot=root,state="preparing",files=m.files,completed=0,before=before};WriteJournal(work,j);
  Say("本次完整备份及恢复记录："+work);
  foreach(var f in m.files) {
   CopyChecked(Child(saved??root,f.path),Child(work,f.path),f.sourceSha256);
   CopyChecked(Child(root,f.path),Child(work,"before/"+f.path),before[f.path]);
   CopyChecked(Child(work,"before/"+f.path),Child(work,"undo/"+f.path),before[f.path]);
   string next=Child(work,"stage/"+f.path);Directory.CreateDirectory(Path.GetDirectoryName(next));
   if(install)Apply(Child(work,f.path),Child(package,f.patch),next,f);else CopyChecked(Child(work,f.path),next,f.sourceSha256);
  }
  foreach(var f in m.files) {
   string wanted=install?f.targetSha256:f.sourceSha256;
   if(!Same(Sha(Child(work,f.path)),f.sourceSha256)||!Same(Sha(Child(work,"stage/"+f.path)),wanted)||!Same(Sha(Child(work,"undo/"+f.path)),before[f.path]))throw new Exception("全部暂存校验未通过，原游戏资源未替换。");
  }
  BuildGuard(root,m.steamBuild);AssertSnapshot(root,m,before);WritableAndReserved(root,m);
  j.state=install?"installing":"restoring";WriteJournal(work,j);var changed=new List<PatchFile>();
  try {
   foreach(var f in m.files) {
    Guard(root);string wanted=install?f.targetSha256:f.sourceSha256,current=Child(root,f.path),next=Child(work,"stage/"+f.path);
    if(!Same(Sha(current),before[f.path])||!Same(Sha(next),wanted))throw new Exception("替换前即时校验失败："+f.path);
    if(!Same(before[f.path],wanted)) {File.Replace(next,current,null);changed.Add(f);if(!Same(Sha(current),wanted))throw new Exception("资源替换后校验失败："+f.path);}
    j.completed++;WriteJournal(work,j);
   }
   foreach(var f in m.files)if(!Same(Sha(Child(root,f.path)),install?f.targetSha256:f.sourceSha256))throw new Exception("最终37项校验失败。");
   j.state=install?"installed":"restored";WriteJournal(work,j);
   Say(install?"安装完成，37项资源校验通过。":"还原完成，37项已验证原版资源校验通过。");Say("旧备份和旧日志均保留。本次记录："+work);
  } catch(Exception failure) {
   string recovery;
   try {
    BuildGuard(root,m.steamBuild);Guard(root);
    foreach(var f in changed) {
     string actual=Sha(Child(root,f.path)),wanted=install?f.targetSha256:f.sourceSha256;
     if((!Same(actual,wanted)&&!Same(actual,before[f.path]))||!Same(Sha(Child(work,"undo/"+f.path)),before[f.path]))throw new Exception("回退前发现未知变化，未继续覆盖："+f.path);
    }
    foreach(var f in changed.AsEnumerable().Reverse()) {
     Guard(root);string target=Child(root,f.path);if(Same(Sha(target),before[f.path]))continue;
     File.Replace(Child(work,"undo/"+f.path),target,null);if(!Same(Sha(target),before[f.path]))throw new Exception("回退校验失败："+f.path);
    }
    AssertSnapshot(root,m,before);j.state="rolled_back_after_error";recovery="已校验回退到本次操作前的37项状态。";
   } catch(Exception rollback) {j.state="recovery_required";recovery="自动回退停止："+rollback.Message+"。请保留全部备份；正常关闭游戏后可重试还原，未知修改须先通过 Steam 验证修复。";}
   WriteJournal(work,j);throw new Exception("本次操作未完成。"+recovery+"\n恢复记录："+work,failure);
  }
 }

 static string FindRoot() {
  var steam=Registry.CurrentUser.OpenSubKey(@"Software\Valve\Steam");string path=steam==null?null:steam.GetValue("SteamPath")as string;
  if(path==null)return "";var libraries=new List<string>{path};string vdf=Path.Combine(path,"steamapps","libraryfolders.vdf");
  if(File.Exists(vdf))foreach(Match match in Regex.Matches(File.ReadAllText(vdf),"\"path\"\\s+\"([^\"]+)\""))libraries.Add(match.Groups[1].Value.Replace("\\\\","\\"));
  return libraries.Select(p=>Path.Combine(p,"steamapps","common","Battle Realms")).FirstOrDefault(Directory.Exists)??"";
 }
 public static int Main(string[] args) {
  bool interactive=args.Length==0;int result=1;Mutex held=null;string completion="操作失败，按 Esc 退出";
  try {
   OpenLog();Console.OutputEncoding=Encoding.UTF8;Console.InputEncoding=Encoding.UTF8;
   json=new JavaScriptSerializer { MaxJsonLength=8000000 };
   Trace("BRZH v0.95 installer r2；交互="+interactive+"；安装包="+package+"；工作目录="+Environment.CurrentDirectory);
   string action,root;
   if(interactive) {
    Say("汉化0.95测试版\nSteam AppID 1025600 | 已验证 Build ID 25733254 | 安装器修订号 r2\n非官方测试版，请先备份存档与原文件，并正常退出游戏。\n日志："+logPath);
    root="";try{root=FindRoot();}catch(Exception e){Trace("自动检测目录失败，可手动输入："+e);}
    string choice=null;
    string input=Input("请先粘贴游戏根目录完整路径（可带双引号）。直接回车采用检测结果：\n"+(String.IsNullOrEmpty(root)?"未检测到，请手动填写。":root));
    // Accept the previous menu-first workflow too.
    if(input.Trim()=="1"||input.Trim()=="2") {choice=input.Trim();input=Input("请输入游戏根目录；直接回车采用检测结果：\n"+root);}
    else if(input.Trim()=="3") {Say("已取消，未操作游戏。");completion="已取消，按 Esc 退出";result=0;return result;}
    if(!String.IsNullOrWhiteSpace(input))root=input;
    root=NormalizeRoot(root);Say("已选择游戏根目录："+root);
    if(choice==null) {
     while(true) {choice=Input("1 安装汉化\n2 还原已验证原版资源\n3 退出\n请输入 1、2 或 3：").Trim();if(choice=="1"||choice=="2"||choice=="3")break;Say("输入无效，请重新输入 1、2 或 3。尚未操作游戏。");}
    }
    if(choice=="3") {Say("已取消，未操作游戏。");completion="已取消，按 Esc 退出";result=0;return result;}
    action=choice=="1"?"--install":"--restore";
   }
   else { if(args.Length!=2)throw new Exception("用法：--check / --install / --restore 加游戏目录。");action=args[0];root=args[1]; }
   root=NormalizeRoot(root);held=TakeLock(root);Trace("操作="+action+"；游戏根目录="+root);
   if(action=="--check") {CheckSources(root,Manifest());}
   else if(action=="--install")Install(root);else if(action=="--restore")Restore(root);else throw new Exception("未知操作。");
   completion=action=="--install"?"安装完成，按 Esc 退出":action=="--restore"?"还原完成，按 Esc 退出":"检查完成，按 Esc 退出";
   result=0;Say("操作成功。日志："+logPath);return result;
  } catch(Exception e) {
   try {Trace("操作失败，退出码 1。完整异常："+e);Console.Error.WriteLine("操作失败（退出码 1）："+e.Message+"\n日志："+(String.IsNullOrEmpty(logPath)?"未能创建日志。":logPath));}catch{}
   return 1;
  }
  finally {
   if(held!=null) {try{held.ReleaseMutex();held.Dispose();}catch{}}
   if(interactive) {try{WaitForExit(completion);}catch{}}
   if(log!=null) {try{Trace("程序退出，代码="+result);log.Dispose();}catch{}}
  }
 }
}
