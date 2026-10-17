"""Unchanged cmap reader from the existing font-source audit."""
from pathlib import Path
import struct

def cmap(path):
    b=Path(path).read_bytes();base=struct.unpack_from('>I',b,12)[0]if b[:4]==b'ttcf'else 0
    n=struct.unpack_from('>H',b,base+4)[0];tables={b[base+12+16*i:base+16+16*i]:struct.unpack_from('>II',b,base+20+16*i)for i in range(n)}
    at,size=tables[b'cmap'];count=struct.unpack_from('>H',b,at+2)[0];out={}
    for i in range(count):
        platform,encoding,off=struct.unpack_from('>HHI',b,at+4+8*i)
        if platform not in (0,3):continue
        p=at+off;form=struct.unpack_from('>H',b,p)[0]
        if form==12:
            groups=struct.unpack_from('>I',b,p+12)[0]
            for j in range(groups):
                start,end,first=struct.unpack_from('>III',b,p+16+12*j)
                for cp in range(start,min(end,65535)+1):
                    if first+cp-start:out[cp]=first+cp-start
        elif form==4:
            segs=struct.unpack_from('>H',b,p+6)[0]//2
            ends=struct.unpack_from('>'+str(segs)+'H',b,p+14);starts=struct.unpack_from('>'+str(segs)+'H',b,p+16+2*segs);deltas=struct.unpack_from('>'+str(segs)+'h',b,p+16+4*segs);rp=p+16+6*segs;ranges=struct.unpack_from('>'+str(segs)+'H',b,rp)
            for j in range(segs):
                for cp in range(starts[j],min(ends[j],65534)+1):
                    if ranges[j]:
                        glyph=struct.unpack_from('>H',b,rp+2*j+ranges[j]+2*(cp-starts[j]))[0];glyph=(glyph+deltas[j])&65535 if glyph else 0
                    else:glyph=(cp+deltas[j])&65535
                    if glyph:out.setdefault(cp,glyph)
    return out
