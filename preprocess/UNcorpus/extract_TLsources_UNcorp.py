'''
get TL originals (non-translation) to build the reference subcorpus in translationese studies from UN corpus

What the script does:
loop over all folders of xml in UNv1.0-TEI/ru/ and store text marked <s id="6:1" lang="ru">Original: RUSSIAN</s> in separate plain-text files
# e.g. 2007/ccw/gge/2007/wp_7.xml > 2007_ccw_gge_2007_wp_7.txt

USAGE: python3 extract_TLsources_UNcorp.py /path/to/TL/folder/  e.g. 'downloads/UNv1.0-TEI/ru/
'''

import sys, os
from xml.dom import minidom

rootdir = sys.argv[1] # folder with re-assembled and extracted archive for your TL
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