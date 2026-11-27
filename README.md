# Ecommerce Data Pipeline

Pipeline simples para gerar dados ficticios de ecommerce, armazenar arquivos CSV e popular um banco PostgreSQL.

O projeto gera usuarios, perfis, produtos, pedidos e avaliacoes, com dados coerentes e relacionamentos por UUID. Os arquivos CSV sao criados em `data/raw/` e podem ser importados individualmente ou durante o mesmo processo de geracao.

## Estrutura do projeto

```text
.
├── data/
│   ├── raw/          # CSV gerados
│   ├── processed/    # Dados processados
│   └── exports/      # Exportacoes
├── postgres/
│   └── init.sql      # Schema inicial do banco
├── scripts/
│   ├── docker_start.sh
│   ├── docker_stop.sh
│   └── connect_db.sh
└── src/
    ├── connection.py
    ├── db_settings.py
    ├── generator.py
    └── populate.py
```

## Tecnologias

- Python
- Faker
- PostgreSQL
- Docker Compose
- psycopg2
- python-dotenv

## Banco de dados

O schema inicial cria as seguintes tabelas:

- `user_authentication`: credenciais e email unico dos usuarios
- `user_public_profile`: nome publico e foto
- `user_private_profile`: dados pessoais
- `products`: produtos e precos
- `orders`: pedidos realizados pelos usuarios
- `ratings`: avaliacoes unicas por usuario e produto
- `analytics`: tabela reservada para dados analiticos

Relacionamentos e restricoes importantes:

- Perfis pertencem a usuarios existentes.
- Pedidos pertencem a usuarios e produtos existentes.
- Avaliacoes pertencem a usuarios e produtos existentes.
- Emails sao unicos.
- Cada usuario pode avaliar um produto uma unica vez.
- Ratings devem estar entre 1 e 5.
- Quantidades de pedidos devem ser maiores que zero.

## Configuracao

### 1. Instale as dependencias Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure o ambiente

Crie um arquivo `.env` na raiz do projeto:

```dotenv
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_CONTAINER_PORT=5432
POSTGRES_DB=ecommerce
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

### 3. Inicie o PostgreSQL

No Linux com Docker rootless configurado:

```bash
./scripts/docker_start.sh
```

Ou inicie diretamente com Docker Compose:

```bash
docker compose up -d
```

Na primeira inicializacao, o arquivo `postgres/init.sql` cria o schema automaticamente.

### 4. Conecte-se ao banco

```bash
./scripts/connect_db.sh
```

Para encerrar o container:

```bash
./scripts/docker_stop.sh
```

## Geracao e importacao de dados

Execute os comandos a partir da raiz do projeto.

### Gerar e inserir dados

```bash
python src/populate.py \
  --users 10000 \
  --products 1000 \
  --orders 50000 \
  --ratings 20000
```

O comando gera os CSVs em `data/raw/` e os importa no banco.

### Gerar dados sem inserir no banco

```bash
python src/populate.py \
  --users 10000 \
  --products 1000 \
  --orders 50000 \
  --ratings 20000 \
  --generate-only
```

### Importar CSVs existentes

```bash
python src/populate.py --import-only
```

### Importar ignorando duplicados

```bash
python src/populate.py --import-only --ignore-duplicates
```

### Limpar tabelas antes da importacao

```bash
python src/populate.py --import-only --truncate
```

### Usar um diretorio CSV personalizado

```bash
python src/populate.py \
  --users 1000 \
  --products 100 \
  --orders 5000 \
  --ratings 2000 \
  --output-dir "/caminho/para/csv"
```

Os arquivos gerados sao:

- `user_authentication.csv`
- `user_public_profile.csv`
- `user_private_profile.csv`
- `products.csv`
- `orders.csv`
- `ratings.csv`

## Distribuicoes dos dados

A geracao atual utiliza distribuicoes aleatorias para aproximar dados realistas:

- Precos de custo: distribuicao normal com media 150 e desvio padrao 50.
- Quantidade de pedidos: distribuicao normal limitada entre 1 e 10.
- Avaliacoes: distribuicao normal limitada entre 1 e 5.
- Precos de venda: calculados a partir do custo com margem aleatoria entre 15% e 50%.
- Emails: gerados sem repeticoes dentro da mesma execucao.
- Avaliacoes: cada par usuario-produto aparece somente uma vez.

## Comportamento de importacao

As importacoes usam `COPY` para tabelas sem conflitos e `INSERT ... ON CONFLICT DO NOTHING` quando `--ignore-duplicates` esta ativo.

Ao finalizar, o programa informa se todos os arquivos foram importados ou se ocorreram erros. Erros em linhas individuais sao registrados no terminal e a transacao da linha problematica e revertida.

## TO DO

- [ ] Adicionar testes automatizados para geracao de CSV e importacao no banco.
- [ ] Validar os parametros da linha de comando e os caminhos de entrada.
- [ ] Tornar o volume de dados do Docker Compose portavel entre ambientes.
- [ ] Adicionar suporte a configuracoes via arquivo YAML ou JSON.
- [ ] Criar validacoes de integridade apos a importacao.
- [ ] Adicionar uma tabela de execucoes e registrar contagens de linhas processadas.
- [ ] Exportar consultas e metricas de analise para `data/exports/`.
- [ ] Adicionar dataset de pedidos com produtos e usuarios consistentes.
- [ ] Melhorar a geracao de URLs de foto e campos JSONB de especificacoes.
- [ ] Implementar logging estruturado em vez de mensagens apenas no terminal.
- [ ] Criar um Makefile ou scripts unificados para configuracao e execucao.
- [ ] Documentar exemplos de consultas SQL para analise dos dados.
- [ ] Criar arquivos python para analise de dados
