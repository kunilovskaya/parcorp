## Parallel Corpora: processing, building and using in research

## The repository has scripts
(1) to pre-process the downloaded or pre-existing corpora: 

- make them more comparable and balanced
- filter noise

(2) bulding a corpus from them, inc. automating google-translator
**see [code](https://github.com/kunilovskaya/scrape) and instructions for scraping parallel texts from a website (with multilingual BBC as example)**

(3) produce corpus stats for structured and cleaned plain text collection (or parsed texts)

(4) parse the raw multi-lingual data structured as a tree of folders

(5) *stats* folder contains scripts that demonstrate approaches for statistics extraction from various formats and for various types of linguistic items

(6) (advanced) to extract text-level frequencies of 45 translationese indicators into a single tsv file with metadata from folder names 

The repository includes data folders (*parsing/clean* *translationese/parsed* and *formats*) that contain toy corpora for practice, and the *stats/tables* folder with the output of stats-extractors that are used as input to stats-analysers

NB! most scripts expect all inputs (data, imported modules, support lists) in the same folder and need to be started from this folder.


## Case-study: A register-balanced corpus for translationese research)

Inter alia, the repository includes the python3 code used to create a register-balanced EN>RU parallel corpus for translationese research. 
The parallel subcorpora for each register are complemented with register-comparable non-translations in source and target.
The raw text data is sourced from the following corpora:

### Registers and the sources of data
(1) fiction
- parallel: [Russian National Corpus, RNC](http://www.ruscorpora.ru/new/) available upon request
- comparable: RNC, BNC

(2) media
- parallel: self-compiled corpus (mostly text-pairs from BBC and InoSMI)
- comparable: RNC (main), BNC

(3) official (NB! no sentence-aligned data)
- parallel: [UN documents](https://conferences.unite.un.org/UNCORPUS/en/DownloadOverview#download)
- comparable: UN Russian sources

(4) popsci
- parallel: self-compiled corpus of 10 popular-scientific books
- comparable: self-compiled corpus of comparable 14 Russian books + RNC, BNC

(5) ted (NB! subtitling is it's own translation genre!)
- parallel: 100 talks from [TedTalks category science](https://www.ted.com/talks?sort=newest&topics%5B%5D=Science) for 2016-2018
- comparable: 100 talks on academic topics from Russian [PostNauka lectorium](https://postnauka.ru/) recorded 2016-2018

(6) web corpus (NB! a random collection of aligned sentences, not texts)
- parallel: [Yandex 1M-token parallel corpus](https://translate.yandex.ru/corpus)
- reference: a 4.9K-texts random subset of [Araneum Minimum](http://unesco.uniba.sk/aranea_about/index.html) provided by the author 
We represented the Yandex English source texts with functional vectors, clustered the data on these representations and retained four strong clusters while discrding the two smaller ones.
Araneum Russian texts were reduced to a subset that is functionally comparable to the centroids of the four clusters (see [Kunilovskaya et al. 2019](https://comparable.limsi.fr/bucc2019/BUCC2019-proceedings.pdf#page=44) for details)

(7) News Commentary corpus (NB! no document separation)
- parallel: chunked into files
- reference: political and economic articles from 200M token RNC newspaper subcorpus 

### Preprocessing approaches:

Before going to UDpipe for parsing, the texts were filtered for:
- sentences/lines shorter that 4 words;
- texts shorter than 400 words;
- UNcorpus: all lines in CAPS, in non-uft8 encoding, starting with Статья and ЧАСТЬ;
- some unmotivated linebreaks were fixed (with re.sub(r'([а-я,;-])\n([а-яА-Я])', r'\1 \2', text));
- lines starting with lowercase alphabet character or not ending in end-of-sentence punctuation

At feature extraction stage, we further filter out:
- sentences consisting of punctuation marks only (ex. '.)') and of numeral and a punctuation (ex. '3.', 'II.')


### Other available parallel resources that remained outside this project for various reasons
- EuroParl adapted for translationese studies (no Russian): see [Alina Karakanta's post](https://medium.com/machine-translation-fbk/weve-told-you-before-re-discovering-translationese-in-machine-translation-research-6159ed45c085)
- mozilla transvision [localization corpus](https://transvision.mozfr.org/downloads/) (no Russian reference; includes 17.5 K sentence pairs longer that 2 tokens)
- [Parallel Corpora for European Languages](https://paracrawl.eu/): Russian component exists on the side of the main framework
- source-less translations identified in RNC
- subtitle and other minor and specific genres from [OPUS](http://opus.nlpl.eu/)
- multiple student translations from [Russian Learner Translation Corpus, RusLTC](https://www.rus-ltc.org/search)
 
