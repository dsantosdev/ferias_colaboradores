# region Imports
from database import get_db_connection
from models import Colaborador
from utils import sugerir_periodo_ferias
from tabulate import tabulate
from colorama import init, Fore
# endregion

# region Listagem de Colaboradores
def listar_colaboradores():
    init()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM colaboradores")
        rows = cursor.fetchall()

    table = []
    for row in rows:
        colaborador = Colaborador(row["nome"], row["data_contratacao"], row["ultimas_ferias"], row["preferencia_ferias"])
        status = colaborador.status_ferias()
        periodo1, periodo2 = sugerir_periodo_ferias(colaborador.preferencia_ferias, colaborador.proximo_periodo_ferias())
        color = Fore.RED if status == "Pendente" else Fore.YELLOW if status == "Pendente (15 dias)" else Fore.GREEN
        table.append([
            color + row["nome"],
            row["data_contratacao"],
            row["ultimas_ferias"] or "N/A",
            row["preferencia_ferias"],
            status,
            periodo1.strftime("%Y-%m-%d"),
            periodo2.strftime("%Y-%m-%d") if periodo2 else "N/A"
        ])

    print(tabulate(table, headers=["Nome", "Contratação", "Últimas Férias", "Dias", "Status", "Período 1", "Período 2"], tablefmt="grid"))
# endregion