#!/usr/bin/env python3
"""Fail closed before any public GitHub push. Stdlib only."""
import json,sys,re
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
errors=[]
for p in root.rglob('*'):
    if not p.is_file(): continue
    rel=p.relative_to(root).as_posix(); low=rel.lower()
    if '.git/' in low or p.name in ('.DS_Store',): continue
    if any(part in ('pages','search','monitor-logs','Shared_Research_and_UAI') for part in p.relative_to(root).parts) and rel.startswith(('Library_Website/data/','Library_Source/')):
        errors.append('restricted content path: '+rel)
    if p.suffix.lower() in ('.pdf','.epub','.mobi','.zip','.7z','.tar','.rar','.docx','.pptx'):
        errors.append('full source/download artifact: '+rel)
    if 'library_source/library/' in low or 'library_source/docs/' in low:
        errors.append('private source path: '+rel)
    if re.search(r'(credential|secrets|password|private-key|monitor-config)\.(uai|json|php|txt)$', p.name,re.I) and not p.name.endswith('monitor-config.example.php'):
        errors.append('possible private record: '+rel)
    if p.suffix=='.uai' or p.name=='AGENTS.md' and rel!='AGENTS.md':
        text=p.read_text(encoding='utf-8')
        if set(''.join(text.splitlines()))-set('ᚠᚢᚦᚨᚱᚲᚷᚹᚺᚾᛁᛃᛇᛈᛉᛊ'):
            errors.append('non-runic local memory/AGENTS: '+rel)
readme=(root/'README.md').read_text(encoding='utf-8')
try:
    cat=json.loads((root/'Library_Source/metadata/books.json').read_text())['books']
    if len(cat)!=14 or sum(b['print_page_count'] for b in cat)!=1925: errors.append('catalog count mismatch')
    for b in cat:
        for k in ('canonical_book_url','canonical_first_page_url'):
            if b[k] not in readme: errors.append('README missing '+str(b['number'])+' '+k)
except Exception as exc: errors.append('bad catalog: '+str(exc))
if not (root/'AGENTS.md').exists():errors.append('missing public agent router')
if errors:
    print('PUBLIC REPOSITORY AUDIT FAIL\n'+'\n'.join(errors[:30]));sys.exit(1)
print('PUBLIC REPOSITORY AUDIT PASS: 14 book metadata records, no known private/full-text artifacts, deep links present')
