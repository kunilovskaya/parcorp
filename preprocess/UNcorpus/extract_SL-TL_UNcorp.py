'''
TASK:
from reassembled extracted XML archives for each language in a language pair downloaded from https://conferences.unite.un.org/UNCORPUS/en/DownloadOverview
get a collection of plain texts for SL that are translated into selected TL (default English > Russian, adjust the code for other pairs)

Steps in the code:
(1) get a list of filepaths for texts in UNv1.0-TEI/en/ that are marked as Original: ENGLISH
(2) follow the paths to see whether there are corresponding texts in UNv1.0-TEI/ru/ and get them

USAGE: python3 extract_SL-TL_UNcorp.py /path/to/TL/folder/  e.g. 'downloads/UNv1.0-TEI/en/
'''

import sys, os
from xml.dom import minidom

source_rootdir = sys.argv[1] # folder with re-assembled and extracted archive for your SL

# parent directory
parent = os.path.join(source_rootdir, os.pardir)
source_outto = os.path.abspath(parent) + '/parallel/en/'
target_outto = os.path.abspath(parent) + '/parallel/ru/'
os.makedirs(source_outto, exist_ok=True)
os.makedirs(target_outto, exist_ok=True)
print(source_outto)

all_source = 0
marked_source = 0
pairs = 0
notarget = 0
source_errors = 0
target_errors = 0
same_length = 0
for subdir, dirs, files in os.walk(source_rootdir):
        for file in files:
            source_filepath = subdir + os.sep + file
            
            if source_filepath.endswith(".xml"):
                all_source += 1
                temp = open(source_filepath, 'r').read()
                if 'Original: ENGLISH' in temp: # adjust accordingly
                    marked_source += 1
                    
                    target_filepath = source_filepath.replace('en', 'ru')
                    if os.path.isfile(target_filepath):
                        
                        try:
                            target_doc = minidom.parse(target_filepath)
                            target_node = target_doc.documentElement
                            target_segs = target_doc.getElementsByTagName("s")
                        except:
                            target_segs = None
                            target_errors += 1
                        try:
                            source_doc = minidom.parse(source_filepath)
                            source_node = source_doc.documentElement
                            source_segs = source_doc.getElementsByTagName("s")
                        except:
                            source_segs = None
                            source_errors += 1
                            # print('No translation into the target')
                            continue
                            
                        if source_segs and target_segs:
                            rel_path = os.path.relpath(source_filepath, source_rootdir)  # path, start
                            # adjust languages
                            source_outname = 'en_' + '_'.join((rel_path).split('/')).replace('.xml', '.txt')
                            target_outname = 'ru_' + '_'.join((rel_path).split('/')).replace('.xml', '.txt')
                            pairs += 1
                            
                            if len(source_segs) == len(target_segs):
                                same_length += 1
                                
                            with open(source_outto + source_outname, 'w') as source, open(target_outto + target_outname, 'w') as target:
                                for source_seg in source_segs:
                                    # lang = seg.getAttributeNode('lang').nodeValue
                                    try:
                                        stext = source_seg.childNodes[-1].data
                                        source.write(stext + '\n')
                                    except IndexError:
                                        continue
                                for target_seg in target_segs:
                                    # lang = seg.getAttributeNode('lang').nodeValue
                                    try:
                                        ttext = target_seg.childNodes[-1].data
                                        target.write(ttext + '\n')
                                    except IndexError:
                                        continue
                    else:
                        notarget += 1
                        
print('All texts in SL: %d, originals: %d' % (all_source, marked_source))
print('Total number of text pairs: %d' % pairs)
print('Ratio of pairs where texts have same sent count %.1f' % (same_length/pairs*100))
print('Unable to retrieve text: Source %d; Target %d' % (source_errors, target_errors))