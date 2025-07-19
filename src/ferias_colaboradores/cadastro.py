# region Imports
from database import get_db_connection, init_db
from models import Colaborador
from utils import validar_data
# endregion

# region Cadastro de Colaborador
def cadastrar_colaborador():
    init_db()
    nome = input("Nome do colaborador: ")
    while True:
        data_contratacao = input("Data de contratação (YYYY-MM-DD): ")
        if validar_data(data_contratacao):
            break
        print("Data inválida! Use o formato YYYY-MM-DD.")

    ultimas_ferias = input("Últimas férias (YYYY-MM-DD, deixe em branco se não houver): ")
    if ultimas_ferias and not validar_data(ultimas_ferias):
        print("Data inválida! Cadastro cancelado.")
        return

    while True:
        preferencia = input("Preferência de férias (15 ou 30 dias): ")
        if preferencia in ("15", "30"):
            preferencia = int(preferencia)
            break
        print("Escolha 15 ou 30 dias!")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO colaboradores (nome, data_contratacao, ultimas_ferias, preferencia_ferias) VALUES (?, ?, ?, ?)",
            (nome, data_contratacao, ultimas_ferias or None, preferencia)
        )
    print(f"Colaborador {nome} cadastrado com sucesso!")
# endregion