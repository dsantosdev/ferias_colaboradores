import tkinter as tk
from tkinter import ttk, messagebox
from .cadastro import cadastrar_colaborador, adicionar_ferias
from .listagem import listar_colaboradores

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Férias")
        
        # Frame para botões no topo
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)
        
        # Botões de ação
        self.btn_adicionar_colaborador = tk.Button(self.button_frame, text="Adicionar Colaborador", command=self.abrir_janela_adicionar_colaborador)
        self.btn_adicionar_colaborador.pack(side='left', padx=5)
        
        self.btn_adicionar_ferias = tk.Button(self.button_frame, text="Adicionar Férias", command=self.abrir_janela_adicionar_ferias)
        self.btn_adicionar_ferias.pack(side='left', padx=5)
        
        # Treeview
        self.tree = ttk.Treeview(self.root, columns=("Matricula", "Nome", "Admissão", "Penúltima", "Última", "Próxima 1", "Próxima 2", "Deseja", "Opção"), show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar cabeçalhos e colunas
        for col in ("Matricula", "Nome", "Admissão", "Penúltima", "Última", "Próxima 1", "Próxima 2", "Deseja", "Opção"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50, stretch=True)
        
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

    def mostrar_menu_contexto(self, event):
        # Exibir menu de contexto no local do clique
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def abrir_janela_adicionar_colaborador(self):
        # Desativar botão de adicionar férias
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
                # Reativar ambos os botões
                self.btn_adicionar_colaborador.config(state='normal')
                self.btn_adicionar_ferias.config(state='normal')
            except Exception as e:
                messagebox.showerror("Erro", str(e))
        
        tk.Button(janela, text="Salvar", command=salvar).pack(pady=10)
        janela.protocol("WM_DELETE_WINDOW", lambda: [self.btn_adicionar_ferias.config(state='normal'), janela.destroy()])

    def abrir_janela_adicionar_ferias(self):
        # Desativar botão de adicionar colaborador
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
                # Reativar ambos os botões
                self.btn_adicionar_colaborador.config(state='normal')
                self.btn_adicionar_ferias.config(state='normal')
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
        # Implementar edição (exemplo, pode ser ajustado conforme necessário)
        messagebox.showinfo("Editar", f"Editar colaborador com matrícula {matricula} (funcionalidade a implementar).")

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

        self.tree.tag_configure("red", background="red", foreground="white")
        self.tree.tag_configure("yellow", background="yellow", foreground="black")
        self.tree.tag_configure("green", background="green", foreground="white")