# region Imports
from datetime import datetime
from ferias_colaboradores.database import get_db_connection
from ferias_colaboradores.models import Colaborador
from ferias_colaboradores.utils import sugerir_periodo_ferias
# endregion

# region Listagem de Colaboradores
def listar_colaboradores(exibir_todos_anos=False):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM colaboradores")
        colaboradores = cursor.fetchall()
        cursor.execute("SELECT DISTINCT ano FROM ferias_historico ORDER BY ano")
        anos = [row[0] for row in cursor.fetchall()]

    table_data = []
    for col in colaboradores:
        # Verificar se data_contratacao é válida
        data_contratacao = col[3]
        if data_contratacao is None:
            continue  # Ignorar linhas com data_contratacao nula
        try:
            colaborador = Colaborador(col[2], data_contratacao, col[4], col[0])  # nome, data_contratacao, preferencia_ferias, id
            status = colaborador.status_ferias()
            periodo1, periodo2 = sugerir_periodo_ferias(colaborador.preferencia_ferias, colaborador.proximo_periodo_ferias())
            color = "red" if status == "Pendente" else "yellow" if status == "Pendente (15 dias)" else "green"
            row = [
                color,  # Coluna oculta para cor
                col[1],  # Matrícula
                col[0],  # ID
                col[2],  # Nome
                data_contratacao,  # Contratação
                col[4],  # Dias
                status,  # Status
                colaborador.dias_direito(),  # Dias Direito
                periodo1.strftime("%Y-%m-%d"),  # Período 1
                periodo2.strftime("%Y-%m-%d") if periodo2 else "N/A"  # Período 2
            ]
            historico = colaborador.historico_ferias()
            if exibir_todos_anos:
                for ano in anos:
                    ferias_ano = next((f for f in historico if f[0] == ano), None)
                    row.append(ferias_ano[1] if ferias_ano else "N/A")
            else:
                ultimo_ano = max([f[0] for f in historico] or [datetime.now().year])
                ferias_ultimo = next((f for f in historico if f[0] == ultimo_ano), None)
                row.append(ferias_ultimo[1] if ferias_ultimo else "N/A")
            table_data.append(row)
        except ValueError:
            continue  # Ignorar linhas com formato de data inválido
    return table_data, anos if exibir_todos_anos else [datetime.now().year] if not table_data else [ultimo_ano]
# endregion