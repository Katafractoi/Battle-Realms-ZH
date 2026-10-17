"""Repack changed compressed entries, retaining all other physical H2O segments."""
import collections
import struct
import zlib
from patch_lte_h2o import literal_dcl

def repack_preserving_segments(source,replacements,decode):
    assert source[480]==0x1a and struct.unpack_from('<I',source,481)[0]==7
    count=struct.unpack_from('<I',source,485)[0]
    second=513+40*count
    assert source[513:second]==source[second:second+40*count]
    rows=[struct.unpack_from('<10I',source,513+40*i) for i in range(count)]
    owners=collections.defaultdict(list)
    for i,r in enumerate(rows):owners[r[6]].append(i)
    offsets=sorted(owners)
    ends={v:(offsets[j+1] if j+1<len(offsets) else len(source)) for j,v in enumerate(offsets)}
    result=bytearray(source[:offsets[0]])
    for offset in offsets:
        indexes=owners[offset]
        changed=[i for i in indexes if i in replacements]
        new_offset=len(result)
        if changed:
            assert len(indexes)==len(changed)==1,'Shared replacement segment'
            i=changed[0];r=rows[i]
            assert r[3]!=r[4],'Only verified compressed replacements supported'
            assert ends[offset]-offset==r[4]+12,'Unexpected replacement segment tail'
            raw=replacements[i];packed=literal_dcl(raw)
            assert decode(packed,len(raw))==raw
            crc=zlib.crc32(raw)
            result.extend(struct.pack('<III',len(packed),len(raw),crc));result.extend(packed)
            for table in [513,second]:
                for slot,value in [(3,len(raw)),(4,len(packed)),(8,crc)]:struct.pack_into('<I',result,table+i*40+slot*4,value)
        else:
            result.extend(source[offset:ends[offset]])
        for i in indexes:
            for table in [513,second]:struct.pack_into('<I',result,table+i*40+24,new_offset)
    return bytes(result)
