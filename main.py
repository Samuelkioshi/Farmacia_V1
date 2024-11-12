from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc

app = Flask(__name__)
app.secret_key = 'chave_secreta'

# Configuração da conexão com o banco de dados
conn_str = (
    "DRIVER={SQL Server};"
    "SERVER=Samuel;"
    "DATABASE=FARMACIA_DB;"
    "Trusted_Connection=yes;"
)

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn

# Rota da página inicial
@app.route('/')
def home():
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    cursor = conn.cursor()

    # Consulta produtos com base na pesquisa
    if search_query:
        cursor.execute("SELECT ID_PROD, NOME_PROD, FABRICANTE, DT_VALIDADE, QNTD_ESTOQUE, VALOR, SECAO FROM TB_PRODUTOS WHERE NOME_PROD LIKE ?", f'%{search_query}%')
    else:
        cursor.execute("SELECT ID_PROD, NOME_PROD, FABRICANTE, DT_VALIDADE, QNTD_ESTOQUE, VALOR, SECAO FROM TB_PRODUTOS")
    
    produtos = cursor.fetchall()

    # Consulta todos os clientes
    cursor.execute("SELECT ID, NOME, TELEFONE, EMAIL, GENERO, CPF, IDADE, CEP, ENDERECO FROM TB_CLIENTES")
    clientes = cursor.fetchall()

    conn.close()
    return render_template('home.html', produtos=produtos, clientes=clientes, search_query=search_query)

# Rota da página de administração
@app.route('/admin', methods=['GET'])
def admin_access():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Consulta todos os produtos
    cursor.execute("SELECT ID_PROD, NOME_PROD, SECAO, DESCRICAO FROM TB_PRODUTOS")
    produtos = cursor.fetchall()

    # Consulta todos os clientes
    cursor.execute("SELECT ID, NOME FROM TB_CLIENTES")
    clientes = cursor.fetchall()

    conn.close()
    return render_template('admin.html', produtos=produtos, clientes=clientes)

# Rotas para manipulação de produtos
@app.route('/adicionar_produto', methods=['POST'])
def adicionar_produto():
    nome = request.form['nome']
    fabricante = request.form['fabricante']
    dt_validade = request.form['dt_validade']
    qntd_estoque = request.form['qntd_estoque']
    valor = request.form['valor']
    secao = request.form['secao']
    descricao = request.form['descricao']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO TB_PRODUTOS (NOME_PROD, FABRICANTE, DT_VALIDADE, QNTD_ESTOQUE, VALOR, SECAO, DESCRICAO) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (nome, fabricante, dt_validade, qntd_estoque, valor, secao, descricao))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_access'))

@app.route('/excluir_produto/<int:id_prod>', methods=['POST'])
def excluir_produto(id_prod):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM TB_PRODUTOS WHERE ID_PROD = ?", id_prod)
    conn.commit()
    conn.close()

    return redirect(url_for('admin_access'))

@app.route('/editar_produto/<int:id_prod>', methods=['POST'])
def editar_produto(id_prod):
    nome_prod = request.form['nome_prod']
    fabricante = request.form['fabricante']
    dt_validade = request.form['dt_validade']
    qntd_estoque = request.form['qntd_estoque']
    valor = request.form['valor']
    secao = request.form['secao']
    descricao = request.form['descricao']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE TB_PRODUTOS SET NOME_PROD = ?, FABRICANTE = ?, DT_VALIDADE = ?, QNTD_ESTOQUE = ?, VALOR = ?, SECAO = ?, DESCRICAO = ? WHERE ID_PROD = ?",
        (nome_prod, fabricante, dt_validade, qntd_estoque, valor, secao, descricao, id_prod)
    )
    conn.commit()
    conn.close()

    flash('Produto atualizado com sucesso!')
    return redirect(url_for('admin_access'))


# Rotas para manipulação de clientes
@app.route('/adicionar_cliente', methods=['POST'])
def adicionar_cliente():
    nome = request.form['nome']
    telefone = request.form['telefone']
    email = request.form['email']
    genero = request.form['genero']
    cpf = request.form['cpf']
    idade = request.form['idade']
    cep = request.form['cep']
    endereco = request.form['endereco']
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT CPF FROM TB_CLIENTES WHERE CPF = ?", cpf)
    cliente_existente = cursor.fetchone()

    if cliente_existente:
        flash('CPF já cadastrado!')
        conn.close()
        return redirect(url_for('admin_access'))

    cursor.execute("INSERT INTO TB_CLIENTES (NOME, TELEFONE, EMAIL, GENERO, CPF, IDADE, CEP, ENDERECO) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (nome, telefone, email, genero, cpf, idade, cep, endereco))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_access'))

@app.route('/excluir_cliente/<int:id_cliente>', methods=['POST'])
def excluir_cliente(id_cliente):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM TB_CLIENTES WHERE ID = ?", id_cliente)
    conn.commit()
    conn.close()

    return redirect(url_for('admin_access'))

@app.route('/editar_cliente/<int:id_cliente>', methods=['POST'])
def editar_cliente(id_cliente):
    nome = request.form['nome']
    telefone = request.form['telefone']
    email = request.form['email']
    genero = request.form['genero']
    cpf = request.form['cpf']
    idade = request.form['idade']
    cep = request.form['cep']
    endereco = request.form['endereco']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT CPF FROM TB_CLIENTES WHERE CPF = ? AND ID <> ?", (cpf, id_cliente))
    cliente_existente = cursor.fetchone()

    if cliente_existente:
        flash('CPF já cadastrado!')
        conn.close()
        return redirect(url_for('admin_access'))

    cursor.execute("UPDATE TB_CLIENTES SET NOME = ?, TELEFONE = ?, EMAIL = ?, GENERO = ?, CPF = ?, IDADE = ?, CEP = ?, ENDERECO = ? WHERE ID = ?",
                   (nome, telefone, email, genero, cpf, idade, cep, endereco, id_cliente))
    conn.commit()
    conn.close()

    flash('Atualizado!')

    return redirect(url_for('admin_access'))

if __name__ == '__main__':
    app.run(debug=True)
