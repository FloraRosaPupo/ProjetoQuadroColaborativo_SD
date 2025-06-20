#!/bin/bash

# Script para build e execução do Quadro Branco Colaborativo com Docker

set -e

echo "🚀 Quadro Branco Colaborativo - Build Script"
echo "=============================================="

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se o Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado."
    echo "📝 Copiando arquivo de exemplo..."
    cp env.example .env
    echo "✅ Arquivo .env criado. Por favor, configure suas variáveis de ambiente:"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_API_KEY"
    echo "   - FLASK_SECRET_KEY"
    echo ""
    echo "💡 Edite o arquivo .env com suas configurações do Supabase"
    exit 1
fi

# Função para mostrar menu
show_menu() {
    echo ""
    echo "Escolha uma opção:"
    echo "1) Build e executar (foreground)"
    echo "2) Build e executar (background)"
    echo "3) Apenas build"
    echo "4) Parar containers"
    echo "5) Ver logs"
    echo "6) Limpar containers e imagens"
    echo "0) Sair"
    echo ""
    read -p "Digite sua opção: " choice
}

# Função para build e execução
build_and_run() {
    echo "🔨 Construindo imagem Docker..."
    docker-compose build
    
    if [ "$1" = "background" ]; then
        echo "🚀 Executando em background..."
        docker-compose up -d
        echo "✅ Aplicação iniciada em background!"
        echo "🌐 Acesse: http://localhost:5000"
        echo "📋 Para ver logs: ./build.sh"
    else
        echo "🚀 Executando em foreground..."
        echo "🌐 Acesse: http://localhost:5000"
        echo "⏹️  Para parar, pressione Ctrl+C"
        echo ""
        docker-compose up
    fi
}

# Função para parar containers
stop_containers() {
    echo "🛑 Parando containers..."
    docker-compose down
    echo "✅ Containers parados!"
}

# Função para ver logs
show_logs() {
    echo "📋 Mostrando logs..."
    docker-compose logs -f
}

# Função para limpar
cleanup() {
    echo "🧹 Limpando containers e imagens..."
    docker-compose down --rmi all --volumes --remove-orphans
    echo "✅ Limpeza concluída!"
}

# Menu principal
while true; do
    show_menu
    
    case $choice in
        1)
            build_and_run "foreground"
            break
            ;;
        2)
            build_and_run "background"
            break
            ;;
        3)
            echo "🔨 Construindo imagem Docker..."
            docker-compose build
            echo "✅ Build concluído!"
            ;;
        4)
            stop_containers
            ;;
        5)
            show_logs
            ;;
        6)
            cleanup
            ;;
        0)
            echo "👋 Até logo!"
            exit 0
            ;;
        *)
            echo "❌ Opção inválida. Tente novamente."
            ;;
    esac
done 