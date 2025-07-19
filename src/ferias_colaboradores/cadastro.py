# region Imports
from ferias_colaboradores.database import get_db_connection
# endregion

# region Cadastro de Colaboradores
def cadastrar_colaborador(matricula, nome, data_contratacao, preferencia_ferias):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO colaboradores (matricula, nome, data_contratacao, preferencia_ferias) VALUES (?, ?, ?, ?)",
            (matricula, nome, data_contratacao, preferencia_ferias)
        )
        conn.commit()
# endregion