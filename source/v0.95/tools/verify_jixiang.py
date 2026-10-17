"""Verify documented Jixiang raster generation against a selected snapshot copy."""
import argparse
import io
from pathlib import Path
from PIL import Image,ImageFont
import br_review_common as core
from br_review_common import load,sha,raw_entry
from font_codec import parse_lfr,render
from build_resources import ROOT

def verify(resource_root,ttf,blast_dll):
    cfg=load(ROOT/'font/generator-config.json')
    if sha(ttf.read_bytes())!=cfg['sourceFontSha256']:raise ValueError('Jixiang source hash mismatch')
    core.DEC=core.decoder(blast_dll)
    source=(resource_root/'Interface/Interface_Text.H2O').read_bytes()
    mapping=load(ROOT/'tools/interface-font-entry-map.json')
    groups=parse_lfr(raw_entry(source,0))[3]
    cache={};checked=0
    for size,uvh,names,glyphs in groups:
        face=ImageFont.truetype(str(ttf),size);by={g[1]:g for g in glyphs};height=round(uvh*512)
        for cp in cfg['regeneratedCodepoints']:
            g=by[cp];name=names[g[0]]
            if name not in cache:cache[name]=Image.open(io.BytesIO(raw_entry(source,mapping['Fonts\\'+name]))).convert('RGBA')
            x,y,w=round(g[4]*512),round(g[5]*512),round(g[2])
            if cache[name].getchannel('A').crop((x,y,x+w,y+height)).tobytes()!=render(chr(cp),face,w,height).tobytes():raise ValueError('Jixiang raster differs: '+str((size,cp)))
            checked+=1
    return {'documentedCharacters':len(cfg['regeneratedCodepoints']),'verifiedGlyphRecords':checked,
            'groups':len(groups),'fullAtlasFromTtfOnlyRebuildClaimed':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('resource-root','ttf','blast-dll'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();print(verify(a.resource_root,a.ttf,a.blast_dll))
