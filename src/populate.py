# Popula as tabelas utilizando dados em csv

import argparse
from pathlib import Path
from connection import get_connection, close_connection
from generator import DataGenerator

def truncate_tables(conn):
    #Truncate todas as tabeals
    tables = [
        'ratings',
        'orders', 
        'user_private_profile',
        'user_public_profile',
        'user_authentication',
        'products'
    ]
    
    with conn.cursor() as cursor:
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
    conn.commit()

def copy_from_csv(conn, table_name, csv_path, columns=None, on_conflict=False):
    """    
    Args:
        conn: Database connection
        table_name: Name of the table to import to
        csv_path: Path to CSV file
        columns: Optional list of column names
        on_conflict: If True, use INSERT with ON CONFLICT DO NOTHING instead of COPY
    
    Retorna True se a importacao nao teve errors, caso contrário, falso
    """
    has_errors = False
    
    if on_conflict:
    # usar INSERT com ON CONFLICT DO NOTHING para tabelas com UNIQUE
        import csv as csv_module
        with open(csv_path, 'r') as f:
            reader = csv_module.DictReader(f)
            for row in reader:
                try:
                    if columns:
                        column_str = ', '.join(columns)
                        placeholders = ', '.join(['%s'] * len(columns))
                        values = []
                        for col in columns:
                            val = row[col]
                            if val == '' or val == 'None':
                                values.append(None)
                            else:
                                values.append(val)
                    else:
                        columns_list = list(row.keys())
                        column_str = ', '.join(columns_list)
                        placeholders = ', '.join(['%s'] * len(columns_list))
                        values = []
                        for v in row.values():
                            if v == '' or v == 'None':
                                values.append(None)
                            else:
                                values.append(v)
                
                    with conn.cursor() as cursor:
                        cursor.execute(
                            f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING",
                            values
                        )
                        conn.commit()
                except Exception as e:
                    # Pular linhas que causam erros (incluindo violacoes de foreign key)
                    conn.rollback()
                    print(f"Erro ao inserir linha em {table_name}: {e}")
                    has_errors = True
                    continue
    else:
        # usar COPY pra tabelas sem UNIQUE
        try:
            with open(csv_path, 'r') as f:
                with conn.cursor() as cursor:
                    if columns:
                        column_str = ', '.join(columns)
                        cursor.copy_expert(f"COPY {table_name} ({column_str}) FROM STDIN WITH CSV HEADER", f)
                    else:
                        cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", f)
            conn.commit()
        except Exception as e:
            print(f"Erro ao importar {table_name}: {e}")
            has_errors = True
    
    return not has_errors


# Interface de terminal para inserir os dados, ex.:
# Gerar dados e inserir
# python populate.py --users 10 --products 10 --orders 50 --ratings 20
# Gear dados sem inserir
# python populate.py --users 10 --products 10 --orders 50 --ratings 20 --generate-only
# Importar dados do csv
# python src/populate.py --import-only
# Diretorio de saida customizado
# python src/populate.py --users 10 --products 10 --output-dir '/path/to/custom/dir'

def main():
    parser = argparse.ArgumentParser(description="Gerar arquivo CSV e popular DB")
    parser.add_argument("--users", type=int, default=10000, help="Numero de usuarios")
    parser.add_argument("--products", type=int, default=1000, help="Numero de produtos")
    parser.add_argument("--orders", type=int, default=50000, help="Numero de pedidos")
    parser.add_argument("--ratings", type=int, default=20000, help="Numero de avaliacoes")
    parser.add_argument("--output-dir", type=str, default="../data/raw", help="Diretorio de saida do CSV")
    parser.add_argument("--generate-only", action="store_true", help="Apenas gera arquivo CSV, nao insere na DB")
    parser.add_argument("--import-only", action="store_true", help="Apenas insere CSV ja gerado na DB")
    parser.add_argument("--truncate", action="store_true", help="Limpa as tabelas antes de inserir (TRUNCATE)")
    parser.add_argument("--ignore-duplicates", action="store_true", help="Ignora duplicatas usando ON CONFLICT DO NOTHING")
    
    args = parser.parse_args()

    generator = DataGenerator(args.output_dir)

    if not args.import_only:
        print("=== Gerando arquivos CSV ===")
        
        print(f"Gerando {args.users} users...")
        user_ids = generator.generate_users(args.users)
        
        print(f"Gerando {args.products} products...")
        product_ids = generator.generate_products(args.products)
        
        print(f"Gerando {args.orders} orders...")
        generator.generate_orders(args.orders, user_ids, product_ids)
        
        print(f"Gerando {args.ratings} ratings...")
        generator.generate_ratings(args.ratings, user_ids, product_ids)
        
        print("CSV geradas com sucesso!")
        print(f"Arquivos salvos em: {Path(args.output_dir).resolve()}")
        
        if args.generate_only:
            return

    if not args.generate_only:
        print("\n=== Inserindo no Banco de Dados ===")
        
        conn = get_connection()
        has_errors = False
        try:
            if args.truncate:
                print("Limpando tabelas existentes...")
                truncate_tables(conn)
            
            csv_dir = Path(args.output_dir)
            
            # Inserir usuarios
            print("Importando user_authentication...")
            if not copy_from_csv(conn, 'user_authentication', csv_dir / 'user_authentication.csv', on_conflict=args.ignore_duplicates):
                has_errors = True
            
            print("Importando user_public_profile...")
            if not copy_from_csv(conn, 'user_public_profile', csv_dir / 'user_public_profile.csv', on_conflict=args.ignore_duplicates):
                has_errors = True
            
            print("Importando user_private_profile...")
            if not copy_from_csv(conn, 'user_private_profile', csv_dir / 'user_private_profile.csv', on_conflict=args.ignore_duplicates):
                has_errors = True
            
            # ... produtos
            print("Importando products...")
            if not copy_from_csv(conn, 'products', csv_dir / 'products.csv', on_conflict=args.ignore_duplicates):
                has_errors = True
            
            # ... pedidos
            print("Importando orders...")
            if not copy_from_csv(conn, 'orders', csv_dir / 'orders.csv', on_conflict=args.ignore_duplicates):
                has_errors = True
            
            # ... avaliacoess
            print("Importando ratings...")
            if not copy_from_csv(conn, 'ratings', csv_dir / 'ratings.csv', 
                         columns=['user_id', 'product_id', 'rating', 'comment', 'publication_date'],
                         on_conflict=args.ignore_duplicates):
                has_errors = True
            
            if not has_errors:
                print("Banco de Dados populado com sucesso!")
            else:
                print("Erros na importacao, cheque o log")
            
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            raise
        finally:
            close_connection(conn)

if __name__ == "__main__":
    main()
