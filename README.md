Inicializar container e banco de dados

  Use os scripts .sh na pasta scripts/ para inicializar e fechar o container, e depois conectar-se ao banco de dados.

Gerar e Inserir dados com python

  Gerar dados e inserir:
    python src/populate.py --users 10 --products 10 --orders 50 --ratings 20
    
  Gerar dados sem inserir: 
    python src/populate.py --users 10 --products 10 --orders 50 --ratings 20 --generate-only

  Importar dados do csv:
    python src/populate.py --import-only

  Importar ignorando duplicados:
    python src/populate.py --import-only --ignore-duplicates

  Limpar tabelas antes de inserir:
    python src/populate.py --import-only --truncate

  Diretorio de saida customizado:
    python src/populate.py --users 10 --products 10 --output-dir '/path/to/custom/dir'
