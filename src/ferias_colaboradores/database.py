# region Imports
import sqlite3
from contextlib import contextmanager
# endregion

# region Conexão com Banco de Dados
@contextmanager
def get_db_connection():
    conn = sqlite3.connect("ferias.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

# region Inicialização do Banco
def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS colaboradores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data_contratacao TEXT NOT NULL,
                ultimas_ferias TEXT,
                preferencia_ferias INTEGER NOT NULL CHECK(preferencia_ferias IN (15, 30))
            )
        """)
# endregion