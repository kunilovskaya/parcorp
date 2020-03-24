## Building a register-balanced parallel corpus for translationese research

This repository has the python3 code used to create a register-balanced EN>RU parallel corpus for translationese research. 
The six parallel subcorpora are complemented with register-comparable non-translations.

## The repository includes scripts
(1) to pre-process the downloaded or pre-existing corpora: 
- make them more comparable and balanced
- filter noise
(2) produce corpus stats for structured and cleaned plain text collection
(3) parse the raw multi-lingual data structured as a tree of folders
(4) to extract text-level frequencies of 45 translationese indicators into a single tsv file with folder-names informed metadata

NB! most scripts expect to have all inputs (data, imported modules, support lists) in the same folder and need to be started from this folder.

The raw text data is sources from the following corpora:

### Registers and the sources of data
(1) fiction
- parallel: [Russian National Corpus, RNC](http://www.ruscorpora.ru/new/) available upon request
- comparable: RNC

(2) media
- parallel: self-compiled corpus (mostly text-pairs from BBC and InoSMI)
- comparable: RNC (main)

(3) official
- parallel: [UN documents](https://conferences.unite.un.org/UNCORPUS/en/DownloadOverview#download)
- comparable: UN Russian sources

(4) popsci
- parallel: self-compiled corpus of 10 popular-scientific books
- comparable: self-compiled corpus of comparable 14 Russian books

(5) ted
- parallel: 100 talks from [TedTalks category science](https://www.ted.com/talks?sort=newest&topics%5B%5D=Science) for 2016-2018
- comparable: 100 talks on academic topics from Russian [PostNauka lectorium](https://postnauka.ru/) recorded 2016-2018

(6) web corpus
- parallel: [Yandex 1M-token parallel corpus](https://translate.yandex.ru/corpus)
- reference: a 4.9K-texts random subset of [Araneum Minimum](http://unesco.uniba.sk/aranea_about/index.html) provided by the author 
We represented the Yandex English source texts with functional vectors, clustered the data on these representations and retained four strong clusters while discrding the two smaller ones.
Araneum Russian texts were reduced to a subset that is functionally comparable to the centroids of the four clusters (see [Kunilovskaya et al. 2019](https://comparable.limsi.fr/bucc2019/BUCC2019-proceedings.pdf#page=44) for details)

### Preprocessing

Before going to UDpipe for parsing, the texts were filtered for:
- sentences/lines shorter that 4 words;
- texts shorter than 400 words;
- UNcorpus: all lines in CAPS, in non-uft8 encoding, starting with Статья and ЧАСТЬ;
- some unmotivated linebreaks were fixed (with re.sub(r'([а-я,;-])\n([а-яА-Я])', r'\1 \2', text));
- lines starting with lowercase alphabet character or not ending in end-of-sentence punctuation

At feature extraction stage, we further filter out:
- sentences consisting of punctuation marks only (ex. '.)') and of numeral and a punctuation (ex. '3.', 'II.')

NB! to ensure some sample-size balance (and where document segmentation was absent: ex. Yandex), we split texts into agreeable chunks of up to 500 sentences.
NB! all parallel components are document-aligned only!

**Basic statistical parameters of the register-balanced translationese corpus** (based on pre-processed text before annotation)

  registers   |    source   |  target    |    ref      |
  :---------- |------------:|-----------:|------------:| 
 media        |             |            |             |
   * texts    |    549      |   549      |   1,562     |
   * words    |   642,137   |  595,780   |  268,7215   |
 official (UN)|             |            |             |
   - texts    |    186      |   186      |   274       |
   - words    | 1,098,950   | 1,048,423  | 1,076,034   |
 tedtalks     |             |            |             |
   - texts    |    100      |   100      |   100       |
   - words    |   259,103   | 207,779    | 188,528     |
 yandexweb    |             |            |             |
   - texts    |  1,574      |   1,574    |   1,224     |
   - words    | 16,631,680  | 14,548,943 | 1,189,420   |
 popsci       |             |            |             |
   - texts    |  100        |  100       |   100       |
   - words    | 826,018     | 735,724    |  854,270    |
 fiction      |             |            |             |
   - texts    |  170        |  170       |   100       |
   - words    | 9,619,912   |  8,272,870 |  94,066     |
 

### Other available parallel resources that remained outside this project for various reasons
- EuroParl adapted for translationese studies (no Russian): see [Alina Karakanta's post](https://medium.com/machine-translation-fbk/weve-told-you-before-re-discovering-translationese-in-machine-translation-research-6159ed45c085)
- mozilla transvision [localization corpus](https://transvision.mozfr.org/downloads/) (no Russian reference; includes 17.5 K sentence pairs longer that 2 tokens)
- [Parallel Corpora for European Languages](https://paracrawl.eu/): Russian component exists on the side of the main framework
- source-less translations identified in RNC
- subtitle and other minor and specific genres from [OPUS](http://opus.nlpl.eu/)
- multiple student translations from [Russian Learner Translation Corpus, RusLTC](https://www.rus-ltc.org/search)
 
