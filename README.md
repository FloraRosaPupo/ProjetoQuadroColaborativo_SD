# Quadro Branco Colaborativo

Projeto acadêmico de Sistemas Distribuídos (UFV–Rio Paranaíba, 2025/1): interface desktop para autenticação, sessões e desenho compartilhado.

## Stack e organização
Python, PySide6, Supabase e websocket-client.

Mantida a separação entre `client/ui`, `client/services` e o worker de comunicação. É uma aplicação desktop coesa; criar camadas de MVVM vazias não melhora essa fronteira. O cliente Supabase é carregado sob demanda e a integração aceita substituição nos testes.

## Executar
Requer Python 3.11+ e um projeto Supabase com o esquema e as políticas de acesso correspondentes à aplicação.

```sh
git clone https://github.com/FloraRosaPupo/ProjetoQuadroColaborativo_SD.git
cd ProjetoQuadroColaborativo_SD
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

Antes de executar, defina `SUPABASE_URL` e `SUPABASE_KEY` no ambiente do terminal. `.env.example` documenta os nomes; o programa não carrega `.env` automaticamente. `WHITEBOARD_WS_URL` permite trocar o servidor de métricas. Use somente chave pública anon/publishable no cliente e configure RLS no Supabase.

## Testes
```sh
python -m unittest discover -s tests -v
```
Os testes de contagem e falha de comunicação não exigem Qt, conta Supabase ou rede. A CI executa esses testes; a interface e o serviço remoto exigem validação integrada separada.

## Limitações e configuração externa
O repositório não inclui migrações SQL para reconstruir o backend. A contagem em `core_integration.py` estima participantes que desenharam, não presença online. O protocolo de métricas em `ws_client.py` conserva os campos do servidor original; sua contagem de sessões não deve ser interpretada como presença de usuários.

Uma chave privilegiada estava presente em `config/settings.py`: ela foi removida da versão atual, mas precisa ser revogada/rotacionada pelo proprietário no Supabase, pois permanece no histórico público.

## Licença
Não há licença de distribuição definida neste repositório.


## Funcionalidades

- Autenticação.
- desenho compartilhado.
- envio de métricas de sessões.


## Organização e manutenção

Mantida a separação entre `client/ui`, `client/services` e o worker de comunicação. É uma aplicação desktop coesa; criar camadas de MVVM vazias não melhora essa fronteira. O cliente Supabase é carregado sob demanda e a integração aceita substituição nos testes.

Veja [a revisão de desenvolvimento](docs/REVISAO.md) para decisões, testes e limites, e [o guia de contribuição](CONTRIBUTING.md) para o fluxo de manutenção.
