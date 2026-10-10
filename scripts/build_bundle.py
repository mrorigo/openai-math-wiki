#!/usr/bin/env python3
"""Regenerate the openai-math-wiki OKF bundle from a snapshot of github.com/openai/math.

Usage:  python3 build_bundle.py [math-root] [bundle-dir]
Defaults: math-root  = ../../math          (sibling of the wiki's parent)
          bundle-dir = ../bundle          (inside the wiki root)
"""
import json, os, re, sys, unicodedata
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(WIKI, "..", "math"))
BUNDLE = os.path.join(WIKI, "bundle")
GH = "https://github.com/openai/math"
RELEASE = "2026-10-06"          # OpenAI Math Release publication date

if len(sys.argv) > 1:
    REPO = sys.argv[1]
if len(sys.argv) > 2:
    BUNDLE = sys.argv[2]


# ---------------------------------------------------------------------------
# 1. CONTENTS.md -> families + papers (titles, abstracts, pdf paths, notes)
# ---------------------------------------------------------------------------
def parse_contents(repo):
    text = open(os.path.join(repo, "CONTENTS.md"), encoding="utf-8").read()
    idx = text.find("## Manuscript map")
    body = text[idx:] if idx != -1 else text

    families, papers = [], []
    lines = body.splitlines()
    i = 0
    cur_fam, cur_paper = None, None

    def flush():
        nonlocal cur_paper
        if cur_paper is not None:
            cur_paper["abstract"] = cur_paper["abstract"].strip()
            papers.append(cur_paper)
            cur_paper = None

    fam_re = re.compile(r'^\s*\*\*(\d{3})\.\s+(.+?)\*\*\s*(.*)$')
    paper_re = re.compile(r'^\s*&emsp;\[(.+?)\]\((.*)\)\s*(?:—\s*(.+))?\s*$')

    while i < len(lines):
        line = lines[i]
        mfam = fam_re.match(line)
        if mfam:
            flush()
            fam = {"num": int(mfam.group(1)),
                   "title": mfam.group(2).rstrip("."),
                   "desc": mfam.group(3), "papers": []}
            i += 1
            while i < len(lines):
                l2 = lines[i]
                if fam_re.match(l2) or paper_re.match(l2):
                    break
                if "</td>" in l2 or "</table>" in l2:
                    break
                if l2.strip() == "":
                    i += 1
                    continue
                fam["desc"] += " " + l2.strip()
                i += 1
            fam["desc"] = re.sub(r"\s+", " ", fam["desc"]).strip()
            families.append(fam)
            cur_fam = fam
            continue
        mpaper = paper_re.match(line)
        if mpaper:
            flush()
            cur_paper = {"title": mpaper.group(1), "pdf": mpaper.group(2),
                         "note": mpaper.group(3) or "", "abstract": ""}
            i += 1
            while i < len(lines):
                l2 = lines[i]
                if fam_re.match(l2) or paper_re.match(l2):
                    break
                if "</td>" in l2 or "</table>" in l2:
                    break
                cur_paper["abstract"] += l2 + "\n"
                i += 1
            if cur_fam is not None:
                cur_fam["papers"].append(cur_paper)
            continue
        i += 1
    flush()

    for f in families:
        if re.search(r"\(\[Lean\]\(lean/docs/\d{3}\.md\)\)", f["desc"]):
            f["lean_doc"] = True
        f["desc"] = re.sub(r"\s*\(\[Lean\]\([^)]*\)\)", "", f["desc"]).strip()
    return families, papers


# ---------------------------------------------------------------------------
# 2. overview.tex -> disciplines + family->discipline mapping
# ---------------------------------------------------------------------------
def read_group(s, i):
    depth = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("unbalanced braces")


def parse_overview(repo):
    tex = open(os.path.join(repo, "overview.tex"), encoding="utf-8").read()
    discs, fam_to_disc = [], {}
    cur = None
    pos = 0
    pat = re.compile(r"\\(cataloguesection|resultentry)\{")
    while True:
        m = pat.search(tex, pos)
        if not m:
            break
        cmd = m.group(1)
        p = m.end() - 1
        args = []
        while p < len(tex) and tex[p] == "{":
            g, p = read_group(tex, p)
            args.append(g)
        if cmd == "cataloguesection":
            if cur:
                discs.append(cur)
            cur = {"name": args[0], "subject": int(args[1]), "families": []}
        else:
            fid = int(args[0])
            cur["families"].append(fid)
            fam_to_disc[fid] = {"name": cur["name"], "subject": cur["subject"]}
        pos = p
    if cur:
        discs.append(cur)
    return discs, fam_to_disc


# ---------------------------------------------------------------------------
# 3. preprint READMEs + formalization.yaml + reasoning traces
# ---------------------------------------------------------------------------
def parse_meta(repo):
    months = {n: i for i, n in enumerate(
        ["January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December"], 1)}
    readme_meta = {}
    for d in sorted(os.listdir(os.path.join(repo, "preprints"))):
        rp = os.path.join(repo, "preprints", d, "README.md")
        if not os.path.exists(rp):
            continue
        txt = open(rp, encoding="utf-8", errors="replace").read()
        meta = {"date": None, "citation_key": None, "has_version_note": False}
        m = re.search(r"^Date:\s*(.+)$", txt, re.M)
        if m:
            mm = re.match(r"([A-Z][a-z]+)\s+(\d{1,2}),\s+(\d{4})", m.group(1).strip())
            if mm:
                meta["date"] = f"{mm.group(3)}-{months[mm.group(1)]:02d}-{int(mm.group(2)):02d}"
        m = re.search(r"@misc\{([^,]+),", txt)
        if m:
            meta["citation_key"] = m.group(1).strip()
        meta["has_version_note"] = "Version note" in txt
        readme_meta[d] = meta

    lean_txt = open(os.path.join(repo, "lean", "formalization.yaml"), encoding="utf-8").read()
    lean_pdfs = {f"preprints/{m.group(1)}" for m in
                 re.finditer(r"id:\s+\.\./preprints/(\S+)", lean_txt)}

    readme_top = open(os.path.join(repo, "README.md"), encoding="utf-8").read()
    traces = {int(m.group(1)): m.group(2) for m in
              re.finditer(r"\| (\d{3}) \| \[[^\]]+\]\((reasoning_traces/[^)]+\.pdf)\)", readme_top)}
    return readme_meta, lean_pdfs, traces


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower())
    return text.strip("-")


def clean_md(text):
    return re.sub(r"\s+", " ", text).strip()


def yaml_escape(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def front(title, type_, desc=None, resource=None, tags=None, ts=None):
    lines = ["---"]
    if title:
        lines.append(f"title: {yaml_escape(title)}")
    lines.append(f"type: {type_}")
    if desc:
        lines.append("description: |-")
        for ln in desc.splitlines() or [""]:
            lines.append(("    " + ln) if ln else "    ")
    if resource:
        lines.append(f"resource: {resource}")
    if tags:
        lines.append("tags: [" + ", ".join(tags) + "]")
    if ts:
        lines.append(f"timestamp: {ts}")
    lines.append("---")
    return "\n".join(lines)


def w(rel, content):
    path = os.path.join(BUNDLE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def paper_slug(d):
    return d.replace("(", "-").replace(")", "-")


def ml(text, target):
    t = f"<{target}>" if ("(" in target or ")" in target or " " in target) else target
    return f"[{text}]({t})"


# ---------------------------------------------------------------------------
# assemble
# ---------------------------------------------------------------------------
families, papers_in = parse_contents(REPO)
discs, fam_disc_map = parse_overview(REPO)
readme_meta, lean_pdfs, traces = parse_meta(REPO)

for d in discs:
    d["slug"] = slugify(d["name"])
disc_slug_of = {d["name"]: d["slug"] for d in discs}

papers = []
for p in papers_in:
    parts = p["pdf"].split("/")
    d = parts[1] if len(parts) >= 3 else None
    fam = next((f for f in families if p in f["papers"]), None)
    fam_num = fam["num"] if fam else 0
    disc = fam_disc_map.get(fam_num, {"name": "Unclassified"})
    rm = readme_meta.get(d, {})
    date = rm.get("date")
    if not date and d:
        m = re.search(r"-([A-Z][a-z]+)-(\d{1,2})-(\d{4})$", d)
        if m:
            months = {n: i for i, n in enumerate(
                ["January", "February", "March", "April", "May", "June", "July",
                 "August", "September", "October", "November", "December"], 1)}
            date = f"{m.group(3)}-{months[m.group(1)]:02d}-{int(m.group(2)):02d}"
    papers.append({
        "dir": d, "file": parts[-1], "pdf_rel": p["pdf"], "title": p["title"],
        "note": p.get("note", ""), "abstract": p["abstract"], "family": fam_num,
        "disc": disc["name"], "disc_slug": disc_slug_of.get(disc["name"], "unclassified"),
        "date": date, "citation_key": rm.get("citation_key") or f"OAI:{d}",
        "lean": p["pdf"] in lean_pdfs, "trace": fam_num in traces,
    })

fam_papers = defaultdict(list)
for p in papers:
    fam_papers[p["family"]].append(p)
fam_by_num = {f["num"]: f for f in families}

paper_lean = sum(1 for p in papers if p["lean"])
print(f"parsed: {len(families)} families, {len(papers)} papers, "
      f"{len(discs)} disciplines, {paper_lean} lean-formalized")

# ---- index.md + log.md ----
w("log.md", """# Bundle log

Chronological log of changes to this OKF bundle.

## 2026-10-10 - Initial build

- Generated an OKF knowledge base from a snapshot of github.com/openai/math cloned 2026-10-10.
- Extracted 719 manuscripts (type `Paper`) from CONTENTS.md, 372 result families (type `Result`) and 17 disciplines (type `Discipline`) from overview.tex.
- Abstracts come from CONTENTS.md; dates and citation keys from each preprints/*/README.md; Lean-formalization status from lean/formalization.yaml; reasoning summaries from the repository README.md.
- Preprint directories not referenced by the current catalogue (earlier versions of revised papers) are intentionally not included.
""")

# ---- disciplines ----
for d in discs:
    sl = d["slug"]
    fams_in = [n for n in d["families"] if n in fam_by_num]
    n_papers = sum(len(fam_by_num[n]["papers"]) for n in fams_in)
    n_lean = sum(1 for n in fams_in if fam_by_num[n].get("lean_doc"))
    n_trace = sum(1 for n in fams_in if n in traces)
    rows = [f"- [{n:03d}. {fam_by_num[n]['title']}](../results/{n:03d}-{slugify(fam_by_num[n]['title'])}.md)"
            for n in sorted(fams_in)]
    extra = []
    if n_lean:
        extra.append(f"{n_lean} with Lean formalizations")
    if n_trace:
        extra.append(f"{n_trace} with reasoning summaries")
    detail = " (" + ", ".join(extra) + ")" if extra else ""
    w(f"disciplines/{sl}.md",
      front(d["name"], "Discipline",
            desc=f"{len(fams_in)} result families and {n_papers} manuscripts in the OpenAI Math Release.",
            resource=f"{GH}/blob/main/overview.pdf",
            tags=["openai-math", f"discipline-{sl}"], ts=RELEASE) + f"""

# {d["name"]}

{n_papers} manuscripts across {len(fams_in)} result families{detail}.

## Result families

{chr(10).join(rows)}
""")

w("disciplines/index.md", "# Disciplines\n\n17 subject areas from the collection overview. [Result families](../results/index.md) · [Papers](../papers/index.md)\n\n" +
  "\n".join(f"- [{d['name']}]({d['slug']}.md)" for d in sorted(discs, key=lambda x: x["name"].lower())) + "\n")

# ---- results ----
res_meta = {}
for f in families:
    n = f["num"]
    disc = fam_disc_map.get(n, {"name": "Unclassified"})
    disc_slug = disc_slug_of.get(disc["name"], "unclassified")
    rsl = slugify(f["title"])
    pfiles = fam_papers[n]
    resource = f"{GH}/blob/main/{pfiles[0]['pdf_rel']}"
    tags = ["openai-math", f"discipline-{disc_slug}", f"family-{n:03d}"]
    if f.get("lean_doc"):
        tags.append("lean-doc")
    is_trace = n in traces
    if is_trace:
        tags.append("reasoning-trace")

    body = [f"# {n:03d}. {f['title']}", "",
            f"> Discipline: {ml(disc['name'], f'../disciplines/{disc_slug}.md')}",
            f"> Manuscripts: **{len(pfiles)}**", ""]
    flags = []
    if f.get("lean_doc"):
        flags.append(f"[Lean formalization of headline result]({GH}/blob/main/lean/docs/{n:03d}.md)")
    if is_trace:
        flags.append(f"[Abridged reasoning summary]({GH}/blob/main/{traces[n]})")
    if flags:
        body += ["  ·  ".join(flags), ""]
    body += ["## Description", "", clean_md(f["desc"]), "", "## Manuscripts", ""]
    for p in sorted(pfiles, key=lambda x: (bool(x["note"]), x["title"])):
        label = p["title"] + (f" — {p['note']}" if p["note"] else "")
        mark = " ".join(t for t in (["`lean-formalized`"] if p["lean"] else []) + (["`reasoning-trace`"] if p["trace"] else []))
        pp_target = f"../papers/{paper_slug(p['dir'])}.md"
        row = f"- {ml(label, pp_target)}"
        if mark:
            row += f" ({mark})"
        row += f" — *{p['date'] or 'n.d.'}*"
        body.append(row)

    w(f"results/{n:03d}-{rsl}.md",
      front(f"{n:03d}. {f['title']}", "Result", desc=clean_md(f["desc"]),
            resource=resource, tags=tags, ts=RELEASE) + "\n\n" + "\n".join(body) + "\n")
    res_meta[n] = {"slug": rsl, "disc_slug": disc_slug, "trace": is_trace}

w("results/index.md", "# Result families\n\n372 numbered results. [Disciplines](../disciplines/index.md) · [Papers](../papers/index.md)\n\n" +
  "\n".join(f"- [{n:03d}. {fam_by_num[n]['title']}]({n:03d}-{res_meta[n]['slug']}.md)" for n in sorted(fam_by_num)) + "\n")

# ---- papers ----
for p in papers:
    n = p["family"]
    pdf_abs = f"{GH}/blob/main/{p['pdf_rel']}"
    res_slug = res_meta[n]["slug"]
    tags = ["openai-math", f"discipline-{p['disc_slug']}", f"family-{n:03d}"]
    if p["lean"]:
        tags.append("lean-formalized")

    fam_label = f"{n:03d}. {fam_by_num[n]['title']}"
    res_target = f"../results/{n:03d}-{res_slug}.md"
    disc_target = f"../disciplines/{p['disc_slug']}.md"
    src_label = f"{p['dir']}/{p['file']}"
    body = [f"# {p['title']}", "",
            f"> Result family: {ml(fam_label, res_target)}",
            f"> Discipline: {ml(p['disc'], disc_target)}",
            f"> Date: {p['date'] or 'unknown'}",
            f"> Source: {ml(src_label, pdf_abs)}", ""]
    flags = []
    if p["lean"]:
        flags.append("[Lean formalized](https://github.com/openai/math/blob/main/lean/formalization.yaml)")
    if p["trace"]:
        flags.append(f"[Reasoning summary]({GH}/blob/main/{traces[n]})")
    if p["note"]:
        flags.append(f"*Note:* {p['note']}")
    if flags:
        body += ["  ·  ".join(flags), ""]
    body += ["## Abstract", "", p["abstract"].strip(), "",
             "## Citation", "", f"**Key:** `{p['citation_key']}`", "",
             "```bibtex",
             f"@misc{{{p['citation_key']},",
             "  author = {OpenAI},",
             f"  title = {{{p['title']}}},",
             "  year = {2026},",
             f"  howpublished = {{OpenAI Math Release preprint \\url{{{pdf_abs}}}}}",
             "}", "```"]

    w(f"papers/{paper_slug(p['dir'])}.md",
      front(p["title"], "Paper", desc=p["abstract"].strip(), resource=pdf_abs,
            tags=tags, ts=p["date"] or RELEASE) + "\n\n" + "\n".join(body) + "\n")

w("papers/index.md", "# Papers\n\n719 manuscripts. [Disciplines](../disciplines/index.md) · [Result families](../results/index.md)\n\n" +
  "\n".join(f"- [{p['family']:03d}. {p['title']}]({paper_slug(p['dir'])}.md) — *{p['date'] or 'n.d.'}*"
            for p in sorted(papers, key=lambda x: (x["family"], x["title"].lower()))) + "\n")

# ---- root index ----
w("index.md", f"""# OpenAI Math Wiki

An [Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) bundle describing the **OpenAI Math Release**: 719 mathematical manuscripts covering 372 result families across 17 disciplines, published in [github.com/openai/math](https://github.com/openai/math) on October 6, 2026 under Apache-2.0. The results were produced by an unreleased internal OpenAI frontier model for model-development evaluation on open research problems.

## Navigation

- [Disciplines](disciplines/index.md) — 17 subject areas
- [Result families](results/index.md) — 372 numbered results
- [Papers](papers/index.md) — 719 manuscripts with abstracts

## Conventions

Every concept document carries `type`, `title`, `description`, `resource`, `tags`, and `timestamp` in its YAML frontmatter:

- `type: Discipline` — a subject area from the collection overview.
- `type: Result` — one numbered result family from the manuscript catalogue.
- `type: Paper` — a single manuscript; the `resource` links to the PDF in the OpenAI repository.

Papers link to their result family and discipline; result families link to their papers. Tags use a controlled vocabulary: `discipline-<slug>`, `family-<NNN>`, `lean-formalized`, `reasoning-trace`.

## Statistics

- 719 papers, 372 result families, 17 disciplines.
- {paper_lean} papers with a Lean formalization (tagged `lean-formalized`).
- {len(traces)} result families with an abridged reasoning summary (tagged `reasoning-trace`).
- Repository snapshot date: 2026-10-10.

## Managing the store

This directory is both the OKF bundle and the [rust-okf](https://github.com/origo/rust-okf) store root (`okf.toml` + `.okf-index/`). The indexer skips `index.md`, `log.md`, and dot-directories, so the store can live inside the bundle.

```bash
cd openai-math-wiki
okf init-config        # (re)create okf.toml
okf add .              # full (re)build of the hybrid index
okf update .           # incremental update after editing documents
okf compact            # merge segments and clear tombstones
okf search "quasi-Riemann hypothesis"
okf search "Selmer corank" --filter-type Paper --filter-tag family-002 --json
okf serve --bind 127.0.0.1:8787
```
""")

print("wrote bundle to", BUNDLE)