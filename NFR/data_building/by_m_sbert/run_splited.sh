#!/bin/bash

for i in {0..10};do
  python 3.build_sbert_dataset_splited.py --query-embedding cache/query_embedding\
   --corpus-embedding cache/corpus_embedding.$i --shard-i $i --shard-max-len 250000 --workers 20 --report-every 1000
done