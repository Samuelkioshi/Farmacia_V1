from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc

app = Flask(__name__)
app.secret_key = 'chave_secreta'  

conn_str = (
    "DRIVER={SQL Server};"
    "SERVER=Samuel;"
    "DATABASE=FARMACIA_DB;"
    "Trusted_Connection=yes;"
)

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT ID_PROD, NOME_PROD, FABRICANTE, DT_VALIDADE, QNTD_ESTOQUE, VALOR FROM TB_PRODUTOS")
    produtos = cursor.fetchall()

    cursor.execute("SELECT ID, NOME, TELEFONE, EMAIL, GENERO, CPF, IDADE, CEP, ENDERECO FROM TB_CLIENTE")
    clientes = cursor.fetchall()

    conn.close()
    return render_template('home.html', produtos=produtos, clientes=clientes)

@app.route('/adicionar_produto', methods=['POST'])
def adicionar_produto():
    nome = request.form['nome']
    fabricante = request.form['fabricante']
    dt_validade = request.form['dt_validade']
    qntd_estoque = request.form['qntd_estoque']
    valor = request.form['valor']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO TB_PRODUTOS (NOME_PROD, FABRICANTE, DT_VALIDADE, QNTD_ESTOQUE, VALOR) VALUES (?, ?, ?, ?, ?)",
                   (nome, fabricante, dt_validade, qntd_estoque, valor))
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

@app.route('/excluir_produto/<int:id_prod>', methods=['POST'])
def excluir_produto(id_prod):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM TB_PRODUTOS WHERE ID_PROD = ?", id_prod)
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

@app.route('/editar_produto/<int:id_prod>', methods=['POST'])
def editar_produto(id_prod):
    nome = request.form['nome']
    fabricante = request.form['fabricante']
    dt_validade = request.form['dt_validade']
    qntd_estoque = request.form['qntd_estoque']
    valor = request.form['valor']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE TB_PRODUTOS SET NOME_PROD = ?, FABRICANTE = ?, DT_VALIDADE = ?, QNTD_ESTOQUE = ?, VALOR = ? WHERE ID_PROD = ?",
                   (nome, fabricante, dt_validade, qntd_estoque, valor, id_prod))
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

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

    cursor.execute("SELECT CPF FROM TB_CLIENTE WHERE CPF = ?", cpf)
    cliente_existente = cursor.fetchone()

    if cliente_existente:
        flash('CPF já cadastrado!')
        conn.close()
        return redirect(url_for('home'))

    cursor.execute("INSERT INTO TB_CLIENTE (NOME, TELEFONE, EMAIL, GENERO, CPF, IDADE, CEP, ENDERECO) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (nome, telefone, email, genero, cpf, idade, cep, endereco))
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

@app.route('/excluir_cliente/<int:id_cliente>', methods=['POST'])
def excluir_cliente(id_cliente):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM TB_CLIENTE WHERE ID = ?", id_cliente)
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

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

    # Verifica se o CPF já está cadastrado em outro cliente
    cursor.execute("SELECT CPF FROM TB_CLIENTE WHERE CPF = ? AND ID <> ?", (cpf, id_cliente))
    cliente_existente = cursor.fetchone()

    if cliente_existente:
        flash('CPF já cadastrado!')
        conn.close()
        return redirect(url_for('home'))

    cursor.execute("UPDATE TB_CLIENTE SET NOME = ?, TELEFONE = ?, EMAIL = ?, GENERO = ?, CPF = ?, IDADE = ?, CEP = ?, ENDERECO = ? WHERE ID = ?",
                   (nome, telefone, email, genero, cpf, idade, cep, endereco, id_cliente))
    conn.commit()
    conn.close()

    # Adiciona uma mensagem flash para indicar que a atualização foi bem-sucedida
    flash('Atualizado!')

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
