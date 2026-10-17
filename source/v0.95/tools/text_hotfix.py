"""Stable-ID text preview, validation, version-bound delta build and offline recovery."""
import argparse
import csv
import json
from pathlib import Path
import br_review_common as core
from br_review_common import load, save, sha, rebuild, verify_only_text
from review_validation import validate_edits
from refresh_snapshot import COLUMNS
from build_resources import ROOT, safe_path
from resource_delta import make_patch, apply_patch

def read_csv(path, baseline):
    by = {r['key']:r for r in baseline['rows']}
    with path.open(encoding='utf-8-sig',newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != COLUMNS:
            raise ValueError('CSV columns changed')
        seen, edits = set(), []
        for row in reader:
            key = row['key']
            if key not in by or key in seen:
                raise ValueError('Unknown or duplicate stable ID: ' + key)
            expected = by[key]
            if any(row[k] != str(expected[k]) for k in COLUMNS if k not in ('new','action')):
                raise ValueError('Protected source field changed: ' + key)
            seen.add(key)
            edits.append({'key':key,'new':row['new'],'action':row['action']})
        if seen != set(by):
            raise ValueError('Missing stable IDs')
    return edits

def preview(path):
    baseline = load(ROOT / 'translations/baseline.json')
    edits = read_csv(path, baseline)
    changes, risks = validate_edits(edits, baseline)
    report = {'schema':'brzh-text-preview/1','version':'v0.95',
              'baselineSha256':sha((ROOT / 'translations/baseline.json').read_bytes()),
              'changedTextFields':len(changes),'blocksBuild':any(r['blocksCandidate'] for r in risks),
              'fontsAndUiRebuilt':False,'automaticReflow':False,'changes':risks}
    return baseline, changes, report

def build(csv_path, resource_root, output, blast_dll, hotfix_id):
    if output.exists():
        raise FileExistsError(output)
    baseline, changes, report = preview(csv_path)
    if report['blocksBuild']:
        raise ValueError('Missing glyphs block text-only hotfix; see preview')
    if not changes:
        raise ValueError('No changed text')
    core.DEC = core.decoder(blast_dll)
    # Tie the hotfix to the complete selected base, including its font and UI.
    for a in baseline['resources']:
        if sha(safe_path(resource_root,a['archive']).read_bytes()) != a['sha256']:
            raise ValueError('Base snapshot hash mismatch: ' + a['archive'])
    output.mkdir(parents=True)
    files = []
    for a in baseline['resources']:
        rows = [r for r in baseline['rows'] if r['archive']==a['archive']]
        edits = {r['key']:changes[r['key']] for r in rows if r['key'] in changes}
        if not edits:
            continue
        source = safe_path(resource_root,a['archive']).read_bytes()
        target = rebuild(source,rows,edits)
        verify_only_text(source,target,rows,edits)
        patch = make_patch(source,target,rows[0]['kind']=='map_title')
        if apply_patch(source,patch) != target:
            raise ValueError('Exact hotfix delta readback failed')
        name = 'patches/%02d.brzh.gz' % len(files)
        p = output / name
        p.parent.mkdir(exist_ok=True)
        p.write_bytes(patch)
        files.append({'path':a['archive'],'sourceSha256':sha(source),'targetSha256':sha(target),
                      'sourceBytes':len(source),'targetBytes':len(target),'patch':name,
                      'patchSha256':sha(patch),'changedKeys':list(edits)})
    manifest = {'schema':'brzh-text-hotfix/1','version':'v0.95','steamBuild':'25733254',
                'hotfixId':hotfix_id,'baseSnapshotId':report['baselineSha256'],
                'requiredBaseFiles':[{'path':a['archive'],'sha256':a['sha256']} for a in baseline['resources']],
                'files':files,'fontsAndUiRebuilt':False,'originalGameArchivesIncluded':False}
    save(output/'hotfix-manifest.json',manifest)
    save(output/'preview.json',report)
    return {'changedTextFields':len(changes),'changedResources':len(files),'patchBytes':sum((output/r['patch']).stat().st_size for r in files)}

def apply_copy(package, resource_root, output):
    if output.exists():
        raise FileExistsError(output)
    m = load(package/'hotfix-manifest.json')
    if m['schema'] != 'brzh-text-hotfix/1':
        raise ValueError('Hotfix schema')
    for a in m['requiredBaseFiles']:
        if sha(safe_path(resource_root,a['path']).read_bytes()) != a['sha256']:
            raise ValueError('Hotfix requires a different base: '+a['path'])
    # Validate every patch before writing any backups/candidates.
    for a in m['files']:
        if sha(safe_path(package,a['patch']).read_bytes()) != a['patchSha256']:
            raise ValueError('Hotfix patch hash mismatch')
    output.mkdir(parents=True)
    files = []
    for a in m['files']:
        source = safe_path(resource_root,a['path']).read_bytes()
        target = apply_patch(source,safe_path(package,a['patch']).read_bytes())
        if sha(source) != a['sourceSha256'] or sha(target) != a['targetSha256']:
            raise ValueError('Hotfix reconstruction hash mismatch')
        for folder,blob in [('backup',source),('candidate',target)]:
            path = safe_path(output/folder,a['path'])
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(blob)
            if path.read_bytes() != blob:
                raise ValueError('Hotfix output readback mismatch')
        files.append({k:a[k] for k in ('path','sourceSha256','targetSha256')})
    save(output/'recovery.json',{'schema':'brzh-recovery/1','hotfixId':m['hotfixId'],'files':files})
    return {'candidateResources':len(files),'sourceDirectoryWritten':False}

def restore_copy(applied, output):
    if output.exists():
        raise FileExistsError(output)
    m = load(applied/'recovery.json')
    buffers = []
    for a in m['files']:
        before = safe_path(applied/'backup',a['path']).read_bytes()
        after = safe_path(applied/'candidate',a['path']).read_bytes()
        if sha(before) != a['sourceSha256'] or sha(after) != a['targetSha256']:
            raise ValueError('Recovery files changed; refusing to overwrite newer work')
        buffers.append((a['path'],before))
    output.mkdir(parents=True)
    for relative,blob in buffers:
        dest = safe_path(output,relative)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(blob)
    return {'restoredResources':len(buffers),'sourceDirectoryWritten':False}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command',required=True)
    s = sub.add_parser('preview'); s.add_argument('--csv',type=Path,required=True); s.add_argument('--report',type=Path,required=True)
    s = sub.add_parser('build')
    for name in ('csv','resource-root','output','blast-dll'): s.add_argument('--'+name,type=Path,required=True)
    s.add_argument('--hotfix-id',required=True)
    s = sub.add_parser('apply-copy')
    for name in ('package','resource-root','output'): s.add_argument('--'+name,type=Path,required=True)
    s = sub.add_parser('restore-copy')
    for name in ('applied','output'): s.add_argument('--'+name,type=Path,required=True)
    args = p.parse_args()
    if args.command == 'preview':
        _,_,result=preview(args.csv);save(args.report,result)
        result={k:v for k,v in result.items() if k!='changes'}
    elif args.command == 'build': result=build(args.csv,args.resource_root,args.output,args.blast_dll,args.hotfix_id)
    elif args.command == 'apply-copy': result=apply_copy(args.package,args.resource_root,args.output)
    else: result=restore_copy(args.applied,args.output)
    print(json.dumps(result,ensure_ascii=True))

if __name__ == '__main__':
    main()
