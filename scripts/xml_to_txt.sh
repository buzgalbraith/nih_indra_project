## Take title and text from PubMed xml put in txt doc ## 
#!/bin/bash
source .venv/bin/activate
new_dir=data/processed_data/pubmed
mkdir -p $new_dir
for f in $( find data/original_data/pubmed -name "*.xml" ); do
	pr=$(dirname $f)
	f_name=$(basename $f )
	new_name=$(echo $f_name | sed 's/xml/txt/' )
	python3 scripts/xml_convert.py $f  > $new_dir/$new_name
done
