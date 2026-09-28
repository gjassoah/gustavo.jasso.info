# Metadata corrections and remaining review

Checked 2026-09-28. The four corrections below were approved and applied.

- [x] `Jas24c`: change `doi = {10.4171/owr/2020/3}` to
  `doi = {10.4171/OWR/2024/20}`. The URL already targets the correct report.
  The MFO DOI `10.14760/OWR-2024-20` and EMS DOI are both legitimate identifiers
  for this report, so that difference in the old YAML is not an error.
  Sources: https://ems.press/journals/owr/articles/14298370 and
  https://publications.mfo.de/handle/mfo/4215

- [x] `Jas24b`: change `pages = {1449--1454}` to `pages = {1449--1453}`.
  Both the publisher's displayed citation and BibTeX export give 1449–1453.
  Source: https://comptes-rendus.academie-sciences.fr/mathematique/articles/10.5802/crmath.655/

- [x] `MR3799490`: change editor `Frauke Bleher, Frauke` to `Bleher, Frauke`.
  The current export produces “F. Frauke Bleher”. The AMS list identifies
  Frauke Bleher alongside Graham J. Leuschke, Ralf Schiffler and Dan Zacharia.
  Source: https://www.ams.org/books/conm/709/conm709-endmatter.pdf

- [x] Replace placeholder `editor = {w}` in `Jas24c` with
  `editor = {Keller, Bernhard and Krause, Henning and Lowen, Wendy and Solotar, Andrea}`
  and in `Jas20a` with
  `editor = {Amiot, Claire and Crawley-Boevey, William and Iyama, Osamu and Krause, Henning}`.
  These are the organizers credited for the respective reports.
  Sources: https://ems.press/journals/owr/articles/14298370 and
  https://ems.press/journals/owr/articles/17466

Resolved with the user-provided AMS record on 2026-09-28: “The derived
Auslander–Iyama correspondence” (`JKM22`) is now an `@Article` in
J. Amer. Math. Soc. 40 (2027), no. 1, 1–127. The acceptance note was removed.
AMS's Crossref deposit confirms volume, issue and pages, and gives January 2027
as the issue's print date; the online publication date is 21 August 2026.
The citation uses the issue year, 2027. Authors, appendix credit and arXiv link
were retained.
Sources:
https://pubs.ams.org/JAMS/2027-40-01/S0894-0347-2026-01079-X
https://api.crossref.org/works/10.1090/jams/1079
