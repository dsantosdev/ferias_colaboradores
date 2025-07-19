# Sistema de Acompanhamento de Férias

Sistema em Python para gerenciar férias de colaboradores em escala 12x36, respeitando a CLT.

## Instalação
1. Clone o repositório: `git clone https://github.com/dsantosdev/ferias_colaboradores.git`
2. Crie um ambiente virtual: `python -m venv venv`
3. Ative o ambiente: `source venv/bin/activate` (Linux/Mac) ou `venv\Scripts\activate` (Windows)
4. Instale as dependências: `pip install -r requirements.txt`
5. Execute o programa: `python -m ferias_colaboradores.main`

## Funcionalidades
- Cadastro de colaboradores com nome, data de contratação, últimas férias e preferência (15 ou 30 dias).
- Listagem com cores: vermelho (30 dias pendentes), amarelo (15 dias pendentes), verde (férias em dia).
- Sugestão de períodos de férias (verão/inverno para 15 dias).
- Banco de dados SQLite para persistência.

## Estrutura
- `main.py`: Ponto de entrada.
- `database.py`: Conexão com SQLite.
- `models.py`: Modelo de dados.
- `utils.py`: Funções utilitárias.
- `cadastro.py`: Cadastro de colaboradores.
- `listagem.py`: Listagem com cores.
- `regras_clt.py`: Regras da CLT.

## Como Contribuir
1. Fork o repositório.
2. Crie uma branch: `git checkout -b minha-feature`
3. Commit suas mudanças: `git commit -m 'Minha feature'`
4. Push para o GitHub: `git push origin minha-feature`
5. Crie um Pull Request.