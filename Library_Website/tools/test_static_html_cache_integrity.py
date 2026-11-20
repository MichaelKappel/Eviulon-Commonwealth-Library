#!/usr/bin/env python3
"""Fast adversarial tests: never accept static HTML solely from filesystem mtimes."""
from __future__ import annotations
import hashlib, importlib.util, json, os, pathlib, tempfile

def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    module_file=pathlib.Path(__file__).with_name('build_static_html.py')
    spec=importlib.util.spec_from_file_location('eviulon_cache_builder_under_test', module_file)
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    with tempfile.TemporaryDirectory(prefix='eviulon-static-cache-integrity-') as td:
        root=pathlib.Path(td);cache=root/'html-cache';cache.mkdir()
        (root/'RELEASE_ID.txt').write_text('fixture-release\n')
        builder.ROOT=root;builder.CACHE=cache;builder.MANIFEST=cache/'manifest.json';builder.CHECKPOINT=cache/'.render-checkpoint.json'
        mapping={'/book-one/1/':'books/book-one/1.html','/research/eviulon/report-one/1/':'research/eviulon/report-one/1.html'}
        builder.routes=lambda:mapping
        state={'digest':'source_v1','text':'original','calls':0}
        builder.dependencies=lambda:state['digest']
        def render(route):
            state['calls']+=1
            return ('<!doctype html><html><head><link rel="canonical" href="'+builder.BASE+route+'">'
                '<script type="application/ld+json">{}</script></head><body><main>'+
                state['text']+'—'+route+'</main></body></html>').encode()
        builder.render=render
        # Source had older mtime than a forged/stale cached page; no manifest.
        for rel in mapping.values():
            f=cache/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b'<!doctype html><stale>')
            os.utime(f,(4102444800,4102444800))
        builder.build()
        assert state['calls']==2,'Cache reused without trustworthy content provenance'
        assert not builder.CHECKPOINT.exists()
        # Verified complete manifest: zero dynamic regeneration needed.
        state['calls']=0;builder.build()
        assert state['calls']==0,'Verified unchanged snapshot was unnecessarily re-rendered'
        # An attacker or broken copy corrupts just one snapshot and forges its mtime.
        f=cache/mapping['/book-one/1/'];f.write_bytes(b'<!doctype html>altered');os.utime(f,(4102444800,4102444800))
        state['calls']=0;builder.build()
        assert state['calls']==1,'Per-snapshot SHA-256 corruption was not detected'
        # Source bytes change while file modified times are deliberately preserved.
        state.update(digest='source_v2',text='correct-new-content',calls=0)
        for rel in mapping.values():os.utime(cache/rel,(4102444800,4102444800))
        builder.build()
        assert state['calls']==2,'Changed source digest did not invalidate old snapshots'
        assert all(b'correct-new-content' in (cache/rel).read_bytes() for rel in mapping.values())
        # Simulate interrupted build with one checkpointed good snapshot.
        current=json.loads(builder.MANIFEST.read_text());first=current['snapshots'][0]
        builder.MANIFEST.unlink();(cache/mapping['/research/eviulon/report-one/1/']).unlink()
        builder.CHECKPOINT.write_text(json.dumps({'dependency_sha256':'source_v2','snapshots':[first]}))
        state['calls']=0;builder.build()
        assert state['calls']==1,'Interrupted build did not resume verified item safely'
        assert not builder.CHECKPOINT.exists(),'Finished build left stale checkpoint'
        # Even a syntactically valid checkpoint with an old digest cannot authorize reuse.
        builder.CHECKPOINT.write_text(json.dumps({'dependency_sha256':'source_v1','snapshots':current['snapshots']}))
        state['calls']=0;builder.build()
        assert state['calls']==0,'Valid completed manifest should remain authoritative'
        assert not builder.CHECKPOINT.exists()
    print('PASS: static HTML build safety (no mtime trust, digest invalidation, per-page SHA, resumable checkpoints, atomic completion)')
if __name__=='__main__':main()
