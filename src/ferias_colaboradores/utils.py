# region Imports
from datetime import datetime, timedelta

# endregion

# region Utilidades
def validar_data(data, format="%d-%m-%Y"):
    try:
        if not data:
            return False
        datetime.strptime(data, format)
        return True
    except ValueError:
        return False

def sugerir_periodo_ferias(preferencia, data_base):
    if not data_base:
        return None, None

    # Meses disponíveis para férias
    meses_verao = [(1, 1), (2, 1)]  # Janeiro e Fevereiro
    meses_inverno = [(7, 1), (8, 1)]  # Julho e Agosto
    meses_adicionais = [(3, 1), (4, 1), (5, 1), (6, 1), (9, 1), (10, 1), (11, 1), (12, 1)]  # Outros meses
    meses_disponiveis = meses_verao + meses_inverno + meses_adicionais

    # Consultar quantos colaboradores estão agendados por mês
    from ferias_colaboradores.database import get_db_connection
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT data_inicio FROM ferias_historico WHERE ano = ?", (data_base.year,))
        ferias_existentes = [datetime.strptime(row[0], "%Y-%m-%d") for row in cursor.fetchall()]

    def contar_ferias_no_mes(data):
        return sum(1 for f in ferias_existentes if f.year == data.year and f.month == data.month)

    def encontrar_proximo_periodo(mes, dia):
        data = datetime(data_base.year, mes, dia)
        while contar_ferias_no_mes(data) >= 2:  # Máximo de 2 colaboradores por mês
            data += timedelta(days=30)  # Tenta o próximo mês
            if data.year > data_base.year:  # Evita ultrapassar o ano
                return None
        return data

    if preferencia == 15:
        # Sugerir 15 dias em um mês disponível
        for mes, dia in meses_disponiveis:
            data_sugerida = encontrar_proximo_periodo(mes, dia)
            if data_sugerida:
                return data_sugerida, None
        return None, None
    elif preferencia == 30:
        # Sugerir 15 dias no verão e 15 dias no inverno (ou outros meses disponíveis)
        periodo1, periodo2 = None, None
        for mes, dia in meses_verao:  # Prioriza verão para período 1
            data_sugerida = encontrar_proximo_periodo(mes, dia)
            if data_sugerida:
                periodo1 = data_sugerida
                break
        for mes, dia in meses_inverno:  # Prioriza inverno para período 2
            data_sugerida = encontrar_proximo_periodo(mes, dia)
            if data_sugerida and (not periodo1 or data_sugerida.month != periodo1.month):
                periodo2 = data_sugerida
                break
        if not periodo2:  # Se não encontrou no inverno, tenta outros meses
            for mes, dia in meses_adicionais:
                data_sugerida = encontrar_proximo_periodo(mes, dia)
                if data_sugerida and (not periodo1 or data_sugerida.month != periodo1.month):
                    periodo2 = data_sugerida
                    break
        return periodo1, periodo2
    return None, None
# endregion