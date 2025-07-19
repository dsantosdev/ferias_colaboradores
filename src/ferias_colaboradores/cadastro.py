from datetime import datetime
from .database import get_db_connection

def cadastrar_colaborador(matricula, nome, data_contratacao, preferencia_ferias):
    try:
        data = datetime.strptime(data_contratacao, "%d/%m/%Y").strftime("%Y-%m-%d")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO colaboradores (matricula, nome, data_contratacao, preferencia_ferias) VALUES (?, ?, ?, ?)",
                (matricula, nome, data, preferencia_ferias)
            )
            conn.commit()
    except ValueError:
        raise ValueError("Formato de data inválido. Use dd/mm/aaaa.")
    except Exception as e:
        raise Exception(f"Erro ao cadastrar colaborador: {e}")

def adicionar_ferias(matricula, data_inicio, duracao):
    try:
        data = datetime.strptime(data_inicio, "%d/%m/%Y").strftime("%Y-%m-%d")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
            result = cursor.fetchone()
            if not result:
                raise ValueError("Colaborador não encontrado.")
            colaborador_id = result[0]
            cursor.execute(
                "INSERT INTO ferias_historico (colaborador_id, ano, data_inicio, duracao) VALUES (?, ?, ?, ?)",
                (colaborador_id, datetime.strptime(data, "%Y-%m-%d").year, data, duracao)
            )
            conn.commit()
    except ValueError as e:
        raise ValueError(f"Formato de data inválido. Use dd/mm/aaaa. {str(e)}")
    except Exception as e:
        raise Exception(f"Erro ao adicionar férias: {e}")