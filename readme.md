## Projeto Flask com MySQL - Biblioteca

Este é um projeto básico utilizando Flask com integração ao MySQL para gerenciar uma biblioteca de livros.

### Pré-requisitos

- Python: [Download Python](https://www.python.org/downloads/)
- Flask: Instale usando `pip install Flask`
- MySQL Server: Baixe e instale em [dev.mysql.com](https://dev.mysql.com/downloads/mysql/)
- Flask-MySQLdb: Instale usando `pip install Flask-MySQLdb`

### Configuração

1. Clone o repositório ou baixe o código-fonte.
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure o MySQL:
   - Crie um banco de dados chamado `biblioteca`.
   - Execute o script SQL para criar a tabela de livros dentro do banco de dados.
   

````sql

CREATE DATABASE biblioteca;

USE biblioteca;

CREATE TABLE livros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    autor VARCHAR(255) NOT NULL,
    genero VARCHAR(255) NOT NULL,
    editora VARCHAR(255) NOT NULL,
    ano INT NOT NULL,
    quantidade INT DEFAULT 0
);

CREATE TABLE alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_completo VARCHAR(255) NOT NULL,
    RA VARCHAR(20) NOT NULL,
    sala VARCHAR(20) NOT NULL,
    data_retirada DATE NOT NULL,
    data_devolucao DATE NOT NULL,
    livro_id INT,
    FOREIGN KEY (livro_id) REFERENCES livros(id)
);

``sql

4. Edite as configurações do MySQL no arquivo `app.py` conforme necessário.

### Executando o Projeto

1. No terminal, navegue até o diretório do projeto.
2. Execute o comando: `python app.py`
3. Abra seu navegador e vá para `http://localhost:5000/` para acessar a aplicação.

### Funcionalidades

- Adicionar livros
- Pesquisar livros por título ou autor
- Editar quantidade de livros
- Excluir livros da biblioteca

### Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para enviar pull requests ou reportar problemas.

### Autor

Felipe Oliveira Silva
Guilherme Arlindo Dantas da Silva
Sarah de Jesus Silva
Luana Vitoria Cardia de Oliveira

### Licença

Este projeto está licenciado sob a [Licença XYZ](link-da-licenca).
