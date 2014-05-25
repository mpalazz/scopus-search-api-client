import pycurl
import xml.etree.ElementTree as ET
import cStringIO

APIKEY = '4180d0d1db751b3002edc47967a007e1' # insert your API key here

curl = pycurl.Curl()
curl.setopt(pycurl.FAILONERROR, True)
#curl.setopt(pycurl.CONNECTTIMEOUT, 15)
#curl.setopt(pycurl.TIMEOUT, 15)
curl.setopt(pycurl.HTTPHEADER, [
	'X-ELS-APIKey: ' + APIKEY,
	'X-ELS-ResourceVersion: XOCS',
	'accept: application/xml, text/xml'])


def perform_query(query):
	xml_buffer = cStringIO.StringIO()
	
	try:
		curl.setopt(pycurl.URL, query)
		curl.setopt(pycurl.WRITEFUNCTION, xml_buffer.write)
		curl.perform()
		
		if curl.getinfo(pycurl.RESPONSE_CODE) >= 300:
			print 'Scopus API HTTP error response code:', str(curl.getinfo(pycurl.RESPONSE_CODE))
			return None
		else:
			return xml_buffer.getvalue()
	except Exception, error:
		print 'Scopus API error:', str(error)
		return None

def get_authors_by_affiliation_id(aff_id, start_offset=1):
	authors_by_affiliation_id_query = 'http://api.elsevier.com/content/affiliation/AFFILIATION_ID:'
	query_parameters = '?view=authors&count=500&start=' + str(start_offset)
	query = authors_by_affiliation_id_query + str(aff_id) + query_parameters
	
	return perform_query(query)
	
	
def get_authors_by_name(surname, name):
	authors_by_name_query_start = 'http://api.elsevier.com/content/search/index:AUTHOR?query=authlast('
	authors_by_name_query_middle = ')%20AND%20authfirst('
	authors_by_name_query_end = ')'
	query = authors_by_name_query_start + str(surname) + authors_by_name_query_middle + str(name) + authors_by_name_query_end
	
	return perform_query(query)
	

def get_author_profile_by_author_id(author_id):
	author_profile_by_author_id_query = 'http://api.elsevier.com/content/author/AUTHOR_ID:'
	query = author_profile_by_author_id_query + str(author_id)
	
	return perform_query(query)


def get_documents_by_author_id(author_id, start_offset=0):
	documents_by_author_id_query_start = 'http://api.elsevier.com/content/search/index:SCOPUS?query=au-id('
	documents_by_author_id_query_end = ')&sort=citedby-count&count=200&start='
	query = documents_by_author_id_query_start + str(author_id) + documents_by_author_id_query_end + str(start_offset)
	
	return perform_query(query)

def get_document_by_eid(eid):
	#query = 'http://api.elsevier.com/content/search/index:SCOPUS?query=DOI(' + str(eid) + ')?view=FULL'
	#query = 'http://api.elsevier.com/content/article/SCOPUS_ID:' + str(eid) + ''
	query = 'http://api.elsevier.com/content/abstract/EID:' + eid# + '?view=FULL'
	
	return perform_query(query)

def authenticate():
	query = 'http://api.elsevier.com/authenticate'
	
	return perform_query(query)
