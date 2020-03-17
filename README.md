## handling parallel data

This repository has the code I used to create a register-balanced EN>RU parallel corpus, complete with comparable non-translations for each register for translationese studies.

We source data from the following corpora (some of which have been transformed to a collection of plain-text files from an xml/tmx or single-file corpora before):

### Registers and the sources of data
(1) fiction
- parallel: [Russian National Corpus, RNC](http://www.ruscorpora.ru/new/) available upon request
- comparable: RNC

(2) media
- parallel: self-compiled corpus (mostly text-pairs from BBC and InoSMI) + RNC
- comparable: RNC (main)

(3) official
- parallel: [UN documents](https://conferences.unite.un.org/UNCORPUS/en/DownloadOverview#download)
- comparable: UN Russian sources

(4) popsci
- parallel: self-compile corpus of 10 popular-scientific books
- comparable: self-compiled corpus of comparable 14 Russian books

(5) ted
- parallel: 100 talks from [TedTalks category science](https://www.ted.com/talks?sort=newest&topics%5B%5D=Science) for 2016-2018
- comparable: 100 talks on academic topics from Russian [PostNauka lectorium](https://postnauka.ru/) recorded 2016-2018

(6) web corpus
- parallel: [Yandex 1M-token parallel corpus](https://translate.yandex.ru/corpus)
- reference: a 4.9K-texts random subset of [Araneum Minimum](http://unesco.uniba.sk/aranea_about/index.html) provided by the author

### Preprocessing

The texts passed to UDpipe were filtered for:
- sentences/lines shorter that 4 words;
- texts shorter than 400 words;
- UNcorpus: all lines in CAPS, in non-uft8 encoding, starting with Статья and ЧАСТЬ;
- some unmotivated linebreaks were fixed (with re.sub(r'([а-я,;-])\n([а-яА-Я])', r'\1 \2', text));
- lines starting with lowercase alphabet character or not ending in end-of-sentence punctuation

At feature extraction stage, we further filter out:
- sentences consisting of punctuation marks only (ex. '.)') and of numeral and a punctuation (ex. '3.', 'II.')

The repository includes scripts
- to produce separate text files from pre-existing single-file or few-big-files corpora
- to preprocess and parse the raw multi-lingual data structured as a tree of folders
- to extract text-level frequencies of 45 translationese indicators into a single tsv file with folder-names informed metadata

### Other available parallel resources that remained outside this project for various reasons
- EuroParl adapted for translationese studies (no Russian): see [Alina Karakanta's post](https://medium.com/machine-translation-fbk/weve-told-you-before-re-discovering-translationese-in-machine-translation-research-6159ed45c085)
- mozilla transvision [localization corpus](https://transvision.mozfr.org/downloads/) (no Russian reference; includes 17.5 K sentence pairs longer that 2 tokens)
- [Parallel Corpora for European Languages](https://paracrawl.eu/): Russian component exists on the side of the main framework, but I have one web corpus already
- source-less translations identified in RNC
- subtitle and other minor and specific genres from [OPUS](http://opus.nlpl.eu/)
- multiple student translations from [Russian Learner Translation Corpus, RusLTC](https://www.rus-ltc.org/search)
 
