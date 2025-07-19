# region Imports
from cadastro import cadastrar_colaborador
from listagem import listar_colaboradores
# endregion

# region Menu Principal
def main():
    while True:
        print("\nSistema de Acompanhamento de Férias")
        print("1. Cadastrar colaborador")
        print("2. Listar colaboradores")
        print("3. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_colaborador()
        elif opcao == "2":
            listar_colaboradores()
        elif opcao == "3":
            print("Saindo...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()
# endregion