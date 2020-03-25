# coding: utf-8
# getting Russian reference from UN corpus downloaded from https://conferences.unite.un.org/UNCORPUS/en/DownloadOverview#download (should be 403 files in UNv1.0-TEI/ru/ folder)

# loop over all folders of xml in UNv1.0-TEI/ru/ and store text marked <s id="6:1" lang="ru">Original: RUSSIAN</s> in separate plain-text files
# e.g. 2007/ccw/gge/2007/wp_7.xml > 2007_ccw_gge_2007_wp_7.txt

import sys, os
from xml.dom import minidom

rootdir = '/home/u2/resources/corpora/parallel/UNv1.0-TEI/ru/'
# parent directory
parent = os.path.join(rootdir, os.pardir)
outto = os.path.abspath(parent) + '/ru_sources/'
os.makedirs(outto, exist_ok=True)

print(outto)

rus = 0
errors = 0
tot_xmls = 0
for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            filepath = subdir + os.sep + file
            rel_path = os.path.relpath(filepath, rootdir) # path, start
            if filepath.endswith(".xml"):
                tot_xmls += 1
                temp = open(filepath, 'r').read()
                if 'Original: RUSSIAN' in temp:
                    outname = '_'.join((rel_path).split('/')).replace('.xml', '.txt')
                    rus += 1

                    try:
                        doc = minidom.parse(filepath)
                        node = doc.documentElement
                        segs = doc.getElementsByTagName("s")
                    except:
                        errors += 1
                        continue
                    with open(outto + outname, 'w') as outfile:
                        for seg in segs:
                            # lang = seg.getAttributeNode('lang').nodeValue
                            text = seg.childNodes[-1].data
                            outfile.write(text + '\n')
                        
print('All %d, rus %d' % (tot_xmls, rus))