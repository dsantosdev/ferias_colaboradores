from datetime import datetime
from .database import get_db_connection
from .models import Colaborador

def listar_colaboradores():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM colaboradores")
        colaboradores = cursor.fetchall()

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
                "green",  # Cor (mantida para compatibilidade)
                col[1],  # Matrícula
                col[2],  # Nome
                datetime.strptime(data_contratacao, "%Y-%m-%d").strftime("%d/%m/%Y"),  # Admissão
                datetime.strptime(ferias_passadas[1][1], "%Y-%m-%d").strftime("%d/%m/%Y") if len(ferias_passadas) > 1 else "N/A",  # Penúltima
                datetime.strptime(ferias_passadas[0][1], "%Y-%m-%d").strftime("%d/%m/%Y") if ferias_passadas else "N/A",  # Última
                datetime.strptime(ferias_futuras[0][1], "%Y-%m-%d").strftime("%d/%m/%Y") if ferias_futuras else "N/A",  # Próxima 1
                datetime.strptime(ferias_futuras[1][1], "%Y-%m-%d").strftime("%d/%m/%Y") if len(ferias_futuras) > 1 else "N/A",  # Próxima 2
                "N/A",  # Deseja (não implementado no banco)
                str(col[4])  # Opção (15 ou 30 dias)
            ]
            table_data.append(row)
        except (ValueError, IndexError) as e:
            print(f"Aviso: Erro ao processar linha com matrícula {col[1]}: {e}")
            continue
    if not table_data:
        print("Aviso: Nenhum dado válido encontrado para exibir.")
    return table_data