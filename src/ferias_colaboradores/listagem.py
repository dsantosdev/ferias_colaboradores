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
    data_atual = datetime.now()

    for col in colaboradores:
        data_contratacao = col[3]
        if data_contratacao is None:
            print(f"Aviso: Linha com matrícula {col[1]} tem data_contratacao nula, ignorando.")
            continue
        try:
            colaborador = Colaborador(col[2], data_contratacao, col[4], col[0])
            status = colaborador.status_ferias()
            color = "red" if status == "Pendente" else "yellow" if status == "Pendente (15 dias)" else "green"
            data_contratacao_fmt = datetime.strptime(data_contratacao, "%Y-%m-%d").strftime("%d-%m-%Y")
            row = [
                color,
                col[1],  # Matrícula
                col[2],  # Nome
                data_contratacao_fmt,  # Contratação
                col[4],  # Dias
                status,  # Status
                colaborador.dias_direito(),  # Dias Direito
            ]
            historico = colaborador.historico_ferias()
            ferias_passadas = sorted(
                [(ano, data_inicio) for ano, data_inicio in historico if datetime.strptime(data_inicio, "%Y-%m-%d") < data_atual],
                key=lambda x: datetime.strptime(x[1], "%Y-%m-%d"),
                reverse=True
            )[:2]  # Pega até as 2 últimas férias tiradas
            ferias_futuras = sorted(
                [(ano, data_inicio) for ano, data_inicio in historico if datetime.strptime(data_inicio, "%Y-%m-%d") >= data_atual],
                key=lambda x: datetime.strptime(x[1], "%Y-%m-%d")
            )
            
            if exibir_todos_anos:
                for ano in anos:
                    ferias_ano = next((f for f in historico if int(f[0]) == ano), None)
                    row.append(ferias_ano[1] if ferias_ano else "N/A")
            else:
                # Adiciona até 2 últimas férias tiradas
                for i in range(2):
                    if i < len(ferias_passadas):
                        row.append(datetime.strptime(ferias_passadas[i][1], "%Y-%m-%d").strftime("%d-%m-%Y"))
                    else:
                        row.append("N/A")
                # Adiciona férias futuras, se houver
                if ferias_futuras:
                    row.append(ferias_futuras[0][1])  # Primeira futura
                else:
                    row.append("N/A")
            table_data.append(row)
        except ValueError as e:
            print(f"Aviso: Erro ao processar linha com matrícula {col[1]}: {e}")
            continue
    if not table_data:
        print("Aviso: Nenhum dado válido encontrado para exibir.")
    return table_data, anos if exibir_todos_anos else [datetime.now().year] if not table_data else [max(anos, default=datetime.now().year)]
# endregion