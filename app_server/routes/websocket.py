from flask import request
from flask_socketio import emit, Namespace, disconnect, join_room


def init_websocket(socketio):
    socketio.on_namespace(AgentsRunningNamespace('/agents_running'))

    # print('init_websocket')

    @socketio.on_error_default  # handles all namespaces without an explicit error handler
    def default_error_handler(e):
        print("default_error_handler:", e)
        # send({'error': str(e)})
        disconnect()
        return

    @socketio.on('connect')
    def connect_handler(namespace):
        if namespace != '/agents_running':
            print('Client connected to namespace:', namespace)
            return False  # 拒绝连接

    @socketio.on('disconnect')
    def disconnect_handler():
        print('Client disconnected')


class AgentsRunningNamespace(Namespace):

    # 客户端连接时触发
    def on_connect(self):
        print(f'Client connected to {self.namespace}')
        # 检查task_id
        task_id = request.args.get('task_id')
        if not task_id:
            # 没有task_id,拒绝
            print('no task id')
            emit('res', {'error': 'no task id'})
            return False
        # 加入任务房间
        join_room(task_id)
        emit('res', {'result': '你好'}, room=task_id)
        print('Client connected, task_id :' + task_id)

    # 客户端发送消息时触发
    @staticmethod
    # @jwt_required()
    def on_next_agent(self, data):
        # 检查task_id
        task_id = request.args.get('task_id')
        if not task_id:
            # 没有task_id,拒绝
            print('Client sent message(next agent): ' + str(data))
            emit('res', {'error': 'no task id'})
            return False
            # task_id与user的权限校验
        # uid = get_jwt_identity()
        # err = validate_task_user_permission(task_id, uid)
        # if err is not None:
        #     emit('res', {'error': err})
        #     return False
        if task_id != data.get('task_id'):
            # 房间不匹配
            emit('res', {'error': 'wrong task id'})
            return False

        # 校验通过,获取input
        input_data = data.get('data')
        print(f'Received data: {input_data}')

        # 返回结果
        emit('res', {'result': 'success'})
        print('Client sent message(next agent): ' + str(data))

    @staticmethod
    def on_send_to_task(event, task_id, data):
        emit(event, {'msg': data}, room=task_id)
        return
