# region Imports
from datetime import datetime
from dateutil.relativedelta import relativedelta
# endregion

# region Modelo Colaborador
class Colaborador:
    def __init__(self, nome, data_contratacao, ultimas_ferias, preferencia_ferias):
        self.nome = nome
        self.data_contratacao = datetime.strptime(data_contratacao, "%Y-%m-%d")
        self.ultimas_ferias = datetime.strptime(ultimas_ferias, "%Y-%m-%d") if ultimas_ferias else None
        self.preferencia_ferias = preferencia_ferias

    def proximo_periodo_ferias(self):
        if not self.ultimas_ferias:
            return self.data_contratacao + relativedelta(years=1)
        return self.ultimas_ferias + relativedelta(years=1)

    def status_ferias(self):
        hoje = datetime.now()
        proximo = self.proximo_periodo_ferias()
        if hoje >= proximo:
            return "Pendente" if self.preferencia_ferias == 30 else "Pendente (15 dias)"
        return "Em dia"
# endregion