# Conecta a database usando as configuracoes de db_settings.py

from db_settings import DatabaseSettings
import psycopg2

def get_connection():
    #Conecta usando valores pegos por db_settings.py
    config = DatabaseSettings.get_config_dict()
    return psycopg2.connect(**config)

def close_connection(conn):
    # Fechar conexao
    if conn:
        conn.close()
