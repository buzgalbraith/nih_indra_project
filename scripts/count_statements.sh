## count the number of Indra statements produced ## 
#!/bin/bash 

touch outputs/statement_counts.csv
echo "source,batch,statement_count" > outputs/statement_counts.csv
for f in $( find outputs -name stmts.json ); do 
	python scripts/count_json.py $f >> outputs/statement_counts.csv
done
