"""Existing v0.95 validation; baseline is the selected release snapshot."""
from br_review_common import *

def validate_edits(input_rows,baseline):
    by={r['key']:r for r in baseline['rows']};seen=set();changes={};risks=[]
    adv=load(PACKAGE/'font-advances32.json')['advance']
    for e in input_rows:
        if not isinstance(e,dict) or set(e)!={'key','new','action'} or any(not isinstance(e[k],str)for k in e):raise ValueError('Edit fields must be strings')
        key=e['key']
        if key in seen or key not in by:raise ValueError('Unknown/duplicate key '+key)
        seen.add(key);r=by[key];new=e['new'];action=e['action'] or 'AUTO'
        if action not in ('AUTO','KEEP','SET','CLEAR'):raise ValueError('Action must be AUTO/KEEP/SET/CLEAR')
        if action=='KEEP':
            if new:raise ValueError('KEEP with nonempty New Chinese')
            continue
        if action=='AUTO' and not new:continue
        if action=='CLEAR':
            if new:raise ValueError('CLEAR requires empty New Chinese')
            if tokens(r['rawText']):raise ValueError('Cannot clear required format placeholders')
            new=''
        elif not new:raise ValueError('SET requires text; use CLEAR to empty intentionally')
        safe_unicode(new)
        if action!='CLEAR':
            if tokens(new)!=tokens(r['rawText']):raise ValueError('Format token sequence changed '+key)
            if (whitespace(new)!=whitespace(r['rawText']) or controls(new)!=controls(r['rawText'])):raise ValueError('Whitespace/control sequence changed '+key)
        if r['kind']=='ini_name':
            new.encode('cp936')
            if '\r'in new or '\n'in new or '\0'in new:raise ValueError('INI Name line injection')
        if r['kind']=='map_title' and len((new+'\0').encode('utf-16le'))//2>256:raise ValueError('Map title exceeds verified length bound')
        if new==r['rawText']:continue
        changes[key]=new;m=width(new,adv);reasons=[]
        if r['kind']!='ini_name' and m['missingGlyphs']:reasons.append('缺少字体字形；禁止自动补字或换字体')
        if r['budget'] is not None and m['maxAdvance']>r['budget']+.01:reasons.append('行宽超出已标定预算')
        if r['budget'] is None:reasons.append('控件宽度未完整标定，须人工实机确认')
        if len(new)>len(r['current']):reasons.append('字数增加')
        if re.findall(r'\d+(?:\.\d+)?',new)!=re.findall(r'\d+(?:\.\d+)?',r['rawText']):reasons.append('文字中的数字发生变化')
        if action=='CLEAR':reasons.append('显式清空；地图将使用保留的文件名回退')
        risks.append({'key':key,'before':r['current'],'after':new,'action':action,'budget':r['budget'],'measurementNominal':32,'beforeMeasure':r['measure'],'afterMeasure':m,'reasons':reasons,'blocksCandidate':bool(r['kind']!='ini_name' and m['missingGlyphs'])})
    return changes,risks
