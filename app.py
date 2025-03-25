from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3, os
from docx import Document
from weasyprint import HTML

app = Flask(__name__)
app.secret_key = 'chave-secreta-supersegura'
DATABASE = 'contrato.db'
CONTRATO_DIR = 'contratos/gerados'

os.makedirs(CONTRATO_DIR, exist_ok=True)

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            endereco TEXT,
            objetivo TEXT,
            quem_assina TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS socios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER,
            nome TEXT,
            cpf TEXT,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        )""")

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'senha123':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Usuário ou senha incorretos'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('form.html')

@app.route('/criar', methods=['POST'])
@login_required
def criar():
    nome_empresa = request.form['nome_empresa']
    endereco = request.form['endereco']
    objetivo = request.form['objetivo']
    quem_assina = request.form['quem_assina']

    socios = []
    i = 0
    while True:
        nome = request.form.get(f'nome_socio_{i}')
        cpf = request.form.get(f'cpf_socio_{i}')
        if nome and cpf:
            socios.append((nome, cpf))
            i += 1
        else:
            break

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO empresas (nome, endereco, objetivo, quem_assina) VALUES (?, ?, ?, ?)",
                  (nome_empresa, endereco, objetivo, quem_assina))
        empresa_id = c.lastrowid
        for socio in socios:
            c.execute("INSERT INTO socios (empresa_id, nome, cpf) VALUES (?, ?, ?)",
                      (empresa_id, socio[0], socio[1]))
        conn.commit()

    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)
