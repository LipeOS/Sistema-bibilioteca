# biblioteca_app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_mysqldb import MySQL
import logging

# Inicialização do app e configuração
app = Flask(__name__)
app.secret_key = 'some_secret_key'  # Necessário para usar flash messages

# Configurações do banco de dados
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'biblioteca'
app.config['MYSQL_HOST'] = 'localhost'

# Inicialização do MySQL
mysql = MySQL(app)

# Configuração do logging para depuração
logging.basicConfig(level=logging.DEBUG)

# --------------------------------------
# Função de ajuda para executar consultas
# --------------------------------------
def execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    cursor = mysql.connection.cursor()
    cursor.execute(query, params)
    result = None
    if fetch_one:
        result = cursor.fetchone()
    elif fetch_all:
        result = cursor.fetchall()
    if commit:
        mysql.connection.commit()
    cursor.close()
    return result

# --------------------------------------
# Rotas principais
# --------------------------------------

# Rota para página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para exibir todos os livros
@app.route('/all_books')
def all_books():
    livros = execute_query("SELECT * FROM livros", fetch_all=True)
    return render_template('all_books.html', livros=livros)

# --------------------------------------
# Rotas CRUD para livros
# --------------------------------------

# Adicionar um novo livro ao banco de dados
@app.route('/add_book', methods=['POST'])
def add_book():
    # Coleta de dados do formulário
    titulo = request.form['titulo']
    autor = request.form['autor']
    genero = request.form['genero']
    editora = request.form['editora']
    ano = request.form['ano']
    quantidade = request.form['quantidade']

    # Inserção no banco de dados
    execute_query(
        'INSERT INTO livros (titulo, autor, genero, editora, ano, quantidade) VALUES (%s, %s, %s, %s, %s, %s)',
        (titulo, autor, genero, editora, ano, quantidade), commit=True
    )
    return redirect(url_for('index'))

# Editar um livro existente
@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    if request.method == 'POST':
        # Atualização do livro com dados do formulário
        try:
            titulo = request.form['titulo']
            autor = request.form['autor']
            genero = request.form['genero']
            editora = request.form['editora']
            ano = request.form['ano']
            quantidade = request.form['quantidade']
            
            # Executa a atualização no banco
            execute_query(
                'UPDATE livros SET titulo = %s, autor = %s, genero = %s, editora = %s, ano = %s, quantidade = %s WHERE id = %s',
                (titulo, autor, genero, editora, ano, quantidade, id), commit=True
            )
            return redirect(url_for('all_books'))
        except KeyError as e:
            # Lida com campos faltantes
            flash(f"Erro: Campo {e.args[0]} faltando no formulário.", "danger")
            return redirect(url_for('edit_book', id=id))
    else:
        # Exibe o formulário de edição
        livro = execute_query('SELECT * FROM livros WHERE id = %s', (id,), fetch_one=True)
        return render_template('edit_book.html', livro=livro)

# Excluir um livro
@app.route('/delete_book/<int:id>', methods=['POST'])
def delete_book(id):
    execute_query('DELETE FROM livros WHERE id = %s', (id,), commit=True)
    return redirect(url_for('all_books'))

# --------------------------------------
# Rotas para operações de empréstimo
# --------------------------------------

# Rota para retirar livros
@app.route('/retirar_livros', methods=['GET', 'POST'])
def retirar_livros():
    if request.method == 'POST':
        livro_id = request.form['livro_id']
        quantidade = int(request.form['quantidade'])

        # Verifica e atualiza a quantidade no estoque
        livro = execute_query('SELECT quantidade FROM livros WHERE id = %s', (livro_id,), fetch_one=True)
        if livro:
            quantidade_estoque = livro[0]
            if quantidade_estoque >= quantidade:
                nova_quantidade = quantidade_estoque - quantidade
                execute_query('UPDATE livros SET quantidade = %s WHERE id = %s', (nova_quantidade, livro_id), commit=True)
                return redirect(url_for('retirar_livros'))
            else:
                return "Quantidade solicitada maior do que a disponível.", 400
        else:
            return "Livro não encontrado.", 404

    # Exibe lista de livros para retirada
    livros = execute_query("SELECT * FROM livros", fetch_all=True)
    return render_template('retirar_livros.html', livros=livros)

# Rota para escolher um livro e registrar o empréstimo
@app.route('/escolher_livro/<int:livro_id>', methods=['GET', 'POST'])
def escolher_livro(livro_id):
    if request.method == 'POST':
        # Coleta de dados do formulário de empréstimo
        nome_completo = request.form['nome_completo']
        RA = request.form['RA']
        sala = request.form['sala']
        data_retirada = request.form['data_retirada']
        data_devolucao = request.form['data_devolucao']

        # Registra o empréstimo no banco de dados
        execute_query(
            'INSERT INTO alunos (nome_completo, RA, sala, data_retirada, data_devolucao, livro_id) VALUES (%s, %s, %s, %s, %s, %s)',
            (nome_completo, RA, sala, data_retirada, data_devolucao, livro_id), commit=True
        )
        return redirect(url_for('livros_retidos'))

    # Exibe o formulário de empréstimo
    livro = execute_query('SELECT * FROM livros WHERE id = %s', (livro_id,), fetch_one=True)
    return render_template('formulario_retirada.html', livro=livro)

# Rota para listar livros emprestados
@app.route('/livros_retidos')
def livros_retidos():
    query = request.args.get('query', '')
    if query:
        query = f"%{query}%"
        sql = """
            SELECT alunos.id, alunos.nome_completo, alunos.sala, alunos.RA, livros.titulo, alunos.data_devolucao
            FROM alunos
            JOIN livros ON alunos.livro_id = livros.id
            WHERE alunos.nome_completo LIKE %s OR livros.titulo LIKE %s
        """
        retirados = execute_query(sql, (query, query), fetch_all=True)
    else:
        sql = """
            SELECT alunos.id, alunos.nome_completo, alunos.sala, alunos.RA, livros.titulo, alunos.data_devolucao
            FROM alunos
            JOIN livros ON alunos.livro_id = livros.id
        """
        retirados = execute_query(sql, fetch_all=True)
    return render_template('livros_retidos.html', retirados=retirados)

# Rota para devolver livro
@app.route('/devolver_livro/<int:id>', methods=['POST'])
def devolver_livro(id):
    execute_query('DELETE FROM alunos WHERE id = %s', (id,), commit=True)
    return redirect(url_for('livros_retidos'))

# --------------------------------------
# Rota de busca de livros (API)
# --------------------------------------

@app.route('/search_books')
def search_books():
    query = request.args.get('query', '')
    livros = execute_query(
        "SELECT * FROM livros WHERE titulo LIKE %s OR autor LIKE %s OR genero LIKE %s",
        (f'%{query}%', f'%{query}%', f'%{query}%'), fetch_all=True
    )
    return jsonify(livros)

# Inicia o servidor
if __name__ == '__main__':
    app.run(debug=True)
