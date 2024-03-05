from http import HTTPStatus

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

from app_server import db
from app_server.models.chapter import Chapter
from app_server.models.novel import GetNovelByBookId
from app_server.vaildate.vaildate_chapter import validate_chapter_data

chapter_bp = Blueprint('chapter', __name__)


@chapter_bp.route('/chapter', methods=['POST'])
# @jwt_required()
def create_chapter():
    try:
        data = request.get_json()

        # 参数校验
        err = validate_chapter_data(data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})
        else:
            book_id = data.get('book_id')
            novel = GetNovelByBookId(book_id)

            if not novel:
                return jsonify({"code": HTTPStatus.NOT_FOUND, "msg": "novel not found."})

            # 将小说的第三方id保存
            data['novel_id'] = novel.id
            data.pop("book_id", None)
            chapter = Chapter(**data)
            # uid = get_jwt_identity()
            # chapter.user_id = uid
            chapter.user_id = 1
            chapter.create()
            return jsonify({"code": HTTPStatus.OK, "msg": "success"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@chapter_bp.route('/chapter/<int:aid>', methods=['GET'])
@jwt_required()
def get_chapter(aid):
    try:
        chapter = Chapter.query.get(aid)

        if not chapter or chapter.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "chapter not found."
            })

        data = chapter.to_dict()

        uid = get_jwt_identity()
        if chapter.user_id == uid:
            # 可以进行编辑
            data['is_edit'] = True

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": data
        })

    except Exception as e:
        return jsonify({
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "msg": str(e)
        })


@chapter_bp.route('/chapter/', methods=['PUT'])
@jwt_required()
def update_chapter():
    try:
        data = request.get_json()
        aid = data.get('id')
        chapter = Chapter.query.get(aid)

        if not chapter or chapter.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "chapter not found."
            })

        err = ""
        uid = get_jwt_identity()
        if uid != chapter.user_id:
            err = "uid error."

        if uid != data.get('user_id'):
            err = "user_id error"

        if len(err) != 0:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        # 必填校验
        err = validate_chapter_data(data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        # Exclude create_time and update_time from the update
        data.pop("create_time", None)
        data.pop("update_time", None)

        chapter.query.filter_by(id=data.pop("id")).update(data)
        db.session.commit()

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@chapter_bp.route('/chapter/<int:cid>', methods=['DELETE'])
@jwt_required()
def delete_chapter(aid):
    try:
        chapter = Chapter.query.get(aid)
        uid = get_jwt_identity()
        if not chapter or chapter.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "Permission denied"})

        # 逻辑删除角色
        chapter.status = 0
        db.session.commit()

        return jsonify({'code': HTTPStatus.OK, 'msg': 'chapter deleted'})

    except Exception as e:

        db.session.rollback()

        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@chapter_bp.route('/chapters/<int:tid>', methods=['GET'])
@jwt_required()
def get_chapters(tid):
    try:
        uid = get_jwt_identity()
        last_id = request.args.get('last_id')
        page = request.args.get('page', 1, type=int)

        # 查询条件应始终过滤状态
        query = Chapter.query.filter(Chapter.novel_id == tid, Chapter.status > 0)

        # # 设置排序方式为id降序
        # query = query.order_by(desc(Chapter.id))

        if last_id:
            # 根据last_id分页
            query = query.filter(Chapter.id < last_id)
            # 分页
        pagination = query.paginate(page=page, per_page=10)

        chapter = pagination.items

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": {
                'chapter': [c.to_dict() for c in chapter],
                'page': page,
                'total': pagination.pages
            }
        })
    except Exception as e:
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})
