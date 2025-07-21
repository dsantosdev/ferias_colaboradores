# interface.py
import tkinter as tk
from tkinter import ttk, messagebox, font
from .cadastro import cadastrar_colaborador, adicionar_ferias
from .listagem import listar_colaboradores
from .database import get_db_connection
from datetime import datetime

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Férias")
        self.sort_column = None
        self.sort_reverse = False
        
        # Frame para botões no topo
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)
        
        # Botões de ação
        self.btn_adicionar_colaborador = tk.Button(self.button_frame, text="Adicionar Colaborador", command=self.abrir_janela_adicionar_colaborador)
        self.btn_adicionar_colaborador.pack(side='left', padx=5)
        
        self.btn_adicionar_ferias = tk.Button(self.button_frame, text="Adicionar Férias", command=self.abrir_janela_adicionar_ferias)
        self.btn_adicionar_ferias.pack(side='left', padx=5)
        
        # Treeview com nova coluna "Dias a Tirar"
        self.tree = ttk.Treeview(self.root, columns=("Matricula", "Nome", "Admissão", "Penúltima", "Última", "Próxima 1", "Próxima 2", "Deseja", "Opção", "Dias a Tirar"), show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar cabeçalhos e colunas
        self.font = font.Font(family="Helvetica", size=10)
        for col in ("Matricula", "Nome", "Admissão", "Penúltima", "Última", "Próxima 1", "Próxima 2", "Deseja", "Opção", "Dias a Tirar"):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=self.font.measure(col + "  "), minwidth=50, stretch=True)
        
        # Menu de contexto
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Editar Colaborador", command=self.editar_colaborador)
        self.context_menu.add_command(label="Adicionar Férias", command=self.abrir_janela_adicionar_ferias)
        self.context_menu.add_command(label="Excluir Colaborador", command=self.excluir_colaborador)
        self.tree.bind("<Button-3>", self.mostrar_menu_contexto)
        
        # Configurar cores
        self.tree.tag_configure("red", background="red", foreground="white")
        self.tree.tag_configure("yellow", background="yellow", foreground="black")
        self.tree.tag_configure("green", background="green", foreground="white")
        self.tree.tag_configure("disabled", foreground="gray")
        
        self.atualizar_lista()

    def sort_by_column(self, col):
        table_data = [(self.tree.set(item, col), item) for item in self.tree.get_children()]
        table_data.sort(reverse=self.sort_reverse)
        for index, (val, item) in enumerate(table_data):
            self.tree.move(item, '', index)
        self.sort_reverse = not self.sort_reverse
        self.sort_column = col

    def ajustar_largura_colunas(self, table_data):
        for col_idx, col in enumerate(self.tree["columns"]):
            max_width = self.font.measure(col + "  ")
            for row in table_data:
                cell_text = str(row[col_idx + 1])
                width = self.font.measure(cell_text + "  ")
                if width > max_width:
                    max_width = width
            self.tree.column(col, width=max_width)

    def mostrar_menu_contexto(self, event):
        print("Clique com botão direito detectado em y =", event.y)
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def abrir_janela_adicionar_colaborador(self):
        self.btn_adicionar_ferias.config(state='disabled')
        janela = tk.Toplevel(self.root)
        janela.title("Adicionar Colaborador")
        janela.geometry("300x250")
        janela.transient(self.root)
        janela.grab_set()
        
        tk.Label(janela, text="Matrícula:").pack(pady=5)
        matricula_entry = tk.Entry(janela)
        matricula_entry.pack()
        
        tk.Label(janela, text="Nome:").pack(pady=5)
        nome_entry = tk.Entry(janela)
        nome_entry.pack()
        
        tk.Label(janela, text="Data de Contratação (dd/mm/aaaa):").pack(pady=5)
        data_entry = tk.Entry(janela)
        data_entry.pack()
        
        tk.Label(janela, text="Preferência de Férias (15 ou 30 dias):").pack(pady=5)
        preferencia_entry = tk.Entry(janela)
        preferencia_entry.pack()
        
        def salvar():
            matricula = matricula_entry.get()
            nome = nome_entry.get()
            data = data_entry.get()
            preferencia = preferencia_entry.get()
            try:
                preferencia = int(preferencia) if preferencia in ('15', '30') else 30
                cadastrar_colaborador(matricula, nome, data, preferencia)
                self.atualizar_lista()
                janela.destroy()
                self.btn_adicionar_ferias.config(state='normal')
            except Exception as e:
                messagebox.showerror("Erro", str(e))
        
        tk.Button(janela, text="Salvar", command=salvar).pack(pady=10)
        janela.protocol("WM_DELETE_WINDOW", lambda: [self.btn_adicionar_ferias.config(state='normal'), janela.destroy()])

    def abrir_janela_adicionar_ferias(self):
        self.btn_adicionar_colaborador.config(state='disabled')
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um colaborador.")
            self.btn_adicionar_colaborador.config(state='normal')
            return
        matricula = self.tree.item(selected_item, 'values')[0]
        janela = tk.Toplevel(self.root)
        janela.title("Adicionar Férias")
        janela.geometry("300x200")
        janela.transient(self.root)
        janela.grab_set()
        
        tk.Label(janela, text="Data de Início (dd/mm/aaaa):").pack(pady=5)
        data_entry = tk.Entry(janela)
        data_entry.pack()
        
        tk.Label(janela, text="Duração (15 ou 30 dias):").pack(pady=5)
        duracao_entry = tk.Entry(janela)
        duracao_entry.pack()
        
        def salvar():
            data = data_entry.get()
            duracao = duracao_entry.get()
            try:
                duracao = int(duracao) if duracao in ('15', '30') else 30
                adicionar_ferias(matricula, data, duracao)
                self.atualizar_lista()
                janela.destroy()
                self.btn_adicionar_colaborador.config(state='normal')
            except Exception as e:
                messagebox.showerror("Erro", str(e))
        
        tk.Button(janela, text="Salvar", command=salvar).pack(pady=10)
        janela.protocol("WM_DELETE_WINDOW", lambda: [self.btn_adicionar_colaborador.config(state='normal'), janela.destroy()])

    def editar_colaborador(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um colaborador.")
            return
        matricula = self.tree.item(selected_item, 'values')[0]
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nome, data_contratacao, opcao FROM colaboradores WHERE matricula = ?", (matricula,))
            dados = cursor.fetchone()
            if not dados:
                messagebox.showerror("Erro", "Colaborador não encontrado.")
                return
            nome, data_contratacao, opcao = dados

        janela = tk.Toplevel(self.root)
        janela.title("Editar Colaborador")
        janela.geometry("300x250")
        janela.transient(self.root)
        janela.grab_set()

        tk.Label(janela, text="Matrícula:").pack(pady=5)
        tk.Label(janela, text=matricula).pack()

        tk.Label(janela, text="Nome:").pack(pady=5)
        nome_entry = tk.Entry(janela)
        nome_entry.insert(0, nome)
        nome_entry.pack()

        tk.Label(janela, text="Data de Contratação (dd/mm/aaaa):").pack(pady=5)
        data_entry = tk.Entry(janela)
        data_entry.insert(0, data_contratacao.strftime("%d/%m/%Y") if isinstance(data_contratacao, datetime) else data_contratacao)
        data_entry.pack()

        tk.Label(janela, text="Preferência de Férias (15 ou 30 dias):").pack(pady=5)
        preferencia_entry = tk.Entry(janela)
        preferencia_entry.insert(0, str(opcao))
        preferencia_entry.pack()

        def salvar():
            novo_nome = nome_entry.get()
            nova_data = data_entry.get()
            nova_preferencia = preferencia_entry.get()
            try:
                nova_preferencia = int(nova_preferencia) if nova_preferencia in ('15', '30') else opcao
                data_obj = datetime.strptime(nova_data, "%d/%m/%Y").strftime("%Y-%m-%d")
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE colaboradores SET nome = ?, data_contratacao = ?, opcao = ? WHERE matricula = ?",
                                   (novo_nome, data_obj, nova_preferencia, matricula))
                    conn.commit()
                self.atualizar_lista()
                janela.destroy()
            except ValueError as e:
                messagebox.showerror("Erro", f"Formato de data inválido. Use dd/mm/aaaa. {str(e)}")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tk.Button(janela, text="Salvar", command=salvar).pack(pady=10)
        janela.protocol("WM_DELETE_WINDOW", lambda: janela.destroy())

    def excluir_colaborador(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um colaborador.")
            return
        matricula = self.tree.item(selected_item, 'values')[0]
        if messagebox.askyesno("Confirmação", f"Excluir colaborador com matrícula {matricula}?"):
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ferias_historico WHERE colaborador_id = (SELECT id FROM colaboradores WHERE matricula = ?)", (matricula,))
                cursor.execute("DELETE FROM colaboradores WHERE matricula = ?", (matricula,))
                conn.commit()
            self.atualizar_lista()

    def atualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        table_data = listar_colaboradores()
        print("Dados da tabela:", table_data)
        if not table_data:
            print("Aviso: Nenhum colaborador válido para exibir na tabela.")
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
        self.ajustar_largura_colunas(table_data)