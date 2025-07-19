# region Imports
from datetime import datetime
from dateutil.relativedelta import relativedelta
# endregion

# region Funções Utilitárias
def validar_data(data_str):
    try:
        datetime.strptime(data_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def sugerir_periodo_ferias(preferencia, data_referencia):
    if preferencia == 15:
        verao = datetime(data_referencia.year, 1, 1)  # Janeiro (verão)
        inverno = datetime(data_referencia.year, 7, 1)  # Julho (inverno)
        if data_referencia.month <= 6:
            return verao, inverno
        return inverno, verao
    return data_referencia, None
# endregion