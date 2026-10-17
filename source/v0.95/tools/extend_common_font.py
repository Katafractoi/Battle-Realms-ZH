"""Build the separate +1500 Jixiang font upgrade in a fresh offline directory.

Uses the accepted renderer and append-only LFR algorithm. New atlas pages use
the glyph advance plus one pixel as their grid stride; existing glyphs never move.
"""
import argparse
import copy
import io
import json
import math
from pathlib import Path
from PIL import Image, ImageFont
import br_review_common as core
from br_review_common import load, save, sha, raw_entry, index
from font_codec import parse_lfr, serialize_lfr, render, tga_bytes
from font_cmap import cmap
from br_repack_preserve_raw import repack_preserving_segments
from resource_delta import make_patch, apply_patch, spans
from build_resources import ROOT

def build(resource_root, ttf, blast_dll, output):
    if output.exists():
        raise FileExistsError(output)
    config = load(ROOT/'font/generator-config.json')
    selected = load(ROOT/'font/extension-common1500.json')
    if sha(ttf.read_bytes()) != config['sourceFontSha256']:
        raise ValueError('Expected the unchanged approved Jixiang TTF')
    core.DEC = core.decoder(blast_dll)
    path = resource_root/'Interface/Interface_Text.H2O'
    source = path.read_bytes()
    manifest = load(ROOT/'resources/patch-manifest.json')
    expected = next(r['targetSha256'] for r in manifest['files'] if r['path']==r'Interface\Interface_Text.H2O')
    if sha(source) != expected:
        raise ValueError('Font upgrade requires the selected resource snapshot')
    mapping = load(ROOT/'tools/interface-font-entry-map.json')
    ver,s1,s2,groups,present = parse_lfr(raw_entry(source,0))
    original = copy.deepcopy(groups)
    added = sorted(r['codepoint'] for r in selected['rows'])
    if len(added)!=1500 or len(set(added))!=1500 or set(added)&present or set(added)-set(cmap(ttf)):
        raise ValueError('Extension list is not 1500 supported new codepoints')
    used = {name for g in groups for name in g[2]}
    spare = [p.removeprefix('Fonts\\') for p in mapping if p.lower().endswith('.tga') and p.removeprefix('Fonts\\') not in used]
    replacements, old_images, details = {}, {}, []
    atlas_images = {}
    for size,uvh,names,glyphs in groups:
        height = round(uvh*512)
        width = max(1,round(size*.72))
        last = len(names)-1
        image = Image.open(io.BytesIO(raw_entry(source,mapping['Fonts\\'+names[-1]]))).convert('RGBA')
        if image.size!=(512,512): raise ValueError('Atlas dimensions changed')
        old_images[names[-1]] = image.copy()
        rects = [(round(g[4]*512),round(g[5]*512),round(g[4]*512)+round(g[2]),round(g[5]*512)+height) for g in glyphs if g[0]==last]
        free = []
        # Preserve the existing last-page grid. Mapped empty glyph rectangles are reserved too.
        for y in range(0,512-height+1,height+1):
            for x in range(0,512-width+1,size+1):
                box=(x,y,x+width,y+height)
                overlaps=any(x<b[2] and x+width>b[0] and y<b[3] and y+height>b[1] for b in rects)
                if not overlaps and not image.getchannel('A').crop(box).getbbox():
                    free.append((last,x,y))
        cols,rows=512//(width+1),512//(height+1)
        capacity=cols*rows
        pages=math.ceil(max(0,len(added)-len(free))/capacity)
        if pages>len(spare):
            raise ValueError('Existing named atlas entries exhausted; archive expansion is not supported')
        images={last:image.copy()}
        slots=list(free)
        for _ in range(pages):
            name=spare.pop(0)
            names.append(name)
            page=len(names)-1
            images[page]=Image.new('RGBA',(512,512),(0,0,0,0))
            slots.extend((page,col*(width+1),row*(height+1)) for row in range(rows) for col in range(cols))
        face=ImageFont.truetype(str(ttf),size)
        for cp,(page,x,y) in zip(added,slots):
            alpha=render(chr(cp),face,width,height)
            if not alpha.getbbox(): raise ValueError('Blank new glyph')
            tile=Image.new('RGBA',(width,height),(255,255,255,0))
            tile.putalpha(alpha)
            if images[page].getchannel('A').crop((x,y,x+width,y+height)).getbbox():
                raise ValueError('New glyph overlaps existing pixels')
            images[page].paste(tile,(x,y))
            glyphs.append((page,cp,float(width),width/512,x/512,y/512))
        glyphs.sort(key=lambda g:g[1])
        for page,img in images.items():
            name=names[page]
            atlas_images[name]=img
            replacements[mapping['Fonts\\'+name]]=tga_bytes(img)
        details.append({'size':size,'height':height,'newAdvance':width,'existingAtlases':last+1,
                        'lastPageFreeSlots':len(free),'newPages':pages,'totalPages':len(names),'glyphsPerNewPage':capacity})
        print(json.dumps({'size':size,'newPages':pages,'newGlyphs':len(added)}),flush=True)
    replacements[0]=serialize_lfr(ver,s1,s2,groups)
    candidate=repack_preserving_segments(source,replacements,core.DEC)
    parsed=parse_lfr(raw_entry(candidate,0))
    checked=0
    decoded_images={name:Image.open(io.BytesIO(raw_entry(candidate,mapping['Fonts\\'+name]))).convert('RGBA') for name in atlas_images}
    for old,new in zip(original,parsed[3]):
        if old[0:2]!=new[0:2] or old[2]!=new[2][:len(old[2])]: raise ValueError('Existing font dimensions or page order changed')
        a={g[1]:g for g in old[3]};b={g[1]:g for g in new[3]}
        if set(b)!=set(a)|set(added) or any(a[cp]!=b[cp] for cp in a): raise ValueError('Existing glyph metrics or positions changed')
        for cp in a:
            g=a[cp];name=old[2][g[0]]
            if name in old_images:
                x,y,w=round(g[4]*512),round(g[5]*512),round(g[2]);h=round(old[1]*512)
                box=(x,y,x+w,y+h)
                if old_images[name].crop(box).tobytes()!=atlas_images[name].crop(box).tobytes(): raise ValueError('Existing glyph pixels changed')
        face=ImageFont.truetype(str(ttf),new[0])
        for cp in added:
            g=b[cp];name=new[2][g[0]];x,y,w=round(g[4]*512),round(g[5]*512),round(g[2]);h=round(new[1]*512)
            image=decoded_images[name]
            if image.getchannel('A').crop((x,y,x+w,y+h)).tobytes()!=render(chr(cp),face,w,h).tobytes(): raise ValueError('Generated glyph readback mismatch')
            checked+=1
    oldspans,newspans=spans(source),spans(candidate)
    oldindex,newindex=index(source),index(candidate)
    oldphysical={start:source[start:end] for start,end in oldspans}
    newphysical={start:candidate[start:end] for start,end in newspans}
    for i,(a,b) in enumerate(zip(oldindex,newindex)):
        if i not in replacements and oldphysical[a[6]]!=newphysical[b[6]]:
            raise ValueError('Unchanged physical entry changed')
    patch=make_patch(source,candidate)
    if apply_patch(source,patch)!=candidate: raise ValueError('Font upgrade delta readback failed')
    output.mkdir(parents=True)
    dest=output/'candidate/Interface/Interface_Text.H2O';dest.parent.mkdir(parents=True);dest.write_bytes(candidate)
    (output/'font-upgrade.brzh.gz').write_bytes(patch)
    newpages=sum(r['newPages'] for r in details)
    report={'schema':'brzh-font-upgrade/1','status':'offline-static-validation-passed','version':'v0.95',
            'baseSha256':sha(source),'candidateSha256':sha(candidate),'patchSha256':sha(patch),
            'newCharacters':len(added),'missingSelectedCharacters':0,'newGlyphRecords':checked,
            'baseMappedCodepoints':len(present),'candidateMappedCodepoints':len(parsed[4]),
            'baseCjkCodepoints':sum(0x3400<=cp<=0x9fff for cp in present),
            'candidateCjkCodepoints':sum(0x3400<=cp<=0x9fff for cp in parsed[4]),
            'existingGlyphMetricsAndPixelsPreserved':True,'nonfontPhysicalEntriesPreserved':True,
            'textureSize':[512,512],'newTexturePages':newpages,'newTextureRgbaBytes':newpages*512*512*4,
            'totalTexturePages':sum(len(g[2]) for g in groups),'remainingSpareNamedPages':len(spare),
            'newLfrGlyphRecordBytes':len(added)*20*len(groups),
            'sourceArchiveBytes':len(source),'candidateArchiveBytes':len(candidate),'archiveBytesIncrease':len(candidate)-len(source),
            'patchBytes':len(patch),'changedEntries':sorted(replacements),'groups':details,
            'engineLimits':{'codepointWireBits':16,'atlasIndexWireBits':16,'lfrAtlasCountWireBits':32,
                            'actualMaximumRuntimePages':'unknown; all existing H2O named entries retained; no runtime limit inferred from wire types'},
            'finalV095BaseAligned':load(ROOT/'package-status.json')['finalTextAligned'],
            'notVerified':['Game startup and rendering with the expanded atlas set','Actual GPU residency and device-specific memory behavior'],
            'deployment':'Separate one-time font upgrade. Later text-only hotfixes must bind to the upgraded snapshot hashes.',
            'ttfIncluded':False,'gameDirectoryWritten':False}
    save(output/'font-upgrade-report.json',report)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('resource-root','ttf','blast-dll','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    r=build(a.resource_root,a.ttf,a.blast_dll,a.output)
    print(json.dumps({k:v for k,v in r.items() if k not in ('groups','changedEntries')},ensure_ascii=True))
