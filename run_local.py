#!/usr/bin/env python3
"""
Script para executar a aplicação Flask localmente
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def main():
    """Função principal para executar a aplicação"""
    print("🚀 Iniciando Quadro Branco Colaborativo...")
    
    # Verificar se as variáveis de ambiente estão configuradas
    required_vars = ['SUPABASE_URL', 'SUPABASE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Variáveis de ambiente necessárias não encontradas:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Crie um arquivo .env na raiz do projeto com:")
        print("SUPABASE_URL=sua_url_do_supabase")
        print("SUPABASE_API_KEY=sua_chave_api_do_supabase")
        print("FLASK_SECRET_KEY=sua_chave_secreta_flask")
        sys.exit(1)
    
    # Configurar variáveis de ambiente padrão se não estiverem definidas
    if not os.getenv('FLASK_SECRET_KEY'):
        os.environ['FLASK_SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    print("✅ Configurações carregadas com sucesso!")
    print("🌐 Acesse: http://localhost:5000")
    print("⏹️  Para parar, pressione Ctrl+C")
    print("-" * 50)
    
    # Importar e executar a aplicação
    try:
        from app import app, socketio
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("💡 Certifique-se de que todas as dependências estão instaladas:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao executar a aplicação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 