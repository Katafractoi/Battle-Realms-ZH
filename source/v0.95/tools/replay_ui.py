"""Replay exact UI byte fields on an official archive copy, retaining other entries."""
import argparse
from pathlib import Path
import br_review_common as core
from br_review_common import load,save,sha,raw_entry
from br_repack_preserve_raw import repack_preserving_segments
from build_resources import ROOT

def replay(archive,output,blast_dll):
    if output.exists():raise FileExistsError(output)
    core.DEC=core.decoder(blast_dll)
    plan=load(ROOT/'ui/byte-edits.json')
    source=archive.read_bytes()
    if sha(source)!=plan['sourceArchiveSha256']:raise ValueError('Official UI source hash mismatch')
    replacements={}
    for r in plan['entries']:
        old=raw_entry(source,r['entry'])
        if sha(old)!=r['sourceRawSha256']:raise ValueError('Decoded UI base mismatch')
        new=bytearray(old)
        for e in r['edits']:
            off=e['offset'];before=bytes.fromhex(e['beforeHex']);after=bytes.fromhex(e['afterHex'])
            if len(before)!=len(after) or old[off:off+len(before)]!=before:raise ValueError('UI field mismatch')
            new[off:off+len(after)]=after
        if sha(new)!=r['targetRawSha256']:raise ValueError('Decoded UI result mismatch')
        replacements[r['entry']]=bytes(new)
    result=repack_preserving_segments(source,replacements,core.DEC)
    for r in plan['entries']:
        if sha(raw_entry(result,r['entry']))!=r['targetRawSha256']:raise ValueError('UI archive readback mismatch')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(result)
    return {'changedEntries':len(replacements),'decodedUiMatchesSelectedSnapshot':True,
            'exactArchiveMatch':sha(result)==plan['targetArchiveSha256'],'sha256':sha(result)}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('archive','output','blast-dll'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();print(replay(a.archive,a.output,a.blast_dll))
