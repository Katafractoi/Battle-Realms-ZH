"""Create a bounded wrap experiment on top of confirmed wording edits."""
from pathlib import Path
import csv, json, hashlib, re

source = Path('translations/interface-next-review.csv')
target = Path('experiments/interface-v13-wrap-diagnostic.csv')
rows = list(csv.DictReader(source.open(encoding='utf-8-sig', newline='')))
fields = list(rows[0])

def break_hanzi_runs(text, max_run=5):
    # ASCII spaces are present in all shipped Western-language comparators;
    # insert them only inside uninterrupted CJK runs for a diagnostic candidate.
    out, run = [], 0
    for char in text:
        is_cjk = '\u3400' <= char <= '\u9fff'
        if is_cjk and run >= max_run:
            out.append(' ')
            run = 0
        out.append(char)
        run = run + 1 if is_cjk else 0
    return ''.join(out)

changes=[]
for row in rows:
    name, ident = row['source_file'], int(row['string_id'])
    old = row['chinese']
    if name == r'Text\ENG\WOTW_Console_Tooltips.lte' and ident == 663:
        # One short, still unspaced CJK string, to test length independent of spaces.
        new = '原地坚守'
    elif name == r'Text\ENG\WOTW_Console_Tooltips.lte' and ident == 664:
        # Retain the entire description, but give the word wrapper break points.
        new = break_hanzi_runs(old)
    elif name in (r'Text\ENG\Goals.lte',r'Text\ENG\WOTW_Goals.lte') and ident == 10:
        new = break_hanzi_runs(old)
    else:
        continue
    assert new != old
    row['chinese'] = new
    row['status'] = '受控折行诊断候选，待实机验收'
    row['note'] = (row['note'] + ' | ' if row['note'] else '') + 'v13：仅诊断长串中文自动折行；空格待结果后处理'
    changes.append({'source_file':name,'string_id':ident,'old':old,'new':new,
                    'old_ascii_spaces':old.count(' '),'new_ascii_spaces':new.count(' ')})

assert len(changes)==4
with target.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
Path('experiments/v13-wrap-experiment.json').write_text(json.dumps({'changes':changes,
    'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'candidate_csv_sha256':hashlib.sha256(target.read_bytes()).hexdigest()},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'changed':len(changes),'csv_sha256':hashlib.sha256(target.read_bytes()).hexdigest()},ensure_ascii=True))
