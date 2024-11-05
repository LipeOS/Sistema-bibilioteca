from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mysqldb import MySQL
import logging

app = Flask(__name__)

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'biblioteca'
app.config['MYSQL_HOST'] = 'localhost'

mysql = MySQL(app)

# Configurar logging para debug
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_book', methods=['POST'])
def add_book():
    titulo = request.form['titulo']
    autor = request.form['autor']
    genero = request.form['genero']
    editora = request.form['editora']
    ano = request.form['ano']
    quantidade = request.form['quantidade']

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO livros (titulo, autor, genero, editora, ano, quantidade) VALUES (%s, %s, %s, %s, %s, %s)', (titulo, autor, genero, editora, ano, quantidade))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('index'))

@app.route('/edit_book/<int:id>', methods=['POST'])
def edit_book(id):
    quantidade = request.form['quantidade']
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE livros SET quantidade = %s WHERE id = %s', (quantidade, id))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('all_books'))

@app.route('/delete_book/<int:id>', methods=['POST'])
def delete_book(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM livros WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('all_books'))

@app.route('/all_books')
def all_books():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    cursor.close()
    return render_template('all_books.html', livros=livros)

@app.route('/retirar_livros', methods=['GET', 'POST'])
def retirar_livros():
    if request.method == 'POST':
        livro_id = request.form['livro_id']
        quantidade = request.form['quantidade']
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT quantidade FROM livros WHERE id = %s', (livro_id,))
        livro = cursor.fetchone()
        if livro:
            quantidade_estoque = livro[0]
            if quantidade_estoque >= int(quantidade):
                nova_quantidade = quantidade_estoque - int(quantidade)
                cursor.execute('UPDATE livros SET quantidade = %s WHERE id = %s', (nova_quantidade, livro_id))
                mysql.connection.commit()
                cursor.close()
                return redirect(url_for('retirar_livros'))
            else:
                cursor.close()
                return "Quantidade solicitada maior do que a disponível.", 400
        else:
            cursor.close()
            return "Livro não encontrado.", 404
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    cursor.close()
    return render_template('retirar_livros.html', livros=livros)

@app.route('/escolher_livro/<int:livro_id>', methods=['GET', 'POST'])
def escolher_livro(livro_id):
    if request.method == 'POST':
        nome_completo = request.form['nome_completo']
        RA = request.form['RA']
        sala = request.form['sala']
        data_retirada = request.form['data_retirada']
        data_devolucao = request.form['data_devolucao']

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO alunos (nome_completo, RA, sala, data_retirada, data_devolucao, livro_id) VALUES (%s, %s, %s, %s, %s, %s)', 
                       (nome_completo, RA, sala, data_retirada, data_devolucao, livro_id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('livros_retidos'))

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM livros WHERE id = %s', (livro_id,))
    livro = cursor.fetchone()
    cursor.close()
    return render_template('formulario_retirada.html', livro=livro)

@app.route('/livros_retidos')
def livros_retidos():
    query = request.args.get('query', '')
    cursor = mysql.connection.cursor()
    if query:
        query = f"%{query}%"
        sql = """
            SELECT alunos.id, alunos.nome_completo, alunos.sala, alunos.RA, livros.titulo, alunos.data_devolucao
            FROM alunos
            JOIN livros ON alunos.livro_id = livros.id
            WHERE alunos.nome_completo LIKE %s OR livros.titulo LIKE %s
        """
        cursor.execute(sql, (query, query))
    else:
        sql = """
            SELECT alunos.id, alunos.nome_completo, alunos.sala, alunos.RA, livros.titulo, alunos.data_devolucao
            FROM alunos
            JOIN livros ON alunos.livro_id = livros.id
        """
        cursor.execute(sql)
    
    retirados = cursor.fetchall()
    cursor.close()
    return render_template('livros_retidos.html', retirados=retirados)



@app.route('/devolver_livro/<int:id>', methods=['POST'])
def devolver_livro(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM alunos WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('livros_retidos'))

@app.route('/search_books')
def search_books():
    query = request.args.get('query', '')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM livros WHERE titulo LIKE %s OR autor LIKE %s OR genero LIKE %s", 
                   (f'%{query}%', f'%{query}%', f'%{query}%'))
    livros = cursor.fetchall()
    cursor.close()
    return jsonify(livros)

if __name__ == '__main__':
    app.run(debug=True)
