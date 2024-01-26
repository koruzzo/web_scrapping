"""..."""
from urllib.request import urlopen
from datetime import datetime
import sqlite3
from bs4 import BeautifulSoup

class FromageWEB:
    """..."""
    def __init__(self, bdd_path = 'fromage.db'):
        self.bdd_path = bdd_path
        self.conn = sqlite3.connect(bdd_path)# Connection bdd
        self.create_table_fromage()

    def create_table_fromage(self):
        """..."""
        cursor = self.conn.cursor()
        cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS table_fromage 
            (
                id INTEGER PRIMARY KEY,
                fromage TEXT,
                famille TEXT,
                pate TEXT,
                date TEXT
            )
        '''
        )

    def get_data_with_url(self):
        """..."""
        data = urlopen(
            'https://www.laboitedufromager.com/liste-des-fromages-par-ordre-alphabetique/'
            )
        data = data.read()
        soup = BeautifulSoup(data, features="html.parser")
        trs = soup.find_all('tr')

        for tr in trs:
            td_list = tr.find_all('td')
            if len(td_list) == 3:
                if (
                    td_list[0].text.strip() != ""
                    and "Famille" not in td_list[0].text
                    and "Fromage" not in td_list[0].text
                    and "Pâte" not in td_list[0].text
                    and not td_list[0].find_all('strong')
                ):
                    fromage = td_list[0].text.strip()
                    famille = td_list[1].text.strip()
                    pate = td_list[2].text.strip()
                    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    data_to_insert = (fromage, famille, pate, date)
                    self.insert_into_data(data_to_insert)

    def insert_into_data(self, data):
        """..."""
        cursor = self.conn.cursor()
        cursor.execute(
            '''
                INSERT INTO table_fromage (fromage, famille, pate, date)
                VALUES (?, ?, ?, ?)
            ''',
            data
        )
        self.conn.commit()

    def update_data(self, fromage_id, new_values):
        """..."""
        cursor = self.conn.cursor()
        cursor.execute(
            '''
                UPDATE table_fromage
                SET fromage=?, famille=?, pate=?
                WHERE id=?
            ''',
            (*new_values, fromage_id))
        self.conn.commit()

    def display_data(self):
        """..."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM table_fromage')
        data = cursor.fetchall()
        for row in data:
            print(row)

    def display_data_family(self):
        """..."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT famille, COUNT(fromage) as nombre_fromages 
                FROM table_fromage 
                GROUP BY famille
        ''')
        data = cursor.fetchall()
        for row in data:
            print(row)

    def remove_duplicates(self):
        """..."""
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM table_fromage 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM table_fromage 
                GROUP BY fromage
            )
        ''')
        self.conn.commit()

    def close_connection(self):
        """..."""
        if self.conn:
            self.conn.close()

fromage_web = FromageWEB()
fromage_web.get_data_with_url()
fromage_web.remove_duplicates()
fromage_web.display_data()
fromage_web.display_data_family()
