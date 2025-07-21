import tkinter as tk
from ferias_colaboradores.interface import App
from ferias_colaboradores.database import init_db

def main():
    # Inicializar o banco de dados
    init_db()
    
    # Criar janela principal do Tkinter
    root = tk.Tk()
    
    # Instanciar a aplicação
    app = App(root)
    
    # Iniciar o loop principal
    root.mainloop()

if __name__ == "__main__":
    main()