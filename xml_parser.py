import xml.etree.ElementTree as ET
import os	
		
def is_int(string):
	try:
		num = int(string)
		return True
	except ValueError:
		return False
				
def parse_author_products_xml(root, author_id):
	documents = []

	for entry in root.findall('./*'):
		if entry.tag == '{http://www.w3.org/2005/Atom}entry':
			document = {}
			found_year = False
			
			for attribute in entry.findall('./*'):
				if attribute.tag == '{http://purl.org/dc/elements/1.1/}identifier':
					document['document_id'] = str(attribute.text[10:])
				elif attribute.tag == '{http://purl.org/dc/elements/1.1/}title':
					document['title'] = attribute.text
				elif attribute.tag == '{http://www.w3.org/2005/Atom}citedby-count':
					document['cited_by_count'] = int(attribute.text)
				elif attribute.tag == '{http://prismstandard.org/namespaces/basic/2.0/}coverDate':
					date_split = attribute.text.split('-')
					
					for token in date_split:
						if len(token) == 4 and is_int(token):
							document['year'] = int(token)
							found_year = True
							break
			
			if not found_year:
				cover_display_date = entry.find('./{http://prismstandard.org/namespaces/basic/2.0/}coverDisplayDate')
				if not cover_display_date is None:
					date_split = re.findall(r"[\w']+", cover_display_date.text)
					for token in date_split:
						if len(token) == 4 and is_int(token):
							document['year'] = int(token)
							found_year = True
							break
				
				if not found_year:
					print 'Impossible to extract publication year for a document (author id: ' + str(author_id) + ')'
			
			if len(document) > 0:
				documents.append(document)
			
	return documents
