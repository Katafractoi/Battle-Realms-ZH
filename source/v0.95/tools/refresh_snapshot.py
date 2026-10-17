"""Read the selected snapshot and export portable, stable-ID editable sources."""
import argparse
import csv
import re
from pathlib import Path
import br_review_common as core
from br_review_common import load, save, sha, raw_entry, records, map_title, width, tokens, whitespace, controls
from font_codec import parse_lfr
from build_resources import ROOT, safe_path

COLUMNS = ['key', 'archive', 'resource', 'id', 'kind', 'english', 'current', 'new', 'action']

def refresh(resource_root, blast_dll, final_contract=False):
    core.DEC = core.decoder(blast_dll)
    locations = load(ROOT / 'translations/locations.json')
    manifest = load(ROOT / 'resources/patch-manifest.json')
    rows = [dict(r) for r in locations['rows']]
    previous = load(ROOT / 'translations/baseline.json') if (ROOT / 'translations/baseline.json').exists() else None
    previous_rows = {r['key']:r for r in previous['rows']} if previous else {}
    terms = load(ROOT / 'package-status.json')['requiredTerms']
    resources = []
    for f in manifest['files']:
        path = safe_path(resource_root, f['path'])
        blob = path.read_bytes()
        if sha(blob) != f['targetSha256']:
            raise ValueError('Selected snapshot hash mismatch: ' + f['path'])
        resources.append({'archive':f['path'], 'sha256':f['targetSha256'], 'bytes':len(blob),
                          'englishSha256':f['sourceSha256']})
        cache = {}
        for r in rows:
            if r['archive'] != f['path']:
                continue
            if r['kind'] == 'lte':
                if r['entry'] not in cache:
                    recs = list(records(raw_entry(blob, r['entry'])))
                    if len({v[0] for v in recs}) != len(recs):
                        raise ValueError('Duplicate LTE IDs')
                    cache[r['entry']] = {i:(m,t) for i,m,t,w in recs}
                marker, text = cache[r['entry']][r['id']]
                if marker != r['marker']:
                    raise ValueError('LTE marker changed: ' + r['key'])
            elif r['kind'] == 'map_title':
                text = map_title(raw_entry(blob, r['entry']))[0]
            else:
                found = re.findall(r'(?m)^Name=([^\r\n]*)', blob.decode('cp936'))
                if len(found) != 1:
                    raise ValueError('INI Name count')
                text = found[0]
            if final_contract and r['key'] in previous_rows:
                expected = previous_rows[r['key']]['rawText']
                for old, new in terms.items():
                    expected = expected.replace(old, new)
                if text != expected:
                    raise ValueError('Unexpected text outside the three approved replacements: ' + r['key'])
            r.update(rawText=text, current=text, baselineSha256=sha(text.encode('utf-8')))
        if f['path'] == r'Interface\Interface_Text.H2O':
            font = parse_lfr(raw_entry(blob, 0))
    advances = {str(g[1]):g[2] for g in next(g for g in font[3] if g[0] == 32)[3]}
    for r in rows:
        r['measure'] = width(r['rawText'], advances)
    baseline = {'schema':'brzh-text-baseline/1', 'version':'v0.95', 'steamBuild':'25733254', 'resources':resources, 'rows':rows}
    # Validate the entire contract before replacing source files.
    if len({r['key'] for r in rows}) != len(rows):
        raise ValueError('Duplicate stable key')
    if final_contract:
        residual = [r['key'] for r in rows if any(t in r['rawText'].replace('\n','') for t in terms)]
        if residual:
            raise ValueError('Superseded terms remain: ' + str(residual[:3]))
    save(ROOT / 'translations/baseline.json', baseline)
    save(ROOT / 'translations/font-advances32.json', {'advance':advances})
    save(ROOT / 'font/layout.json', {'version':font[0], 'scale1':font[1], 'scale2':font[2], 'groups':font[3]})
    with (ROOT / 'translations/text.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow({**{k:r[k] for k in COLUMNS if k in r}, 'new':'', 'action':'AUTO'})
    status = load(ROOT / 'package-status.json')
    status['finalTextAligned'] = final_contract
    status['snapshotId'] = sha((ROOT / 'translations/baseline.json').read_bytes())
    status['resourceManifestSha256'] = sha((ROOT / 'resources/patch-manifest.json').read_bytes())
    save(ROOT / 'package-status.json', status)
    return {'rows':len(rows), 'resources':len(resources), 'snapshotId':status['snapshotId'], 'finalTextAligned':final_contract}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--resource-root', type=Path, required=True)
    p.add_argument('--blast-dll', type=Path, required=True)
    p.add_argument('--final-contract', action='store_true', help='Require exact three-term-only change from the previous snapshot')
    args = p.parse_args()
    print(refresh(args.resource_root.resolve(), args.blast_dll, args.final_contract))
