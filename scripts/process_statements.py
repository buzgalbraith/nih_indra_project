import csv
from itertools import combinations
from pathlib import Path
import os

from indra.ontology.bio import bio_ontology
from indra.preassembler import Preassembler
from indra.statements import stmts_from_json_file, stmts_to_json_file
from indra.tools.assemble_corpus import filter_grounded_only

SOURCES = ['pubmed', 'pmc', 'not_pmc']
BASE_PATH = Path("./outputs/")
FILTER_NON_GROUNDED = True
grounded_str = 'grounded' if FILTER_NON_GROUNDED else 'ungrounded'
RESULTS_DIR = BASE_PATH.joinpath(f"subsets_{grounded_str}")
MEMBERSHIP_TSV = RESULTS_DIR / "stmt_membership.tsv"
SUMMARY_TSV = RESULTS_DIR / "stmt_overlap_summary.tsv"


def load_source_stmts(source):
    """Load every stmts.json under outputs/<source>/."""
    stmts = []
    for pth in sorted((BASE_PATH / source).rglob("stmts.json")):
        print(pth.as_posix())
        stmts += stmts_from_json_file(pth)
    return stmts


def main(): 
    os.makedirs(RESULTS_DIR, exist_ok=True)

    pa = Preassembler(bio_ontology)
    ## get all unique hashes for each source ## 
    hashed = dict()
    for source in SOURCES:
        deduped = pa.combine_duplicate_stmts(load_source_stmts(source))
        print(f"{source}: {len(deduped)}")
        if FILTER_NON_GROUNDED:
            proccessed = filter_grounded_only(deduped)
            print(f"{source}: {len(proccessed)} after grounding")
        else:
            proccessed = deduped
        hashed[source] = {s.get_hash(): s for s in proccessed}

    ## map those back to source name ## 
    subsets = {src: set(hashed[src]) for src in SOURCES}

    ## find the statements that are just in one source ## 
    for src in SOURCES:
        others = set().union(*(subsets[o] for o in SOURCES if o != src))
        subsets[f"only_{src}"] = subsets[src] - others
    ## find pairwise overlap ## 
    for sr1, sr2 in combinations(SOURCES, 2):
        others = set().union(*(subsets[o] for o in SOURCES
                               if o not in (sr1, sr2)))
        subsets[f"only_{sr1}_and_{sr2}"] = (subsets[sr1] & subsets[sr2]) - others
    ## find the statements  that are in all three ## 
    subsets["all_sources"] = set.intersection(*(subsets[s] for s in SOURCES))
    ## get save all just in case ## 
    subsets["union"] = set().union(*(subsets[s] for s in SOURCES))

    summary = [(name, len(hashes)) for name, hashes in subsets.items()]
    for name, count in summary:
        print(f"{name}: {count}")

    ## write summary ## 
    with open(SUMMARY_TSV, "w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["comparison", "n_statements"])
        writer.writerows(summary)

    ## write each subset to a file ## 
    all_stmts = dict()
    for src in SOURCES:
        for h, stmt in hashed[src].items():
            all_stmts.setdefault(h, stmt)

    # one row per unique statement, with a 0/1 column per source
    with open(MEMBERSHIP_TSV, "w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["stmt_hash", "stmt_type", "statement"] + SOURCES)
        for h, stmt in all_stmts.items():
            writer.writerow(
                [h, type(stmt).__name__, str(stmt)]
                + [int(h in hashed[src]) for src in SOURCES]
            )

    # one json per subset, merging evidence from every source with the stmt
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, hashes in subsets.items():
        stmts = [hashed[src][h] for src in SOURCES
                 for h in hashes if h in hashed[src]]
        stmts_to_json_file(pa.combine_duplicate_stmts(stmts),
                           RESULTS_DIR / f"{name}.json")


if __name__ == "__main__":
    main()
