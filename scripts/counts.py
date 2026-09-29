import polars as pl 
df = pl.read_csv('outputs/stmt_membership.tsv', separator='\t')
not_pmc = df.filter(pl.col("pubmed").eq(0)).filter(pl.col("pmc").eq(0)).write_csv('outputs/subsets/not_pmc_stmts.tsv', separator='\t')
pmc = df.filter(pl.col("not_pmc").eq(0)).filter(pl.col("pubmed").eq(0)).write_csv('outputs/subsets/pmc_stmts.tsv', separator='\t')
pubmed = df.filter(pl.col("not_pmc").eq(0)).filter(pl.col("pmc").eq(0)).write_csv('outputs/subsets/pubmed_stmts.tsv', separator='\t')
