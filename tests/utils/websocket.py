from flask import Flask
from flask_socketio import SocketIO, Namespace

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


# 命名空间定义
class MyNamespace(Namespace):
    @staticmethod
    def on_connect(self):
        print("Client connected to MyNamespace")

    @staticmethod
    def on_disconnect(self):
        print("Client disconnected from MyNamespace")

    def on_message(self, data):
        print("Received message:", data)
        # 发送回复
        self.emit("response", {"message": "Server received your message"})


# 将命名空间注册到 SocketIO
socketio.on_namespace(MyNamespace('/agents_running'))


@socketio.on('connect', namespace='/agents_running')
def handle_connect():
    print('Client connected')


# 路由定义
@app.route('/')
def index():
    return "ok"


if __name__ == '__main__':
    socketio.run(app,allow_unsafe_werkzeug=True, debug=True)
