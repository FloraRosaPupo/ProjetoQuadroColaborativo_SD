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
import redis
from flasgger import Swagger
from grpc_server import start_grpc_server_in_thread

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*")
swagger = Swagger(app)

# Iniciar o cliente WebSocket em background
start_ws_client()

# Variáveis globais para armazenar dados do quadro
whiteboard_data = {
    'shapes': [],
    'users': set(),
    'session_id': str(uuid.uuid4())
}

# Configuração do Redis
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
REDIS_CHANNEL = 'whiteboard_events'

def publish_event(event_type, data):
    message = json.dumps({'event_type': event_type, 'data': data})
    redis_client.publish(REDIS_CHANNEL, message)

def start_redis_listener(socketio):
    def listen():
        pubsub = redis_client.pubsub()
        pubsub.subscribe(REDIS_CHANNEL)
        for msg in pubsub.listen():
            if msg['type'] == 'message':
                try:
                    payload = json.loads(msg['data'])
                    event_type = payload['event_type']
                    data = payload['data']
                    # Propagar via SocketIO local
                    if event_type == 'shape_created':
                        socketio.emit('shape_created', data, room=data.get('session_id'))
                    elif event_type == 'shape_updated':
                        socketio.emit('shape_updated', data, room=data.get('session_id'))
                    elif event_type == 'shape_deleted':
                        socketio.emit('shape_deleted', data, room=data.get('session_id'))
                    elif event_type == 'canvas_cleared':
                        socketio.emit('canvas_cleared', room=data.get('session_id'))
                except Exception as e:
                    print('Erro ao processar mensagem do Redis:', e)
    thread = threading.Thread(target=listen, daemon=True)
    thread.start()

def log_event(session_id, user_id, event_type, shape_id=None, payload=None):
    supabase = get_supabase_client()
    event_data = {
        'session_id': session_id,
        'user_id': user_id,
        'event_type': event_type,
        'shape_id': shape_id,
        'payload': payload
    }
    try:
        supabase.table('whiteboard_events').insert(event_data).execute()
    except Exception as e:
        print(f"Erro ao registrar evento: {e}")

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
    """Cria uma nova forma
    ---
    tags:
      - Shapes
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            type:
              type: string
            x:
              type: number
            y:
              type: number
            width:
              type: number
            height:
              type: number
            color:
              type: string
            text:
              type: string
            font_size:
              type: integer
    responses:
      200:
        description: Forma criada
        schema:
          type: object
    """
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
        'session_id': whiteboard_data['session_id'],
        'version': 0
    }
    supabase = get_supabase_client()
    try:
        response = supabase.table("whiteboard_shapes").insert(shape_data).execute()
        # SAGA: registrar log externo
        try:
            os.makedirs('logs', exist_ok=True)
            with open('logs/distributed.log', 'a', encoding='utf-8') as f:
                f.write(f"CREATE {shape_data['id']} by {session['user_id']} in session {whiteboard_data['session_id']}\n")
        except Exception as log_exc:
            # Rollback: desfazer criação da forma
            supabase.table("whiteboard_shapes").delete().eq('id', shape_data['id']).execute()
            return jsonify({'error': 'Distributed log failed, rolled back shape creation', 'details': str(log_exc)}), 500
        # Publish para Redis
        publish_event('shape_created', shape_data)
        socketio.emit('shape_created', shape_data, room=whiteboard_data['session_id'])
        # Registrar evento
        log_event(whiteboard_data['session_id'], session['user_id'], 'create', shape_data['id'], shape_data)
        return jsonify(shape_data)
    except Exception as e:
        print("ERRO AO INSERIR SHAPE:", e)
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/shapes/<shape_id>', methods=['PUT'])
def update_shape(shape_id):
    """Atualiza uma forma existente
    ---
    tags:
      - Shapes
    parameters:
      - in: path
        name: shape_id
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            x:
              type: number
            y:
              type: number
            width:
              type: number
            height:
              type: number
            color:
              type: string
            text:
              type: string
            font_size:
              type: integer
            version:
              type: integer
    responses:
      200:
        description: Forma atualizada
        schema:
          type: object
      409:
        description: Conflito de versão
        schema:
          type: object
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    supabase = get_supabase_client()
    try:
        # Buscar a forma atual para checar a versão
        current = supabase.table("whiteboard_shapes").select("version").eq('id', shape_id).execute()
        if not current.data:
            return jsonify({'error': 'Shape not found'}), 404
        current_version = current.data[0].get('version', 0)
        client_version = data.get('version', 0)
        if client_version != current_version:
            return jsonify({'error': 'Conflict', 'message': 'Shape was updated by another user', 'current_version': current_version}), 409
        # Incrementar versão
        data['version'] = current_version + 1
        response = supabase.table("whiteboard_shapes").update(data).eq('id', shape_id).execute()
        # Publish para Redis
        publish_event('shape_updated', {'id': shape_id, **data, 'session_id': whiteboard_data['session_id']})
        socketio.emit('shape_updated', {'id': shape_id, **data}, room=whiteboard_data['session_id'])
        # Registrar evento
        log_event(whiteboard_data['session_id'], session['user_id'], 'update', shape_id, data)
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
        # Publish para Redis
        publish_event('shape_deleted', {'id': shape_id, 'session_id': whiteboard_data['session_id']})
        socketio.emit('shape_deleted', {'id': shape_id}, room=whiteboard_data['session_id'])
        # Registrar evento
        log_event(whiteboard_data['session_id'], session['user_id'], 'delete', shape_id)
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
        # Publish para Redis
        publish_event('canvas_cleared', {'session_id': whiteboard_data['session_id']})
        socketio.emit('canvas_cleared', room=whiteboard_data['session_id'])
        # Registrar evento
        log_event(whiteboard_data['session_id'], session['user_id'], 'clear')
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

@app.route('/api/shapes/rebuild', methods=['GET'])
def rebuild_shapes():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_id required'}), 400
    supabase = get_supabase_client()
    try:
        events = supabase.table('whiteboard_events').select('*').eq('session_id', session_id).order('created_at', asc=True).execute()
        shapes = {}
        for event in events.data:
            etype = event['event_type']
            shape_id = event.get('shape_id')
            payload = event.get('payload')
            if etype == 'create' and shape_id:
                shapes[shape_id] = payload
            elif etype == 'update' and shape_id and shape_id in shapes:
                shapes[shape_id].update(payload)
            elif etype == 'delete' and shape_id and shape_id in shapes:
                del shapes[shape_id]
            elif etype == 'clear':
                shapes = {}
        return jsonify(list(shapes.values()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Configurar host e porta baseado no ambiente
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Iniciando Quadro Branco Colaborativo em {host}:{port}")
    start_grpc_server_in_thread()
    start_redis_listener(socketio)
    socketio.run(app, debug=debug, host=host, port=port, allow_unsafe_werkzeug=True) 