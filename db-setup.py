import sqlite3
from sqlite3 import Error

def main():
    db = './src/arxiv.db'
    sql = """
        CREATE TABLE IF NOT EXISTS papers (
        ID REAL PRIMARY KEY,
        TITLE TEXT NOT NULL,
        AUTHORS TEXT,
        CREATED TEXT,
        UPDATED TEXT,
        SETSPEC TEXT,
        CATEGORIES TEXT,
        ABSTRACT TEXT,
        COMMENTS TEXT,
        REPORTNUM TEXT,
        JOURNALREF,
        DOI TEXT
    );
    """
    conn = create_connection(db)
    conn.execute('DROP TABLE IF EXISTS papers')
    if conn is not None:
        create_table(conn, sql)
    else:
        print('Error creating database connection')

    conn.close()


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def create_table(conn, sql):
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        print('Created table successfully')
    except Error as e:
        print(e)




if __name__ == '__main__':
    main()