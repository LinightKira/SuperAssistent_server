import asyncio
from http import HTTPStatus
from flask import Blueprint, request, jsonify

from app_agents.roles.ai_novle_video_pro import start_ai_novel_video_pro
from app_server.models.novel import GetNovelByBookId

agent_bp = Blueprint('agent', __name__)


@agent_bp.route('/agent/start', methods=['POST'])
def agent_start():
    try:
        data = request.get_json()

        book_id = data.get('book_id')
        novel = GetNovelByBookId(book_id)

        if not novel:
            return jsonify({"code": HTTPStatus.NOT_FOUND, "msg": "novel not found."})

        print('start agent book_id:', novel.id)
        # asyncio.run(start_ai_novel_video(str(novel.id)))  #普通版
        # asyncio.run(start_ai_novel_video_pro(str(novel.id)))  # 高级版
        return jsonify({"code": HTTPStatus.OK, "msg": "success"})

    except Exception as e:
        print('start agent error:', str(e))
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})
