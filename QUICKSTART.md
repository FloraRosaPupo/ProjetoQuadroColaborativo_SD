# 🚀 Guia de Início Rápido

## Pré-requisitos

- Docker e Docker Compose instalados
- Conta no Supabase (gratuita)

## ⚡ Execução Rápida

### 1. Configurar Supabase

1. Acesse [supabase.com](https://supabase.com) e crie uma conta
2. Crie um novo projeto
3. Execute o SQL abaixo no SQL Editor:

```sql
-- Tabela para sessões de usuários
CREATE TABLE whiteboard_sessions (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela para formas do quadro
CREATE TABLE whiteboard_shapes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL,
    x FLOAT NOT NULL,
    y FLOAT NOT NULL,
    width FLOAT DEFAULT 40,
    height FLOAT DEFAULT 40,
    color TEXT DEFAULT '#000000',
    text TEXT,
    font_size INTEGER DEFAULT 14,
    user_id UUID REFERENCES auth.users(id),
    session_id UUID NOT NULL,
    clicked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

4. Copie a URL e API Key do seu projeto

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp env.example .env

# Editar o arquivo .env com suas configurações
```

### 3. Executar com Docker

```bash
# Usar o script automatizado (recomendado)
./build.sh

# Ou executar manualmente
docker-compose up --build
```

### 4. Acessar a Aplicação

Abra seu navegador e acesse: **http://localhost:5000**

## 🛠️ Execução Local (sem Docker)

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python run_local.py
```

## 📋 Comandos Úteis

```bash
# Parar containers
docker-compose down

# Ver logs
docker-compose logs -f

# Rebuild
docker-compose up --build

# Limpar tudo
docker-compose down --rmi all --volumes
```

## 🔧 Solução de Problemas

### Erro de Conexão com Supabase
- Verifique se as credenciais no `.env` estão corretas
- Confirme se as tabelas foram criadas no Supabase

### Erro de Porta em Uso
```bash
# Verificar portas em uso
netstat -tulpn | grep :5000

# Ou usar porta diferente
FLASK_PORT=5001 docker-compose up
```

### Erro de Permissão no Linux/Mac
```bash
chmod +x build.sh
```

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs: `docker-compose logs`
2. Confirme as configurações do Supabase
3. Teste a conexão: `curl http://localhost:5000/health`

## 🎯 Próximos Passos

Após a primeira execução:
1. Crie uma conta no sistema
2. Faça login
3. Comece a desenhar no quadro colaborativo! 