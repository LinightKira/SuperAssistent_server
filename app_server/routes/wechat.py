from http import HTTPStatus

import requests
from flask import request, jsonify, Blueprint
from app_server.models.user import User

from config import Config

wechat_bp = Blueprint('wechat', __name__)


# 登录部分
@wechat_bp.route('/user/wxlogin', methods=['GET', 'POST'])
def wx_login():
    try:
        # data = json.loads(request.get_data().decode('utf-8')) #将前端Json数据转为字典
        # code = data['code'] #前端POST过来的微信临时登录凭证code
        code = request.args.get('wxcode')
        appID = Config.APP_ID  # 开发者关于微信小程序的appID
        appSecret = Config.SECRET  # 开发者关于微信小程序的appSecret

        req_params = {
            'appid': appID,
            'secret': appSecret,
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        print(req_params)
        wx_login_api = 'https://api.weixin.qq.com/sns/jscode2session'
        response_data = requests.get(wx_login_api, params=req_params)  # 向API发起GET请求
        data = response_data.json()
        print(data)
        openid = data['openid']  # 得到用户关于当前小程序的OpenID
        session_key = data['session_key']  # 得到用户关于当前小程序的会话密钥session_key

        # 下面部分是通过判断数据库中用户是否存在来确定添加或返回自定义登录态（若用户不存在则添加；若用户存在，我这里返回的是添加用户时生成的自增长字段UserID）

        if openid and session_key:

            # 在数据库用户表查询（查找得到的OpenID在数据库中是否存在）
            # SQAlchemy语句：
            # user_info = User.query.filter(User.OpenID == openid).first()
            user = User.query.filter(User.openid == openid).first()
            print("user:", user, type(user))
            if not user:
                print("user 不存在")
                user_temp = User(nickname='匿名用户', openid=openid)
                user_temp.create()
                user = User.query.filter(User.openid == openid).first()

            return jsonify({"code": HTTPStatus.OK, "msg": "success", "datas": {"uid": user.id}})
        return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "code已失效或不正确", "datas": ''})

    except Exception as e:
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})
