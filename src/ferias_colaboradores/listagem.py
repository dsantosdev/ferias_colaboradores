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
            ferias_passadas = sorted(
                [(ano, data_inicio) for ano, data_inicio in colaborador.historico_ferias() if datetime.strptime(data_inicio, "%Y-%m-%d") < data_atual],
                key=lambda x: datetime.strptime(x[1], "%Y-%m-%d"),
                reverse=True
            )[:2]
            ferias_futuras = sorted(
                [(ano, data_inicio) for ano, data_inicio in colaborador.historico_ferias() if datetime.strptime(data_inicio, "%Y-%m-%d") >= data_atual],
                key=lambda x: datetime.strptime(x[1], "%Y-%m-%d")
            )
            row = [
                "green",  # Cor (mantida para compatibilidade, pode ser ajustada se necessário)
                col[1],  # Matrícula
                col[2],  # Nome
                datetime.strptime(data_contratacao, "%Y-%m-%d").strftime("%d-%m-%Y"),  # Admissão
                datetime.strptime(ferias_passadas[1][1], "%Y-%m-%d").strftime("%d-%m-%Y") if len(ferias_passadas) > 1 else "N/A",  # Penúltima
                datetime.strptime(ferias_passadas[0][1], "%Y-%m-%d").strftime("%d-%m-%Y") if ferias_passadas else "N/A",  # Última
                datetime.strptime(ferias_futuras[0][1], "%Y-%m-%d").strftime("%d-%m-%Y") if ferias_futuras else "N/A",  # Próxima 1
                datetime.strptime(ferias_futuras[1][1], "%Y-%m-%d").strftime("%d-%m-%Y") if len(ferias_futuras) > 1 else "N/A",  # Próxima 2
                "N/A",  # Deseja (não implementado no banco, placeholder)
                str(col[4])  # Opção (15 ou 30 dias)
            ]
            if exibir_todos_anos:
                for ano in anos:
                    ferias_ano = next((f for f in colaborador.historico_ferias() if int(f[0]) == ano), None)
                    row.append(datetime.strptime(ferias_ano[1], "%Y-%m-%d").strftime("%d-%m-%Y") if ferias_ano else "N/A")
            table_data.append(row)
        except (ValueError, IndexError) as e:
            print(f"Aviso: Erro ao processar linha com matrícula {col[1]}: {e}")
            continue
    if not table_data:
        print("Aviso: Nenhum dado válido encontrado para exibir.")
    return table_data, anos if exibir_todos_anos else [datetime.now().year] if not table_data else [max(anos, default=datetime.now().year)]
# endregion