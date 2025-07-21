# interface.py
import tkinter as tk
from tkinter import ttk, messagebox, font
from .cadastro import cadastrar_colaborador, adicionar_ferias
from .listagem import listar_colaboradores
from .database import get_db_connection
from datetime import datetime, timedelta

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Férias")
        self.sort_column = None
        self.sort_reverse = False
        self.edited_items = {}  # Armazena alterações temporárias
        
        # Frame para botões no topo
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)
        
        # Botão de salvar
        self.btn_salvar = tk.Button(self.button_frame, text="Salvar Alterações", command=self.salvar_alteracoes, state='disabled')
        self.btn_salvar.pack(side='left', padx=5)
        
        # Botões de ação
        self.btn_adicionar_colaborador = tk.Button(self.button_frame, text="Adicionar Colaborador", command=self.abrir_janela_adicionar_colaborador)
        self.btn_adicionar_colaborador.pack(side='left', padx=5)
        
        self.btn_adicionar_ferias = tk.Button(self.button_frame, text="Adicionar Férias", command=self.abrir_janela_adicionar_ferias)
        self.btn_adicionar_ferias.pack(side='left', padx=5)
        
        # Treeview
        self.tree = ttk.Treeview(self.root, columns=("Matricula", "Nome", "Admissão", "Penúltima", "Última", "Próxima 1", "Próxima 2", "Deseja", "Opção", "Dias a Tirar Próximas"), show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar cabeçalhos e colunas
        self.font = font.Font(family="Helvetica", size=10)
        for col in ("Matricula", "Nome", "Admissão", "Penúltima", "Última", "Próxima 1", "Próxima 2", "Deseja", "Opção", "Dias a Tirar Próximas"):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=self.font.measure(col + "  "), minwidth=50, stretch=True)
        
        # Menu de contexto
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Adicionar Férias", command=self.abrir_janela_adicionar_ferias)
        self.context_menu.add_command(label="Excluir Colaborador", command=self.excluir_colaborador)
        self.tree.bind("<Button-3>", self.mostrar_menu_contexto)
        
        # Configurar cores
        self.tree.tag_configure("red", background="red", foreground="white")
        self.tree.tag_configure("yellow", background="yellow", foreground="black")
        self.tree.tag_configure("green", background="green", foreground="white")
        self.tree.tag_configure("disabled", foreground="gray")
        
        # Habilitar edição inline
        self.tree.bind("<Double-1>", self.on_double_click)
        
        self.atualizar_lista()

    def sort_by_column(self, col):
        table_data = [(self.tree.set(item, col), item) for item in self.tree.get_children()]
        # Tratar colunas de data para ordenação correta
        date_columns = ["Admissão", "Penúltima", "Última", "Próxima 1", "Próxima 2"]
        if col in date_columns:
            table_data.sort(key=lambda x: datetime.strptime(x[0].split(" a ")[0], "%d/%m/%Y") if x[0] else datetime.min, reverse=self.sort_reverse)
        else:
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

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        column = self.tree.identify_column(event.x)
        column_name = self.tree.heading(column, 'text')
        current_value = self.tree.set(item, column_name)
        # Para "Próxima 1" e "Próxima 2", extrair apenas a data inicial para edição
        if column_name in ["Próxima 1", "Próxima 2"] and current_value:
            try:
                current_value = current_value.split(" a ")[0]  # Mostra apenas a data inicial ao editar
            except IndexError:
                pass
        self.tree.set(item, column_name, "")
        entry = tk.Entry(self.tree)
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        entry.focus_set()
        
        def save_edit(event=None):
            new_value = entry.get().strip()
            if not new_value:
                entry.delete(0, tk.END)
                entry.insert(0, current_value.split(" a ")[0] if column_name in ["Próxima 1", "Próxima 2"] else current_value)
                return
            # Formatar datas se for um campo de data
            date_columns = ["Admissão", "Penúltima", "Última", "Próxima 1", "Próxima 2"]
            if column_name in date_columns:
                try:
                    # Tentar interpretar como número (ex.: 01092023) e formatar para dd/mm/aaaa
                    if new_value.isdigit() and len(new_value) == 8:
                        new_value = f"{new_value[:2]}/{new_value[2:4]}/{new_value[4:]}"
                    new_value = datetime.strptime(new_value, "%d/%m/%Y").strftime("%Y-%m-%d")
                    self.edited_items[item] = self.edited_items.get(item, {}) | {column_name: new_value}
                    # Recalcular intervalo para "Próxima 1" e "Próxima 2"
                    if column_name in ["Próxima 1", "Próxima 2"]:
                        duracao = int(self.tree.set(item, "Dias a Tirar Próximas") or 0)
                        data_inicio = datetime.strptime(new_value, "%Y-%m-%d")
                        data_fim = data_inicio + timedelta(days=duracao - 1)
                        display_value = f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
                        self.tree.set(item, column_name, display_value)
                except ValueError:
                    messagebox.showerror("Erro", f"Formato de data inválido. Use dd/mm/aaaa ou 8 dígitos (ex.: 01092023).")
                    entry.delete(0, tk.END)
                    entry.insert(0, current_value.split(" a ")[0] if column_name in ["Próxima 1", "Próxima 2"] else current_value)
                    return
            elif column_name == "Opção":
                try:
                    new_value = int(new_value)
                    if new_value not in (15, 30):
                        raise ValueError
                    self.edited_items[item] = self.edited_items.get(item, {}) | {column_name: new_value}
                except ValueError:
                    messagebox.showerror("Erro", "Opção deve ser 15 ou 30.")
                    entry.delete(0, tk.END)
                    entry.insert(0, current_value)
                    return
            elif column_name == "Dias a Tirar Próximas":
                try:
                    new_value = int(new_value)
                    if new_value < 0:
                        raise ValueError
                    self.edited_items[item] = self.edited_items.get(item, {}) | {column_name: new_value}
                    # Atualizar intervalo se "Próxima 1" ou "Próxima 2" foi editada antes
                    for prox_col in ["Próxima 1", "Próxima 2"]:
                        if prox_col in self.edited_items.get(item, {}):
                            data_inicio = datetime.strptime(self.edited_items[item][prox_col], "%Y-%m-%d")
                            data_fim = data_inicio + timedelta(days=new_value - 1)
                            display_value = f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
                            self.tree.set(item, prox_col, display_value)
                except ValueError:
                    messagebox.showerror("Erro", "Dias a Tirar Próximas deve ser um número inteiro positivo.")
                    entry.delete(0, tk.END)
                    entry.insert(0, current_value)
                    return
            else:
                self.edited_items[item] = self.edited_items.get(item, {}) | {column_name: new_value}
            self.tree.set(item, column_name, entry.get() if column_name not in date_columns else datetime.strptime(new_value, "%Y-%m-%d").strftime("%d/%m/%Y"))
            entry.destroy()
            self.btn_salvar.config(state='normal' if self.edited_items else 'disabled')

        def cancel_edit(event=None):
            self.tree.set(item, column_name, current_value)
            entry.destroy()
            if item not in self.edited_items or not self.edited_items[item]:
                self.btn_salvar.config(state='disabled')

        entry.bind("<Return>", save_edit)
        entry.bind("<Escape>", cancel_edit)
        entry.bind("<FocusOut>", save_edit)
        entry.place(x=self.tree.bbox(item, column)[0], y=self.tree.bbox(item, column)[1], 
                    width=self.tree.column(column_name)["width"], height=self.tree.bbox(item, column)[3])

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
                if data.isdigit() and len(data) == 8:
                    data = f"{data[:2]}/{data[2:4]}/{data[4:]}"
                data_obj = datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
                cadastrar_colaborador(matricula, nome, data_obj, preferencia)
                self.atualizar_lista()
                janela.destroy()
                self.btn_adicionar_ferias.config(state='normal')
            except ValueError as e:
                messagebox.showerror("Erro", f"Formato de data inválido. Use dd/mm/aaaa ou 8 dígitos (ex.: 01092023). {str(e)}")
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
                if data.isdigit() and len(data) == 8:
                    data = f"{data[:2]}/{data[2:4]}/{data[4:]}"
                data_obj = datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
                adicionar_ferias(matricula, data_obj, duracao)
                self.atualizar_lista()
                janela.destroy()
                self.btn_adicionar_colaborador.config(state='normal')
            except ValueError as e:
                messagebox.showerror("Erro", f"Formato de data inválido. Use dd/mm/aaaa ou 8 dígitos (ex.: 01092023). {str(e)}")
            except Exception as e:
                messagebox.showerror("Erro", str(e))
        
        tk.Button(janela, text="Salvar", command=salvar).pack(pady=10)
        janela.protocol("WM_DELETE_WINDOW", lambda: [self.btn_adicionar_colaborador.config(state='normal'), janela.destroy()])

    def salvar_alteracoes(self):
        if not self.edited_items:
            return
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for item_id, changes in self.edited_items.items():
                matricula = self.tree.item(item_id, 'values')[0]
                cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (matricula,))
                colaborador_id = cursor.fetchone()[0]
                if "Nome" in changes:
                    cursor.execute("UPDATE colaboradores SET nome = ? WHERE id = ?", (changes["Nome"], colaborador_id))
                if "Admissão" in changes:
                    cursor.execute("UPDATE colaboradores SET data_contratacao = ? WHERE id = ?", (changes["Admissão"], colaborador_id))
                if "Penúltima" in changes:
                    cursor.execute("UPDATE ferias_historico SET data_inicio = ? WHERE colaborador_id = ? AND ano = (SELECT MAX(ano) - 1 FROM ferias_historico WHERE colaborador_id = ?)", (changes["Penúltima"], colaborador_id, colaborador_id))
                if "Última" in changes:
                    cursor.execute("UPDATE ferias_historico SET data_inicio = ? WHERE colaborador_id = ? AND ano = (SELECT MAX(ano) FROM ferias_historico WHERE colaborador_id = ?)", (changes["Última"], colaborador_id, colaborador_id))
                if "Próxima 1" in changes:
                    cursor.execute("UPDATE ferias_historico SET data_inicio = ? WHERE colaborador_id = ? AND ano = (SELECT MIN(ano) FROM ferias_historico WHERE colaborador_id = ? AND data_inicio >= DATE('now'))", (changes["Próxima 1"], colaborador_id, colaborador_id))
                if "Próxima 2" in changes:
                    cursor.execute("UPDATE ferias_historico SET data_inicio = ? WHERE colaborador_id = ? AND ano = (SELECT MIN(ano) FROM ferias_historico WHERE colaborador_id = ? AND data_inicio > (SELECT MIN(data_inicio) FROM ferias_historico WHERE colaborador_id = ? AND data_inicio >= DATE('now')))", (changes["Próxima 2"], colaborador_id, colaborador_id, colaborador_id))
                if "Deseja" in changes:
                    cursor.execute("UPDATE colaboradores SET deseja = ? WHERE id = ?", (changes["Deseja"], colaborador_id))
                if "Opção" in changes:
                    cursor.execute("UPDATE colaboradores SET preferencia = ? WHERE id = ?", (changes["Opção"], colaborador_id))
                if "Dias a Tirar Próximas" in changes:
                    cursor.execute("UPDATE ferias_historico SET duracao = ? WHERE colaborador_id = ? AND ano = (SELECT MIN(ano) FROM ferias_historico WHERE colaborador_id = ? AND data_inicio >= DATE('now'))", (changes["Dias a Tirar Próximas"], colaborador_id, colaborador_id))
            conn.commit()
        self.edited_items.clear()
        self.btn_salvar.config(state='disabled')
        self.atualizar_lista()

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
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM colaboradores WHERE matricula = ?", (row[1],))
                colaborador_id = cursor.fetchone()[0]
                cursor.execute("SELECT data_inicio, duracao FROM ferias_historico WHERE colaborador_id = ? AND data_inicio >= DATE('now') ORDER BY data_inicio LIMIT 2", (colaborador_id,))
                proximas = cursor.fetchall()
                proxima1 = proxima2 = ""
                if proximas:
                    data_inicio1 = datetime.strptime(proximas[0][0], "%Y-%m-%d").strftime("%d/%m/%Y")
                    data_fim1 = datetime.strptime(proximas[0][0], "%Y-%m-%d") + timedelta(days=proximas[0][1] - 1)
                    proxima1 = f"{data_inicio1} a {data_fim1.strftime('%d/%m/%Y')}"
                    if len(proximas) > 1:
                        data_inicio2 = datetime.strptime(proximas[1][0], "%Y-%m-%d").strftime("%d/%m/%Y")
                        data_fim2 = datetime.strptime(proximas[1][0], "%Y-%m-%d") + timedelta(days=proximas[1][1] - 1)
                        proxima2 = f"{data_inicio2} a {data_fim2.strftime('%d/%m/%Y')}"
                cursor.execute("SELECT duracao FROM ferias_historico WHERE colaborador_id = ? AND data_inicio >= DATE('now') ORDER BY data_inicio LIMIT 1", (colaborador_id,))
                proxima_duracao = cursor.fetchone()
                dias_a_tirar = proxima_duracao[0] if proxima_duracao else 0
                values = list(row[1:5]) + [proxima1, proxima2] + list(row[7:]) + [dias_a_tirar]
                item = self.tree.insert("", tk.END, values=values, tags=(row[0],))
                cursor.execute("SELECT ativo FROM colaboradores WHERE matricula = ?", (row[1],))
                ativo = cursor.fetchone()[0]
                if not ativo:
                    self.tree.item(item, tags=(row[0], 'disabled'))
                    self.tree.tag_configure('disabled', foreground="gray")
        self.ajustar_largura_colunas(table_data)