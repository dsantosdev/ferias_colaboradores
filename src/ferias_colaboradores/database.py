import sqlite3
from datetime import datetime
import os
import csv
import chardet

def get_db_connection():
    conn = sqlite3.connect('ferias.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS colaboradores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT UNIQUE,
                nome TEXT,
                data_contratacao TEXT,
                preferencia_ferias INTEGER,
                ativo INTEGER DEFAULT 1
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ferias_historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                colaborador_id INTEGER,
                ano INTEGER,
                data_inicio TEXT,
                duracao INTEGER,
                FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id)
            )
        ''')
        conn.commit()

def importar_csv(caminho_csv):
    # Normalizar caminho do arquivo

    #python
    #from ferias_colaboradores.database import importar_csv
    #importar_csv(r"C:\_Python\ferias_colaboradores\docs\Férias.csv")
    caminho_csv = os.path.normpath(caminho_csv)
    if not os.path.exists(caminho_csv):
        print(f"Erro: Arquivo {caminho_csv} não encontrado.")
        return

    # Detectar codificação do arquivo
    with open(caminho_csv, 'rb') as file:
        result = chardet.detect(file.read())
        encoding = result['encoding'] or 'cp1252'  # Default para ANSI (Windows-1252)
        confidence = result['confidence']
        print(f"Codificação detectada: {encoding} (confiança: {confidence:.2%})")

    def parse_data(data_str):
        print(f"parse_data chamado com: {data_str}")
        if not data_str or data_str == 'N/A':
            print(f"parse_data retornando None para: {data_str}")
            return None
        try:
            # Tentar formato dd/mm/yy
            print(f"Tentando parsear {data_str} como dd/mm/yy")
            data = datetime.strptime(data_str, "%d/%m/%y")
            ano = data.year
            if ano < 100:
                ano += 2000 if ano < 50 else 1900
            result = data.replace(year=ano).strftime("%Y-%m-%d")
            print(f"parse_data sucesso: {data_str} -> {result}")
            return result
        except ValueError:
            try:
                # Tentar formato dd-mm-yyyy
                print(f"Tentando parsear {data_str} como dd-mm-yyyy")
                result = datetime.strptime(data_str, "%d-%m-%Y").strftime("%Y-%m-%d")
                print(f"parse_data sucesso: {data_str} -> {result}")
                return result
            except ValueError:
                print(f"parse_data falhou: Formato de data inválido: {data_str}")
                return None

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            with open(caminho_csv, 'r', encoding=encoding) as file:
                reader = csv.DictReader(file, delimiter=';')
                expected_columns = ['Matricula', 'Nome', 'Admissão', 'Penúltima', 'Última', 'Próxima', 'Deseja', 'Opção']
                if reader.fieldnames != expected_columns:
                    print(f"Erro: Colunas do CSV ({reader.fieldnames}) não correspondem às esperadas ({expected_columns}).")
                    return

                for row_num, row in enumerate(reader, start=1):
                    try:
                        matricula = row['Matricula']
                        nome = row['Nome']
                        print(f"Processando linha {row_num}, matrícula {matricula}")
                        # Formatar nome para title case, preservando conjunções
                        palavras = nome.split()
                        conjuncoes = {'de', 'da', 'do', 'das', 'dos'}
                        nome_formatado = ' '.join(palavra.title() if palavra.lower() not in conjuncoes else palavra.lower() for palavra in palavras)
                        data_contratacao = parse_data(row['Admissão'])
                        if not data_contratacao:
                            print(f"Erro na linha {row_num}, matrícula {matricula}: Data de admissão inválida ({row['Admissão']}). Continuando sem data de admissão.")
                            continue
                        opcao = int(row['Opção']) if row['Opção'] and row['Opção'] in ('15', '30') else 30

                        cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
                        if cursor.fetchone():
                            print(f"Atualizando colaborador com matrícula {matricula}")
                            cursor.execute(
                                "UPDATE colaboradores SET nome = ?, data_contratacao = ?, preferencia_ferias = ? WHERE matricula = ?",
                                (nome_formatado, data_contratacao, opcao, matricula)
                            )
                        else:
                            print(f"Inserindo novo colaborador com matrícula {matricula}")
                            cursor.execute(
                                "INSERT INTO colaboradores (matricula, nome, data_contratacao, preferencia_ferias) VALUES (?, ?, ?, ?)",
                                (matricula, nome_formatado, data_contratacao, opcao)
                            )

                        for campo, ano in [('Penúltima', None), ('Última', None), ('Próxima', datetime.now().year)]:
                            if row[campo] and row[campo] != 'N/A':
                                data_inicio = parse_data(row[campo])
                                if not data_inicio:
                                    print(f"Erro na linha {row_num}, matrícula {matricula}, campo {campo}: Data inválida ({row[campo]}). Pulando inserção de férias.")
                                    continue
                                cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
                                colaborador_id = cursor.fetchone()[0]
                                print(f"Inserindo férias para matrícula {matricula}, campo {campo}, data {data_inicio}")
                                cursor.execute(
                                    "INSERT INTO ferias_historico (colaborador_id, ano, data_inicio, duracao) VALUES (?, ?, ?, ?)",
                                    (colaborador_id, ano if ano else datetime.strptime(data_inicio, "%Y-%m-%d").year, data_inicio, opcao)
                                )

                        # Validar campo Deseja (apenas para verificação, não salvo no banco)
                        if row['Deseja'] and row['Deseja'] != 'N/A':
                            data_deseja = parse_data(row['Deseja'])
                            if not data_deseja:
                                print(f"Erro na linha {row_num}, matrícula {matricula}, campo Deseja: Data inválida ({row['Deseja']}). Ignorando campo Deseja.")
                    except Exception as e:
                        print(f"Erro na linha {row_num}, matrícula {matricula}: {e}")
                        continue
            conn.commit()
            print("Importação do CSV concluída com sucesso!")
    except Exception as e:
        print(f"Erro durante a importação do CSV: {e}")