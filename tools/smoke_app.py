"""Browser smoke test: does the BUILT app actually run?

This exists because four green checks (registry guard, tsc, 16/16 suite, state verifier) all passed
while the shipped bundle was throwing `ReferenceError: __DEFINES__ is not defined` at line 1 and
rendering a blank page. None of those checks loads the page, so none of them can see a broken app.

It asserts, against a served dist/:
  * zero uncaught page errors and zero console errors
  * #root actually has children (React mounted)
  * the UI's own node/edge counters equal the counts in src/data

Usage:
  python tools/smoke_app.py [--url http://localhost:8080] [--cdp http://127.0.0.1:9222]
Exit 1 on any failure; prints SKIP (exit 0) when no browser is reachable, so it never lies by pass.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"


def expected_counts():
    files = ["seed_graph.json"] + sorted(p.name for p in DATA.glob("expansion-*.json"))
    nodes = edges = 0
    for name in files:
        doc = json.loads((DATA / name).read_text(encoding="utf-8"))
        nodes += len(doc.get("nodes") or [])
        edges += len(doc.get("edges") or [])
    return nodes, edges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8080")
    ap.add_argument("--cdp", default="http://127.0.0.1:9222")
    ap.add_argument("--timeout", type=int, default=30)
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:  # pragma: no cover
        print("SKIP: playwright not importable (%s)" % e)
        return 0

    want_nodes, want_edges = expected_counts()
    errors, page_errors = [], []

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.connect_over_cdp(args.cdp)
        except Exception as e:
            print("SKIP: no browser at %s (%s)" % (args.cdp, str(e).splitlines()[0][:90]))
            return 0
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        try:
            page.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout * 1000)
        except Exception as e:
            # A browser was reachable but the app was not: that is a FAILURE, not a skip. A gate that
            # crashes here would exit 1 with a traceback and no diagnosis; a gate that skips would lie.
            print("FAIL: cannot load %s (%s)" % (args.url, str(e).splitlines()[0][:120]))
            print("      is the static server running?  serve_local.cmd  ->  http://localhost:8080")
            page.close()
            return 1
        try:
            page.wait_for_function(
                "() => { const r = document.getElementById('root'); return r && r.children.length > 0; }",
                timeout=args.timeout * 1000,
            )
        except Exception:
            pass
        text = page.evaluate("() => document.body.innerText || ''")
        mounted = page.evaluate(
            "() => { const r = document.getElementById('root'); return r ? r.children.length : 0; }")
        page.close()

    got_nodes = re.search(r"(\d+)\s+Nodes", text)
    got_edges = re.search(r"(\d+)\s+Edges", text)
    got_chunks = re.search(r"bundled corpus excerpt \((\d+) chunks\)", text)

    problems = []
    if page_errors:
        problems.append("uncaught page errors: %s" % page_errors[:3])
    if errors:
        problems.append("console errors: %s" % errors[:3])
    if mounted == 0:
        problems.append("#root is empty - React did not mount")
    if not got_nodes or int(got_nodes.group(1)) != want_nodes:
        problems.append("UI node count %s != data %d" % (got_nodes.group(0) if got_nodes else None, want_nodes))
    if not got_edges or int(got_edges.group(1)) != want_edges:
        problems.append("UI edge count %s != data %d" % (got_edges.group(0) if got_edges else None, want_edges))
    # Globbed like the expansion files and like tools/verify_app_state.py: a new evidence bundle
    # must never be silently invisible to a gate, or the gate can pass while the UI is wrong.
    chunk_bundles = [DATA / "seed-evidence.json"] + sorted(DATA.glob("evidence-bundle-*.json"))
    bundle_chunks = 0
    for b in chunk_bundles:
        if b.exists():
            bundle_chunks += len(json.loads(b.read_text(encoding="utf-8"))["chunks"])
    if not got_chunks or int(got_chunks.group(1)) != bundle_chunks:
        problems.append("UI provenance label says %s chunks, bundle has %d"
                        % (got_chunks.group(1) if got_chunks else None, bundle_chunks))

    print("smoke: url=%s  mounted=%s  nodes=%s  edges=%s  chunks=%s"
          % (args.url, mounted, got_nodes.group(1) if got_nodes else "?",
             got_edges.group(1) if got_edges else "?", got_chunks.group(1) if got_chunks else "?"))
    if problems:
        print("FAIL")
        for p in problems:
            print("  - " + p)
        return 1
    print("PASS - built app runs, React mounted, UI counters match src/data")
    return 0


if __name__ == "__main__":
    sys.exit(main())
