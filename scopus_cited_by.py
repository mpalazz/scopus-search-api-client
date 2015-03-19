import xml.etree.ElementTree as ET
import scopus_api
import xml_parser
import time



def retrieve_cited_count_by_pmid(pmids):
    
    # num_queries = 0
    retry_time = 1
    while True:
        # start_offset = num_queries * 500 + 1
        # print 'Downloading and parsing search list xml n. %s (start offset = %s)' % (str(num_queries + 1), str(start_offset))

        xml_buffer = scopus_api.get_cited_count_by_PMID(pmids)
        
        if  xml_buffer is not None:
            xml_root = ET.fromstring(xml_buffer)
            records = xml_parser.get_cited_count_only(xml_root, pmids)
            break
        else:
            print '  > Retrying in', retry_time, 'seconds...'


            time.sleep(1)
            # break
                
    return records


if __name__ == '__main__':
#sapienza_affiliation_id = '60032350'
#download_author_profiles_to_mongo(sapienza_affiliation_id)
    pmids = [14726593,23579055,24698262]
#print retrieve_author_profile(author_id)
    print retrieve_cited_count_by_pmid(pmids)