import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variaveis de .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class DatabaseSettings:

    @staticmethod
    def get_config_dict():
    # Retorna config de conenxao como um dicionario
        return {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', '5432')),
            'database': os.getenv('POSTGRES_DB'),
            'user': os.getenv('POSTGRES_USER'),
            'password': os.getenv('POSTGRES_PASSWORD'),
        }
    
    @staticmethod
    def get_config_string():
     # Retorna config como string
        config = DatabaseSettings.get_postgres_config()
        return (
            f"postgresql://{config['user']}:{config['password']}"
            f"@{config['host']}:{config['port']}/{config['database']}"
        )
