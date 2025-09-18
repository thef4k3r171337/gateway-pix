import os
import sqlite3
import secrets
import requests
from datetime import datetime
from functools import wraps
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configurações da API externa
CLIENT_ID = os.environ.get('CLIENT_ID', 'iagohotpay(hot)_6656FA84')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET', '4df7c31cad3efc3edadb61eeba0b79fb6bc4c2eef93c11d6e0860589c8fb1315c9cec04d52e633e6b9f9f38f25f2e89f9bc0')

# Inicializar banco de dados
def init_db():
    conn = sqlite3.connect('gateway.db')
    cursor = conn.cursor()
    
    # Tabela de transações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            qr_code_url TEXT,
            pix_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de chaves de API
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_id TEXT UNIQUE NOT NULL,
            secret_key TEXT UNIQUE NOT NULL,
            client_name TEXT NOT NULL,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Autenticação na API externa
def authenticate():
    try:
        response = requests.post('https://api.the-key.club/api/auth/login', 
                               json={'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET})
        if response.status_code == 200:
            return response.json().get('token')
        return None
    except:
        return None

# Middleware de autenticação
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'API key required'}), 401
        
        api_key = auth_header.replace('Bearer ', '')
        
        conn = sqlite3.connect('gateway.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM api_keys WHERE secret_key = ? AND active = 1", (api_key,))
        key_data = cursor.fetchone()
        conn.close()
        
        if not key_data:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Criar depósito PIX
def create_pix_deposit(token, amount, description):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'amount': amount,
            'external_id': f'gw_{secrets.token_hex(8)}',
            'clientCallbackUrl': f"{os.environ.get('BASE_URL', 'https://gateway-pix.onrender.com')}/callback",
            'payer': {
                'name': 'Cliente Gateway',
                'email': 'cliente@gateway.com',
                'document': '12345678901'
            },
            'description': description
        }
        
        response = requests.post('https://api.the-key.club/api/payments/deposit', 
                               json=data, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            return {
                'transaction_id': result.get('transaction_id'),
                'pix_qr_code': result.get('pix_qr_code'),
                'pix_key': result.get('pix_key')
            }
        return None
    except:
        return None

# Rotas da API

@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gateway PIX API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .header { text-align: center; color: #2c3e50; }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { color: #27ae60; font-weight: bold; }
            .url { color: #3498db; }
            .status { color: #e74c3c; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Gateway PIX API</h1>
            <p><span class="status">ONLINE</span> | Versão 3.0</p>
        </div>
        
        <h2>📋 Endpoints Disponíveis:</h2>
        
        <div class="endpoint">
            <span class="method">POST</span> <span class="url">/admin/create_api_key</span><br>
            <small>Criar nova chave de API</small>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <span class="url">/api/v1/charges</span><br>
            <small>Criar cobrança PIX (requer autenticação)</small>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/api/v1/charges/{id}</span><br>
            <small>Consultar status da cobrança (requer autenticação)</small>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/health</span><br>
            <small>Health check do serviço</small>
        </div>
        
        <h2>🔑 Como usar:</h2>
        <ol>
            <li>Crie uma chave de API usando <code>/admin/create_api_key</code></li>
            <li>Use a chave no header: <code>Authorization: Bearer sk_live_...</code></li>
            <li>Crie cobranças PIX usando <code>/api/v1/charges</code></li>
        </ol>
        
        <p><small>Gateway PIX - Processamento de pagamentos instantâneos</small></p>
    </body>
    </html>
    '''
    return html

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Gateway PIX',
        'version': '3.0',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/admin/create_api_key', methods=['POST'])
def create_api_key():
    try:
        data = request.get_json() or {}
        client_name = data.get('client_name', 'Cliente Padrão')
        
        # Gerar chaves
        key_id = f"pk_live_{secrets.token_urlsafe(16)}"
        secret_key = f"sk_live_{secrets.token_urlsafe(32)}"
        
        # Salvar no banco
        conn = sqlite3.connect('gateway.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO api_keys (key_id, secret_key, client_name) VALUES (?, ?, ?)",
            (key_id, secret_key, client_name)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'key_id': key_id,
            'secret_key': secret_key,
            'client_name': client_name,
            'created_at': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/charges', methods=['POST'])
@require_api_key
def create_charge():
    try:
        data = request.get_json()
        
        if not data or not data.get('amount') or not data.get('description'):
            return jsonify({'error': 'amount and description are required'}), 400
        
        # Obter token da API externa
        token = authenticate()
        if not token:
            return jsonify({'error': 'External API authentication failed'}), 500
        
        # Converter centavos para reais se necessário
        amount = data['amount']
        if amount > 100:
            amount = amount / 100
        
        # Criar depósito PIX
        pix_data = create_pix_deposit(token, amount, data['description'])
        if not pix_data:
            return jsonify({'error': 'Failed to create PIX deposit'}), 500
        
        # Salvar no banco
        conn = sqlite3.connect('gateway.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (transaction_id, amount, description, status, qr_code_url, pix_code) VALUES (?, ?, ?, ?, ?, ?)",
            (pix_data['transaction_id'], amount, data['description'], 'pending', pix_data['pix_qr_code'], pix_data['pix_key'])
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'id': pix_data['transaction_id'],
            'status': 'pending',
            'amount': data['amount'],
            'description': data['description'],
            'pix_qr_code': pix_data['pix_qr_code'],
            'pix_copy_paste': pix_data['pix_key'],
            'created_at': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/charges/<transaction_id>', methods=['GET'])
@require_api_key
def get_charge(transaction_id):
    try:
        conn = sqlite3.connect('gateway.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,))
        transaction = cursor.fetchone()
        conn.close()
        
        if not transaction:
            return jsonify({'error': 'Charge not found'}), 404
        
        return jsonify({
            'id': transaction[0],
            'amount': int(transaction[1] * 100),
            'description': transaction[2],
            'status': transaction[3],
            'created_at': transaction[6] if len(transaction) > 6 else datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/callback', methods=['POST'])
def callback():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        transaction_id = data.get('transaction_id')
        status = data.get('status')
        
        if transaction_id and status == 'COMPLETED':
            conn = sqlite3.connect('gateway.db')
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE transactions SET status = ? WHERE transaction_id = ?",
                ('paid', transaction_id)
            )
            conn.commit()
            conn.close()
        
        return jsonify({'message': 'Callback processed'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

# Inicializar banco ao iniciar a aplicação
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
