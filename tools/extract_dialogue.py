"""Export mapped English Dialogue LTE records without changing game files."""
import argparse
import csv
import json
from pathlib import Path
import struct
import zlib
from patch_lte_h2o import decoder, records

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root',type=Path,required=True,
                   help='Directory containing the original Dialogue H2O archives')
    p.add_argument('--blast-dll',type=Path,required=True)
    p.add_argument('--entry-map',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    mapping=json.loads(args.entry_map.read_text(encoding='utf-8'))
    decode=decoder(args.blast_dll)
    results=[]
    for key,entry in mapping.items():
        archive_name=key.split('#entry')[0].split('\\')[-1]
        b=(args.source_root/archive_name).read_bytes()
        if b[480]!=0x1a or struct.unpack_from('<I',b,481)[0]!=7:
            p.error(f'bad H2O archive: {archive_name}')
        f=struct.unpack_from('<10I',b,513+40*entry)
        raw=decode(b[f[6]+12:f[6]+12+f[4]],f[3])
        if zlib.crc32(raw)!=f[8]:p.error(f'CRC mismatch: {key}')
        for ident,marker,text,_ in records(raw):
            results.append({'source_file':key,'string_id':ident,
                            'english':text,'chinese':'','status':'untranslated'})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['source_file','string_id','english','chinese','status'])
        w.writeheader();w.writerows(results)
    print(json.dumps({'mapped_entries':len(mapping),'text_records':len(results)},indent=2))

if __name__=='__main__':main()
