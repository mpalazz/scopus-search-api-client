import xml.etree.ElementTree as ET
import scopus_api
import xml_parser


def retrieve_author_ids_by_affiliation_id(aff_id):
	print 'Retrieving author ids for affiliation id ' + str(aff_id) + '...'
	
	author_id_list = []
	num_queries = 0
	retry_time = 10
	while True:
		start_offset = num_queries * 500 + 1
		print 'Downloading and parsing search list xml n. %s (start offset = %s)' % (str(num_queries + 1), str(start_offset))
		
		xml_buffer = scopus_api.get_authors_by_affiliation_id(str(aff_id), start_offset)
		
		if not xml_buffer is None:
			xml_root = ET.fromstring(xml_buffer)
			ids_to_add = xml_parser.parse_multiple_authors_search_xml(xml_root)
			
			for id_to_add in ids_to_add:
				author_id_list.append(id_to_add)
			
			num_queries += 1
			if len(ids_to_add) == 0:
				break
		else:
			print '  > Retrying in', retry_time, 'seconds...'
			#time.sleep(retry_time)
			break
			
	print '  >', len(author_id_list), 'author ids retrieved!'
	
	return author_id_list
	
	
def retrieve_author_profile(author_id):
	xml_buffer = scopus_api.get_author_profile_by_author_id(author_id)

	if not xml_buffer is None:
		xml_root = ET.fromstring(xml_buffer)
		author_profile_document = xml_parser.parse_author_profile_xml(xml_root)
		
		return author_profile_document
	else:
		return None	


def retrieve_author_documents(author_id):
	xml_buffer = scopus_api.get_documents_by_author_id(author_id)
	
	if not xml_buffer is None:
		xml_root = ET.fromstring(xml_buffer)
		total_results = xml_parser.get_total_results_from_author_products_xml(xml_root) 
		documents = xml_parser.parse_author_products_xml(xml_root, int(author_id))
		
		if not total_results is None and total_results > 200:
			offset_start = 200
			while True:
				xml_buffer = scopus_api.get_documents_by_author_id(author_id, offset_start)
				xml_root = ET.fromstring(xml_buffer)
				documents_to_add = xml_parser.parse_author_products_xml(xml_root, int(author_id))
				
				for doc in documents_to_add:
					documents.append(doc)
				
				offset_start += 200
				if offset_start > total_results:
					break
	
	return documents

if __name__ == '__main__':
	#sapienza_affiliation_id = '60032350'
	#download_author_profiles_to_mongo(sapienza_affiliation_id)
	author_id = '6701771330'
	#print retrieve_author_profile(author_id)
	print retrieve_author_documents(author_id)
