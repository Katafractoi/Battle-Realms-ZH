"""Stage the one-time font upgrade and backup in a fresh directory; no live writes."""
import argparse
from pathlib import Path
from br_review_common import load,save,sha
from resource_delta import apply_patch
from build_resources import safe_path

def stage(package,resource_root,output):
    if output.exists():raise FileExistsError(output)
    report=load(package/'font-upgrade-report.json')
    relative=r'Interface\Interface_Text.H2O'
    source=safe_path(resource_root,relative).read_bytes()
    patch=(package/'font-upgrade.brzh.gz').read_bytes()
    if sha(source)!=report['baseSha256']:raise ValueError('Font upgrade base mismatch')
    if sha(patch)!=report['patchSha256']:raise ValueError('Font upgrade delta mismatch')
    target=apply_patch(source,patch)
    if sha(target)!=report['candidateSha256']:raise ValueError('Font upgrade result mismatch')
    output.mkdir(parents=True)
    for folder,blob in [('backup',source),('candidate',target)]:
        dest=safe_path(output/folder,relative);dest.parent.mkdir(parents=True);dest.write_bytes(blob)
        if sha(dest.read_bytes())!=sha(blob):raise ValueError('Font upgrade output readback mismatch')
    save(output/'recovery.json',{'schema':'brzh-recovery/1','hotfixId':'v0.95-font-common1500',
         'files':[{'path':relative,'sourceSha256':sha(source),'targetSha256':sha(target)}]})
    return {'stagedFontUpgrade':True,'newCharacters':report['newCharacters'],'gameDirectoryWritten':False,
            'runtimeVerificationPending':report['notVerified']}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('package','resource-root','output'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();print(stage(a.package,a.resource_root,a.output))
