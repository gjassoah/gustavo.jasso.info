#!/usr/bin/env python3
"""Generate Hugo data from BibTeX; Pandoc/citeproc owns citation typography."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, quote
import json
import os
import re
import shutil
import subprocess
import sys
from pybtex.database import parse_file
from pybtex.exceptions import PybtexError

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ('preprints', 'books', 'publications', 'proceedings', 'theses')
OUTPUT = ROOT / 'data/bibliography_generated.json'
STYLE = ROOT / 'tools/csl/ams-website.csl'


def pandoc(*args, text=None):
    executable = os.environ.get('PANDOC') or (str(ROOT / '.tools/pandoc/bin/pandoc') if (ROOT / '.tools/pandoc/bin/pandoc').exists() else shutil.which('pandoc') or 'pandoc')
    result = subprocess.run([executable, *map(str, args)], input=text, text=True, capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    return result.stdout


class Citations(HTMLParser):
    """Extract the inner HTML of citeproc's entry divs, including MathML."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.entries = {}
        self.key = None
        self.depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.key is None and tag == 'div' and 'csl-entry' in attrs.get('class', '').split():
            self.key = attrs['id'].removeprefix('ref-')
            self.depth = 1
            self.parts = []
        elif self.key is not None:
            if tag == 'div':
                self.depth += 1
            self.parts.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if self.key is not None:
            if tag == 'div':
                self.depth -= 1
            if self.depth == 0:
                self.entries[self.key] = ''.join(self.parts).strip()
                self.key = None
            else:
                self.parts.append(f'</{tag}>')

    def handle_startendtag(self, tag, attrs):
        if self.key is not None:
            self.parts.append(self.get_starttag_text())

    def handle_data(self, data):
        if self.key is not None:
            self.parts.append(data)

    def handle_entityref(self, name):
        self.handle_data('&' + name + ';')

    def handle_charref(self, name):
        self.handle_data('&#' + name + ';')


def arxiv_id(value):
    value = value.replace(r'\_', '_').strip()
    value = re.sub(r'^https?://arxiv.org/(abs|pdf)/', '', value)
    match = re.match(r'(\d{4}\.\d{4,5}(?:v\d+)?|[a-zA-Z.-]+/\d{7}(?:v\d+)?)', value)
    if not match:
        raise ValueError(f'Invalid arXiv identifier: {value}')
    return match[0]


def checked_url(url, local=False):
    url = url.replace(r'\_', '_').strip()
    if local:
        if not url.startswith('/') or url.startswith('//'):
            raise ValueError(f'pdfurl must be a site-root path: {url}')
        path = (ROOT / 'static' / url.lstrip('/')).resolve()
        if not path.is_relative_to((ROOT / 'static').resolve()) or not path.is_file():
            raise ValueError(f'Missing local PDF: {url}')
    elif urlsplit(url).scheme not in ('http', 'https'):
        raise ValueError(f'Expected HTTP(S) URL: {url}')
    return url


def resource_links(fields):
    links = []
    # Explicit URL takes precedence: exports may contain a stale DOI.
    url = fields.get('url')
    doi = fields.get('doi', '').replace(r'\_', '_')
    if url and 'arxiv.org/' not in url:
        links.append({'label': 'Publication', 'url': checked_url(url)})
        if doi and 'doi.org/' in url and url.split('doi.org/', 1)[1].lower() != doi.lower():
            print(f'WARNING: DOI {doi} disagrees with URL {url}; using URL.', file=sys.stderr)
    elif doi:
        links.append({'label': 'Publication', 'url': checked_url('https://doi.org/' + doi)})
    eprint = fields.get('arxiv-id')
    if not eprint and fields.get('eprint') and fields.get('eprinttype', fields.get('archiveprefix', 'arXiv')).lower() == 'arxiv':
        eprint = fields['eprint']
    if not eprint and url and 'arxiv.org/' in url:
        eprint = url
    if eprint:
        links.append({'label': 'arXiv', 'url': 'https://arxiv.org/abs/' + arxiv_id(eprint)})
    for field, label, base in [('mrnumber', 'MathSciNet', 'https://mathscinet.ams.org/mathscinet/lookup?mr='), ('zbl', 'zbMATH', 'https://zbmath.org/')]:
        if fields.get(field):
            links.append({'label': label, 'url': base + quote(fields[field], safe='.')})
    if fields.get('pdfurl'):
        links.append({'label': 'PDF', 'url': checked_url(fields['pdfurl'], local=True)})
    return links


def generate():
    sources = {}
    references = []
    seen = set()
    for group in GROUPS:
        path = ROOT / 'resources/bibtex' / (group + '.bib')
        try:
            database = parse_file(path)
        except PybtexError as error:
            raise ValueError(f'{path.relative_to(ROOT)}: {error}') from error
        document = json.loads(pandoc('-f', 'biblatex', '-t', 'json', path))
        refs = {r['c']['id']['c']: r for r in document['meta']['references']['c']}
        notes = {r['id']: r.get('note', '') for r in json.loads(pandoc('-f', 'biblatex', '-t', 'csljson', path))}
        sources[group] = []
        for key, entry in database.entries.items():
            if key in seen or not re.fullmatch(r'[A-Za-z0-9_.:-]+', key):
                raise ValueError(f'Duplicate or unsupported citation key: {key}')
            seen.add(key)
            fields = {k.lower(): v for k, v in entry.fields.items()}
            ref = refs[key]
            meta = ref['c']
            if not meta.get('title') or not meta.get('author'):
                raise ValueError(f'{key}: author and title are required')
            # Workshop abstracts exported as proceedings also carry journal data.
            if fields.get('journal') and entry.type.lower() == 'inproceedings':
                meta['type'] = {'t': 'MetaString', 'c': 'article-journal'}
                meta['container-title'] = {'t': 'MetaString', 'c': fields['journal']}
                if fields.get('number'):
                    meta['issue'] = {'t': 'MetaString', 'c': fields['number']}
            links = resource_links(fields)
            arxiv = next((link for link in links if link['label'] == 'arXiv'), None)
            if arxiv and entry.type.lower() in ('online', 'misc', 'unpublished') and not fields.get('journal'):
                identifier = arxiv['url'].rsplit('/abs/', 1)[1]
                category = fields.get('primaryclass', fields.get('eprintclass', ''))
                if not category:
                    match = re.search(r'\[([^\]]+)\]', fields.get('eprint', fields.get('arxiv-id', '')))
                    category = match[1] if match else ''
                label = 'arXiv:' + identifier + (f' [{category}]' if category else '')
                meta['type'] = {'t': 'MetaString', 'c': 'manuscript'}
                meta['number'] = {'t': 'MetaInlines', 'c': [
                    {'t': 'Link', 'c': [['', [], []], [{'t': 'Str', 'c': label}], [arxiv['url'], '']]}
                ]}
                if 'issued' not in meta:
                    year_code = int(identifier.split('/')[-1][:2])
                    year = (1900 if year_code >= 91 else 2000) + year_code
                    meta['issued'] = {'t': 'MetaString', 'c': str(year)}
                links = [link for link in links if link['label'] != 'arXiv']
            if fields.get('webstatus'):
                status_doc = json.loads(pandoc('-f', 'markdown-raw_html', '-t', 'json', text=fields['webstatus'].rstrip('.')))
                if len(status_doc['blocks']) != 1 or status_doc['blocks'][0]['t'] != 'Para':
                    raise ValueError(f'{key}: webstatus must be a single paragraph')
                meta['status'] = {'t': 'MetaInlines', 'c': status_doc['blocks'][0]['c']}
            sources[group].append({'key': key, 'fields': fields, 'note': notes[key], 'links': links})
            for field in ('url', 'URL', 'DOI'):
                meta.pop(field, None)
            references.append(ref)
    numbers = {r['key']: len(entries) - i for entries in sources.values() for i, r in enumerate(entries)}

    def prose(value):
        def crossref(match):
            key = match[1]
            if key not in numbers:
                raise ValueError(f'Unknown citation in note: {key}')
            return f'[\\[{numbers[key]}\\]](#ref-{key})'
        value = re.sub(r'\[@([^\]]+)\]', crossref, value)
        if not value:
            return ''
        return pandoc('-f', 'markdown-raw_html', '-t', 'html5', '--mathml', text=value).strip()

    document['meta']['references']['c'] = references
    html = pandoc('-f', 'json', '-t', 'html5', '--citeproc', '--mathml', '--wrap=none',
                  '--csl', STYLE, '-M', 'link-bibliography=false', text=json.dumps(document))
    parser = Citations()
    parser.feed(html)
    if set(parser.entries) != seen:
        raise ValueError('Citeproc did not render every entry')
    data = {}
    for group, entries in sources.items():
        data[group] = []
        for entry in entries:
            fields, key = entry['fields'], entry['key']
            note = prose(fields.get('webnote', entry['note']))
            status = prose(fields.get('webstatus', ''))
            if re.sub(r'[\W_]+', '', note).lower() == re.sub(r'[\W_]+', '', status).lower():
                note = ''
            data[group].append({
                'key': key, 'number': numbers[key], 'citation': parser.entries[key],
                'links': entry['links'],
                'note': note,
                'errata': prose(fields.get('errata', '')),
            })
    serialized = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if not OUTPUT.exists() or OUTPUT.read_text() != serialized:
        staging = OUTPUT.with_suffix('.json.tmp')
        staging.write_text(serialized)
        staging.replace(OUTPUT)
    print(f'Bibliography: {len(seen)} citations generated.')
    return data


if __name__ == '__main__':
    try:
        generate()
    except (ValueError, OSError) as error:
        sys.exit(str(error))
