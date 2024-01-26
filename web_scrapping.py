"""..."""
from urllib.request import urlopen
from datetime import datetime
import sqlite3
from bs4 import BeautifulSoup
from queries import (
    CREATE_TABLE_FROMAGE,
    INSERT_INTO_FROMAGE,
    UPDATE_FROMAGE,
    SELECT_ALL_FROMAGE,
    SELECT_FAMILY_COUNT,
    DELETE_DUPLICATES,
)
from config import FROMAGE_URL

class FromageWEB:
    """..."""
    def __init__(self, bdd_path = 'fromage.db'):
        self.bdd_path = bdd_path
        self.conn = sqlite3.connect(bdd_path)# Connection bdd
        self.create_table_fromage()

    def create_table_fromage(self):
        """..."""
        cursor = self.conn.cursor()
        cursor.execute(CREATE_TABLE_FROMAGE)

    def get_data_with_url(self):
        """..."""
        data = urlopen(FROMAGE_URL)
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
        cursor.execute(INSERT_INTO_FROMAGE, data)
        self.conn.commit()

    def update_data(self, fromage_id, new_values):
        """..."""
        cursor = self.conn.cursor()
        cursor.execute(UPDATE_FROMAGE, (*new_values, fromage_id))
        self.conn.commit()

    def display_data(self):
        """..."""
        cursor = self.conn.cursor()
        cursor.execute(SELECT_ALL_FROMAGE)
        data = cursor.fetchall()
        for row in data:
            print(row)

    def display_data_family(self):
        """..."""
        cursor = self.conn.cursor()
        cursor.execute(SELECT_FAMILY_COUNT)
        data = cursor.fetchall()
        for row in data:
            print(row)

    def remove_duplicates(self):
        """..."""
        cursor = self.conn.cursor()
        cursor.execute(DELETE_DUPLICATES)
        self.conn.commit()

    def close_connection(self):
        """..."""
        if self.conn:
            self.conn.close()

    def give_display_data_family(self):
        """..."""
        cursor = self.conn.cursor()
        cursor.execute(SELECT_FAMILY_COUNT)
        data = cursor.fetchall()
        return data

fromage_web = FromageWEB()
fromage_web.get_data_with_url()
fromage_web.remove_duplicates()
fromage_web.display_data()
