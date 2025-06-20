from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import json
import threading
import time
import os
from dotenv import load_dotenv
from client.services.auth import login, signup, logout, get_current_user
from client.services.supabase_client import get_supabase_client
from ws_client import start_ws_client

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*")

# Iniciar o cliente WebSocket em background
start_ws_client()

# Variáveis globais para armazenar dados do quadro
whiteboard_data = {
    'shapes': [],
    'users': set(),
    'session_id': str(uuid.uuid4())
}

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_route'))
    return render_template('whiteboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if login(email, password):
            user = get_current_user()
            session['user_id'] = user.id
            session['email'] = user.email
            # Garante que o usuário está na tabela whiteboard_sessions
            supabase = get_supabase_client()
            try:
                supabase.table("whiteboard_sessions").insert({"id": user.id, "name": user.email}).execute()
            except Exception as e:
                print("Aviso: usuário já existe em whiteboard_sessions ou erro ao inserir:", e)
            return redirect(url_for('index'))
        else:
            flash('Email ou senha inválidos', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_route():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if signup(email, password):
            flash('Conta criada com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login_route'))
        else:
            flash('Erro ao criar conta', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout_route():
    if 'user_id' in session:
        logout()
        session.clear()
    return redirect(url_for('login_route'))

@app.route('/api/shapes', methods=['GET'])
def get_shapes():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    supabase = get_supabase_client()
    try:
        # Filtra por session_id atual
        response = supabase.table("whiteboard_shapes") \
            .select("*") \
            .eq('session_id', whiteboard_data['session_id']) \
            .execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/shapes', methods=['POST'])
def create_shape():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    shape_data = {
        'id': str(uuid.uuid4()),
        'type': data.get('type'),
        'x': data.get('x'),
        'y': data.get('y'),
        'width': data.get('width', 40),
        'height': data.get('height', 40),
        'color': data.get('color', '#000000'),
        'text': data.get('text'),
        'font_size': data.get('font_size', 14),
        'user_id': session['user_id'],
        'session_id': whiteboard_data['session_id']
    }
    
    supabase = get_supabase_client()
    try:
        response = supabase.table("whiteboard_shapes").insert(shape_data).execute()
        socketio.emit('shape_created', shape_data, room=whiteboard_data['session_id'])
        return jsonify(shape_data)
    except Exception as e:
        print("ERRO AO INSERIR SHAPE:", e)
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/shapes/<shape_id>', methods=['PUT'])
def update_shape(shape_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    supabase = get_supabase_client()
    try:
        response = supabase.table("whiteboard_shapes").update(data).eq('id', shape_id).execute()
        socketio.emit('shape_updated', {'id': shape_id, **data}, room=whiteboard_data['session_id'])
        return jsonify(response.data[0] if response.data else {})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/shapes/<shape_id>', methods=['DELETE'])
def delete_shape(shape_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    supabase = get_supabase_client()
    try:
        response = supabase.table("whiteboard_shapes").delete().eq('id', shape_id).execute()
        socketio.emit('shape_deleted', {'id': shape_id}, room=whiteboard_data['session_id'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_canvas():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    supabase = get_supabase_client()
    try:
        response = supabase.table("whiteboard_shapes").delete().eq('session_id', whiteboard_data['session_id']).execute()
        socketio.emit('canvas_cleared', room=whiteboard_data['session_id'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/count')
def get_user_count():
    supabase = get_supabase_client()
    try:
        response = supabase.table("whiteboard_sessions").select("*", count="exact").execute()
        return jsonify({'count': response.count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Endpoint para verificar se a aplicação está funcionando"""
    return jsonify({
        'status': 'healthy',
        'message': 'Quadro Branco Colaborativo está funcionando!'
    })

@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        join_room(whiteboard_data['session_id'])
        whiteboard_data['users'].add(session['user_id'])
        emit('user_joined', {'user_id': session['user_id'], 'count': len(whiteboard_data['users'])}, room=whiteboard_data['session_id'])

@socketio.on('disconnect')
def handle_disconnect():
    if 'user_id' in session:
        leave_room(whiteboard_data['session_id'])
        whiteboard_data['users'].discard(session['user_id'])
        emit('user_left', {'user_id': session['user_id'], 'count': len(whiteboard_data['users'])}, room=whiteboard_data['session_id'])

if __name__ == '__main__':
    # Configurar host e porta baseado no ambiente
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Iniciando Quadro Branco Colaborativo em {host}:{port}")
    socketio.run(app, debug=debug, host=host, port=port, allow_unsafe_werkzeug=True) 