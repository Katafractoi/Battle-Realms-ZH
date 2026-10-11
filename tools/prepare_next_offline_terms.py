"""Prepare reversible, source-keyed wording edits without touching game assets."""
from pathlib import Path
import csv, json, hashlib

src = Path('translations/interface-baseline.csv')
dst = Path('translations/interface-next-review.csv')
rows = list(csv.DictReader(src.open(encoding='utf-8-sig', newline='')))
fields = list(rows[0])
changes = []

for row in rows:
    name, ident, english = row['source_file'], int(row['string_id']), row['english']
    old, new = row['chinese'], row['chinese']
    if name.endswith('Front_End.lte') and ident == 87:
        assert english == 'Mature' and not old
        new = '血腥效果'
    elif name.endswith('Console_Tooltips.lte') and 434 <= ident <= 437:
        assert english.endswith('Unit Alchemy') and old.endswith('单位炼化')
        new = old.removesuffix('单位炼化') + '兵种训练'
    elif name.endswith('Console_Tooltips.lte') and 510 <= ident <= 513:
        assert english.endswith('Tech Tree') and old.endswith('技术树')
        new = old.removesuffix('技术树') + '科技树'
    elif name.endswith('Game_Keys.lte') and ident == 1015:
        assert english == 'Tech tree'
        new = '科技树'
    elif '战技' in old and ('Battle Gear' in english or 'BattleGear' in english or 'Battlegear' in english or 'battle gear' in english):
        new = old.replace('战技', '技能')
    elif name.endswith('Game_Keys.lte') and english.startswith('Cycle through '):
        assert ident in (1003, 1006, 1007, 1009, 1072)
        if ident in (1006, 1007):
            target = '农舍' if ident == 1006 else '闲置农民'
            new = '依次选中' + target
        else:
            target = {1003: '建筑起火警报', 1009: '战斗警报', 1072: '最近消息的位置'}[ident]
            new = '依次查看' + target
    if new != old:
        row['chinese'] = new
        row['status'] = '显示反馈离线修订，待实机验证'
        row['note'] = (row['note'] + ' | ' if row['note'] else '') + '2026-10-11 显示反馈；按源字段修订'
        changes.append({'source_file': name, 'string_id': ident, 'english': english, 'before': old, 'after': new})

assert len(rows) == 4346
assert len(changes) >= 60
with dst.open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
report = {'source_sha256': hashlib.sha256(src.read_bytes()).hexdigest(),
          'draft_sha256': hashlib.sha256(dst.read_bytes()).hexdigest(),
          'source_rows': len(rows), 'changed_rows': len(changes), 'changes': changes,
          'installed': False}
Path('experiments/next-offline-terms-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'draft': str(dst), 'changed_rows': len(changes), 'source_sha256': report['source_sha256'], 'draft_sha256': report['draft_sha256']}, ensure_ascii=True))
