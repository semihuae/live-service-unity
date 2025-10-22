# Gerekli kütüphaneleri içe aktar
from flask import Flask
from flask_socketio import SocketIO, emit
import os
import eventlet # Procfile'da Eventlet kullandığımız için bu gereklidir.

# Flask uygulamasını ve SocketIO'yu başlat
app = Flask(__name__)
# Gizli anahtarı ortam değişkenlerinden al, ayarlanmamışsa varsayılan kullan.
# IMPORTANT: Use environment variables for the SECRET_KEY in production!
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'skcore_unity_chat_key')

# cors_allowed_origins="*" ile herhangi bir kaynaktan (Unity) bağlantıya izin verilir.
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet') 

# Sunucu durumunu tutmak için basit bir sözlük
server_state = {"current_status": "Idle", "unity_data": 0}

@socketio.on('connect')
def handle_connect():
    """Handles connection event when a Unity client connects."""
    print('Unity Client Connected! New client connection established.')
    # Send the current state immediately upon connection
    emit('server_status', server_state)  

@socketio.on('disconnect')
def handle_disconnect():
    """Handles disconnection event."""
    print('Unity Client Disconnected! A client has disconnected.')

@socketio.on('unity_data_update')
def handle_unity_data_update(data):
    """Handles data sent from Unity (e.g., score, position)."""
    print(f"Data received from Unity: {data}")
    
    # Update server state with incoming data
    if 'score' in data:
        # Securely parse the incoming score data
        score = int(data.get('score', 0)) 
        server_state["unity_data"] = score
        server_state["current_status"] = f"Game in Progress, Score: {score}"
        
        # Critical: Broadcast the new state to all connected clients (including the one that sent the data)
        emit('server_status', server_state, broadcast=True)
        print(f"New state broadcasted: {server_state['current_status']}")

@app.route('/')
def index():
    """Simple HTTP response to check if the server is running."""
    return "<h1>SKCore Unity WebSocket Server Running!</h1>"

# Run the server using socketio.run() only when executed directly (e.g., local testing)
# In deployment (via Procfile), the 'eventlet' command handles the startup.
if __name__ == '__main__':
    print("WebSocket Server starting locally on ws://127.0.0.1:5000/")
    socketio.run(app, port=5000)
