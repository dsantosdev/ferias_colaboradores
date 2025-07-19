# region Imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from ferias_colaboradores.cadastro import cadastrar_colaborador
from ferias_colaboradores.listagem import listar_colaboradores
from ferias_colaboradores.utils import validar_data
from ferias_colaboradores.database import get_db_connection, init_db
from datetime import datetime
# endregion

# region Interface Gráfica
class App(tk.Tk):
    def __init__(self):
        print("Iniciando inicialização da interface...")
        super().__init__()
        self.title("Sistema de Acompanhamento de Férias")
        self.geometry("1200x700")
        init_db()
        print("Banco de dados inicializado.")

        # region Formulário de Cadastro
        self.frame_cadastro = ttk.LabelFrame(self, text="Cadastrar Colaborador")
        self.frame_cadastro.pack(padx=10, pady=10, fill="x")
        print("Frame de cadastro criado.")

        ttk.Label(self.frame_cadastro, text="Matrícula:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_matricula = ttk.Entry(self.frame_cadastro)
        self.entry_matricula.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame_cadastro, text="Nome:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_nome = ttk.Entry(self.frame_cadastro)
        self.entry_nome.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.frame_cadastro, text="Data de Contratação (dd-mm-yyyy):").grid(row=2, column=0, padx=5, pady=5)
        self.entry_contratacao = ttk.Entry(self.frame_cadastro)
        self.entry_contratacao.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.frame_cadastro, text="Preferência de Férias:").grid(row=3, column=0, padx=5, pady=5)
        self.preferencia_var = tk.StringVar(value="30")
        ttk.Radiobutton(self.frame_cadastro, text="15 dias", variable=self.preferencia_var, value="15").grid(row=3, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(self.frame_cadastro, text="30 dias", variable=self.preferencia_var, value="30").grid(row=3, column=1, padx=5, pady=5, sticky="e")

        ttk.Button(self.frame_cadastro, text="Cadastrar Colaborador", command=self.cadastrar_colaborador).grid(row=4, column=0, columnspan=2, pady=10)
        print("Botão de cadastro adicionado.")
        # endregion

        # region Adicionar Férias
        self.frame_ferias = ttk.LabelFrame(self, text="Adicionar Férias")
        self.frame_ferias.pack(padx=10, pady=10, fill="x")
        print("Frame de férias criado.")

        ttk.Label(self.frame_ferias, text="Matrícula:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_matricula_ferias = ttk.Entry(self.frame_ferias)
        self.entry_matricula_ferias.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame_ferias, text="Ano das Férias (YYYY):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_ano = ttk.Entry(self.frame_ferias)
        self.entry_ano.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.frame_ferias, text="Data de Início (dd-mm-yyyy):").grid(row=2, column=0, padx=5, pady=5)
        self.entry_data_ferias = ttk.Entry(self.frame_ferias)
        self.entry_data_ferias.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.frame_ferias, text="Duração (15/30 dias):").grid(row=3, column=0, padx=5, pady=5)
        self.entry_duracao = ttk.Entry(self.frame_ferias)
        self.entry_duracao.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(self.frame_ferias, text="Adicionar Férias", command=self.adicionar_ferias).grid(row=4, column=0, columnspan=2, pady=10)
        print("Botão de adicionar férias adicionado.")
        # endregion

        # region Tabela de Listagem
        self.frame_lista = ttk.LabelFrame(self, text="Lista de Colaboradores")
        self.frame_lista.pack(padx=10, pady=10, fill="both", expand=True)
        print("Frame de listagem criado.")

        self.exibir_todos_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.frame_lista, text="Exibir todos os anos", variable=self.exibir_todos_var, command=self.atualizar_lista).pack(pady=5)

        self.tree = ttk.Treeview(self.frame_lista, show="headings")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Button(self.frame_lista, text="Salvar Alterações", command=self.salvar_alteracoes).pack(pady=5)
        ttk.Button(self.frame_lista, text="Atualizar Lista", command=self.atualizar_lista).pack(pady=10)
        ttk.Button(self.frame_lista, text="Toggle Ativo", command=self.toggle_ativo).pack(pady=5)
        ttk.Button(self.frame_lista, text="Exportar Dados", command=self.exportar_dados).pack(pady=5)
        ttk.Button(self.frame_lista, text="Importar Dados", command=self.importar_dados).pack(pady=5)
        print("Botões de listagem e exportação/importação adicionados.")
        # endregion

        self.atualizar_lista()
        print("Lista atualizada na inicialização.")

    def cadastrar_colaborador(self):
        print("Iniciando cadastrar_colaborador...")
        matricula = self.entry_matricula.get()
        nome = self.entry_nome.get().title()
        data_contratacao = self.entry_contratacao.get()
        preferencia = self.preferencia_var.get()
        print(f"Dados recebidos - Matrícula: {matricula}, Nome: {nome}, Data: {data_contratacao}, Preferência: {preferencia}")

        if not matricula or not nome:
            print("Erro: Matrícula e Nome são obrigatórios!")
            messagebox.showerror("Erro", "Matrícula e Nome são obrigatórios!")
            return
        if not matricula.isdigit():
            print("Erro: Matrícula deve conter apenas números!")
            messagebox.showerror("Erro", "Matrícula deve conter apenas números!")
            return
        if not validar_data(data_contratacao):
            print("Erro: Data de contratação inválida!")
            messagebox.showerror("Erro", "Data de contratação inválida! Use dd-mm-yyyy.")
            return
        if preferencia not in ("15", "30"):
            print("Erro: Escolha 15 ou 30 dias!")
            messagebox.showerror("Erro", "Escolha 15 ou 30 dias!")
            return

        data_contratacao_db = datetime.strptime(data_contratacao, "%d-%m-%Y").strftime("%Y-%m-%d")
        print(f"Data convertida para banco: {data_contratacao_db}")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
            if cursor.fetchone():
                print("Erro: Matrícula já cadastrada!")
                messagebox.showerror("Erro", "Matrícula já cadastrada!")
                return
            cursor.execute(
                "INSERT INTO colaboradores (matricula, nome, data_contratacao, preferencia_ferias) VALUES (?, ?, ?, ?)",
                (matricula, nome, data_contratacao_db, int(preferencia))
            )
            conn.commit()
            print(f"Colaborador {nome} cadastrado com ID {cursor.lastrowid}")
        messagebox.showinfo("Sucesso", f"Colaborador {nome} cadastrado com sucesso!")
        self.entry_matricula.delete(0, tk.END)
        self.entry_nome.delete(0, tk.END)
        self.entry_contratacao.delete(0, tk.END)
        self.atualizar_lista()
        print("Fim do cadastrar_colaborador.")

    def adicionar_ferias(self):
        print("Iniciando adicionar_ferias...")
        matricula = self.entry_matricula_ferias.get()
        ano = self.entry_ano.get()
        data_inicio = self.entry_data_ferias.get()
        duracao = self.entry_duracao.get()
        print(f"Dados recebidos - Matrícula: {matricula}, Ano: {ano}, Data Início: {data_inicio}, Duração: {duracao}")

        if not matricula.isdigit():
            print("Erro: Matrícula deve conter apenas números!")
            messagebox.showerror("Erro", "Matrícula deve conter apenas números!")
            return
        if not ano.isdigit() or len(ano) != 4 or int(ano) < 2000 or int(ano) > datetime.now().year + 1:
            print("Erro: Ano das férias inválido!")
            messagebox.showerror("Erro", "Ano das férias inválido! Use 4 dígitos (ex.: 2025).")
            return
        if not validar_data(data_inicio):
            print("Erro: Data de início inválida!")
            messagebox.showerror("Erro", "Data de início inválida! Use dd-mm-yyyy.")
            return
        if duracao not in ("15", "30"):
            print("Erro: Duração deve ser 15 ou 30 dias!")
            messagebox.showerror("Erro", "Duração deve ser 15 ou 30 dias!")
            return

        data_inicio_db = datetime.strptime(data_inicio, "%d-%m-%Y").strftime("%Y-%m-%d")
        print(f"Data de início convertida para banco: {data_inicio_db}")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
            result = cursor.fetchone()
            if not result:
                print("Erro: Matrícula não encontrada!")
                messagebox.showerror("Erro", "Matrícula não encontrada!")
                return
            colaborador_id = result[0]
            cursor.execute(
                "INSERT INTO ferias_historico (colaborador_id, ano, data_inicio, duracao) VALUES (?, ?, ?, ?)",
                (colaborador_id, ano, data_inicio_db, duracao)
            )
        messagebox.showinfo("Sucesso", f"Férias adicionadas para a matrícula {matricula}!")
        self.entry_matricula_ferias.delete(0, tk.END)
        self.entry_ano.delete(0, tk.END)
        self.entry_data_ferias.delete(0, tk.END)
        self.entry_duracao.delete(0, tk.END)
        self.atualizar_lista()
        print("Fim do adicionar_ferias.")

    def atualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        exibir_todos = self.exibir_todos_var.get()
        table_data, anos = listar_colaboradores(exibir_todos)
        print("Dados da tabela:", table_data)
        print("Colunas configuradas:", ["Cor", "Matrícula", "Nome", "Admissão", "Penúltima", "Última", "Próxima 1", "Próxima 2", "Deseja", "Opção"] if not exibir_todos else ["Cor", "Matrícula", "Nome", "Admissão", "Penúltima", "Última", "Próxima 1", "Próxima 2", "Deseja", "Opção"] + [f"Férias {ano}" for ano in anos])
        if not table_data:
            print("Aviso: Nenhum colaborador válido para exibir na tabela.")

        colunas = ["Cor", "Matrícula", "Nome", "Admissão", "Penúltima", "Última", "Próxima 1", "Próxima 2", "Deseja", "Opção"] if not exibir_todos else ["Cor", "Matrícula", "Nome", "Admissão", "Penúltima", "Última", "Próxima 1", "Próxima 2", "Deseja", "Opção"] + [f"Férias {ano}" for ano in anos]
        self.tree.configure(columns=colunas, displaycolumns=colunas[1:])
        for col in colunas[1:]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50, stretch=True)
        self.tree.column("Cor", width=0, stretch=False)

        for row in table_data:
            print("Inserindo linha:", row)
            item = self.tree.insert("", tk.END, values=row[1:], tags=(row[0],))
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ativo FROM colaboradores WHERE matricula = ?", (row[1],))
                ativo = cursor.fetchone()[0]
                if not ativo:
                    self.tree.item(item, tags=(row[0], 'disabled'))
                    self.tree.tag_configure('disabled', foreground='gray')

        self.tree.tag_configure("red", background="red", foreground="white")
        self.tree.tag_configure("yellow", background="yellow", foreground="black")
        self.tree.tag_configure("green", background="green", foreground="white")

    def salvar_alteracoes(self):
        print("Iniciando salvar_alteracoes...")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for item in self.tree.get_children():
                if self.tree.item(item, "state") != "disabled":
                    values = self.tree.item(item, "values")
                    data_contratacao_db = datetime.strptime(values[4], "%d-%m-%Y").strftime("%Y-%m-%d")
                    cursor.execute(
                        "UPDATE colaboradores SET matricula=?, nome=?, data_contratacao=?, preferencia_ferias=? WHERE id=?",
                        (values[1], values[3], data_contratacao_db, values[5], values[2])
                    )
            conn.commit()
        messagebox.showinfo("Sucesso", "Alterações salvas com sucesso!")
        self.atualizar_lista()
        print("Fim do salvar_alteracoes.")

    def toggle_ativo(self):
        print("Iniciando toggle_ativo...")
        selected_item = self.tree.selection()
        if not selected_item:
            print("Aviso: Nenhum colaborador selecionado!")
            messagebox.showwarning("Aviso", "Selecione um colaborador para alternar o estado!")
            return
        item = selected_item[0]
        with get_db_connection() as conn:
            cursor = conn.cursor()
            values = self.tree.item(item, "values")
            ativo = self.tree.item(item, "state") == "disabled"
            cursor.execute("UPDATE colaboradores SET ativo=? WHERE id=?", (1 if ativo else 0, values[2]))
            conn.commit()
        self.atualizar_lista()
        print("Fim do toggle_ativo.")

    def exportar_dados(self):
        print("Iniciando exportar_dados...")
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM colaboradores")
                colaboradores = cursor.fetchall()
                cursor.execute("SELECT * FROM ferias_historico")
                ferias = cursor.fetchall()
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Tabela", "Matrícula", "ID", "Nome", "DataContratacao", "PreferenciaFerias", "Ativo", "ColaboradorID", "Ano", "DataInicio", "Duracao"])
                for col in colaboradores:
                    writer.writerow(["colaboradores", col[1], col[0], col[2], col[3], col[4], col[5], None, None, None, None])
                for fer in ferias:
                    writer.writerow(["ferias_historico", None, None, None, None, None, None, fer[0], fer[1], fer[2], fer[3]])
            messagebox.showinfo("Sucesso", f"Dados exportados para {file_path}")
        print("Fim do exportar_dados.")

    def importar_dados(self):
        print("Iniciando importar_dados...")
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Pular cabeçalho
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    for row in reader:
                        tabela = row[0]
                        if tabela == "colaboradores":
                            cursor.execute(
                                "INSERT OR IGNORE INTO colaboradores (matricula, nome, data_contratacao, preferencia_ferias, ativo) VALUES (?, ?, ?, ?, ?)",
                                (row[1], row[3], row[4], int(row[5]), int(row[6]) if row[6] else 1)
                            )
                        elif tabela == "ferias_historico":
                            cursor.execute(
                                "INSERT OR IGNORE INTO ferias_historico (colaborador_id, ano, data_inicio, duracao) VALUES (?, ?, ?, ?)",
                                (int(row[7]), row[8], row[9], row[10])
                            )
                    conn.commit()
            messagebox.showinfo("Sucesso", f"Dados importados de {file_path}")
            self.atualizar_lista()
        print("Fim do importar_dados.")
# endregion