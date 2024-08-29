from flask import Flask, render_template, request, session, redirect, url_for
import psycopg2

conexao = psycopg2.connect(database="trabalho",
                           host="localhost",
                           user="postgres",
                           password="12345",
                           port="5432")

app = Flask(__name__)
app.secret_key = 'tanto_faz'

@app.route('/')
def home_page():
    if 'loggedin' in session:
        return render_template('home_page.html')
    return redirect(url_for('login'))

@app.route('/cadastra_usuario', methods=['POST', 'GET'])
def cadastra_usuario():
    nome_usuario = request.form.get('nome_usuario')
    senha_usuario = request.form.get('senha_usuario')
    
    if request.method == 'POST' and len(nome_usuario) > 0 and len(senha_usuario) > 0:
        
        try:
            cur = conexao.cursor()
            sql = 'SELECT * FROM usuario WHERE nome_usuario = %s'
            cur.execute(sql, (nome_usuario,))
            
            account = cur.fetchone()

            if account:
                print('Essa conta já existe')
            else:
                sql = "INSERT INTO usuario (nome_usuario, senha_usuario) VALUES (%s, %s)"
                cur.execute(sql, (nome_usuario, senha_usuario))
                conexao.commit()
                cur.close()

                print("Você foi registrado")
                
                return redirect(url_for('login'))
            
        except Exception as e:
            print(f"Ocorreu um erro ao cadastrar o usuário: {str(e)}")
    else:
        print('Todos os campos são obrigatórios')

    return render_template('cadastra_usuario.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    nome_usuario = request.form.get('login_usuario')
    senha_usuario = request.form.get('login_senha')

    if request.method == 'POST' and len(nome_usuario) > 0 and len(senha_usuario) > 0:
        
        try:
            cur = conexao.cursor()
            sql = 'SELECT * FROM usuario WHERE nome_usuario = %s'
            cur.execute(sql, (nome_usuario,))
            account = cur.fetchone()

            if account:
                senha = account[2]
                if senha_usuario == senha:
                    session['loggedin'] = True
                    session['nome_usuario'] = nome_usuario
                    return redirect(url_for('home_page'))
                else:
                    print('Senha Incorreta!')
            else:
                print('Nome de usuário não encontrado')

        except Exception as e:
            print(f"Ocorreu um erro: {str(e)}")
    else:
        print('Todos os campos são obrigatórios')

    return render_template('login.html')

@app.route('/cadastra_livro', methods=['POST', 'GET'])
def cadastra_livro():
    titulo = request.form.get('titulo')
    ano = request.form.get('ano')
    genero = request.form.get('genero')
    id_autor = request.form.get('id_autor')

    if 'loggedin' in session:
        if request.method == 'POST' and len(titulo) > 0 and len(ano) > 0 and len(genero) > 0 and len(id_autor) > 0:
            
            try:
                
                cur = conexao.cursor()
                    
                sql = 'SELECT id FROM autor WHERE id = %s'
                cur.execute(sql, (id_autor,))
                autor_existente = cur.fetchone()

                if autor_existente:
                    sql = """
                    INSERT INTO livro (titulo, ano, genero, autor_id)
                    VALUES (%s, %s, %s, %s)
                    """
                    cur.execute(sql, (titulo, ano, genero, id_autor))
                    conexao.commit()
                    cur.close()

                    print("Livro cadastrado com sucesso")

                    return redirect(url_for('home_page'))
                else:
                    print(f"Autor com id {id_autor} não encontrado")

            except Exception as e:
                print(f"Ocorreu um erro ao cadastrar o livro: {str(e)}")
        else:
            print('Todos os campos são obrigatórios')

        return render_template('cadastra_livro.html')
    
    return redirect(url_for('login'))

@app.route('/cadastra_autor', methods=['POST', 'GET'])
def cadastra_autor():
    nome = request.form.get('nome_autor')
    nacionalidade = request.form.get('nacionalidade')
    data_nascimento = request.form.get('data_nascimento')

    if 'loggedin' in session:
        if request.method == 'POST' and len(nome) > 0 and len(nacionalidade) > 0 and len(data_nascimento) > 0:
            
            try:
                cur = conexao.cursor()
                sql = """
                INSERT INTO autor (nome, nacionalidade, data_nascimento)
                VALUES (%s, %s, %s)
                """
                cur.execute(sql, (nome, nacionalidade, data_nascimento))
                conexao.commit()
                cur.close()

                print("Autor cadastrado com sucesso")

                return redirect(url_for('home_page'))
            
            except Exception as e:
                print(f"Ocorreu um erro ao cadastrar o autor: {str(e)}")
        else:
            print('Todos os campos são obrigatórios')

        return render_template('cadastrar_autor.html')
    
    return redirect(url_for('login'))

@app.route('/autores')
def lista_autores():
    if 'loggedin' in session:
        try:
            cur = conexao.cursor()
            sql = 'SELECT id, nome FROM autor'
            cur.execute(sql)
            autores = cur.fetchall()
            cur.close()

            return render_template('lista_autores.html', autores=autores)
        
        except Exception as e:
            print(f"Ocorreu um erro ao listar os autores: {str(e)}")
    
    return redirect(url_for('login'))

@app.route('/autor/<int:autor_id>', methods=['GET', 'POST'])
def detalhes_autor(autor_id):
    if 'loggedin' in session:
        if request.method == 'POST':
            try:
                cur = conexao.cursor()
                sql = 'DELETE FROM autor WHERE id = %s'
                cur.execute(sql, (autor_id,))
                conexao.commit()
                cur.close()

                print('Autor deletado com sucesso!')

                return redirect(url_for('lista_autores'))
            
            except Exception as e:
                print(f'Ocorreu um erro ao deletar o autor: {str(e)}')

        try:
            cur = conexao.cursor()
            sql = 'SELECT * FROM autor WHERE id = %s'
            cur.execute(sql, (autor_id,))
            autor = cur.fetchone()
            cur.close()

            if autor:
                return render_template('detalhes_autor.html', autor=autor)
            else:
                return 'Autor não encontrado', 404
            
        except Exception as e:
            print(f'Ocorreu um erro ao buscar os detalhes do autor: {str(e)}')
    
    return redirect(url_for('login'))

        
@app.route('/livros')
def lista_livros():
    if 'loggedin' in session:
        try:
            cur = conexao.cursor()
            sql = 'SELECT id, titulo FROM livro'
            cur.execute(sql)
            livros = cur.fetchall()
            cur.close()

            return render_template('lista_livros.html', livros=livros)
        
        except Exception as e:
            print(f'Ocorreu um erro ao listar os livros: {str(e)}')
    
    return redirect(url_for('login'))

@app.route('/livro/<int:livro_id>', methods=['GET', 'POST'])
def detalhes_livro(livro_id):
    if 'loggedin' in session:
        if request.method == 'POST':
            try:
                cur = conexao.cursor()
                sql = 'DELETE FROM livro WHERE id = %s'
                cur.execute(sql, (livro_id,))
                conexao.commit()
                cur.close()

                print('Livro deletado com sucesso!')

                return redirect(url_for('lista_livros'))
            
            except Exception as e:
                print(f'Ocorreu um erro ao deletar o livro: {str(e)}')

        try:
            cur = conexao.cursor()
            sql = 'SELECT * FROM livro WHERE id = %s'
            cur.execute(sql, (livro_id,))
            livro = cur.fetchone()
            cur.close()

            if livro:
                return render_template('detalhes_livro.html', livro=livro)
            else:
                return 'Livro não encontrado', 404
            
        except Exception as e:
            print(f'Ocorreu um erro ao buscar os detalhes do livro: {str(e)}')
    
    return redirect(url_for('login'))
    
@app.route('/livro/editar/<int:livro_id>', methods=['GET', 'POST'])
def editar_livro(livro_id):
    titulo = request.form.get('titulo')
    ano = request.form.get('ano')
    genero = request.form.get('genero')
    autor_id = request.form.get('autor_id')

    if 'loggedin' in session:
        if request.method == 'POST' and len(titulo) > 0 and len(ano) > 0 and len(genero) > 0 and len(autor_id) > 0:
            
            try:
                cur = conexao.cursor()
                sql = '''
                UPDATE livro
                SET titulo = %s, genero = %s, autor_id = %s, ano = %s
                WHERE id = %s
                '''
                cur.execute(sql, (titulo, genero, autor_id, ano, livro_id))
                conexao.commit()
                cur.close()

                print('Livro atualizado com sucesso!')

                return redirect(url_for('detalhes_livro', livro_id=livro_id))
            
            except Exception as e:
                print(f'Ocorreu um erro ao atualizar o livro: {str(e)}')
        else:
            print('Todos os campos são obrigatórios')

        try:
            cur = conexao.cursor()
            sql = 'SELECT * FROM livro WHERE id = %s'
            cur.execute(sql, (livro_id,))
            livro = cur.fetchone()
            cur.close()

            if livro:
                return render_template('editar_livro.html', livro=livro)
            else:
                return 'Livro não encontrado', 404
            
        except Exception as e:
            print(f'Ocorreu um erro ao buscar os detalhes do livro: {str(e)}')
    
    return redirect(url_for('login'))

@app.route('/autor/editar/<int:autor_id>', methods=['GET', 'POST'])
def editar_autor(autor_id):
    nome = request.form.get('nome_autor')
    nacionalidade = request.form.get('nacionalidade')
    data_nascimento = request.form.get('data_nascimento')

    if 'loggedin' in session:
        if request.method == 'POST' and len(nome) > 0 and len(nacionalidade) > 0 and len(data_nascimento) > 0:
            try:
                cur = conexao.cursor()
                sql = '''
                UPDATE autor
                SET nome = %s, nacionalidade = %s, data_nascimento = %s
                WHERE id = %s
                '''
                cur.execute(sql, (nome, nacionalidade, data_nascimento, autor_id))
                conexao.commit()
                cur.close()

                print('Autor atualizado com sucesso!')

                return redirect(url_for('detalhes_autor', autor_id=autor_id))
            
            except Exception as e:
                print(f'Ocorreu um erro ao atualizar o autor: {str(e)}')
        else:
            print('Todos os campos são obrigatórios')

        try:
            cur = conexao.cursor()
            sql = 'SELECT * FROM autor WHERE id = %s'
            cur.execute(sql, (autor_id,))
            autor = cur.fetchone()
            cur.close()

            if autor:
                return render_template('editar_autor.html', autor=autor)
            else:
                return 'Autor não encontrado', 404
            
        except Exception as e:
            print(f'Ocorreu um erro ao buscar os detalhes do autor: {str(e)}')
            
    return redirect(url_for('login'))