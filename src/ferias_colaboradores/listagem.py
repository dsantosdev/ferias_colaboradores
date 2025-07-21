from datetime import datetime, timedelta
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
                [(ano, data_inicio, duracao) for ano, data_inicio, duracao in colaborador.historico_ferias() if datetime.strptime(data_inicio, "%Y-%m-%d") < data_atual],
                key=lambda x: datetime.strptime(x[1], "%Y-%m-%d"),
                reverse=True
            )
            ferias_futuras = sorted(
                [(ano, data_inicio, duracao) for ano, data_inicio, duracao in colaborador.historico_ferias() if datetime.strptime(data_inicio, "%Y-%m-%d") >= data_atual],
                key=lambda x: datetime.strptime(x[1], "%Y-%m-%d")
            )

            # Determinar a data de referência (duas últimas férias ou data de contratação)
            referencia = datetime.strptime(data_contratacao, "%Y-%m-%d")
            if ferias_passadas:
                ultima_ferias = datetime.strptime(ferias_passadas[0][1], "%Y-%m-%d")
                if len(ferias_passadas) > 1:
                    penultima_ferias = datetime.strptime(ferias_passadas[1][1], "%Y-%m-%d")
                    referencia = penultima_ferias  # Usa a penúltima como base
                else:
                    referencia = ultima_ferias  # Usa a última se só houver uma

            # Calcular períodos aquisitivos e dias tirados
            meses_desde_referencia = (data_atual.year - referencia.year) * 12 + data_atual.month - referencia.month
            periodos_aquisitivos = meses_desde_referencia // 12
            dias_por_periodo = col[4]  # 15 ou 30 dias (valor de "Opção")
            dias_adquiridos = periodos_aquisitivos * dias_por_periodo

            # Calcular dias tirados com base na duração real
            dias_tirados = sum(int(duracao) for _, _, duracao in ferias_passadas)

            dias_a_tirar = max(0, dias_adquiridos - dias_tirados)

            # Determinar a cor com base em períodos vencidos
            cor = "green"
            periodos_tirados = len(ferias_passadas)
            ferias_vencidas = max(0, periodos_aquisitivos - periodos_tirados)
            if ferias_vencidas >= 1:
                cor = "yellow"
                if periodos_aquisitivos >= 2:
                    segundo_periodo_inicio = referencia + timedelta(days=365 * 2)
                    meses_para_vencer = (segundo_periodo_inicio.year - data_atual.year) * 12 + segundo_periodo_inicio.month - data_atual.month
                    if meses_para_vencer <= 6:
                        cor = "red"

            row = [
                cor,  # Cor conforme as diretivas
                col[1],  # Matrícula
                col[2],  # Nome
                datetime.strptime(data_contratacao, "%Y-%m-%d").strftime("%d/%m/%Y"),  # Admissão
                datetime.strptime(ferias_passadas[1][1], "%Y-%m-%d").strftime("%d/%m/%Y") if len(ferias_passadas) > 1 else "N/A",  # Penúltima
                datetime.strptime(ferias_passadas[0][1], "%Y-%m-%d").strftime("%d/%m/%Y") if ferias_passadas else "N/A",  # Última
                datetime.strptime(ferias_futuras[0][1], "%Y-%m-%d").strftime("%d/%m/%Y") if ferias_futuras else "N/A",  # Próxima 1
                datetime.strptime(ferias_futuras[1][1], "%Y-%m-%d").strftime("%d/%m/%Y") if len(ferias_futuras) > 1 else "N/A",  # Próxima 2
                "N/A",  # Deseja (não implementado no banco)
                str(col[4]),  # Opção (15 ou 30 dias)
                str(dias_a_tirar)  # Dias a tirar
            ]
            table_data.append(row)
        except (ValueError, IndexError) as e:
            print(f"Aviso: Erro ao processar linha com matrícula {col[1]}: {e}")
            continue
    if not table_data:
        print("Aviso: Nenhum dado válido encontrado para exibir.")
    return table_data