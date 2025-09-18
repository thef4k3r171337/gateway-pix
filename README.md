# 🚀 Gateway PIX - API de Pagamentos

Gateway de pagamento PIX profissional com API RESTful completa.

## ✨ Funcionalidades

- ✅ **API RESTful** para criar e consultar cobranças PIX
- ✅ **Autenticação** com chaves de API seguras
- ✅ **Integração** com provedor PIX (the-key.club)
- ✅ **Banco de dados** SQLite para persistência
- ✅ **Webhooks** para confirmação de pagamentos
- ✅ **Interface web** para documentação
- ✅ **Deploy automático** no Render

## 🔧 Instalação Local

```bash
# Clonar repositório
git clone https://github.com/SEU_USUARIO/gateway-pix.git
cd gateway-pix

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python app.py
```

## 📋 Uso da API

### 1. Criar Chave de API

```bash
curl -X POST https://seu-gateway.onrender.com/admin/create_api_key \
  -H "Content-Type: application/json" \
  -d '{"client_name": "Minha Empresa"}'
```

### 2. Criar Cobrança PIX

```bash
curl -X POST https://seu-gateway.onrender.com/api/v1/charges \
  -H "Authorization: Bearer sk_live_SUA_CHAVE" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000,
    "description": "Pedido #12345"
  }'
```

### 3. Consultar Status

```bash
curl -X GET https://seu-gateway.onrender.com/api/v1/charges/ID_DA_COBRANCA \
  -H "Authorization: Bearer sk_live_SUA_CHAVE"
```

## 🌐 Deploy no Render

1. Conecte seu repositório GitHub ao Render
2. Crie um novo Web Service
3. Configure as variáveis de ambiente:
   - `CLIENT_ID`: Seu ID na API externa
   - `CLIENT_SECRET`: Seu secret na API externa
   - `BASE_URL`: URL do seu serviço no Render

## 📚 Endpoints

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `GET` | `/` | Documentação da API | ❌ |
| `GET` | `/health` | Health check | ❌ |
| `POST` | `/admin/create_api_key` | Criar chave de API | ❌ |
| `POST` | `/api/v1/charges` | Criar cobrança PIX | ✅ |
| `GET` | `/api/v1/charges/{id}` | Consultar cobrança | ✅ |

## 🔐 Segurança

- Chaves de API com formato `sk_live_...`
- Autenticação via Bearer Token
- Validação de dados de entrada
- Logs de auditoria

## 📞 Suporte

Para suporte técnico, abra uma issue no GitHub.
