"""Patch named LTE records in a Battle Realms H2O v7 archive.

The game assets and PKWare blast DLL are user supplied. Other archive entries
retain their compressed bytes. This tool does not access Steam on its own.
"""
import argparse
import csv
import ctypes
import hashlib
import json
from pathlib import Path
import struct
import zlib


def decoder(dll_path):
    dll = ctypes.CDLL(str(dll_path))
    dll.blast_buffer.argtypes = [ctypes.c_void_p, ctypes.c_uint,
        ctypes.c_void_p, ctypes.c_uint, ctypes.POINTER(ctypes.c_uint),
        ctypes.POINTER(ctypes.c_uint)]
    dll.blast_buffer.restype = ctypes.c_int
    def decode(packed, size):
        if not 0 < size < 32_000_000:
            raise ValueError('raw entry outside allowed bounds')
        out = ctypes.create_string_buffer(size)
        got, unused = ctypes.c_uint(), ctypes.c_uint()
        inp = ctypes.create_string_buffer(packed)
        status = dll.blast_buffer(inp, len(packed), out, size,
                                  ctypes.byref(got), ctypes.byref(unused))
        if status or got.value != size or unused.value:
            raise ValueError(f'blast failed: {status}, {got.value}, {unused.value}')
        return out.raw
    return decode


def literal_dcl(raw):
    # PKWare DCL literal-only encoding; readback is verified with blast.
    lengths = []
    for v in (2,35,36,53,38,23):
        lengths.extend([v & 15] * ((v >> 4)+1))
    width = lengths[15]
    first = 0
    for depth in range(1,width+1):
        if depth != 1:
            first = (first + sum(n == depth-1 for n in lengths)) << 1
    code = first + sum(i < 15 and lengths[i] == width for i in range(16))
    bits=[]
    for byte in raw:
        bits.append(0)
        bits.extend((byte >> i) & 1 for i in range(8))
    bits.append(1)
    bits.extend(1 ^ ((code >> i) & 1) for i in range(width-1,-1,-1))
    bits.extend((255 >> i) & 1 for i in range(8))
    payload=bytearray((0,4))
    for i in range(0,len(bits),8):
        payload.append(sum(bits[i+j] << j for j in range(min(8,len(bits)-i))))
    return bytes(payload)


def records(raw):
    version,count=struct.unpack_from('<II',raw)
    if version != 1:raise ValueError('not an LTE text entry')
    pos=8
    for _ in range(count):
        ident,marker,units=struct.unpack_from('<iBi',raw,pos)
        end=pos+9+2*units
        if units<1 or end>len(raw):raise ValueError('bad LTE record length')
        body=raw[pos+9:end]
        if body[-2:]!=b'\0\0':raise ValueError('missing LTE terminator')
        text=body[:-2].decode('utf-16le')
        yield ident,marker,text,raw[pos:end]
        pos=end
    if pos!=len(raw):raise ValueError('trailing LTE bytes')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive',type=Path,required=True)
    p.add_argument('--blast-dll',type=Path,required=True)
    p.add_argument('--entry-map',type=Path,required=True,
                   help='JSON mapping source_file to numeric archive entry')
    p.add_argument('--translations',type=Path,required=True,
                   help='CSV columns source_file,string_id,english,chinese')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():p.error('output exists; choose a fresh path')
    source=args.archive.read_bytes()
    if source[480]!=0x1a:p.error('invalid H2O marker')
    version,count=struct.unpack_from('<II',source,481)
    if version!=7:p.error('expected H2O v7')
    second=513+40*count
    if source[513:second]!=source[second:second+40*count]:p.error('index copies differ')
    fields=[struct.unpack_from('<10I',source,513+40*i) for i in range(count)]
    first_offset=fields[0][6]
    mapping=json.loads(args.entry_map.read_text(encoding='utf-8'))
    if any('#entry' in key for key in mapping):
        mapping={key:value for key,value in mapping.items()
                 if key.rsplit('\\', 1)[-1].startswith(args.archive.name+'#entry')}
    if len(set(mapping.values()))!=len(mapping):p.error('duplicate archive entry mapping')
    edits={}
    for row in csv.DictReader(args.translations.open(encoding='utf-8-sig',newline='')):
        if not row['chinese'] or row['chinese']==row['english']:continue
        name=row['source_file']
        if name not in mapping:continue
        edits.setdefault(int(mapping[name]),{})[int(row['string_id'])]=(row['english'],row['chinese'])
    decode=decoder(args.blast_dll)
    changed={}
    for i,items in edits.items():
        if not 0<=i<count:p.error(f'bad entry index {i}')
        f=fields[i]
        raw=decode(source[f[6]+12:f[6]+12+f[4]],f[3])
        if zlib.crc32(raw)!=f[8]:p.error(f'CRC mismatch at {i}')
        out=bytearray(raw[:8]);seen=set()
        for ident,marker,text,original in records(raw):
            if ident in items:
                english,chinese=items[ident]
                if text!=english:p.error(f'source mismatch at entry {i} id {ident}')
                body=(chinese+'\0').encode('utf-16le')
                out+=struct.pack('<iBi',ident,marker,len(body)//2)+body
                seen.add(ident)
            else:out+=original
        if seen!=set(items):p.error(f'missing text IDs at entry {i}')
        assert len(list(records(bytes(out))))==len(list(records(raw)))
        changed[i]=bytes(out)
    result=bytearray(source[:first_offset])
    for i,f in enumerate(fields):
        if i in changed:
            raw=changed[i];packed=literal_dcl(raw);crc=zlib.crc32(raw)
            assert decode(packed,len(raw))==raw
            size=len(raw)
        else:
            packed=source[f[6]+12:f[6]+12+f[4]];crc=f[8];size=f[3]
        offset=len(result)
        for table in (513,second):
            at=table+40*i
            for slot,value in ((3,size),(4,len(packed)),(6,offset),(8,crc)):
                struct.pack_into('<I',result,at+4*slot,value)
        result.extend(struct.pack('<III',len(packed),size,crc))
        result.extend(packed)
    if result[513:second]!=result[second:second+40*count]:p.error('rebuilt index mismatch')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(result)
    print(json.dumps({'source_sha256':hashlib.sha256(source).hexdigest(),
      'output_sha256':hashlib.sha256(result).hexdigest(),
      'entries':count,'changed_entries':len(changed),
      'unchanged_entries_preserve_compressed_data':count-len(changed)},indent=2))


if __name__=='__main__':main()
