"""Existing BRZHDP1 reader and physical-span helper."""
import gzip, io, struct
from br_review_common import sha, index

def make_patch(source, target, is_map=False):
    """Existing span-based COPY/DATA format; map bodies use common prefix/suffix."""
    ops = []
    def data(raw):
        if raw: ops.append((1, raw))
    def copy(off, count):
        if count: ops.append((0, off, count))
    if source[480:481] == target[480:481] == b'\x1a':
        src = spans(source)
        dst = spans(target)
        matches = {sha(source[a:b]):(a,b-a) for a,b in src}
        data(target[:dst[0][0]])
        for n,(a,b) in enumerate(dst):
            match = matches.get(sha(target[a:b]))
            if match:
                copy(*match)
            elif is_map:
                # Text hotfixes retain the archive order and resource names.
                x,y = src[n]
                old,new = source[x:y],target[a:b]
                prefix = 0
                for u,v in zip(old,new):
                    if u != v: break
                    prefix += 1
                suffix = 0
                maximum = min(len(old),len(new)) - prefix
                while suffix + 65536 <= maximum and old[len(old)-suffix-65536:len(old)-suffix or None] == new[len(new)-suffix-65536:len(new)-suffix or None]:
                    suffix += 65536
                while suffix < maximum and old[len(old)-suffix-1] == new[len(new)-suffix-1]:
                    suffix += 1
                copy(x,prefix)
                data(new[prefix:len(new)-suffix if suffix else None])
                copy(y-suffix,suffix)
            else:
                data(target[a:b])
    else:
        data(target)
    stream = io.BytesIO()
    stream.write(b'BRZHDP1\0')
    for op in ops:
        if op[0] == 0:
            stream.write(struct.pack('<BQQ',*op))
        else:
            stream.write(struct.pack('<BQ',1,len(op[1])))
            stream.write(op[1])
    stream.write(b'\xff')
    return gzip.compress(stream.getvalue(),compresslevel=9,mtime=0)

def spans(blob):
    offsets=sorted(set(r[6]for r in index(blob)))
    return [(off,offsets[j+1]if j+1<len(offsets)else len(blob))for j,off in enumerate(offsets)]

def apply_patch(source,patch):
    f=io.BytesIO(gzip.decompress(patch));assert f.read(8)==b'BRZHDP1\0';out=bytearray()
    while True:
        tag=f.read(1)
        if tag==b'\xff':break
        if tag==b'\0':
            off,count=struct.unpack('<QQ',f.read(16));assert off+count<=len(source);out.extend(source[off:off+count])
        elif tag==b'\1':
            count=struct.unpack('<Q',f.read(8))[0];data=f.read(count);assert len(data)==count;out.extend(data)
        else:raise ValueError('Bad patch operation')
    assert not f.read();return bytes(out)
