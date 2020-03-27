#!/bin/bash
# run this batch script in terminal from home directory with sh tools/aligner/aligner_demo.sh
cd "`dirname "$0"`"
perl ./scripts/LF_aligner_3.11_with_modules.pl --filetype="t" --infiles="/home/u2/proj/parcorp/rawdata/mock_data/media/source/en/en_11.txt","/home/u2/proj/parcorp/rawdata/mock_data/media/pro/ru/ru_11.txt" --languages="en","ru" --segment="y" --review="xn" --tmx="y" --outfile="/home/u2/out.txt"
perl ./scripts/LF_aligner_3.11_with_modules.pl --filetype="t" --infiles="/home/u2/proj/parcorp/rawdata/mock_data/media/source/en/en_136.txt","/home/u2/proj/parcorp/rawdata/mock_data/media/pro/ru/ru_136.txt" --languages="en","ru" --segment="y" --review="xn" --tmx="y" --outfile="/home/u2/out.txt"
perl ./scripts/LF_aligner_3.11_with_modules.pl --filetype="t" --infiles="/home/u2/proj/parcorp/rawdata/mock_data/media/source/en/en_146.txt","/home/u2/proj/parcorp/rawdata/mock_data/media/pro/ru/ru_146.txt" --languages="en","ru" --segment="y" --review="xn" --tmx="y" --outfile="/home/u2/out.txt"
