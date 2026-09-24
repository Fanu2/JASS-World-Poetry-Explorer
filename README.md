# JASS World Poetry Explorer — FINAL

## Final Frozen Release

**JASS World Poetry Explorer — FINAL** is the final frozen release of the JASS multilingual poetry corpus and its lightweight PySide6 desktop Explorer.

### Final corpus

**10,079 poetry records** across 9 languages:

| Language | Poems |
|---|---:|
| Assamese | 71 |
| Bengali | 6,079 |
| English | 493 |
| French | 100 |
| Hindi | 1,305 |
| Mizo | 82 |
| Punjabi | 629 |
| Spanish | 6 |
| Urdu | 1,314 |
| **Total** | **10,079** |

## Final Mizo addition

Mizo Batch 1 is the final dataset addition to World Poetry.

- 82 Mizo poetry records
- extracted from the saved January 2013 **Mizo Poetry** archive
- 84 source posts inspected
- 1 English-only post excluded
- 1 exact duplicate removed during staging
- source attribution retained where available
- no generic Mizo language corpora were imported into World Poetry

The general Mizo corpora `JASS_Mizo_Corpus_4M.db` and `Mizo_English_Parallel_20K.db` remain separate projects.

## Explorer

The Explorer retains the established three-pane design:

**Languages → Works / Poems → Reader**

Features include:

- multilingual language browser with live counts
- work and poem navigation
- full-text search using SQLite FTS5
- previous / next poem navigation
- copy poem
- bookmarks for the current session
- adjustable reading font size
- dark / light theme
- source-aware poetry records

## Verification

Final database checks:

- SQLite integrity: **OK**
- Poems: **10,079**
- FTS5 records: **10,079**
- Languages: **9**
- Sources: **19**
- Poets / attribution entries: **248**
- Works: **293**

The final database preserves provenance and does not silently remove historically retained source records merely because identical text may occur in different source records.

## Run

Requirements:

- Python 3
- PySide6

Run:

```bash
python JASS_World_Poetry_Explorer_Final.py
```

The bundled `JASS_World_Poetry.db` is the official final corpus database for this release.

## Final status

**FROZEN / FINAL**

No further language or dataset additions are planned for this project. Earlier databases and staging packages are retained as historical checkpoints.
