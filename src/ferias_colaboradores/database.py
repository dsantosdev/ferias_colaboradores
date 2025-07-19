# region Imports
import sqlite3
# endregion

# region Configuração do Banco de Dados
DB_NAME = "ferias.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS colaboradores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT,
                nome TEXT NOT NULL,
                data_contratacao TEXT NOT NULL,
                preferencia_ferias INTEGER NOT NULL,
                ativo INTEGER DEFAULT 1
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ferias_historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                colaborador_id INTEGER,
                ano INTEGER,
                data_inicio TEXT,
                duracao INTEGER,
                FOREIGN KEY (colaborador_id) REFERENCES colaboradores (id)
            )
        """)
        cursor.execute("UPDATE ferias_historico SET ano = 2025 WHERE ano = 1")
        conn.commit()
# endregion