
# 🖥️ Projeto com PySide6 + Supabase

Este projeto foi desenvolvido como parte da disciplina de **Sistemas Distribuídos** do curso de graduação da **Universidade Federal de Viçosa – Campus Rio Paranaíba**.

A aplicação possui uma interface gráfica moderna construída com **PySide6**, estilizada com **QSS**, e se comunica com um backend em **Supabase** para funcionalidades como autenticação e persistência de dados.

## 🔧 Tecnologias Utilizadas

| Camada             | Tecnologia                                                  |
|--------------------|--------------------------------------------------------------|
| Interface gráfica  | [PySide6](https://doc.qt.io/qtforpython/)                   |
| Estilização        | QSS (Qt Style Sheets)                                       |
| Backend            | [Supabase](https://supabase.com)                            |
| Autenticação       | [supabase-py](https://github.com/supabase-community/supabase-py) |
| Desenho no canvas  | `QPainter` e eventos do Qt                                  |

## ✨ Funcionalidades

- Interface gráfica responsiva com PySide6  
- Estilização avançada via QSS  
- Autenticação segura com Supabase  
- Integração em tempo real com banco de dados  
- Área de desenho interativa usando QPainter  

## 🚀 Como rodar o projeto

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-projeto.git
   cd seu-projeto
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  
   pip install -r requirements.txt
   ```

3. Configure suas credenciais do Supabase (ex: `.env` ou diretamente no código).

4. Rode a aplicação:
   ```bash
   python main.py
   ```

## 📂 Estrutura básica

```
📁 seu-projeto/
├── main.py
├── ui/
│   └── ...
├── assets/
│   └── styles.qss
├── services/
│   └── supabase_client.py
└── README.md
```

## 📌 Requisitos

- Python 3.8+
- Conta e projeto no [Supabase](https://supabase.com)
- Qt Designer (opcional para facilitar o design da interface)
