'''
TASK:
Given a query in SL, return all sentence pairs, where sources contain this query.
The script expects a tmx and a list of queries. It can have one query. If you want to search for a WME, use double quotes

NB! to avoid noise, it makes sense to annotate the corpus to get something like CONN_bytheway

USAGE: python3 stats_extraction/parconcord.py formats/media-prof.tmx "by the way"

NB! if you want to save the concordance to a tab-delimited spreadsheet, use:
python3 stats_extraction/parconcord.py formats/media-prof.tmx "by the way" > stats/tables/bytheway_concord.tsv
'''



import sys
from xml.dom import minidom

bitext = sys.argv[1]
query = sys.argv[2]

def get_first_seg_text(tuv):
    
    segs = tuv.getElementsByTagName("seg")

    if len(segs)==0:
        return None

    seg0 = segs[0]

    if len(seg0.childNodes) == 0:
        return ""

    text = seg0.childNodes[-1].data
    
    return text

def find_source(tu, test_str):
    """
    get tuv from tu, if lang=="EN" and contains the query
    """ 
   
    tuvs = tu.getElementsByTagName("tuv")

    for tuv in tuvs:
        lang = tuv.getAttributeNode('xml:lang').nodeValue

        if lang == "EN":
            text = get_first_seg_text(tuv)
        else:
            continue

        if text is None:
            continue

        pos = text.find(test_str)
        if -1==pos:
            continue

        return tuv
    return None

            
def find_translations(tu):

    tuvs = tu.getElementsByTagName("tuv")
    for tuv in tuvs:
        lang = tuv.getAttributeNode('xml:lang').nodeValue
        if lang != "RU":
            continue
        else:
            target = tuv
            
        return target
    return None

def process_tmx(xml, query):
    doc = minidom.parse(xml)
    node = doc.documentElement
    tus = doc.getElementsByTagName("tu")
    
    print('Query', '\t', 'Source', '\t', 'Targets')

    for tu in tus:
        tuv_src = find_source(tu, query)
        if tuv_src is None:
            continue 
        text_src = get_first_seg_text(tuv_src)

        tuv_tr = find_translations(tu)#это список
        if tuv_tr == None:
            continue

        text_tr = get_first_seg_text(tuv_tr)
            #texts_tr.append(text_tr)
        print('\t', text_src, '\t', text_tr)

process_tmx(bitext, query)
