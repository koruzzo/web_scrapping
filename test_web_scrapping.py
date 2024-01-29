"""..."""
import os
from datetime import datetime
import sqlite3
import pytest
from queries import (
    SELECT_ALL_FROMAGE,
    SELECT_DISTINCT_FROMAGE_COUNT,
    SELECT_NULL_ROWS,
    COUNT_FROMAGE_BY_NAME
)
from web_scrapping import FromageWEB

# pylint: disable=redefined-outer-name

@pytest.fixture
def fromage_instance():
    """Cette fonction renvoie une instance de la classe FromageWEB"""
    return FromageWEB('test_fromage.db')

def test_create_table_fromage(fromage_instance):
    """Cette fonction test la creation de table"""
    fromage_instance.create_table_fromage()
    assert os.path.isfile('test_fromage.db')
    fromage_instance.close_connection()

def test_database_connection(fromage_instance):
    """Cette fonction test la connexion avec la BDD"""
    assert fromage_instance.conn is not None
    fromage_instance.close_connection()

def test_columns_in_table_fromage(fromage_instance):
    """Cette fonction test le nom attendu des collones"""
    fromage_instance.create_table_fromage()
    conn = sqlite3.connect('test_fromage.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(table_fromage)")
    columns_info = cursor.fetchall()
    column_names = [info[1] for info in columns_info]
    assert 'fromage' in column_names
    assert 'famille' in column_names
    assert 'pate' in column_names
    assert 'date' in column_names
    conn.close()
    fromage_instance.close_connection()

def test_insert_into_data(fromage_instance):
    """Cette fonction test l'insertion dans la BDD de nouvelles valeurs"""
    data_to_insert = ('Test Fromage', 'Test Famille', 'Test Pate',
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    fromage_instance.insert_into_data(data_to_insert)
    conn = sqlite3.connect('test_fromage.db')
    cursor = conn.cursor()
    cursor.execute(SELECT_ALL_FROMAGE)
    inserted_data = cursor.fetchone()
    conn.close()
    assert inserted_data is not None
    assert inserted_data[1] == 'Test Fromage'
    assert inserted_data[2] == 'Test Famille'
    assert inserted_data[3] == 'Test Pate'
    fromage_instance.close_connection()

def test_no_duplicates_in_fromage_column(fromage_instance):
    """Cette fonction vérifie qu'il n'y ait pas de doublon dans la BDD"""
    conn = sqlite3.connect('test_fromage.db')
    cursor = conn.cursor()
    cursor.execute(SELECT_DISTINCT_FROMAGE_COUNT)
    count_distinct_fromage = cursor.fetchone()[0]
    conn.close()
    fromage_instance.close_connection()
    assert count_distinct_fromage == 1

def test_no_empty_line(fromage_instance):
    """Cette fonction vérifie qu'il n'y ait pas de ligne vide"""
    conn = sqlite3.connect('test_fromage.db')
    cursor = conn.cursor()
    cursor.execute(SELECT_NULL_ROWS)
    data = cursor.fetchall()
    conn.close()
    fromage_instance.close_connection()
    assert len(data) == 0

def test_display_data(fromage_instance, capsys):
    """Cette fonction test l'affichage du programme"""
    data_to_insert = ('Fromage7', 'Famille7', 'Pate7', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    fromage_instance.insert_into_data(data_to_insert)
    fromage_instance.display_data()
    captured_output, _ = capsys.readouterr()
    assert 'Fromage7' in captured_output
    assert 'Famille7' in captured_output
    assert 'Pate7' in captured_output
    fromage_instance.close_connection()

def test_remove_duplicates(fromage_instance):
    """Cette fonction teste la suppression des doublons"""
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data_to_insert_1 = ('Fromage1', 'Famille1', 'Pate1', date_now)
    data_to_insert_2 = ('Fromage1', 'Famille1', 'Pate1', date_now)
    fromage_instance.insert_into_data(data_to_insert_1)
    fromage_instance.insert_into_data(data_to_insert_2)
    conn = sqlite3.connect('test_fromage.db')
    cursor = conn.cursor()
    cursor.execute(COUNT_FROMAGE_BY_NAME, ('Fromage1',))
    count_before = cursor.fetchone()[0]
    conn.close()
    assert count_before == 2
    fromage_instance.remove_duplicates()
    conn = sqlite3.connect('test_fromage.db')
    cursor = conn.cursor()
    cursor.execute(COUNT_FROMAGE_BY_NAME, ('Fromage1',))
    count_after = cursor.fetchone()[0]
    conn.close()
    assert count_after == 1
    fromage_instance.close_connection()

def test_display_data_family(fromage_instance, capsys):
    """Cette fonction test l'affichage du nombre de fromages par famille"""
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data_to_insert_1 = ('Fromage1', 'Famille1', 'Pate1', date_now)
    data_to_insert_2 = ('Fromage2', 'Famille1', 'Pate2', date_now)
    data_to_insert_3 = ('Fromage3', 'Famille2', 'Pate3', date_now)
    fromage_instance.insert_into_data(data_to_insert_1)
    fromage_instance.insert_into_data(data_to_insert_2)
    fromage_instance.insert_into_data(data_to_insert_3)
    fromage_instance.display_data_family()
    captured_output, _ = capsys.readouterr()
    assert 'Famille1' in captured_output
    assert 'Famille2' in captured_output
    fromage_instance.close_connection()

def test_update_data(fromage_instance):
    """Cett fonction test la mise à jour des données"""
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    test_data = ('TestFromage', 'TestFamily', 'TestPate', date_now)
    fromage_instance.insert_into_data(test_data)
    cursor = fromage_instance.conn.cursor()
    cursor.execute(SELECT_ALL_FROMAGE)
    result = cursor.fetchone()
    fromage_id = result[0] if result else None
    new_values = ('UpdatedFromage', 'UpdatedFamily', 'UpdatedPate')
    fromage_instance.update_data(fromage_id, new_values)
    cursor.execute(SELECT_ALL_FROMAGE)
    updated_result = cursor.fetchone()
    assert updated_result[1:4] == new_values
    fromage_instance.close_connection()

def teardown_module():
    """Cette fonction supprime la BDD de test"""
    if os.path.isfile('test_fromage.db'):
        os.remove('test_fromage.db')
