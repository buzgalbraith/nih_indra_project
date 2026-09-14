## directly copy md files to have txt extensions ##
#!/bin/bash
BATCH_SIZE=10
for src in "pmc" "not_pmc" ; do
	echo $src
	new_dir=data/processed_data/$src
	for f in $( find data/original_data/${src}/ -name "*.md" ); do
		f_name=$(basename $f )
		new_name=$(echo $f_name | sed 's/md/txt/' )
		mkdir -p $new_dir
		cp $f $new_dir/$new_name
	done
done
## split files into batches ## 
source .venv/bin/activate
python3 scripts/batch_files.py $BATCH_SIZE

