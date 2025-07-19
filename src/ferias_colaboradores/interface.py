# region Imports
import tkinter as tk
from tkinter import ttk, messagebox, Menu
from ferias_colaboradores.cadastro import cadastrar_colaborador
from ferias_colaboradores.listagem import listar_colaboradores
from ferias_colaboradores.utils import validar_data
from ferias_colaboradores.database import get_db_connection, init_db
from datetime import datetime
# endregion

# region Interface Gráfica
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Acompanhamento de Férias")
        self.geometry("1200x700")
        init_db()

        # region Formulário de Cadastro
        self.frame_cadastro = ttk.LabelFrame(self, text="Cadastrar/Editar Colaborador")
        self.frame_cadastro.pack(padx=10, pady=10, fill="x")

        ttk.Label(self.frame_cadastro, text="Matrícula:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_matricula = ttk.Entry(self.frame_cadastro)
        self.entry_matricula.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame_cadastro, text="Nome:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_nome = ttk.Entry(self.frame_cadastro)
        self.entry_nome.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.frame_cadastro, text="Data de Contratação (dd-mm-yyyy):").grid(row=2, column=0, padx=5, pady=5)
        self.entry_contratacao = ttk.Entry(self.frame_cadastro)
        self.entry_contratacao.grid(row=2, column=1, padx=5, pady=5)
        self.entry_contratacao.bind("<KeyRelease>", self.formatar_data)

        ttk.Label(self.frame_cadastro, text="Preferência de Férias:").grid(row=3, column=0, padx=5, pady=5)
        self.preferencia_var = tk.StringVar(value="30")
        ttk.Radiobutton(self.frame_cadastro, text="15 dias", variable=self.preferencia_var, value="15").grid(row=3, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(self.frame_cadastro, text="30 dias", variable=self.preferencia_var, value="30").grid(row=3, column=1, padx=5, pady=5, sticky="e")

        ttk.Button(self.frame_cadastro, text="Cadastrar/Editar Colaborador", command=self.cadastrar_ou_editar_colaborador).grid(row=4, column=0, columnspan=2, pady=10)
        # endregion

        # region Adicionar Férias
        self.frame_ferias = ttk.LabelFrame(self, text="Adicionar Férias")
        self.frame_ferias.pack(padx=10, pady=10, fill="x")

        ttk.Label(self.frame_ferias, text="Matrícula:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_matricula_ferias = ttk.Entry(self.frame_ferias)
        self.entry_matricula_ferias.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame_ferias, text="Ano das Férias (YYYY):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_ano = ttk.Entry(self.frame_ferias)
        self.entry_ano.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.frame_ferias, text="Data de Início (dd-mm-yyyy):").grid(row=2, column=0, padx=5, pady=5)
        self.entry_data_ferias = ttk.Entry(self.frame_ferias)
        self.entry_data_ferias.grid(row=2, column=1, padx=5, pady=5)
        self.entry_data_ferias.bind("<KeyRelease>", self.formatar_data)

        ttk.Label(self.frame_ferias, text="Duração (15/30 dias):").grid(row=3, column=0, padx=5, pady=5)
        self.entry_duracao = ttk.Entry(self.frame_ferias)
        self.entry_duracao.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(self.frame_ferias, text="Adicionar Férias", command=self.adicionar_ferias).grid(row=4, column=0, columnspan=2, pady=10)
        # endregion

        # region Tabela de Listagem
        self.frame_lista = ttk.LabelFrame(self, text="Lista de Colaboradores")
        self.frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

        self.exibir_todos_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.frame_lista, text="Exibir todos os anos", variable=self.exibir_todos_var, command=self.atualizar_lista).pack(pady=5)

        self.tree = ttk.Treeview(self.frame_lista, show="headings")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.carregar_dados_colaborador)
        self.tree.bind("<Button-3>", self.mostrar_menu_contexto)

        ttk.Button(self.frame_lista, text="Atualizar Lista", command=self.atualizar_lista).pack(pady=10)
        # endregion

        # Menu de Contexto
        self.menu_contexto = Menu(self.tree, tearoff=0)
        self.menu_contexto.add_command(label="Salvar Alterações", command=self.salvar_alteracoes)
        self.menu_contexto.add_command(label="Excluir", command=self.excluir_colaborador)
        self.menu_contexto.add_command(label="Ativar/Desativar", command=self.toggle_ativo)
        self.menu_contexto.add_command(label="Sugerir Férias", command=lambda: self.sugerir_ferias(self.tree.selection()[0] if self.tree.selection() else None))

        self.atualizar_lista()
# endregion

# region Métodos
    def formatar_data(self, event):
        entry = event.widget
        text = entry.get().replace("-", "")
        if not text.isdigit():
            return
        formatted = ""
        if len(text) > 0:
            formatted = text[:2]
        if len(text) > 2:
            formatted = f"{text[:2]}-{text[2:4]}"
        if len(text) > 4:
            formatted = f"{text[:2]}-{text[2:4]}-{text[4:8]}"
        entry.delete(0, tk.END)
        entry.insert(0, formatted[:10])

    def mostrar_menu_contexto(self, event):
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.tree.selection_set(selected_item)
            values = self.tree.item(selected_item, "values")
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ativo FROM colaboradores WHERE matricula = ?", (values[0],))
                ativo = cursor.fetchone()[0]
                self.menu_contexto.entryconfig(2, label="Ativar" if not ativo else "Desativar")
            self.menu_contexto.post(event.x_root, event.y_root)

    def carregar_dados_colaborador(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item = selected_item[0]
        values = self.tree.item(item, "values")
        self.entry_matricula.delete(0, tk.END)
        self.entry_matricula.insert(0, values[0])  # Matrícula
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, values[1])  # Nome
        self.entry_contratacao.delete(0, tk.END)
        self.entry_contratacao.insert(0, values[2])  # Data de Contratação
        self.preferencia_var.set(values[3])  # Preferência de Férias

    def cadastrar_ou_editar_colaborador(self):
        matricula = self.entry_matricula.get()
        nome = self.entry_nome.get()
        data_contratacao = self.entry_contratacao.get()
        preferencia = self.preferencia_var.get()

        if not matricula or not nome:
            messagebox.showerror("Erro", "Matrícula e Nome são obrigatórios!")
            return
        if not matricula.isdigit():
            messagebox.showerror("Erro", "Matrícula deve conter apenas números!")
            return
        if not validar_data(data_contratacao):
            messagebox.showerror("Erro", "Data de contratação inválida! Use dd-mm-yyyy.")
            return
        if preferencia not in ("15", "30"):
            messagebox.showerror("Erro", "Escolha 15 ou 30 dias!")
            return

        # Formatar nome para title case, preservando conjunções
        palavras = nome.split()
        conjuncoes = {'de', 'da', 'do', 'das', 'dos'}
        nome_formatado = ' '.join(palavra.title() if palavra.lower() not in conjuncoes else palavra.lower() for palavra in palavras)

        data_contratacao_db = datetime.strptime(data_contratacao, "%d-%m-%Y").strftime("%Y-%m-%d")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
            result = cursor.fetchone()
            if result:
                cursor.execute(
                    "UPDATE colaboradores SET nome = ?, data_contratacao = ?, preferencia_ferias = ? WHERE matricula = ?",
                    (nome_formatado, data_contratacao_db, int(preferencia), matricula)
                )
                conn.commit()
                messagebox.showinfo("Sucesso", f"Colaborador {nome_formatado} atualizado com sucesso!")
            else:
                cursor.execute(
                    "INSERT INTO colaboradores (matricula, nome, data_contratacao, preferencia_ferias) VALUES (?, ?, ?, ?)",
                    (matricula, nome_formatado, data_contratacao_db, int(preferencia))
                )
                conn.commit()
                messagebox.showinfo("Sucesso", f"Colaborador {nome_formatado} cadastrado com sucesso!")
        self.entry_matricula.delete(0, tk.END)
        self.entry_nome.delete(0, tk.END)
        self.entry_contratacao.delete(0, tk.END)
        self.preferencia_var.set("30")
        self.atualizar_lista()

    def excluir_colaborador(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um colaborador para excluir!")
            return
        item = selected_item[0]
        values = self.tree.item(item, "values")
        matricula = values[0]
        if messagebox.askyesno("Confirmar", f"Deseja excluir o colaborador com matrícula {matricula}?"):
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
                colaborador_id = cursor.fetchone()[0]
                cursor.execute("DELETE FROM ferias_historico WHERE colaborador_id = ?", (colaborador_id,))
                cursor.execute("DELETE FROM colaboradores WHERE matricula = ?", (matricula,))
                conn.commit()
            messagebox.showinfo("Sucesso", "Colaborador excluído com sucesso!")
            self.atualizar_lista()

    def adicionar_ferias(self):
        matricula = self.entry_matricula_ferias.get()
        ano = self.entry_ano.get()
        data_inicio = self.entry_data_ferias.get()
        duracao = self.entry_duracao.get()

        if not matricula.isdigit():
            messagebox.showerror("Erro", "Matrícula deve conter apenas números!")
            return
        if not ano.isdigit() or len(ano) != 4 or int(ano) < 2000 or int(ano) > datetime.now().year + 1:
            messagebox.showerror("Erro", "Ano das férias inválido! Use 4 dígitos (ex.: 2025).")
            return
        if not validar_data(data_inicio):
            messagebox.showerror("Erro", "Data de início inválida! Use dd-mm-yyyy.")
            return
        if duracao not in ("15", "30"):
            messagebox.showerror("Erro", "Duração deve ser 15 ou 30 dias!")
            return

        data_inicio_db = datetime.strptime(data_inicio, "%d-%m-%Y").strftime("%Y-%m-%d")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Erro", "Matrícula não encontrada!")
                return
            colaborador_id = result[0]
            cursor.execute(
                "INSERT INTO ferias_historico (colaborador_id, ano, data_inicio, duracao) VALUES (?, ?, ?, ?)",
                (colaborador_id, int(ano), data_inicio_db, int(duracao))
            )
            conn.commit()
        messagebox.showinfo("Sucesso", f"Férias adicionadas para a matrícula {matricula}!")
        self.entry_matricula_ferias.delete(0, tk.END)
        self.entry_ano.delete(0, tk.END)
        self.entry_data_ferias.delete(0, tk.END)
        self.entry_duracao.delete(0, tk.END)
        self.atualizar_lista()

    def formatar_ano(self, event):
        pass

    def atualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        exibir_todos = self.exibir_todos_var.get()
        table_data, anos = listar_colaboradores(exibir_todos)
        print("Dados da tabela:", table_data)
        print("Colunas configuradas:", ["Cor", "Matrícula", "Nome", "Contratação", "Dias", "Status", "Dias Direito", "Últimas Férias 1", "Últimas Férias 2", "Férias Futuras"] if not exibir_todos else ["Cor", "Matrícula", "Nome", "Contratação", "Dias", "Status", "Dias Direito"] + [f"Férias {ano}" for ano in anos])
        if not table_data:
            print("Aviso: Nenhum colaborador válido para exibir na tabela.")

        colunas = ["Cor", "Matrícula", "Nome", "Contratação", "Dias", "Status", "Dias Direito", "Últimas Férias 1", "Últimas Férias 2", "Férias Futuras"] if not exibir_todos else ["Cor", "Matrícula", "Nome", "Contratação", "Dias", "Status", "Dias Direito"] + [f"Férias {ano}" for ano in anos]
        self.tree.configure(columns=colunas, displaycolumns=colunas[1:])
        for col in colunas[1:]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50, stretch=True)
        self.tree.column("Cor", width=0, stretch=False)

        for row in table_data:
            print("Inserindo linha:", row)
            item = self.tree.insert("", tk.END, values=row[0:], tags=(row[0],))
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
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for item in self.tree.get_children():
                if self.tree.item(item, "state") != "disabled":
                    values = self.tree.item(item, "values")
                    try:
                        data_contratacao_db = datetime.strptime(values[2], "%d-%m-%Y").strftime("%Y-%m-%d")
                        cursor.execute(
                            "UPDATE colaboradores SET nome = ?, data_contratacao = ?, preferencia_ferias = ? WHERE matricula = ?",
                            (values[1], data_contratacao_db, values[3], values[0])
                        )
                    except ValueError:
                        messagebox.showerror("Erro", f"Data de contratação inválida para matrícula {values[0]}! Use dd-mm-yyyy.")
                        return
            conn.commit()
        messagebox.showinfo("Sucesso", "Alterações salvas com sucesso!")
        self.atualizar_lista()

    def toggle_ativo(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um colaborador para alternar o estado!")
            return
        item = selected_item[0]
        values = self.tree.item(item, "values")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ativo FROM colaboradores WHERE matricula = ?", (values[0],))
            ativo = cursor.fetchone()[0]
            novo_estado = 1 if not ativo else 0
            cursor.execute("UPDATE colaboradores SET ativo = ? WHERE matricula = ?", (novo_estado, values[0]))
            conn.commit()
        self.atualizar_lista()
 
    def sugerir_ferias(self, item):
        values = self.tree.item(item, "values")
        matricula = values[0]
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, preferencia_ferias FROM colaboradores WHERE matricula = ?", (matricula,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Erro", "Colaborador não encontrado!")
                return
            colaborador_id, preferencia = result
            cursor.execute("SELECT data_inicio FROM ferias_historico WHERE colaborador_id = ? AND ano = ?", (colaborador_id, datetime.now().year))
            ferias_existentes = [datetime.strptime(row[0], "%Y-%m-%d") for row in cursor.fetchall()]
    
        data_base = datetime(datetime.now().year, 1, 1)
        meses_disponiveis = [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (12, 1)]
    
    def contar_ferias_no_mes(data):
        return sum(1 for f in ferias_existentes if f.year == data.year and f.month == data.month)
    
    def encontrar_proximo_periodo(mes, dia):
        data = datetime(data_base.year, mes, dia)
        while contar_ferias_no_mes(data) >= 2:
            data += timedelta(days=30)
            if data.year > data_base.year:
                return None
        return data

        periodo1, periodo2 = None, None
        if preferencia == 15:
            for mes, dia in meses_disponiveis:
                data_sugerida = encontrar_proximo_periodo(mes, dia)
                if data_sugerida:
                    periodo1 = data_sugerida
                    break
        elif preferencia == 30:
            for mes, dia in meses_disponiveis:
                data_sugerida = encontrar_proximo_periodo(mes, dia)
                if data_sugerida:
                    periodo1 = data_sugerida
                    break
            for mes, dia in meses_disponiveis:
                data_sugerida = encontrar_proximo_periodo(mes, dia)
                if data_sugerida and (not periodo1 or data_sugerida.month != periodo1.month):
                    periodo2 = data_sugerida
                    break

        mensagem = f"Sugestão de férias para matrícula {matricula}:\n"
        mensagem += f"Período 1: {periodo1.strftime('%d-%m-%Y') if periodo1 else 'N/A'}\n"
        if preferencia == 30:
            mensagem += f"Período 2: {periodo2.strftime('%d-%m-%Y') if periodo2 else 'N/A'}"
        messagebox.showinfo("Sugestão de Férias", mensagem)

    def preencher_do_clipboard(self):
        clipboard_text = pyperclip.paste()
        lines = clipboard_text.strip().split('\n')
        if len(lines) == 4 and lines[0].isdigit() and len(lines[2].split()) >= 2 and '/' in lines[3]:
            matricula = lines[0]
            nome = ' '.join(lines[2].split()).title()
            data = lines[3].split('/')
            if len(data) == 3 and data[0].isdigit() and data[1].isdigit() and data[2].isdigit():
                data_contratacao = f"{data[0].zfill(2)}-{data[1].zfill(2)}-{data[2]}"
                self.entry_matricula.delete(0, tk.END)
                self.entry_matricula.insert(0, matricula)
                self.entry_nome.delete(0, tk.END)
                self.entry_nome.insert(0, nome)
                self.entry_contratacao.delete(0, tk.END)
                self.entry_contratacao.insert(0, data_contratacao)
            else:
                messagebox.showerror("Erro", "Formato de data inválido! Use dd/mm/yyyy.")
        else:
            messagebox.showerror("Erro", "Formato inválido no clipboard! Use: matrícula, função, nome, data (dd/mm/yyyy).")
# endregion