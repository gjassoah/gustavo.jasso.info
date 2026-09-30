# gustavo.jasso.info

Source code for [Gustavo Jasso’s professional website](https://gustavo.jasso.info),
built with [Hugo](https://gohugo.io/). The site uses simple design elements to
indicate institutional affiliation, with an emphasis on simple navigation and
maintenance.

The five main pages are Home, Teaching, Research, Research group and Resources.
Home and Teaching have English and German versions. The other three pages share
English content while retaining navigation in the selected language.

## Build and preview

The build requires Git, Hugo, Python 3.10 or newer, and Pandoc 3.6.4. The commands
below install the Python dependencies in a virtual environment and download a
verified Pandoc binary into `.tools/`. The Pandoc installer supports Linux
x86_64; on other platforms, install Pandoc separately and make it available on
`PATH`, or set `PANDOC` to its executable path.

```sh
git clone git@git.sr.ht:~gjasso/gustavo.jasso.info
cd gustavo.jasso.info
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/requirements.txt
python3 tools/install-pandoc.py
```

To build the site:

```sh
.venv/bin/python tools/site.py build
```

The build first generates the bibliography, then runs Hugo. The resulting site
is written to `public/`. Use this command instead of invoking `hugo` directly,
since Hugo alone does not regenerate the bibliography.

To preview changes locally:

```sh
.venv/bin/python tools/site.py serve
```

The preview is available at <http://localhost:1313/>. Changes to the BibTeX files
or citation style regenerate the bibliography; Hugo reloads the site when its
content, templates or styles change. Stop any existing server using the same
port before starting the preview. Additional arguments are passed to Hugo, for
example `serve --port 1314` or `build --minify`.

## Content and design

| Location | Contents |
| --- | --- |
| `content/en/`, `content/de/` | Page text and navigation metadata |
| `data/` | Courses, students, activities and other structured content |
| `resources/bibtex/` | Personal bibliography |
| `layouts/` | Hugo templates and shortcodes |
| `static/css/style.css` | Site styles |
| `static/js/navigation.js` | Navbar behaviour |
| `static/pdf/`, `static/img/`, `static/fonts/` | PDFs, images and fonts |
| `config.toml` | Site and language configuration |

The German Research, Research group and Resources pages use
`contentLanguage: en` to render the corresponding English page. Edit their
content in `content/en/`.

## Bibliography

Edit the five BibTeX files to add, remove or update entries:

| File | Section |
| --- | --- |
| `preprints.bib` | Preprints |
| `books.bib` | Books |
| `publications.bib` | Publications |
| `proceedings.bib` | Proceedings, extended abstracts and other writings |
| `theses.bib` | Theses and dissertations |

Entries retain their file order, with descending numbering within each section.
Pandoc formats the citations using the local
[AMS CSL adaptation](tools/csl/ams-website.csl). Author names are abbreviated to
initials, titles are italicised, and volume numbers use regular weight.

Links, status, notes and errata are stored in the BibTeX entries. `webstatus`
appears parenthetically at the end of a citation. Notes and errata are labelled
separately. Local PDF links use `pdfurl`, with paths relative to the site root,
for example `/pdf/mfo/OWR-2024-20-jasso.pdf`.

The [bibliography guide](tools/BIBLIOGRAPHY.md) describes the supported fields,
arXiv citations and references between entries. The Research group page retains
its separate bibliography in `data/bibliography/research_group.yaml`.

The generated file `data/bibliography_generated.json` is excluded from Git.
To regenerate it without building the site:

```sh
.venv/bin/python tools/site.py bibliography
```

## Checks and deployment

Run the bibliography tests with:

```sh
.venv/bin/python tools/test_bibliography.py
```

Local build and preview commands do not publish the site.

See [LICENSE.md](LICENSE.md) for the repository licence. The CSL files retain
their own attribution and CC BY-SA 3.0 licence notices.
