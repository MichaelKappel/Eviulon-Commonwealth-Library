#!/usr/bin/env python3
"""Create heading-only discovery index from the actual page-block JSON.
No generated prose, no full text export, no dependency beyond Python stdlib.
"""
import json,re,pathlib,unicodedata
ROOT=pathlib.Path(__file__).resolve().parents[1]; DATA=ROOT/'data'
books=json.loads((DATA/'books.json').read_text(encoding='utf-8'))
# These cutoffs exclude pre-content table of contents pages without losing verified chapters.
cutoff={1:5,2:5,3:7,4:4,5:4,6:5,7:5,8:3,9:3,10:5,11:4,12:4,13:4,14:3}
starts=re.compile(r'^(chapter\s+(?:\d+|[IVXLC]+|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Thirteen|Fourteen|Fifteen|Sixteen|Seventeen|Eighteen|Nineteen|Twenty|Twenty-One|Twenty-Two)\b|part\s+(?:[IVXLC]+|one|two|three|four|five|six|\d+)\b|prologue\b|epilogue\b|preface\b|introduction\b|conclusion\b|appendix\s+[A-Z0-9]+\b|afterword\b|foundational declaration\b)',re.I)
kind_re=re.compile(r'^(chapter|part|prologue|epilogue|preface|introduction|conclusion|appendix|afterword|foundational declaration)',re.I)

def tight(s):return ' '.join(s.split())
def valid_title(s): return bool(starts.match(s)) and len(s)<160

def read_book(b):
    ans=[]; last_key=set()
    for n in range(cutoff[b['number']],b['page_count']+1):
        path=DATA/'pages'/b['slug']/f'{n:04d}.json'
        page=json.loads(path.read_text(encoding='utf-8'))
        blocks=page['blocks']
        for idx,block in enumerate(blocks):
            raw=tight(block.get('text',''))
            if not valid_title(raw):continue
            if block.get('kind')!='heading' and idx>1:continue
            # Body blocks starting a chapter count only as a heading when at the very
            # beginning of a printed page, to avoid capturing prose or contents lists.
            if block.get('kind')!='heading' and not raw.lower().startswith(('chapter ','part ','appendix ')):continue
            rest=blocks[idx+1] if idx+1<len(blocks) else None
            label=raw
            # Printer line wrap can split the section heading across two blocks.
            if rest:
                suffix=tight(rest.get('text',''))
                need_more=(raw.endswith((':','—','-','·')) or
                           raw.lower().endswith(('the','to','of','and','we','with','without','rights','memory,','mind,','rights,','are','whose')) or
                           (raw.lower().startswith(('chapter ','preface','introduction','part ')) and len(raw)<26))
                if (need_more and suffix and len(suffix)<=75 and
                    not re.search(r'[.!?]$',suffix) and
                    not valid_title(suffix)):
                    label=raw.rstrip()+ ' '+suffix
            label=tight(label)
            if len(label)>180:label=raw
            category=kind_re.match(label).group(1).lower()
            if category=='foundational declaration':category='declaration'
            anchor=f'section-{n}-{idx+1}'
            key=(n,idx)
            if key in last_key:continue
            last_key.add(key)
            ans.append({'title':label,'category':category,'page':n,'block_index':idx,'anchor':anchor,'url':f"/{b['slug']}/{n}/#{anchor}"})
    return ans

def main():
    counts={}
    for b in books:
        sections=read_book(b)
        target=DATA/'sections'/f"{b['slug']}.json"
        target.write_text(json.dumps(sections,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        counts[b['slug']]=len(sections)
        print(f"{b['number']:02d}: {len(sections)} anchors, {sum(x['category']=='chapter' for x in sections)} chapters, {b['title']}")
    print('Total:',sum(counts.values()))
if __name__=='__main__':main()
