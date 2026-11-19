#!/usr/bin/env python3
"""Real HTTP regression for research reference links (stdlib, no paid services)."""
import argparse
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.request import urlopen


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.in_research = False
        self.depth = 0
        self.in_anchor = False
        self.link = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "article" and "research-body" in attributes.get("class", "").split():
            self.in_research = True
            self.depth = 1
            return
        if not self.in_research:
            return
        if tag not in ("area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"):
            self.depth += 1
        if tag == "a":
            self.in_anchor = True
            self.link = {"href": attributes.get("href", ""), "rel": attributes.get("rel", ""), "target": attributes.get("target", ""), "label": ""}

    def handle_endtag(self, tag):
        if not self.in_research:
            return
        if tag == "a" and self.in_anchor:
            self.links.append(self.link)
            self.in_anchor = False
            self.link = None
        self.depth -= 1
        if self.depth <= 0:
            self.in_research = False

    def handle_data(self, data):
        if self.in_anchor and self.link is not None:
            self.link["label"] += data


def fetch(base, path):
    with urlopen(base.rstrip("/") + path, timeout=20) as reply:
        if reply.status != 200:
            raise AssertionError(f"{path}: expected 200, got {reply.status}")
        return reply.read().decode("utf-8")


def run(base):
    examples = {
        "/research/eviulon/eviulon-library-preservation-audit/6/": (
            "https://eviulon.com/.well-known/eviulon-agent-entry.json",
            "https://library.eviulon.com/",
        ),
        "/research/eviulon/eviulon-ai-access-architecture/3/": (
            "https://json-schema.org/draft/2020-12/schema",
            "https://api.eviulon.org/mcp",
        ),
    }
    total = 0
    for path, targets in examples.items():
        parser = Links()
        html = fetch(base, path)
        parser.feed(html)
        assert parser.links, f"no research links found: {path}"
        for target in targets:
            candidates = [r for r in parser.links if r["href"] == target]
            assert candidates, f"unlinked expected URL {target} on {path}"
            for record in candidates:
                assert record["label"].strip(), (path, target, "empty link")
                assert urlparse(record["href"]).scheme in ("http", "https")
            total += 1
        new = [r for r in parser.links if "external" in r["rel"].split()]
        assert new, f"no plain URL linkified on {path}"
        for link in new:
            assert link["target"] == "_blank" and "noopener" in link["rel"].split()
            assert not link["href"].lower().startswith(("javascript:", "data:", "file:"))
            total += 1
    # Previously-linked references must remain anchored and readable.
    old = Links()
    old.feed(fetch(base, "/research/eviulon/eviulon-infrastructure-resilience-plan/5/"))
    assert any(link["href"] == "https://www.merriam-webster.com/dictionary/evulgate" for link in old.links)
    total += 1
    print(f"PASS: {total} live HTTP link checks across three real research sections (local or specified host)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--http", required=True, help="base URL of test server")
    args = p.parse_args()
    run(args.http)
