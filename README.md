# 🖥️ Quadro Branco Colaborativo em Tempo Real

Este projeto foi desenvolvido como parte da disciplina de **Sistemas Distribuídos** (SIN142), ministrada pelo Prof. Dr. Pedro Damaso na **Universidade Federal de Viçosa – Campus Rio Paranaíba**, durante o período letivo 2025/1.

A proposta consiste na criação de um sistema distribuído com **comunicação em tempo real**, onde múltiplos usuários podem interagir simultaneamente em um quadro branco digital. A sincronização das ações entre os usuários é feita de forma assíncrona, com foco em **baixa latência**, **consistência de estado** e **controle de concorrência**.

## 🎯 Objetivos do Projeto

- Desenvolver uma aplicação distribuída interativa;
- Aplicar técnicas de **comunicação assíncrona** e **invocação remota**;
- Garantir **controle de concorrência**, **replicação**, **transações distribuídas** e **sincronização em tempo real**;
- Criar sessões colaborativas entre clientes com **estado consistente do quadro branco**.

## 🧩 Tecnologias Utilizadas

| Camada             | Tecnologia                                                  |
|--------------------|--------------------------------------------------------------|
| Interface gráfica  | [PySide6](https://doc.qt.io/qtforpython/)                   |
| Estilização        | QSS (Qt Style Sheets)                                       |
| Backend            | [Supabase](https://supabase.com)                            |
| Autenticação       | [supabase-py](https://github.com/supabase-community/supabase-py) |
| Desenho no canvas  | `QPainter` e eventos do Qt                                  |

## 🛠️ Funcionalidades Implementadas

- Gerenciamento de sessões (criação e entrada via ID)
- Desenho de formas simples (linhas, retângulos, círculos)
- Adição e movimentação de caixas de texto
- Sincronização das ações em tempo real entre os clientes
- Exclusão de objetos do quadro
- Autenticação de usuários via Supabase

## 🌐 Arquitetura

- **Servidor Central (via Supabase)**: atua como coordenador das sessões, recebendo e armazenando eventos, controlando concorrência e broadcast de ações.
- **Clientes (PySide6 + QPainter)**: interface gráfica interativa, comunicação via chamadas REST e eventos assíncronos.

## 💡 Conceitos Aplicados

- Comunicação indireta (cliente ↔ backend ↔ clientes)
- Controle de concorrência com travas otimizadas
- Invocação remota (via chamadas assíncronas Supabase)
- Replicação de estado entre usuários
- Modelo de consistência eventual com broadcast manual

## 📂 Estrutura do Projeto

```
📁 client/
├── 📁 services/
│   ├── __init__.py
│   ├── auth.py
│   ├── core_integration.py
│   ├── session_manager.py
│   └── supabase_client.py
├── 📁 ui/
│   └── __init__.py
├── __pycache__/  # arquivos compilados automaticamente (ignorar)
├── config/       # (adicione uma explicação se necessário)
README.md
run.py
run_visualizacao.py

```

## 🚀 Como executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-projeto.git
   cd seu-projeto
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure suas credenciais do Supabase (`.env` ou direto no código).

4. Execute a aplicação:
   ```bash
   python main.py
   ```

## 📌 Requisitos

- Python 3.8+
- Conta no [Supabase](https://supabase.com)
- Qt Designer (opcional, para editar a interface)

---

# Quadro Branco Colaborativo - Flask/Docker

Um quadro branco colaborativo em tempo real desenvolvido com Flask, Socket.IO e Supabase, containerizado com Docker.

## 🚀 Funcionalidades

- **Desenho colaborativo em tempo real**: Múltiplos usuários podem desenhar simultaneamente
- **Formas geométricas**: Quadrados, círculos, triângulos e texto
- **Seleção de cores**: Paleta de cores personalizável
- **Autenticação**: Sistema de login/registro com Supabase
- **Sincronização**: Todas as alterações são sincronizadas em tempo real
- **Interface responsiva**: Design moderno e intuitivo

## 🛠️ Tecnologias

- **Backend**: Flask (Python)
- **WebSockets**: Flask-SocketIO
- **Frontend**: HTML5 Canvas, JavaScript, CSS3
- **Banco de Dados**: Supabase (PostgreSQL)
- **Containerização**: Docker
- **Autenticação**: Supabase Auth

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Conta no Supabase (gratuita)

## 🔧 Configuração

### 1. Configurar Supabase

1. Crie uma conta em [supabase.com](https://supabase.com)
2. Crie um novo projeto
3. Configure as tabelas necessárias:

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

4. Configure as políticas de segurança (RLS) conforme necessário

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
SUPABASE_URL=sua_url_do_supabase
SUPABASE_API_KEY=sua_chave_api_do_supabase
FLASK_SECRET_KEY=sua_chave_secreta_flask
```

### 3. Executar com Docker

```bash
# Construir e executar com Docker Compose
docker-compose up --build

# Ou executar em background
docker-compose up -d --build
```

### 4. Executar Localmente (sem Docker)

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python app.py
```

## 🌐 Acesso

Após executar a aplicação, acesse:
- **Local**: http://localhost:5000
- **Docker**: http://localhost:5000

## 🌐 Acesso Externo na Rede

Após executar a aplicação, outros usuários na mesma rede podem acessar via:
- http://192.168.100.12:5000

Certifique-se de que o firewall permite conexões na porta 5000.

## 📁 Estrutura do Projeto

```
ProjetoQuadroColaborativo_SD/
├── app.py                 # Aplicação principal Flask
├── requirements.txt       # Dependências Python
├── Dockerfile            # Configuração Docker
├── docker-compose.yml    # Orquestração Docker
├── .dockerignore         # Arquivos ignorados no Docker
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── login.html        # Página de login
│   ├── register.html     # Página de registro
│   └── whiteboard.html   # Página principal do quadro
├── client/               # Código do cliente
│   └── services/         # Serviços
│       ├── auth.py       # Autenticação
│       └── supabase_client.py # Cliente Supabase
├── config/               # Configurações
│   └── settings.py       # Configurações do projeto
└── ws_client.py          # Cliente WebSocket
```

## 🔌 API Endpoints

### Autenticação
- `GET /login` - Página de login
- `POST /login` - Processar login
- `GET /register` - Página de registro
- `POST /register` - Processar registro
- `GET /logout` - Logout

### Quadro Branco
- `GET /` - Página principal (requer autenticação)
- `GET /api/shapes` - Listar formas
- `POST /api/shapes` - Criar forma
- `PUT /api/shapes/<id>` - Atualizar forma
- `DELETE /api/shapes/<id>` - Deletar forma
- `POST /api/clear` - Limpar quadro
- `GET /api/users/count` - Contagem de usuários

## 🎨 Funcionalidades do Quadro

### Ferramentas Disponíveis
- **Quadrado**: Desenhar quadrados
- **Círculo**: Desenhar círculos
- **Triângulo**: Desenhar triângulos
- **Texto**: Adicionar texto
- **Seletor de Cor**: Escolher cor das formas
- **Limpar**: Limpar todo o quadro
- **Excluir**: Remover forma selecionada

### Interações
- **Clique**: Selecionar forma
- **Arrastar**: Mover forma
- **Clique + Arrastar**: Criar nova forma

## 🔒 Segurança

- Autenticação obrigatória para acessar o quadro
- Validação de dados no servidor
- Proteção CSRF
- Sessões seguras

## 🚀 Deploy

### Docker Compose (Recomendado)
```bash
docker-compose up -d --build
```

### Docker Manual
```bash
# Construir imagem
docker build -t whiteboard-app .

# Executar container
docker run -p 5000:5000 whiteboard-app
```

### Produção
Para deploy em produção, considere:
- Usar um servidor WSGI como Gunicorn
- Configurar proxy reverso (Nginx)
- Usar variáveis de ambiente para configurações sensíveis
- Configurar SSL/TLS
- Implementar monitoramento e logs

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Se encontrar algum problema ou tiver dúvidas:
1. Verifique se todas as dependências estão instaladas
2. Confirme se as configurações do Supabase estão corretas
3. Verifique os logs da aplicação
4. Abra uma issue no repositório

## 🔄 Migração do PySide6

Este projeto foi migrado de PySide6 (aplicação desktop) para Flask (aplicação web) para permitir:
- Deploy em containers Docker
- Acesso via navegador web
- Melhor escalabilidade
- Facilidade de manutenção
- Compatibilidade com diferentes sistemas operacionais


