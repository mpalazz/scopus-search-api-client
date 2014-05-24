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

def parse_document_xml(root):
	document = {}
	document['title'] = ""
	document['date'] = ""
	document['issn'] = []
	document['isbn'] = []
	coredata = root.find('./{http://www.elsevier.com/xml/svapi/abstract/dtd}coredata')
	
	for field in coredata:		
		if field.tag == "{http://prismstandard.org/namespaces/basic/2.0/}publicationName":
			document['title'] = field.text
		elif field.tag == "{http://prismstandard.org/namespaces/basic/2.0/}coverDate":
			document['date'] = field.text
		elif field.tag == "{http://prismstandard.org/namespaces/basic/2.0/}issn":
			li = document['issn']
			li.append(field.text)
		elif field.tag == "{http://prismstandard.org/namespaces/basic/2.0/}isbn":
			li = document['isbn']
			li.append(field.text)
			
	return document

def parse_multiple_authors_search_xml(root):
	author_id_list = []
	for author_id in root.findall('./documents/author-profile/{http://purl.org/dc/elements/1.1/}identifier'):
		author_id_list.append(author_id.text[10:])
			
	return author_id_list
