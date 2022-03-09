import pandas as pd
import json
import sqlite3
from sqlite3 import Error

def main():
    data = json.load(open('testdata3k.json'))
    db = 'arxiv.db'
    conn = create_connection(db)

    for i, paper in enumerate(data):
        paper_info = get_paper_info(paper)
        print(f'Inserting paper #{i + 1}', end='\r')
        insert_paper(conn, paper_info)

    print('Closed database successfully')

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