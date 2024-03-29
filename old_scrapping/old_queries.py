"""
Ensemble des requetes SQL utilisées dans le programme
"""

CREATE_TABLE_FROMAGE = '''
    CREATE TABLE IF NOT EXISTS table_fromage 
    (
        id INTEGER PRIMARY KEY,
        fromage TEXT,
        famille TEXT,
        pate TEXT,
        date TEXT
    )
'''
CHECK_IF_EXIST = '''
SELECT COUNT(*) FROM table_fromage WHERE fromage = ?
'''

INSERT_INTO_FROMAGE = '''
    INSERT INTO table_fromage (fromage, famille, pate, date)
    VALUES (?, ?, ?, ?)
'''

UPDATE_FROMAGE = '''
    UPDATE table_fromage
    SET fromage=?, famille=?, pate=?
    WHERE id=?
'''

SELECT_ALL_FROMAGE = 'SELECT * FROM table_fromage'

SELECT_FAMILY_COUNT = '''
    SELECT famille, COUNT(fromage) as nombre_fromages 
        FROM table_fromage 
        GROUP BY famille
'''

DELETE_DUPLICATES = '''
    DELETE FROM table_fromage 
    WHERE id NOT IN (
        SELECT MIN(id) 
        FROM table_fromage 
        GROUP BY fromage
    )
'''

SELECT_DISTINCT_FROMAGE_COUNT = 'SELECT COUNT(DISTINCT fromage) FROM table_fromage'

SELECT_NULL_ROWS = '''
    SELECT * FROM table_fromage WHERE 
        fromage IS NULL OR 
        famille IS NULL OR 
        pate IS NULL OR 
        date IS NULL
'''

COUNT_FROMAGE_BY_NAME = 'SELECT COUNT(*) FROM table_fromage WHERE fromage = ?'

__all__ = [
    'CREATE_TABLE_FROMAGE',
    'INSERT_INTO_FROMAGE',
    'UPDATE_FROMAGE',
    'SELECT_ALL_FROMAGE',
    'SELECT_FAMILY_COUNT',
    'DELETE_DUPLICATES',
    'SELECT_DISTINCT_FROMAGE_COUNT',
    'SELECT_NULL_ROWS',
    'COUNT_FROMAGE_BY_NAME',
    'CHECK_IF_EXIST'
]