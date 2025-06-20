# Estágio 1: Builder - Gera os arquivos gRPC
FROM python:3.11-slim as builder

WORKDIR /build

# Instala as ferramentas gRPC
RUN pip install grpcio-tools~=1.54.0

# Copia o arquivo .proto
COPY grpc_shapes.proto .

# Gera os arquivos Python a partir do .proto
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. grpc_shapes.proto


# Estágio 2: Final - A imagem da aplicação
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de dependências de runtime
COPY requirements.txt .

# Instalar dependências Python de runtime
RUN pip install --no-cache-dir -r requirements.txt

# Copiar os arquivos gRPC gerados do estágio 'builder'
COPY --from=builder /build/grpc_shapes_pb2.py .
COPY --from=builder /build/grpc_shapes_pb2_grpc.py .

# Copiar o restante do código da aplicação
COPY . .

# Expor porta
EXPOSE 5000

# Variáveis de ambiente
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Comando para executar a aplicação
CMD ["python", "app.py"] 