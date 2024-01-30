# FromageWEB Web Scraping Readme


## Fichier 1 : web_scrapping.py :

### Description

Le fichier `web_scrapping.py` contient une classe Python `FromageWEB` qui permet de scraper des données à partir d'un site web sur les fromages. Le script utilise BeautifulSoup pour extraire les données HTML, pandas pour les manipulations de données, SQLite pour la gestion de la base de données, et requests pour les requêtes HTTP.

### Fonctionnalités

1. **Initialisation de la classe:**
    - La classe `FromageWEB` est initialisée avec un chemin vers une base de données SQLite (par défaut `fromage.db`).
    - Une connexion à la base de données est établie lors de l'initialisation, et la table `fromage` est créée si elle n'existe pas.

2. **Récupération des données du site:**
    - La méthode `get_data_with_url` extrait les données du site spécifié par la constante `FROMAGE_URL`.
    - Les données sont filtrées et insérées dans la base de données.

3. **Mise à jour des données à partir des URLs:**
    - La méthode `update_data_new_url` récupère les URLs des fromages stockés dans la base de données et met à jour les informations telles que l'URL de l'image, le prix, la description, la note, le nombre de commentaires, etc.

4. **Téléchargement et sauvegarde d'images:**
    - La méthode `download_and_save_image` télécharge et sauvegarde une image à partir d'une URL. Elle vérifie d'abord si l'image existe déjà dans le stockage pour éviter les téléchargements redondants.

5. **Manipulation de la base de données:**
    - D'autres méthodes telles que `insert_into_data`, `update_data`, `display_data`, `display_data_family`, et `remove_duplicates` sont fournies pour effectuer diverses opérations sur la base de données.

6. **Fermeture de la connexion:**
    - La méthode `close_connection` ferme la connexion à la base de données.

7. **Utilisation du script:**
    - La dernière partie du fichier utilise la classe `FromageWEB` pour effectuer des opérations telles que la récupération des données, la suppression des doublons et la mise à jour des informations à partir des URLs.

### Dépendances

Le script utilise les bibliothèques suivantes :
- `urllib.request` pour ouvrir des URLs.
- `sqlite3` pour la gestion de la base de données SQLite.
- `time` pour mesurer le temps d'exécution.
- `os`, `io` pour les opérations liées aux fichiers.
- `requests` pour effectuer des requêtes HTTP.
- `pandas` pour manipuler les données.
- `BeautifulSoup` pour l'analyse HTML.
- `queries.py` et `config.py` pour les requêtes SQL et les configurations.

### Utilisation

```python
# Exemple d'utilisation
fromage_web = FromageWEB()
fromage_web.get_data_with_url()
fromage_web.remove_duplicates()
fromage_web.update_data_new_url()
```
Puis on lance via la commande python : `python web_scrapping.py`

### Remarques

- Assurez-vous d'avoir installé les bibliothèques nécessaires via `pip install -r requirements.txt`.
