#!/bin/bash 
source ./.venv/bin/activate
# for src in $(ls data/example | grep "reformat" ) ; do
## larger full-text articles batches ## 
for src in "pmc" "not_pmc" ; do
	echo $src
	for batch in $( ls data/processed_data/$src | grep batch* ); do
		echo $batch
		mkdir -p outputs/$src/$batch
		python -m indra_reading.scripts.read_files \
			-r=reach \
			-n=16 \
			data/processed_data/$src/$batch \
			outputs/$src/$batch
	done
done

## XML small enough do not need to batch ## 
for src in "pubmed" ; do
	echo $src
	mkdir -p outputs/$src
	python -m indra_reading.scripts.read_files \
		-r=reach \
		-n=16 \
		data/processed_data/$src \
		outputs/$src
done
