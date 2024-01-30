"""..."""
from urllib.request import urlopen
import sqlite3
import time
import os
import io
import requests
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
        """
        Sommaire :
            Initialise une instance de la classe FromageWEB.

        Paramètres :
            - bdd_path (str) : Chemin vers la base de données SQLite.
        """
        self.bdd_path = bdd_path
        self.conn = sqlite3.connect(bdd_path)# Connection bdd
        self.create_table_fromage()

    def create_table_fromage(self):
        """
        Sommaire :
            Crée la table 'fromage' dans la base de données en utilisant la requête 
            CREATE_TABLE_FROMAGE.
        """
        cursor = self.conn.cursor()
        cursor.execute(CREATE_TABLE_FROMAGE)

    def get_data_with_url(self):
        """
        Sommaire :
            Récupère et filtre les premières données souhaitées sur le site.
            Cette fonction extrait les données du site défini par FROMAGE_URL,
            les filtre et les insère dans la base de données.
        """
        data = urlopen(FROMAGE_URL)
        data = data.read()
        soup = BeautifulSoup(data, features="html.parser")
        trs = soup.find_all('tr')
        data_list = []
        for tr in trs:
            td_list = tr.find_all('td')
            if len(td_list) == 3:
                if (
                    #Filtre classique
                    td_list[0].text.strip() != ""
                    and "Famille" not in td_list[0].text
                    and "Fromage" not in td_list[0].text
                    and "Pâte" not in td_list[0].text
                    and not td_list[0].find_all('strong')
                ):
                    fromage = td_list[0].text.strip()
                    famille = td_list[1].text.strip()
                    pate = td_list[2].text.strip()
                    date = pd.Timestamp.now()

                    #Conditions d'existance de l'url
                    lien = [a['href'].rsplit('/', 2)[-2]
                             for a in soup.find_all('a') if fromage in a.text]
                    lien = [str(url) for url in lien]
                    lien = list(set([url.rstrip('/') + '/' for url in lien]))
                    lien = ','.join(lien) if lien else None

                    date_str = str(date)
                    data_to_insert = (fromage, famille, pate, date_str, lien)
                    data_list.append(data_to_insert)

        df = pd.DataFrame(data_list, columns=['fromage', 'famille', 'pate', 'date', 'lien'])

        #Elimination des valeurs en trop
        df['lien'] = df['lien'].astype(str).str.split(',').str[0]
        df['lien'].replace('', pd.NA, inplace=True)
        for _, row in df.iterrows():
            self.insert_into_data(tuple(row))

    #--VERSION SIMPLE INSERTION--
    def update_data_new_url(self):
        """
        Sommaire :
            Met à jour les données provenant des URLs des fromages.
            Cette fonction récupère les données supplémentaires à partir des URLs
            stockées dans la base de données et les met à jour dans la base de données.
        """
        start_time = time.time()
        cursor = self.conn.cursor()
        cursor.execute(SELECT_LINKS_URL)
        rows = cursor.fetchall()
        updated = False
        data_to_insert = []  # Liste pour stocker toutes les données à insérer

        for row in rows:
            fromage = row[0]
            links = row[1].split(',') if row[1] else []
            for link in links:
                print(f"Updating data for {fromage} with link {link}")
                additional_data = self.get_additional_data(fromage, link)
                if additional_data:
                    data_to_insert.append((
                        additional_data['image_url'],
                        additional_data['image_save'],
                        additional_data['prix'],
                        additional_data['description'],
                        additional_data['note'],
                        additional_data['nb_commentaires'],
                        fromage,
                        link
                    ))
                    print("..DONE..")
                    updated = True

        if data_to_insert:
            cursor.executemany(UPDATE_QUERIES, data_to_insert)
            self.conn.commit()

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Update URL took {elapsed_time} seconds.")
        return updated


    #--VERSION MULTI INSERTION--
    # def update_data_new_url(self):
    #     """
    #     Sommaire :
    #         Met à jour les données provenant des URLs des fromages.
    #         Cette fonction récupère les données supplémentaires à partir des URLs
    #         stockées dans la base de données et les met à jour dans la base de données.
    #     """
    #     start_time = time.time()
    #     cursor = self.conn.cursor()
    #     cursor.execute(SELECT_LINKS_URL)
    #     rows = cursor.fetchall()
    #     updated = False
    #     for row in rows:
    #         fromage = row[0]
    #         links = row[1].split(',') if row[1] else []
    #         for link in links:
    #             print(f"Updating data for {fromage} with link {link}")
    #             additional_data = self.get_additional_data(fromage, link)
    #             #Mise a jour de la BDD
    #             if additional_data:
    #                 cursor.execute(UPDATE_QUERIES, (
    #                     additional_data['image_url'],
    #                     additional_data['image_save'],
    #                     additional_data['prix'],
    #                     additional_data['description'],
    #                     additional_data['note'],
    #                     additional_data['nb_commentaires'],
    #                     fromage,
    #                     link
    #                 ))
    #                 print("..DONE..")
    #             updated = True
    #     self.conn.commit()
    #     end_time = time.time()
    #     elapsed_time = end_time - start_time
    #     print(f"Update URL took {elapsed_time} seconds.")
    #     return updated

    def get_additional_data(self, fromage_name, link):
        """
        Sommaire :
            Récupère des données supplémentaires à partir de l'URL d'un fromage donné.

        Paramètres :
        - fromage_name (str) : Nom du fromage.
        - link (str) : Lien vers la page du fromage.

        Retourne :
            Un dictionnaire contenant des données supplémentaires telles que l'URL de l'image,
            le prix, la description, la note, le nombre de commentaires, etc.
        """
        try:
            url = "https://www.laboitedufromager.com/fromage/" + link
            response = requests.get(url, timeout=5)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching additional data for {fromage_name}: {e}")
            return None
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, features="html.parser")

            #Conditions d'existance de l'url
            image_url = soup.find('img', {'class': 'wp-post-image'})['src'] if soup.find('img', {'class': 'wp-post-image'}) else None
            image_element = soup.find('img', {'class': 'wp-post-image'})
            if image_element:
                image_url = image_element['src']
                image_save = self.download_and_save_image(image_url, fromage_name, link)
            else:
                image_url = None
                image_save = None

            #Conditions d'existance du prix
            price_span = soup.find('div',{'class':'product_infos'})
            if price_span:
                price_bdi = price_span.find('p',{'class':'price'})
                if price_bdi:
                    price = price_bdi.text.strip()
                else:
                    price = None
            else:
                price = None

            #Conditions d'existance de la description
            description_div = soup.find('div',
                                        {'class': 'woocommerce-product-details__short-description'})
            description = description_div.text.strip() if description_div else None

            #Condition d'existance de la notation
            # star_rating_div = soup.find('div', {'class': 'star-rating'})
            # star_rating = star_rating_div.get('aria-label') if star_rating_div else None

            star_rating_div_1 = soup.find('div',{'class':'product_infos'})
            if star_rating_div_1 :
                star_rating_div_2 = soup.find('div', {'class': 'star-rating'})
                if star_rating_div_2 :
                    star_rating = star_rating_div_2.get('aria-label')
                else :
                    star_rating = None
            else :
                star_rating = None


            #Conditions d'existance du nombre de note
            reviews_tab_li = soup.find('li', {'class': 'reviews_tab'})
            reviews_text = reviews_tab_li.find('a').text.strip() if reviews_tab_li else None

            return {
                'image_url': image_url,
                'image_save': image_save,
                'prix': price,
                'description': description,
                'note': star_rating,
                'nb_commentaires': reviews_text
            }
        else:
            print(f"Failed to fetch additional data for {fromage_name}")
            return None

    def download_and_save_image(self, image_url, fromage_name, link):
        """
        Sommaire :
            Télécharge et sauvegarde une image à partir de l'URL donnée.

        Paramètres :
            - image_url (str) : URL de l'image à télécharger.
            - fromage_name (str) : Nom du fromage associé à l'image.
            - link (str) : Lien vers la page du fromage.

        Retourne : 
            Les données de l'image sous forme d'octets.
        """
        image_filename = f"{fromage_name}_{link.split('/')[-2]}.jpg"
        image_path = os.path.join("images", image_filename)

        #On vérifie que l'image n'existe pas déjàs dans le fichier images
        if os.path.exists(image_path):
            print(f"Image already exists: {image_path}")
            with open(image_path, 'rb') as image_file:
                image_data_bytes = io.BytesIO(image_file.read()).read()
            return image_data_bytes
        try:
            response = requests.get(image_url, timeout=5)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image for {fromage_name}: {e}")
            return None
        if response.status_code == 200:
            image_data = response.content
            with open(image_path, 'wb') as image_file:
                image_file.write(image_data)
            print(f"Image downloaded: {image_path}")
            image_data_bytes = io.BytesIO(image_data).read()
            return image_data_bytes
        else:
            print(f"Failed to download image for {fromage_name}")
            return None

    def insert_into_data(self, data):
        """
        Sommaire :
            Insère des données dans la table 'fromage' de la base de données.

        Paramètres :
            - data (tuple) : Tuple de données à insérer.
        """
        cursor = self.conn.cursor()
        cursor.execute(INSERT_INTO_FROMAGE, data)
        self.conn.commit()

    def update_data(self, fromage_id, new_values):
        """
        Sommaire :
            Met à jour la table 'fromage' avec de nouvelles valeurs.

        Paramètres :
            - fromage_id (int) : Identifiant du fromage à mettre à jour.
            - new_values (tuple) : Nouvelles valeurs à appliquer.
        """
        cursor = self.conn.cursor()
        cursor.executemany(UPDATE_FROMAGE, (*new_values, fromage_id))
        self.conn.commit()

    def display_data(self):
        """
        Sommaire :
            Affiche toutes les données de la table 'fromage'.
        """
        cursor = self.conn.cursor()
        cursor.execute(SELECT_ALL_FROMAGE)
        data = cursor.fetchall()
        for row in data:
            print(row)

    def display_data_family(self):
        """
        Sommaire :
            Affiche les données de la table en les catégorisant par famille
            à l'aide de la requete SQL SELECT_FAMILY_COUNT
        """
        cursor = self.conn.cursor()
        cursor.execute(SELECT_FAMILY_COUNT)
        data = cursor.fetchall()
        for row in data:
            print(row)

    def remove_duplicates(self):
        """
        Sommaire :
            Supprime les doublons de la table 'fromage'.
        """
        cursor = self.conn.cursor()
        cursor.execute(DELETE_DUPLICATES)
        self.conn.commit()

    def close_connection(self):
        """
        Sommaire :
            Ferme la connexion à la base de données.
        """
        if self.conn:
            self.conn.close()

    def give_display_data_family(self):
        """
        Sommaire :
            Récupère et retourne les valeurs de la requête SQL SELECT_FAMILY_COUNT.
        Retourne :
            Les valeurs de la requête SQL SELECT_FAMILY_COUNT
        """
        cursor = self.conn.cursor()
        cursor.execute(SELECT_FAMILY_COUNT)
        data = cursor.fetchall()
        return data

    def check_data_exists(self, fromage_name):
        """
        Sommaire :
            Vérifie si les données pour un fromage donné existent déjà dans la base de données.

        Retourne :
            True si les données existent, False sinon.
        """
        cursor = self.conn.cursor()
        cursor.execute(CHECK_IF_EXIST, (fromage_name,))
        count = cursor.fetchone()[0]
        return count > 0


# Utilisation de la classe FromageWEB
fromage_web = FromageWEB()
fromage_web.get_data_with_url()
fromage_web.remove_duplicates()
fromage_web.update_data_new_url()
