from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
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

@app.route('/admin', methods=['GET'])
def admin_access():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT ID_PROD, NOME_PROD, SECAO, VALOR, DESCRICAO FROM TB_PRODUTOS")
    produtos = cursor.fetchall()

    cursor.execute("SELECT ID, NOME, CPF, TELEFONE, EMAIL FROM TB_CLIENTES")
    clientes = cursor.fetchall()

    conn.close()
    return render_template('admin.html', produtos=produtos, clientes=clientes)

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

@app.route('/editar_produto/<int:id_prod>', methods=['GET', 'POST'])
def editar_produto(id_prod):
    if request.method == 'POST':
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
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TB_PRODUTOS WHERE ID_PROD = ?", id_prod)
        produto = cursor.fetchone()
        conn.close()

        return render_template('editar_produto.html', produto=produto)

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
    if cursor.fetchone():
        flash('CPF já cadastrado!')
        conn.close()
        return redirect(url_for('admin_access'))

    cursor.execute("INSERT INTO TB_CLIENTES (NOME, TELEFONE, EMAIL, GENERO, CPF, IDADE, CEP, ENDERECO) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (nome, telefone, email, genero, cpf, idade, cep, endereco))
    conn.commit()
    conn.close()
    flash('Cliente adicionado com sucesso!')
    return redirect(url_for('admin_access'))

@app.route('/excluir_cliente/<int:id>', methods=['POST'])
def excluir_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM TB_CLIENTES WHERE ID = ?", id)
    conn.commit()
    conn.close()
    flash('Cliente excluído com sucesso!')
    return redirect(url_for('admin_access'))

@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        email = request.form['email']
        genero = request.form['genero']
        cpf = request.form['cpf']
        idade = request.form['idade']
        cep = request.form['cep']
        endereco = request.form['endereco']

        cursor.execute(
            "UPDATE TB_CLIENTES SET NOME = ?, TELEFONE = ?, EMAIL = ?, GENERO = ?, CPF = ?, IDADE = ?, CEP = ?, ENDERECO = ? WHERE ID = ?",
            (nome, telefone, email, genero, cpf, idade, cep, endereco, id)
        )
        conn.commit()
        conn.close()

        flash('Cliente atualizado com sucesso!')
        return redirect(url_for('admin_access'))

    else:
        cursor.execute("SELECT * FROM TB_CLIENTES WHERE ID = ?", id)
        cliente = cursor.fetchone()
        conn.close()

        return render_template('editar_cliente.html', cliente=cliente)

# Rota para exibir o produto detalhado
@app.route('/produto/<int:id_prod>', methods=['GET'])
def produto(id_prod):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TB_PRODUTOS WHERE ID_PROD = ?", (id_prod,))
    produto = cursor.fetchone()
    conn.close()

    if produto:
        return jsonify({
            'ID_PROD': produto.ID_PROD,
            'NOME_PROD': produto.NOME_PROD,
            'FABRICANTE': produto.FABRICANTE,
            'SECAO': produto.SECAO,
            'DESCRICAO': produto.DESCRICAO,
            'VALOR': produto.VALOR,
            'QNTD_ESTOQUE': produto.QNTD_ESTOQUE,
            'DT_VALIDADE': produto.DT_VALIDADE
        })
    else:
        return jsonify({'error': 'Produto não encontrado'}), 404
    
@app.before_request
def inicializar_carrinho():
    if 'carrinho' not in session:
        session['carrinho'] = []

@app.route('/adicionar_ao_carrinho', methods=['POST'])
def adicionar_ao_carrinho():
    product_id = request.json.get('id')
    # Adiciona o produto ao carrinho (com quantidade padrão de 1)
    session['carrinho'].append({'id': product_id, 'quantidade': 1})
    session.modified = True
    return jsonify({"message": "Produto adicionado ao carrinho!"})

@app.route('/carrinho')
def carrinho():
    conn = get_db_connection()
    cursor = conn.cursor()
    produtos_carrinho = []
    total_carrinho = 0

    # Calcula informações do carrinho com base na sessão
    for item in session['carrinho']:
        cursor.execute("SELECT ID_PROD, NOME_PROD, VALOR FROM TB_PRODUTOS WHERE ID_PROD = ?", (item['id'],))
        produto = cursor.fetchone()
        if produto:
            quantidade = item['quantidade']
            valor_total_produto = produto.VALOR * quantidade
            produtos_carrinho.append({
                'ID_PROD': produto.ID_PROD,
                'NOME_PROD': produto.NOME_PROD,
                'VALOR': produto.VALOR,
                'quantidade': quantidade,
                'total_produto': valor_total_produto
            })
            total_carrinho += valor_total_produto

    conn.close()
    return render_template('carrinho.html', produtos=produtos_carrinho, total_carrinho=total_carrinho)   

@app.route('/alterar_quantidade', methods=['POST'])
def alterar_quantidade():
    data = request.get_json()
    produto_id = data['id']
    quantidade = data['quantidade']
    
    # Lógica para alterar quantidade do produto no carrinho
    # Exemplo:
    # carrinho.alterar_quantidade(produto_id, quantidade)

    return jsonify({"success": True, "message": "Quantidade atualizada com sucesso."})

# Remover produto do carrinho
@app.route('/remover_produto', methods=['POST'])
def remover_produto():
    data = request.get_json()
    produto_id = data['id']
    
    # Lógica para remover produto do carrinho
    # Exemplo:
    # carrinho.remover_produto(produto_id)

    return jsonify({"success": True, "message": "Produto removido com sucesso."})

if __name__ == '__main__':
    app.run(debug=True)
