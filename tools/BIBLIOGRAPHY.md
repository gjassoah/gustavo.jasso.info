# Bibliography workflow

The five files in `resources/my-publications/bib/` are the only source for the
Research page's bibliography. They belong to the private `my-publications`
repository (`gjassoah/my-publications`), a git submodule shared with the CV, and
are not edited here: edit them in that repository (or in the submodule checkout),
commit and push there, then record the new version in this repository with
`git add resources/my-publications`. After cloning, run
`git submodule update --init`. Edit entries there, including notes and errata.
The Research group page still uses its separate existing YAML bibliography.

## Setup

Hugo and Python 3.10 or newer are required. On Linux x86_64:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/requirements.txt
python3 tools/install-pandoc.py
```

The installer verifies the pinned Pandoc 3.6.4 archive and installs only its
binary inside ignored `.tools/`; it does not change system packages. On other
platforms, install Pandoc 3.6.4 separately. `PANDOC` can override the executable.
Otherwise the local pinned binary takes precedence over the system version.
A system Pandoc without the local binary also works; the tests pass with 3.11.
The same setup runs in GitHub Actions.

## Build and preview

```sh
.venv/bin/python tools/site.py build
.venv/bin/python tools/site.py serve
```

Additional arguments go to Hugo, e.g. `serve --port 1313` or `build --minify`.
Stop an existing `hugo server` before starting the wrapper on the same port.
The preview watches BibTeX and CSL changes, regenerates the bibliography and
lets Hugo refresh the page. An invalid edit reports an error and keeps the last
valid bibliography. Production builds fail if generation fails.

`tools/site.py bibliography` regenerates only the bibliography. Plain `hugo`
does not run the generator; use the wrapper to avoid stale citations.
Generated `data/bibliography_generated.json` is ignored and never hand-edited.

## Categories and order

- `preprints.bib`: Preprints
- `books.bib`: Books
- `publications.bib`: Publications
- `proceedings.bib`: Proceedings, extended abstracts and other writings
- `theses.bib`: Theses and dissertations

Entries appear in file order. Each category is numbered in descending order,
as on the previous website. Put new entries at the top when appropriate.
Citation keys must be unique across the five files and use letters, digits,
periods, underscores, colons or hyphens. Each entry has a stable `ref-KEY` anchor.

## Fields

Use ordinary BibTeX/BibLaTeX fields for author, title, journal, booktitle, year,
volume, number, pages, publisher, editor and thesis type/school. Keep full author
names; CSL abbreviates given names. LaTeX accents and inline mathematics are
converted by Pandoc. arXiv-only entries include a linked `arXiv:ID [primaryClass]`
identifier in the citation; the redundant arXiv link below is omitted. If no year
is supplied, the first-submission year is taken from the identifier. Math is emitted as native MathML, with no client-side library.

| Field | Website use |
| --- | --- |
| `url` | Publication link; takes precedence over DOI |
| `doi` | Publication link when no non-arXiv URL is present |
| `eprint`, `eprinttype = {arXiv}` | arXiv link |
| `archiveprefix = {arXiv}`, `arxiv-id` | Also supported |
| `mrnumber` | MathSciNet link |
| `zbl` | zbMATH link |
| `pdfurl` | Local PDF path, e.g. `/pdf/mfo/OWR-2024-20-jasso.pdf` |
| `note`, `addendum` | Notes, parsed as BibLaTeX by Pandoc |
| `webnote` | Optional Markdown replacement for the displayed note |
| `webstatus` | Optional Markdown parenthetical at the end of the citation |
| `errata` | Markdown errata, separate from the citation |

`webnote = {}` hides a note on the website while retaining its BibTeX `note`
field. `@Comment` starts a separate BibTeX entry; it cannot comment out fields
inside another entry.

The fields `selected` and `significant` are used by the CV and ignored here.
`file` was a private JabRef attachment field and has been removed from the data;
the paper copies are in `my-publications/pdfs/KEY.pdf` and are not published.
Local PDF paths are checked against `static/`; missing files fail the build.
An arXiv subject suffix such as `~[math.RT]` is removed from generated URLs.
A DOI/URL disagreement produces a warning and uses the explicit URL.

Notes can refer to entries with `[@KEY]`; the generator supplies a linked current
number. For example, `comprises publication [@BGJ13]` follows that article even
when list numbering changes. Missing referenced keys fail the build.
The existing thesis remarks now live in `theses.bib`.

Oberwolfach abstracts exported as `@InProceedings` with a `journal` field render
as journal contributions, with their individual page range. The exported
workshop description remains available in `note`. Displayed notes are labelled
“Note:”; errata remain labelled “Errata:”. Duplicate note/status text is shown
only once, as a parenthetical status.

## Style and tests

`tools/csl/ams-website.csl` is the local adaptation of the vendored AMS numeric
style. It initializes names, italicizes titles, uses regular-weight volumes,
formats chapters and theses, and leaves numbering and resource links to Hugo.
The upstream attribution and CC BY-SA 3.0 license remain in both CSL files.
The upstream file was downloaded on 2026-09-28 from
https://raw.githubusercontent.com/citation-style-language/styles/master/american-mathematical-society-numeric.csl
(SHA-256 `ed8e575eb64f65da11aa4327bf7d4cc99bfdce4f61757b2bf8b0329d70a42ea1`).
No network lookup occurs during normal bibliography generation.

```sh
.venv/bin/python tools/test_bibliography.py
```

Pending metadata corrections are recorded in `BIBLIOGRAPHY-REVIEW.md`; they are
not applied automatically. The old personal YAML lists have been retired after
transferring missing links, statuses, notes and errata. Their history remains in Git.
