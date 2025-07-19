# region Imports
from datetime import datetime
from dateutil.relativedelta import relativedelta
# endregion

# region Regras da CLT
def verificar_eligibilidade_ferias(data_contratacao, ultimas_ferias):
    data_contratacao = datetime.strptime(data_contratacao, "%Y-%m-%d")
    hoje = datetime.now()
    periodo_aquisitivo = data_contratacao + relativedelta(years=1)
    if ultimas_ferias:
        ultimas_ferias = datetime.strptime(ultimas_ferias, "%Y-%m-%d")
        periodo_aquisitivo = ultimas_ferias + relativedelta(years=1)
    return hoje >= periodo_aquisitivo
# endregion