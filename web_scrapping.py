"""..."""
from urllib.request import urlopen
from datetime import datetime
import sqlite3
import time
import os
import io
import requests
from PIL import Image
import pandas as pd
from bs4 import BeautifulSoup
from queries import (
    CREATE_TABLE_FROMAGE,
    INSERT_INTO_FROMAGE,
    UPDATE_FROMAGE,
    SELECT_ALL_FROMAGE,
    SELECT_FAMILY_COUNT,
    DELETE_DUPLICATES,
    CHECK_IF_EXIST,
    SELECT_LINKS_URL,
    UPDATE_QUERIES
)
from config import FROMAGE_URL

class FromageWEB:
    """..."""
    def __init__(self, bdd_path = 'fromage.db'):
        self.bdd_path = bdd_path
        self.conn = sqlite3.connect(bdd_path)# Connection bdd
        self.create_table_fromage()

    def create_table_fromage(self):
        """Cette fonction créer la table via la requete CREATE_TABLE_FROMAGE"""
        cursor = self.conn.cursor()
        cursor.execute(CREATE_TABLE_FROMAGE)

    def get_data_with_url(self):
        """Cette fonction récupère et filtre les données voulues sur le site"""
        data = urlopen(FROMAGE_URL)
        data = data.read()
        soup = BeautifulSoup(data, features="html.parser")
        trs = soup.find_all('tr')

        data_list = []

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
                    lien = [a['href'].rsplit('/', 2)[-2]
                             for a in soup.find_all('a') if fromage in a.text]
                    lien = [str(url) for url in lien]
                    lien = list(set([url.rstrip('/') + '/' for url in lien]))
                    lien = ','.join(lien) if lien else None
                    data_to_insert = (fromage, famille, pate, date, lien)
                    data_list.append(data_to_insert)
        df = pd.DataFrame(data_list, columns=['fromage', 'famille', 'pate', 'date', 'lien'])
        df['lien'] = df['lien'].astype(str).str.split(',').str[0]
        df['lien'].replace('', pd.NA, inplace=True)
        for _, row in df.iterrows():
            self.insert_into_data(tuple(row))

    def get_additional_data(self, fromage_name, link):
        """..."""
        try:
            url = "https://www.laboitedufromager.com/fromage/" + link
            response = requests.get(url, timeout=5)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching additional data for {fromage_name}: {e}")
            return None
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, features="html.parser")
            image_url = soup.find('img', {'class': 'wp-post-image'})['src'] if soup.find('img', {'class': 'wp-post-image'}) else None
            image_element = soup.find('img', {'class': 'wp-post-image'})
            if image_element:
                image_url = image_element['src']
                image_pil = self.download_and_save_image(image_url, fromage_name, link)
            else:
                image_url = None
                image_pil = None
            price = soup.find('bdi').text.strip() if soup.find('bdi') else None
            description_div = soup.find('div',
                                        {'class': 'woocommerce-product-details__short-description'})
            description = description_div.text.strip() if description_div else None
            star_rating_div = soup.find('div', {'class': 'star-rating'})
            star_rating = star_rating_div.get('aria-label') if star_rating_div else None
            reviews_tab_li = soup.find('li', {'class': 'reviews_tab'})
            reviews_text = reviews_tab_li.find('a').text.strip() if reviews_tab_li else None
            return {
                'image_url': image_url,
                'image_pil': image_pil,
                'prix': price,
                'description': description,
                'note': star_rating,
                'nb_commentaires': reviews_text
            }
        else:
            print(f"Failed to fetch additional data for {fromage_name}")
            return None

    def update_url(self):
        """..."""
        start_time = time.time()
        cursor = self.conn.cursor()
        cursor.execute(SELECT_LINKS_URL)
        rows = cursor.fetchall()
        updated = False
        for row in rows:
            fromage = row[0]
            links = row[1].split(',') if row[1] else []
            for link in links:
                print(f"Updating data for {fromage} with link {link}")
                additional_data = self.get_additional_data(fromage, link)

                if additional_data:
                    cursor.execute(UPDATE_QUERIES, (
                        additional_data['image_url'],
                        additional_data['image_pil'],
                        additional_data['prix'],
                        additional_data['description'],
                        additional_data['note'],
                        additional_data['nb_commentaires'],
                        fromage,
                        link
                    ))
                    print("..DONE..")
                updated = True
        self.conn.commit()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Update URL took {elapsed_time} seconds.")
        return updated

    def download_and_save_image(self, image_url, fromage_name, link):
        """..."""
        try:
            response = requests.get(image_url, timeout=5)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image for {fromage_name}: {e}")
            return None
        if response.status_code == 200:
            image_data = response.content
            image_filename = f"{fromage_name}_{link.split('/')[-2]}.jpg"
            image_path = os.path.join("images", image_filename)
            with open(image_path, 'wb') as image_file:
                image_file.write(image_data)
            print(f"Image downloaded: {image_path}")
            image_data_bytes = io.BytesIO(image_data).read()
            return image_data_bytes
        else:
            print(f"Failed to download image for {fromage_name}")
            return None


    def insert_into_data(self, data):
        """Cette fonction insert des données dans la table"""
        cursor = self.conn.cursor()
        cursor.execute(INSERT_INTO_FROMAGE, data)
        self.conn.commit()

    def update_data(self, fromage_id, new_values):
        """Cette fonction met à jour la table avec de nouvelles valeurs"""
        cursor = self.conn.cursor()
        cursor.executemany(UPDATE_FROMAGE, (*new_values, fromage_id))
        self.conn.commit()

    def display_data(self):
        """Cette fonction affiche les données de la table"""
        cursor = self.conn.cursor()
        cursor.execute(SELECT_ALL_FROMAGE)
        data = cursor.fetchall()
        for row in data:
            print(row)

    def display_data_family(self):
        """
            Cette fonction affiche les données de la table en les catégorisant par famille
            à l'aide de la requete SQL SELECT_FAMILY_COUNT
        """
        cursor = self.conn.cursor()
        cursor.execute(SELECT_FAMILY_COUNT)
        data = cursor.fetchall()
        for row in data:
            print(row)

    def remove_duplicates(self):
        """Cette fonction supprime les duplicats"""
        cursor = self.conn.cursor()
        cursor.execute(DELETE_DUPLICATES)
        self.conn.commit()

    def close_connection(self):
        """..."""
        if self.conn:
            self.conn.close()

    def give_display_data_family(self):
        """Cette fonction récupère et retourne les valeurs de la requete SQL SELECT_FAMILY_COUNT"""
        cursor = self.conn.cursor()
        cursor.execute(SELECT_FAMILY_COUNT)
        data = cursor.fetchall()
        return data

    def update_from_url(self):
        """
            Cette fonction récupère les données de l'URL et les met à jour dans la base de données.
            Elle vérifie si les données sont déjà présentes dans la base avant de les insérer.
        """
        data = urlopen(FROMAGE_URL)
        data = data.read()
        soup = BeautifulSoup(data, features="html.parser")
        trs = soup.find_all('tr')
        updated = False
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
                    if not self.check_data_exists(fromage):
                        self.insert_into_data(data_to_insert)
                        updated = True
        return updated

    def check_data_exists(self, fromage_name):
        """
            Vérifie si les données pour un fromage donné existent déjà dans la base.
            Retourne True si les données existent, False sinon.
        """
        cursor = self.conn.cursor()
        cursor.execute(CHECK_IF_EXIST, (fromage_name,))
        count = cursor.fetchone()[0]
        return count > 0



fromage_web = FromageWEB()
fromage_web.get_data_with_url()
fromage_web.remove_duplicates()
fromage_web.update_url()
