import re	

		
def is_int(string):
	try:
		num = int(string)
		return True
	except ValueError:
		return False

def  get_cited_count_only(root, pmids):
	record = {}
	for elem in root.iter('{http://www.w3.org/2005/Atom}entry'):
		# check for error tag
		# if error - check google scholar. 

		if  elem.find('{http://www.w3.org/2005/Atom}error') is not None:
			print 'error in scopus request'
		idEntry =  elem.find( \
			'{http://www.w3.org/2005/Atom}pubmed-id')
		if idEntry is not None:
			
			assert idEntry.text.strip() in pmids, \
				'%s not in pmids' %idEntry.text.strip() 

			pmid = idEntry.text.strip()

			citeEntry =  elem.find( \
				'{http://www.w3.org/2005/Atom}citedby-count')

			if citeEntry is not None:
				record[pmid]  =  int(citeEntry.text)
			else:
				print 'no citation entry found'
				record[pmid]  =  -1
				
	if type(pmids)==str:
		pmids = [pmids]					
	for pmid in pmids:
		if pmid not in record:
			record[pmid] = -1

	return record



def get_total_results_from_author_products_xml(root):
	elem = root.find('./{http://a9.com/-/spec/opensearch/1.1/}totalResults')
	try:
		total_results = int(elem.text)
		return total_results
	except ValueError:
		print '   > ERROR parsing total results'
		return None

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


def add_affiliations_to_list(affiliation_list, affiliation_superblock):
	for affiliation_block in affiliation_superblock.findall('./affiliation'):
		add_affiliation_document_to_list(affiliation_list, affiliation_block)

		
def add_affiliation_document_to_list(affiliation_list, affiliation_block):
	affiliation_doc = {}
	
	try:
		affiliation_doc['affiliation_id'] = int(affiliation_block.attrib['affiliation-id'])
		affiliation_doc['type'] = affiliation_block.find('./ip-doc').attrib['type']
		affiliation_doc['parent_id'] = int(affiliation_block.attrib['parent'])
	except KeyError:
		pass
	
	for field in affiliation_block.findall('./ip-doc/*'):
		if field.tag == 'afnameid':
			affiliation_doc['afnameid'] = affiliation_block.find('./ip-doc/afnameid').text
		elif field.tag == 'afdispname':
			affiliation_doc['afdispname'] = affiliation_block.find('./ip-doc/afdispname').text
		elif field.tag == 'preferred-name':
			affiliation_doc['preferred_name'] = affiliation_block.find('./ip-doc/preferred-name').text
		elif field.tag == 'parent-preferred-name':
			affiliation_doc['parent_preferred_name'] = affiliation_block.find('./ip-doc/parent-preferred-name').text
		elif field.tag == 'sort-name':
			affiliation_doc['sort_name'] = affiliation_block.find('./ip-doc/sort-name').text
		elif field.tag == 'org-domain':
			affiliation_doc['org_domain'] = affiliation_block.find('./ip-doc/org-domain').text
		elif field.tag == 'org-URL':
			affiliation_doc['org_url'] = affiliation_block.find('./ip-doc/org-URL').text
		elif field.tag == 'address':
			address_doc = {}
			
			if not affiliation_block.find('./ip-doc/address/address-part') is None:
				address_doc['address_part'] = affiliation_block.find('./ip-doc/address/address-part').text
			if not affiliation_block.find('./ip-doc/address/city') is None:
				address_doc['city'] = affiliation_block.find('./ip-doc/address/city').text
			if not affiliation_block.find('./ip-doc/address/state') is None:
				address_doc['state'] = affiliation_block.find('./ip-doc/address/state').text
			if not affiliation_block.find('./ip-doc/address/postal-code') is None:
				address_doc['postal_code'] = affiliation_block.find('./ip-doc/address/postal-code').text
			if not affiliation_block.find('./ip-doc/address/country') is None:
				address_doc['country'] = affiliation_block.find('./ip-doc/address/country').text
			
			affiliation_doc['address'] = address_doc
		
	affiliation_list.append(affiliation_doc)


def add_journals_to_list(journal_list, journal_history_block):
	for journal_block in journal_history_block.findall('./journal'):
		add_journal_document_to_list(journal_list, journal_block)


def add_journal_document_to_list(journal_list, journal_block):
	journal_doc = {}
	
	try:
		journal_doc['type'] = journal_block.attrib['type']
	except KeyError:
		pass
	
	for field in journal_block.findall('./*'):
		if field.tag == 'sourcetitle':
			journal_doc['sourcetitle'] = journal_block.find('./sourcetitle').text
		elif field.tag == 'sourcetitle-abbrev':
			journal_doc['sourcetitle_abbrev'] = journal_block.find('./sourcetitle-abbrev').text
		elif field.tag == 'issn':
			journal_doc['issn'] = journal_block.find('./issn').text
		
		
	journal_list.append(journal_doc)
	

def add_name_document_to_list(names_list, name_block):
	name = {}
	if not name_block.find('./initials') is None:
		name['initials'] = name_block.find('./initials').text
	if not name_block.find('./indexed-name') is None:
		name['indexed-name'] = name_block.find('./indexed-name').text
	if not name_block.find('./surname') is None:
		name['surname'] = name_block.find('./surname').text
	if not name_block.find('./given-name') is None:
		name['given-name'] = name_block.find('./given-name').text
	names_list.append(name)
	
	
def parse_author_profile_xml(root):
	doc = {}
	name_variants = []
	journal_history = []
	affiliation_current = []
	affiliation_history = []
	
	for child in root.findall('./*/*'):
		if child.tag == '{http://purl.org/dc/elements/1.1/}identifier':
			doc['author_id'] = int(child.text[10:])
		elif child.tag == 'document-count':
			doc['document_count'] = int(child.text)
		elif child.tag == 'cited-by-count':
			doc['cited_by_count'] = int(child.text)
		elif child.tag == 'citation-count':
			doc['citation_count'] = int(child.text)
		elif child.tag == 'publication-range':
			try:
				doc['publication_start'] = int(child.attrib['start'])
			except KeyError:
				pass
			try:
				doc['publication_end'] = int(child.attrib['end'])
			except KeyError:
				pass
		elif child.tag == 'classificationgroup':
			classification_doc = {}
			
			for field in child.findall('./classifications/classification'):
				classification_doc[field.text] = int(field.attrib['frequency'])
				
			doc['classifications'] = classification_doc
		elif child.tag == 'affiliation-current':
			add_affiliations_to_list(affiliation_current, child)
		elif child.tag == 'affiliation-history':
			add_affiliations_to_list(affiliation_history, child)
		elif child.tag == 'journal-history':
			add_journals_to_list(journal_history, child)
		elif child.tag == 'preferred-name' or child.tag == 'name-variant':
			add_name_document_to_list(name_variants, child)

	doc['affiliation_current'] = affiliation_current
	doc['affiliation_history'] = affiliation_history
	doc['journal_history'] = journal_history
	doc['names'] = name_variants;
	
	return doc
