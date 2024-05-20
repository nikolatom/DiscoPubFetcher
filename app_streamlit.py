import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
import re
import urllib.parse
import shutil
import tempfile

# Helper functions
def get_main_url(url):
    return "/".join(url.split("/")[:3])

def save_pdf_from_url(pdf_url, directory, name, headers):
    try:
        response = requests.get(pdf_url, headers=headers, allow_redirects=True)
        with open(f'{directory}/{name}.pdf', 'wb') as f:
            f.write(response.content)
        return True
    except requests.RequestException as e:
        st.error(f"Failed to download PDF: {e}")
        return False

# Finder functions for extracting PDF URLs from different journals
def acs_publications(req, soup):
    possible_links = [x for x in soup.find_all('a') if type(x.get('title')) == str and ('high-res pdf' in x.get('title').lower() or 'low-res pdf' in x.get('title').lower())]
    if possible_links:
        pdf_url = get_main_url(req.url) + possible_links[0].get('href')
        return pdf_url
    return None

def direct_pdf_link(req, soup):
    if req.content[-4:] == '.pdf':
        return req.content
    return None

def future_medicine(req, soup):
    possible_links = soup.find_all('a', attrs={'href': re.compile("/doi/pdf")})
    if possible_links:
        pdf_url = get_main_url(req.url) + possible_links[0].get('href')
        return pdf_url
    return None

def generic_citation_labelled(req, soup):
    possible_links = soup.find_all('meta', attrs={'name': 'citation_pdf_url'})
    if possible_links:
        return possible_links[0].get('content')
    return None

def nejm(req, soup):
    possible_links = [x for x in soup.find_all('a') if type(x.get('data-download-type')) == str and (x.get('data-download-type').lower() == 'article pdf')]
    if possible_links:
        pdf_url = get_main_url(req.url) + possible_links[0].get('href')
        return pdf_url
    return None

def pubmed_central_v2(req, soup):
    possible_links = soup.find_all('a', attrs={'href': re.compile('/pmc/articles')})
    if possible_links:
        pdf_url = "https://www.ncbi.nlm.nih.gov" + possible_links[0].get('href')
        return pdf_url
    return None

def science_direct(req, soup):
    new_uri = urllib.parse.unquote(req.url)
    req = requests.get(new_uri, allow_redirects=True)
    soup = BeautifulSoup(req.content, 'lxml')
    possible_links = soup.find_all('meta', attrs={'name': 'citation_pdf_url'})
    if possible_links:
        pdf_url = possible_links[0].get('content')
        return pdf_url
    return None

def fetch_pdf(pmid, output_dir, unfetched_pmids, max_attempts=3):
    uri = f"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id={pmid}&retmode=ref&cmd=prlinks"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    attempt = 0
    while attempt < max_attempts:
        try:
            response = requests.get(uri, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                finders = [acs_publications, direct_pdf_link, future_medicine, generic_citation_labelled, nejm, pubmed_central_v2, science_direct]
                for finder in finders:
                    pdf_url = finder(response, soup)
                    if pdf_url and save_pdf_from_url(pdf_url, output_dir, pmid, headers):
                        st.success(f"Successfully fetched {pmid}")
                        return
            else:
                st.error(f"Failed to fetch page for PMID {pmid}, HTTP status code: {response.status_code}")
        except requests.ConnectionError as e:
            st.warning(f"Connection error on attempt {attempt+1} for {pmid}: {e}")
        attempt += 1

    unfetched_pmids.append(pmid)
    st.error(f"Failed to fetch {pmid} after {max_attempts} attempts")

# Streamlit UI
st.title('DiscoPubFetcher - automatic pdf download')
uploaded_file = st.file_uploader("Upload a file with PMIDs (each PMID on a new line or separated by commas):", type=['txt'])
pmid_input = st.text_input('Or enter PMID(s) manually (separated by commas):')
results_file_name = st.text_input('Results folder name:', 'pubmed_down_results')
max_attempts = st.number_input('Max retry attempts:', min_value=1, max_value=10, value=3, step=1)
submit = st.button('Fetch Articles')

def process_pmids(pmids):
    with tempfile.TemporaryDirectory() as temp_dir:
        unfetched_pmids = []
        for pmid in pmids:
            fetch_pdf(pmid.strip(), temp_dir, unfetched_pmids, max_attempts)
        if unfetched_pmids:
            with open(os.path.join(temp_dir, 'unfetched_pmids.tsv'), 'w') as f:
                for pmid in unfetched_pmids:
                    f.write(f"{pmid}\n")
        shutil.make_archive(temp_dir, 'zip', temp_dir)
        st.success('Processing complete!')
        st.download_button('Download Results', data=open(f'{temp_dir}.zip', 'rb').read(), file_name=f'{results_file_name}.zip')

if submit:
    if uploaded_file is not None:
        stringio = uploaded_file.getvalue().decode("utf-8")
        pmids = stringio.replace('\n', ',').split(',')
    elif pmid_input:
        pmids = pmid_input.split(',')
    else:
        st.warning('Please provide PMIDs either by uploading a file or entering them manually.')
        
    if pmids:
        process_pmids(pmids)
