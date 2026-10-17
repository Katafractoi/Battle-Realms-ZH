"""Portable subset of the existing v0.95 text-only review core."""
from pathlib import Path
import collections, hashlib, json, re, struct, unicodedata, zlib
from patch_lte_h2o import decoder, records, literal_dcl
from font_codec import parse_lfr
from br_repack_preserve_raw import repack_preserving_segments
HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent / 'translations'
DEC = None
TOKEN_RE = re.compile(r'%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[hlL]?[diuoxXfFeEgGaAcspn%]|\{[^{}\r\n]*\}|<[/!A-Za-z][^<>\r\n]*>|\\[nrt0]')

def sha(b): return hashlib.sha256(b).hexdigest().upper()

def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def save(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def index(blob):
    if blob[480] != 0x1a or struct.unpack_from('<I',blob,481)[0] != 7: raise ValueError('Not H2O v7')
    n = struct.unpack_from('<I',blob,485)[0]
    if blob[513:513+40*n] != blob[513+40*n:513+80*n]: raise ValueError('Duplicate H2O indexes differ')
    return [struct.unpack_from('<10I',blob,513+40*i) for i in range(n)]


def raw_entry(blob, i):
    r=index(blob)[i]
    if r[3]==r[4]: return blob[r[6]:r[6]+r[3]]
    raw=DEC(blob[r[6]+12:r[6]+12+r[4]],r[3])
    if zlib.crc32(raw)!=r[8]: raise ValueError(f'Entry CRC {i}')
    return raw

def map_title(raw):
    if raw[4]!=0: raise ValueError('Unexpected map title type')
    units=struct.unpack_from('<I',raw,5)[0]
    if units>256: raise ValueError('Map title bounds')
    wire=raw[9:9+2*units]
    if units and not wire.endswith(b'\0\0'): raise ValueError('Map title terminator')
    return wire[:-2].decode('utf-16le') if units else '', 9+2*units

def whitespace(s): return ''.join(c for c in s if c.isspace())

def controls(s): return [f'U+{ord(c):04X}' for c in s if unicodedata.category(c) in ('Cc','Cf')]

def tokens(s): return TOKEN_RE.findall(s)

def safe_unicode(s):
    if len(s)>32767: raise ValueError('Excel cell exceeds 32767 characters')
    if any((ord(c)<32 and c not in '\t\n\r') or 0xD800<=ord(c)<=0xDFFF or ord(c) in (0xfffe,0xffff) for c in s): raise ValueError('Invalid XML/Unicode control character')
    s.encode('utf-16le')

def width(s, advances):
    missing=sorted(set(c for c in s if c not in '\n\r\t' and str(ord(c)) not in advances))
    lines=[sum(advances.get(str(ord(c)),0) for c in line if c not in '\r\t') for line in s.split('\n')]
    return {'lineAdvances':lines,'maxAdvance':max(lines,default=0),'missingGlyphs':missing,'hasTab':'\t' in s}

def repack_raw(source, replacements):
    """Rebuild raw map segments only. Name table and all non-title bytes persist."""
    rows=index(source); owners=collections.defaultdict(list)
    for i,r in enumerate(rows): owners[r[6]].append(i)
    offsets=sorted(owners); ends={v:offsets[j+1] if j+1<len(offsets) else len(source) for j,v in enumerate(offsets)}
    out=bytearray(source[:offsets[0]])
    for off in offsets:
        ids=owners[off]; changed=[i for i in ids if i in replacements]; newoff=len(out)
        if changed:
            if len(ids)!=1: raise ValueError('Shared raw map segment')
            i=ids[0];r=rows[i]
            if r[3]!=r[4] or ends[off]-off!=r[3]: raise ValueError('Unexpected raw map segment')
            raw=replacements[i];out.extend(raw)
            for tab in (513,513+40*len(rows)):
                for slot,val in ((3,len(raw)),(4,len(raw)),(8,zlib.crc32(raw))):struct.pack_into('<I',out,tab+40*i+4*slot,val)
        else:out.extend(source[off:ends[off]])
        for i in ids:
            for tab in (513,513+40*len(rows)):struct.pack_into('<I',out,tab+40*i+24,newoff)
    return bytes(out)

def rebuild(blob, rows, edits):
    if not edits:return blob
    if all(r['kind']=='ini_name' for r in rows):
        if len(edits)!=1:raise ValueError('INI has one authorized Name field')
        row=next(r for r in rows if r['key'] in edits);old=row['rawText'].encode('cp936');new=edits[row['key']].encode('cp936')
        before=b'Name='+old;after=b'Name='+new
        if blob.count(before+b'\r\n')!=1:raise ValueError('INI Name baseline mismatch')
        return blob.replace(before+b'\r\n',after+b'\r\n',1)
    grouped=collections.defaultdict(list)
    for r in rows:
        if r['key'] in edits:grouped[r['entry']].append(r)
    replaced={}
    for i,items in grouped.items():
        raw=raw_entry(blob,i)
        if items[0]['kind']=='map_title':
            if len(items)!=1:raise ValueError('Duplicate map title')
            r=items[0];old,end=map_title(raw)
            if old!=r['rawText']:raise ValueError('Map baseline differs')
            s=edits[r['key']];body=(s+'\0').encode('utf-16le') if s else b''
            replaced[i]=raw[:5]+struct.pack('<I',len(body)//2)+body+raw[end:]
        else:
            changes={r['id']:(r['rawText'],edits[r['key']]) for r in items};out=bytearray(raw[:8]);seen=set()
            for ident,marker,text,wire in records(raw):
                if ident in changes:
                    old,new=changes[ident]
                    if old!=text:raise ValueError('LTE baseline differs')
                    body=(new+'\0').encode('utf-16le');out+=struct.pack('<iBi',ident,marker,len(body)//2)+body;seen.add(ident)
                else:out+=wire
            if seen!=set(changes):raise ValueError('Missing LTE ID')
            replaced[i]=bytes(out)
    if all(r['kind']=='map_title' for r in rows):return repack_raw(blob,replaced)
    return repack_preserving_segments(blob,replaced,DEC)

def verify_only_text(before,after,rows,edits):
    if not edits:
        if before!=after:raise ValueError('No-change roundtrip drift')
        return
    if rows[0]['kind']=='ini_name':
        r=rows[0]
        expected=before.replace(b'Name='+r['rawText'].encode('cp936')+b'\r\n',b'Name='+edits[r['key']].encode('cp936')+b'\r\n',1)
        if expected!=after:raise ValueError('INI non-Name bytes changed')
        return
    allrows={r['entry']:r for r in rows if r['kind']=='map_title'}
    ltes=collections.defaultdict(dict)
    for r in rows:
        if r['kind']=='lte':ltes[r['entry']][r['id']]=r
    a,b=index(before),index(after)
    if len(a)!=len(b):raise ValueError('Entry count changed')
    start=513+80*len(a)
    if before[:513]!=after[:513] or before[start:min(r[6] for r in a)]!=after[start:min(r[6] for r in b)]:raise ValueError('Archive header/name metadata changed')
    for i,(ra,rb) in enumerate(zip(a,b)):
        changed=[r for r in rows if r['entry']==i and r['key'] in edits]
        if not changed:
            # Compare entire physical storage, including original compression headers.
            ao=min([r[6] for r in a if r[6]>ra[6]]+[len(before)])
            bo=min([r[6] for r in b if r[6]>rb[6]]+[len(after)])
            if before[ra[6]:ao]!=after[rb[6]:bo]:raise ValueError(f'Untouched physical segment changed {i}')
        elif i in allrows:
            old=raw_entry(before,i);new=raw_entry(after,i);ot,oe=map_title(old);nt,ne=map_title(new)
            if old[:5]!=new[:5] or old[oe:]!=new[ne:] or nt!=edits[allrows[i]['key']]:raise ValueError('Non-title map bytes changed')
        else:
            old=list(records(raw_entry(before,i)));new=list(records(raw_entry(after,i)))
            if len(old)!=len(new):raise ValueError('LTE count changed')
            for x,y in zip(old,new):
                r=ltes[i].get(x[0]);expected=edits.get(r['key'],x[2]) if r else x[2]
                if x[:2]!=y[:2] or expected!=y[2] or (expected==x[2] and x[3]!=y[3]):raise ValueError('Unauthorized LTE record delta')
