# Exploration using INDRA Readers on non-PubMed Data Sources

Runs the [REACH](https://github.com/clulab/reach) machine reader (via
[`indra_reading`](https://github.com/gyorilab/indra_reading)) over three corpora
of biomedical articles and counts the INDRA statements extracted from each, so
that yield from full text (PMC and non-PMC) can be compared against yield from
PubMed titles + abstracts alone.

## Data sources

Articles live under `data/original_data/<source>/`, one directory per source:

| Source | Contents | Native format |
| --- | --- | --- |
| `pmc` | Open-access full text available from PubMed Central | `.md` (converted from PDF) |
| `not_pmc` | Full text obtained outside PMC | `.md` (converted from PDF) |
| `pubmed` | PubMed records — title and abstract only | `.xml` |

`data/acc_avail_20260404.csv` is the accession manifest (`pmid, dir, doi,
full_text_link, year`) describing which articles were available from where.
`data/example/` holds a handful of files from each source, before and after
conversion, for spot-checking the pipeline.

## Setup

Requires Python 3.13+, [uv](https://docs.astral.sh/uv/), and a JVM (REACH is a
Scala program).

1. Clone the reader repos into `readers/`:

   ```bash
   git clone https://github.com/gyorilab/indra_reading.git readers/indra_reading
   git clone https://github.com/clulab/reach.git             readers/reach
   ```

   (`readers/eidos` and `readers/sparser` are also checked out but are not used
   by the current pipeline.)

2. Build the REACH fat JAR:

   ```bash
   cd readers/reach && sbt assembly
   ```

   This produces `readers/reach/target/scala-2.12/reach-<version>-FAT.jar`.

3. Point INDRA at it, in `~/.config/indra/config.ini`:

   ```ini
   [indra]
   REACHPATH = /abs/path/to/readers/reach/target/scala-2.12/reach-1.6.3-SNAPSHOT-FAT.jar
   REACH_VERSION = 1.6.3-SNAPSHOT
   ```

4. Create the environment:

   ```bash
   uv sync --extra dev
   ```

5. Extract the original file set into `data/original_data/`.

## Pipeline

Run from the repository root; each step writes into the directory the next one
reads from.

### 1. Convert to plain text

REACH consumes `.txt`, so both corpora are normalized first into
`data/processed_data/<source>/`.

```bash
bash scripts/xml_to_txt.sh   # pubmed:         .xml -> title + abstract .txt
bash scripts/md_to_txt.sh    # pmc / not_pmc:  .md  -> .txt, then batches them
```

`xml_to_txt.sh` drives `scripts/xml_convert.py`, which pulls `ArticleTitle` and
`AbstractText` out of each PubMed record and prints them as `Title:` /
`Abstract:` lines. Records missing a title or abstract get a warning printed
ahead of the output — which, because the script redirects stdout into the `.txt`
file, lands in the converted text itself; grep `data/processed_data/pubmed/` for
`has no title` / `has not abstract` to find them.

`md_to_txt.sh` copies the Markdown full text across unchanged (only the
extension changes) and then calls `scripts/batch_files.py` to shard each source
into `batch_N/` subdirectories of `BATCH_SIZE` files (default 10). Batching keeps
any single REACH invocation small enough to finish and makes a crash cost one
batch rather than the whole run. PubMed is left unbatched — titles and abstracts
are small enough to read in one pass.

### 2. Read

```bash
bash scripts/run_reach.sh
```

Runs `indra_reading.scripts.read_files` with `-r=reach -n=16` over every batch,
writing `readings.json` and `stmts.json` per batch to
`outputs/<source>/<batch>/` (and `outputs/pubmed/` for the unbatched source).
This is the slow step — it is a full REACH pass over every document.

### 3. Check and count

```bash
bash scripts/check_batches.sh      # prints any batch dir with no stmts.json
bash scripts/count_statements.sh   # -> outputs/statement_counts.csv
```

`count_statements.sh` walks every `stmts.json` and, via
`scripts/count_json.py`, emits `source,batch,statement_count`.

## Results

`outputs/statement_counts.csv` holds one row per batch. As of the last full run:

| Source | Batches | Statements |
| --- | --- | --- |
| `not_pmc` | 302 | 21,329 |
| `pmc` | 179 | 20,778 |
| `pubmed` | 1 | 3,447 |

Note that batch counts are not directly comparable across sources without also
accounting for documents per batch, and that `pubmed` covers the same articles
as the other two sources but with only title and abstract text.

## Layout

```
data/
  original_data/{pmc,not_pmc,pubmed}/   source documents (.md/.pdf, .xml)
  processed_data/{pmc,not_pmc}/batch_N/ batched .txt input for REACH
  processed_data/pubmed/                unbatched .txt input
  example/                              small before/after sample of each source
outputs/
  {pmc,not_pmc}/batch_N/                readings.json, stmts.json per batch
  pubmed/                               readings.json, stmts.json
  statement_counts.csv                  source,batch,statement_count
readers/                                reader checkouts (reach, indra_reading, ...)
scripts/                                pipeline scripts, in the order above
```

`data/`, `outputs/`, `readers/`, and `reach_outputs.tar.gz` are large and not
tracked in git.
