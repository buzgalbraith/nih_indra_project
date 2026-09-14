## check to make sure that all batches have some kind of statements ## 
#!/bin/bash
for src in "pmc" "not_pmc"; do
  for d in outputs/$src/*; do
    [ -f "$d/stmts.json" ] || echo "Missing in: $d"
  done
done
