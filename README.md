# Sistema de Biblioteca 📘

Este é um sistema de biblioteca acadêmica desenvolvido em **Django** e **Python**, projetado para controle de operações de uma biblioteca. Foi implantado no **PythonAnywhere**, permitindo acesso remoto para testes de funcionalidades.

## ⚙️ Funcionalidades Principais

- **Usuários Externos**: Consultar o catálogo de livros por autor, título e assunto.
- **Alunos e Professores**: Consultar catálogo, visualizar lista de livros, reservar exemplares e visualizar multas (se houver).
- **Bibliotecários**: Cadastrar e listar livros, gerenciar empréstimos e devoluções, aplicar multas por atrasos e marcar exemplares indisponíveis.
- **Administrador**: Acessa todas as funcionalidades dos bibliotecários e pode gerenciar perfis de usuários.

## 🔧 Tecnologias Utilizadas

- **Python 3.10**
- **Django 5.1.2**
- **SQLite** para o banco de dados.
- **Git e GitHub** para controle de versão.
- **PythonAnywhere** para hospedagem do sistema da biblioteca.

## 📁 Estrutura do Projeto

- **SistemaBiblioteca/**: Diretório principal do projeto.
  - **sistema-biblioteca/**: Configurações e arquivos principais do Django (settings.py, urls.py, wsgi.py).
  - **catalogo/**: Aplicação interna de funcionalidades da biblioteca (models.py, views.py, templates/).

## 🚀 Implantação no PythonAnywhere

Para implantar o sistema foi necessário criar uma conta no site, onde não precisa de licenças pagas, é possível realizar deploys com a conta free, apesar de ter planos pagos. Depois da conta criada, basta clonar o repositório do GitHub, configurar o env e instalar as dependências (tudo isso no bash do console). Após isso, é necessário configurar o wsgi e pronto, projeto online!

## 🌐 Como Acessar o Sistema

O sistema está disponível no **PythonAnywhere**. Qualquer pessoa com o link do sistema pode acessar o projeto.

Link: https://isabellasmou.pythonanywhere.com/catalogo/
