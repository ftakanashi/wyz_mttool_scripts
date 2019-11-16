## wyz_mttool_scripts
This is a repo saving some scripts developed by myself, using to do MT tasks(especially preprocessing).
For usage, run the script with option --help.

- chinese_tokenize.py
> Tokenize Chinese corpus based on jieba tokenizer.

- extract_hyp_wei.py
> Extract all hypothesis rows in a generate log file produced by fairseq/generate.py
> NOTE: fairseq <= 0.8.0 may place a sum of log probabilities before the first token of the row. Remember to remove it
> if you need to calculate BLEU score later.

- split_text_abs.py
> Split a whole bunch of text data into train/valid/test dataset.
> Outputing files like train.src|tgt valid.src|tgt test.src|tgt

- who_is_using_gpu.py
> Usage: python who_is_using_gpu.py <pid>
> The pid can be fetched by running command nvidia-smi.