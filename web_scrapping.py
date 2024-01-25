"""..."""
from urllib.request import urlopen # pylint: disable=unused-import
from datetime import datetime # pylint: disable=unused-import
import sqlite3 # pylint: disable=unused-import
import pytest # pylint: disable=unused-import
from bs4 import BeautifulSoup # pylint: disable=unused-import
import pandas as pd # pylint: disable=unused-import

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
                pate TEXT
            )
        '''
        )

    def get_data_with_url(self):
        """..."""
        data = urlopen(
            'https://www.laboitedufromager.com/liste-des-fromages-par-ordre-alphabetique/'
            )
        data = data.read()
        soup = BeautifulSoup(data)
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
                    data_to_insert = (fromage, famille, pate)
                    self.insert_into_data(data_to_insert)

    def insert_into_data(self, data):
        """..."""
        cursor = self.conn.cursor()
        cursor.execute(
            '''
                INSERT INTO table_fromage (fromage, famille, pate)
                VALUES (?, ?, ?)
            ''',
            data
        )
        self.conn.commit()

    def display_data(self):
        """..."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM table_fromage')
        data = cursor.fetchall()
        for row in data:
            print(row)
    
    def close_connection(self):
        """..."""
        if self.conn:
            self.conn.close()

fromage_web = FromageWEB()
fromage_web.get_data_with_url()
fromage_web.display_data()
