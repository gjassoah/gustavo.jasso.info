"""Integration checks for citation rendering and BibTeX-only maintenance."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import bibliography as bib


class BibliographyTests(unittest.TestCase):
    def test_resource_links(self):
        self.assertEqual(bib.arxiv_id('2603.14970~[math.RT]'), '2603.14970')
        self.assertEqual(bib.arxiv_id('math/0301234v2'), 'math/0301234v2')
        links = bib.resource_links({'doi': r'10.1007/example\_4', 'eprint': '2501.08255', 'mrnumber': '123', 'zbl': '1234.56789'})
        self.assertEqual([x['label'] for x in links], ['Publication', 'arXiv', 'MathSciNet', 'zbMATH'])
        self.assertEqual(links[0]['url'], 'https://doi.org/10.1007/example_4')
        with self.assertRaises(ValueError):
            bib.checked_url('/pdf/missing-test-file.pdf', local=True)
        with self.assertRaises(ValueError):
            bib.checked_url('javascript:alert(1)')

    def test_full_generation_and_updates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = root / 'resources/bibtex'
            sources.mkdir(parents=True)
            fixtures = {
                'preprints': r'@online{GJN26, author={Gómez, Juan Omar}, title={Sample}, eprint={2606.19485}, primaryclass={math.RT}, publisher={arXiv}, webstatus={submitted}, note={submitted}}',
                'books': r'@unpublished{Book, author={Example, Alice}, title={Book}, note={In progress}}',
                'publications': r'@article{Jas16, author={Jasso, Gustavo}, title={$n$-exact categories}, journal={Math. Z.}, volume={283}, year={2016}, errata={A correction}}' + '\n' +
                                r'@article{BJT16, author={Example, Alice}, title={Removable}, year={2016}}' + '\n' +
                                r'@article{Jas15a, author={Example, Alice}, title={Another paper}, year={2015}}',
                'proceedings': r'@online{JM25b, author={Jasso, Gustavo and Muro, Fernando}, title={Minimal $A_\infty$-algebras}, eprint={2508.18852~[math.RT]}}',
                'theses': r'@phdthesis{JasPhD, author={Jasso, Gustavo}, title={Thesis}, school={Nagoya University}, year={2014}, addendum={comprises publications [@Jas15a] and [@Jas16]}}',
            }
            for group, text in fixtures.items():
                (sources / (group + '.bib')).write_text(text + '\n')
            (root / 'data').mkdir()
            (root / 'static').symlink_to(bib.ROOT / 'static', target_is_directory=True)
            output = root / 'data/bibliography_generated.json'
            pandoc = os.environ.get('PANDOC') or (str(bib.ROOT / '.tools/pandoc/bin/pandoc') if (bib.ROOT / '.tools/pandoc/bin/pandoc').exists() else shutil.which('pandoc'))
            with patch.object(bib, 'ROOT', root), patch.object(bib, 'OUTPUT', output), patch.dict('os.environ', {'PANDOC': pandoc}), contextlib.redirect_stdout(io.StringIO()):
                data = bib.generate()
                self.assertEqual([len(data[k]) for k in bib.GROUPS], [1, 1, 3, 1, 1])
                entries = {r['key']: r for rows in data.values() for r in rows}
                self.assertIn('J. O. Gómez', entries['GJN26']['citation'])
                self.assertIn('>arXiv:2606.19485 [math.RT]</a> (2026) (submitted).', entries['GJN26']['citation'])
                self.assertNotIn(', arXiv.', entries['GJN26']['citation'])
                self.assertFalse(entries['GJN26']['note'])
                self.assertFalse(entries['GJN26']['links'])
                self.assertIn('>arXiv:2508.18852 [math.RT]</a> (2025).', entries['JM25b']['citation'])
                self.assertIn('<math ', entries['JM25b']['citation'])
                self.assertNotIn('$', entries['JM25b']['citation'])
                self.assertIn('283 (2016)', entries['Jas16']['citation'])
                self.assertIn('href="#ref-Jas15a">[1]</a>', entries['JasPhD']['note'])
                self.assertEqual(sum(bool(r['errata']) for r in entries.values()), 1)
                original = output.read_bytes()
                bib.generate()
                self.assertEqual(original, output.read_bytes())
                publications = root / 'resources/bibtex/publications.bib'
                saved = publications.read_text()
                # Removing the oldest article requires updating its cross-reference too.
                # Removing an unrelated entry renumbers the remaining list automatically.
                from pybtex.database import parse_file
                database = parse_file(publications)
                del database.entries['BJT16']
                publications.write_text(database.to_string('bibtex'))
                changed = bib.generate()
                self.assertEqual(len(changed['publications']), 2)
                self.assertNotIn('BJT16', [r['key'] for r in changed['publications']])
                self.assertIn('href="#ref-Jas16">[2]</a>', changed['theses'][0]['note'])
                publications.write_text(saved + '\n@article{TestNew, author={Example, Alice}, title={Test title}, year={2026}}\n')
                changed = bib.generate()
                self.assertEqual(len(changed['publications']), 4)
                self.assertIn('A. Example', changed['publications'][-1]['citation'])
                # Duplicate keys across files fail before replacing the last good output.
                last_good = output.read_bytes()
                with (root / 'resources/bibtex/books.bib').open('a') as f:
                    f.write('\n@book{TestNew, author={Other, Bob}, title={Duplicate}}\n')
                with self.assertRaisesRegex(ValueError, 'Duplicate'):
                    bib.generate()
                self.assertEqual(last_good, output.read_bytes())
                (sources / 'books.bib').write_text('@book{Broken,\n  @Comment note = {Hidden}\n}\n')
                with self.assertRaisesRegex(ValueError, r'resources/bibtex/books.bib:.*line 2'):
                    bib.generate()
                self.assertEqual(last_good, output.read_bytes())


if __name__ == '__main__':
    unittest.main()
