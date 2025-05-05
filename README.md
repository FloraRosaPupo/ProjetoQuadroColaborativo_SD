
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


