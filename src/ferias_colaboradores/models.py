# region Imports
from datetime import datetime
from ferias_colaboradores.database import get_db_connection
# endregion

# region Modelos
class Colaborador:
    def __init__(self, nome, data_contratacao, preferencia_ferias, id):
        self.nome = nome
        self.data_contratacao = datetime.strptime(data_contratacao, "%Y-%m-%d")
        self.preferencia_ferias = int(preferencia_ferias)
        self.id = id

    def historico_ferias(self):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ano, data_inicio FROM ferias_historico WHERE colaborador_id = ?", (self.id,))
            return cursor.fetchall()

    def proximo_periodo_ferias(self):
        historico = self.historico_ferias()
        if not historico:
            return datetime(self.data_contratacao.year + 1, 1, 1)
        ultimo_ano = max(int(f[0]) for f in historico)
        return datetime(ultimo_ano + 1, 1, 1)

    def dias_direito(self):
        anos_servico = (datetime.now().year - self.data_contratacao.year)
        return min(30, 15 + (anos_servico * 2))  # Exemplo: máximo 30 dias

    def status_ferias(self):
        proximo = self.proximo_periodo_ferias()
        dias_restantes = (proximo - datetime.now()).days
        if dias_restantes <= 0:
            return "Pendente"
        elif dias_restantes <= 15:
            return "Pendente (15 dias)"
        return "Ok"
# endregion