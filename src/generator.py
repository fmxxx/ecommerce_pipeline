from faker import Faker
import uuid
import csv
import random
from pathlib import Path
from datetime import datetime

fake = Faker('pt_BR')

class DataGenerator:
    # Gera dados com faker para popular as tabelas

    def __init__(self, output_dir='../data/raw'):
        self.fake = Faker('pt_BR')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_users(self, count):
        # Gera usuarios com UUIDs consistentes
        user_ids = []
        used_emails = set()

        with open(self.output_dir / 'user_authentication.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'email', 'password_hash', 'created_at'])

            with open(self.output_dir / 'user_public_profile.csv', 'w', newline='') as f2:
                writer2 = csv.writer(f2)
                writer2.writerow(['user_id', 'display_name', 'photo_url', 'member_since'])

                with open(self.output_dir / 'user_private_profile.csv', 'w', newline='') as f3:
                    writer3 = csv.writer(f3)
                    writer3.writerow(['user_id', 'full_name', 'cpf', 'phone', 'birth_date', 'gender'])

                    for _ in range(count):
                        user_id = str(uuid.uuid4())
                        user_ids.append(user_id)
                        created_at = datetime.now().isoformat()
                        member_since = datetime.now().isoformat()

                        # user_authentication - garantir email unico
                        while True:
                            email = self.fake.email()
                            if email not in used_emails:
                                used_emails.add(email)
                                break
                        
                        password_hash = f'fake_hash_{self.fake.password()}'
                        writer.writerow([user_id, email, password_hash, created_at])

                        # user_private_profile
                        display_name = self.fake.first_name()
                        photo_url = None  # TODO: generate photo URL
                        writer2.writerow([user_id, display_name, photo_url, member_since])

                        # user_private_profile
                        full_name = self.fake.name()
                        cpf = self.fake.cpf()
                        phone = self.fake.phone_number()
                        birth_date = self.fake.date_of_birth().isoformat()
                        gender = self.fake.random_element(['Masculino', 'Feminino', 'Outro'])
                        writer3.writerow([user_id, full_name, cpf, phone, birth_date, gender])

        return user_ids

    def generate_products(self, count):
        # Retorna uma lista de product_id para usar como Foreign key

        product_ids = []

        with open(self.output_dir / 'products.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['uuid', 'name', 'category', 'cost_price', 'sale_price', 'text_description', 'specifications'])

            for _ in range(count):
                product_id = str(uuid.uuid4())
                product_ids.append(product_id)

                name = self.fake.sentence(nb_words=4)[:-1]
                category = self.fake.word()
                
                # cost_price com uma distribuição normal (mean=150, std=50)
                cost_price = max(10, round(random.gauss(150, 50), 2))
                
                # sale_price calculado a partir de cost_price com margem de lucro aleatória (1.15 to 1.5)
                profit_margin = random.uniform(1.15, 1.5)
                sale_price = round(cost_price * profit_margin, 2)
                
                text_description = self.fake.text()
                specifications = None  # Talvez adicionar arquivos JSONB no futuro para especificacoes

                writer.writerow([product_id, name, category, cost_price, sale_price, text_description, specifications])

        return product_ids

    def generate_orders(self, count, user_ids, product_ids):
        with open(self.output_dir / 'orders.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['uuid', 'user_id', 'product_id', 'order_date', 'quantity'])

            for _ in range(count):
                user_id = self.fake.random_element(user_ids)
                product_id = self.fake.random_element(product_ids)
                
                # quantity com distribuicao normal (mean=3, std=2), entre 1 e 10
                quantity = max(1, min(10, int(round(random.gauss(3, 2)))))
                
                order_date = self.fake.date_time_between(start_date='-1y').isoformat()

                writer.writerow([str(uuid.uuid4()), user_id, product_id, order_date, quantity])

    def generate_ratings(self, count, user_ids, product_ids):
        with open(self.output_dir / 'ratings.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'product_id', 'rating', 'comment', 'publication_date'])

            used_combinations = set()
            generated = 0
            
            while generated < count:
                user_id = self.fake.random_element(user_ids)
                product_id = self.fake.random_element(product_ids)
                combination = (user_id, product_id)
                
                if combination in used_combinations:
                    continue
                
                used_combinations.add(combination)
                
                # Rating com distribuicao normal (mean=4, std=1), entre 1 e 5
                rating = max(1, min(5, int(round(random.gauss(4, 1)))))
                
                comment = self.fake.text()
                publication_date = self.fake.date_time_between(start_date='-6m').isoformat()

                writer.writerow([user_id, product_id, rating, comment, publication_date])
                generated += 1
