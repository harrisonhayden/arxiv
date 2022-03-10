import os.path
import requests
import xmltodict
from datetime import datetime
import time
import sqlite3
from sqlite3 import Error

BASE = 'http://export.arxiv.org/oai2?verb=ListRecords'
DIR = os.path.dirname(os.path.abspath('all-papers.py'))
DB_PATH = os.path.join(DIR, 'arxiv.db')

def main():
    # initial request for every single paper (returns first 1000)
    print('Fetching first 1000 papers...')
    response = requests.get(f'{BASE}&metadataPrefix=arXiv')

    # grabbing resumption token for subsequent requests
    initial_dict = xmltodict.parse(response.text)
    first_thousand_papers = initial_dict['OAI-PMH']['ListRecords']['record']
    total_papers = int(initial_dict['OAI-PMH']['ListRecords']['resumptionToken']['@completeListSize'])
    res_token = initial_dict['OAI-PMH']['ListRecords']['resumptionToken']['#text']

    conn = create_connection('arxiv.db')
    insert_all(conn, first_thousand_papers, 1)

    print('Sleeping...', end='\x1b[1K\r')
    time.sleep(5)

    all_papers_to_db(conn, res_token, total_papers)
    conn.close()
    print('Closed database successfully.')
    print(f'Time finished: {datetime.now().strftime("%m/%d/%Y %H:%M:%S")}')


def all_papers_to_db(conn, res_token, total):
    batch_num = 2
    # keep requesting with new response token. once token has no text field, we're at the end
    while res_token:
        num_done = 1000 * (batch_num - 1)
        percent_done = round(100 * (num_done / total), 2)
        print(f'{num_done} papers finished ({percent_done}%). Fetching next 1000 papers...')
        response = requests.get(f'{BASE}&resumptionToken={res_token}')
        response_dict = xmltodict.parse(response.text)
        papers = response_dict['OAI-PMH']['ListRecords']['record']
        res_token = response_dict['OAI-PMH']['ListRecords']['resumptionToken'].get('#text')
        insert_all(conn, papers, batch_num)
        batch_num += 1

        # print('Sleeping...', end='\x1b[1K\r')
        # time.sleep(5)

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def insert_paper(conn, paper):
    sql = """
        INSERT INTO papers(ID, TITLE, AUTHORS, CREATED, UPDATED, SETSPEC, CATEGORIES, ABSTRACT, COMMENTS, REPORTNUM, JOURNALREF, DOI)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    cursor = conn.cursor()
    cursor.execute(sql, paper)
    conn.commit()

def insert_all(conn, papers, batch_num):
    for i, paper in enumerate(papers):
        paper_info = get_paper_info(paper)
        print(f'Inserting paper #{1000 * (batch_num - 1) + i + 1}', end='\r')
        insert_paper(conn, paper_info)

def get_authors(authors):
    author_list = []
    for author in authors:
        author_list.append(author['keyname'])
    return ', '.join(author_list)

def get_sets(setSpec):
    return ', '.join(setSpec)

def get_paper_info(paper):
    main = paper['metadata']['arXiv']
    setSpec = paper['header'].get('setSpec')
    authors = main['authors']['author']
    ID = main['id']
    TITLE = main['title']
    if type(authors) is list:
        AUTHORS = get_authors(authors)
    else:
        AUTHORS = authors['keyname']
    CREATED = main.get('created')
    UPDATED = main.get('updated')
    if type(setSpec) is list:
        SETSPEC = get_sets(setSpec)
    else:
        SETSPEC = setSpec
    CATEGORIES = main.get('categories')
    ABSTRACT = main.get('abstract')
    COMMENTS = main.get('comments')
    REPORTNUM = main.get('report-no')
    JOURNALREF = main.get('journal-ref')
    DOI = main.get('doi')

    return (ID, TITLE, AUTHORS, CREATED, UPDATED, SETSPEC, CATEGORIES, ABSTRACT, COMMENTS, REPORTNUM, JOURNALREF, DOI)

if __name__ == '__main__':
    main()