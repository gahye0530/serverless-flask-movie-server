# 로그아웃(POST)

from flask_jwt_extended import get_jwt
from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource

jwt_blacklist = set()

class UserLogoutResource(Resource) :
    @jwt_required()
    def post(self) :
        jti = get_jwt()['jti']
        print(jti)
        jwt_blacklist.add(jti)

        return {'result':'로그아웃 되었습니다.'}