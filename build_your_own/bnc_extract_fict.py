'''
This script extracts texts of specified genres from BNC.
This is how to move all original xmls from the downloaded archive:
-- go the Texts folder and
-- 2554/download/Texts$ find ./ -name "*.xml" -exec cp -rv {} '/where/to/bnc_xml_ol/' \;
-- replace punctuation tags not to lose them
sed -i 's/<c c5="/<w c5="/g' *.xml
sed -i 's/<\/c>/<\/w>/g' *.xml
This is a list of the codes inserted by David Lee for the BNC World Edition.
http://www.lexically.net/downloads/version4/handling_bnc/index.html?dave_lees_class_codes.htm

Usage:
provided that you edit the paths to input and output in lines 49-50 and have cleaners.py in the working directory, i.e. the folder from which you run the script:
python3 bnc_extract_fict.py

'''

import os, re, sys
from xml.dom import minidom
from cleaners import sent_filter
import numpy as np

def genres2files(doc, outf):
    sentences = doc.getElementsByTagName("s")
    wc = 0
    for i in sentences:
        sent = []
        # if you don't see the punctuation in the output, you did not replace the pspecial punct tags in the input xml!
        words = i.getElementsByTagName("w")
        for word in words:
            try:
                token = word.childNodes[-1].data.strip()
                sent.append(token)
            except:
                continue
        
        sent = ' '.join(sent)
        # filtering short and long sentences outside 5-75 range (for tokenized text)
        sent = sent_filter(sent, min=5, max=75, lang='en')
        if sent:
            words = sent.split()
            wc += len(words)
            outf.write(sent + '\n')
    
    outf.close()
    
    return wc


rootdir = '/media/u2/Seagate Expansion Drive/corpora/all_bnc_xml_punct-caredfor/'
outto = '/home/u2/proj/regbalance/lms/raw/fict/en/'
os.makedirs(outto, exist_ok=True)

fict_count = 0

tot_count = 0
bad_files = []
tot_wc = []
fns = []
files = os.listdir(rootdir)
docs = [f for f in files if f.endswith('.xml')]

allfiles = 0

for i, file in enumerate(docs):
    if i % 100 == 0:
        print('I have already analyzed %s texts' % i, file=sys.stderr)
    allfiles += 1
    doc = minidom.parse(rootdir + file)
    node = doc.documentElement
    types = doc.getElementsByTagName("classCode")
    for typ in types:
        try:
            if typ.getAttributeNode('scheme').nodeValue.strip() == 'DLEE':
                if typ.childNodes[-1].data.strip() == 'W fict prose':
                    fict_count += 1
                    outname = file.replace('.xml', '.txt')
                    out = open(outto + outname, 'w')
                    wc = genres2files(doc, out)
                    tot_wc.append(wc)
                    fns.append(file)
                else:
                    continue
            else:
                continue
        except:
            continue

print('Total number of docs processed:', allfiles)
print('Final counts:\nFICT %d' % fict_count)
print('Total wc:', sum(tot_wc))

# check for wc outliers
idx = np.where(abs(tot_wc - np.mean(tot_wc)) > 5.0 * np.std(tot_wc))
listed = idx[0].tolist()
if len(listed) != 0:
    for i in listed:
        print(fns[i])
else:
    print('===No wc outliers detected (5 SD)===')
