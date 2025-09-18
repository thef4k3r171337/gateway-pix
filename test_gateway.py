#!/usr/bin/env python3
"""
Script de teste para o Gateway PIX
"""

import requests
import json
import time

# Configuração
BASE_URL = "http://localhost:5000"  # Mude para sua URL do Render quando necessário

def test_health():
    """Testar health check"""
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check OK")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def create_api_key():
    """Criar chave de API"""
    print("\n🔑 Criando chave de API...")
    try:
        response = requests.post(f"{BASE_URL}/admin/create_api_key", 
                               json={"client_name": "Teste Automatico"})
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Chave criada: {data['secret_key'][:20]}...")
            return data['secret_key']
        else:
            print(f"❌ Erro ao criar chave: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def test_auth_required():
    """Testar se autenticação é obrigatória"""
    print("\n🔒 Testando autenticação obrigatória...")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/charges", 
                               json={"amount": 1000, "description": "teste"})
        if response.status_code == 401:
            print("✅ Autenticação obrigatória funcionando")
            return True
        else:
            print(f"⚠️ Problema na autenticação: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def create_charge(api_key):
    """Criar cobrança PIX"""
    print("\n💳 Criando cobrança PIX...")
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "amount": 500,  # R$ 5,00
            "description": "Teste automatico do gateway"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/charges", 
                               json=data, headers=headers)
        
        if response.status_code == 201:
            charge = response.json()
            print(f"✅ Cobrança criada: {charge['id']}")
            print(f"   Status: {charge['status']}")
            print(f"   Valor: R$ {charge['amount']/100:.2f}")
            return charge['id']
        else:
            print(f"❌ Erro ao criar cobrança: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def get_charge(api_key, charge_id):
    """Consultar cobrança"""
    print(f"\n📊 Consultando cobrança {charge_id}...")
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{BASE_URL}/api/v1/charges/{charge_id}", 
                              headers=headers)
        
        if response.status_code == 200:
            charge = response.json()
            print(f"✅ Consulta realizada:")
            print(f"   ID: {charge['id']}")
            print(f"   Status: {charge['status']}")
            print(f"   Descrição: {charge['description']}")
            return True
        else:
            print(f"❌ Erro na consulta: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("🚀 Iniciando testes do Gateway PIX\n")
    
    # Teste 1: Health check
    if not test_health():
        print("❌ Aplicação não está respondendo")
        return
    
    # Teste 2: Autenticação obrigatória
    test_auth_required()
    
    # Teste 3: Criar chave de API
    api_key = create_api_key()
    if not api_key:
        print("❌ Não foi possível criar chave de API")
        return
    
    # Teste 4: Criar cobrança
    charge_id = create_charge(api_key)
    if not charge_id:
        print("❌ Não foi possível criar cobrança")
        return
    
    # Teste 5: Consultar cobrança
    get_charge(api_key, charge_id)
    
    print("\n🎉 Todos os testes concluídos!")
    print(f"\n📋 Informações para uso:")
    print(f"   Base URL: {BASE_URL}")
    print(f"   API Key: {api_key}")
    print(f"   Charge ID: {charge_id}")

if __name__ == "__main__":
    main()
