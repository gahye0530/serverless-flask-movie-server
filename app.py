# 메인

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from config import config
from resources.favorite import FavoriteListResource, FavoriteResource
from resources.login import UserLoginResource
from resources.logout import UserLogoutResource, jwt_blacklist
from resources.register import UserRegisterResource
# from resources.movie import MovieInfoResource, MovieRealtimeRecommandResource, MovieRecommandResource, MovieSearchResource
from resources.review import MovieReviewResource
from resources.userinfo import UserInfoResource

app = Flask(__name__)


app.config.from_object(config)
jwt = JWTManager(app)
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload) :
    jti = jwt_payload['jti']
    return jti in jwt_blacklist


api = Api(app)
api.add_resource(UserRegisterResource,'/api/v1/user/register')
api.add_resource(UserLoginResource,'/api/v1/user/login')
api.add_resource(UserInfoResource,'/api/v1/user/me')
api.add_resource(UserLogoutResource, '/api/v1/user/logout')
# api.add_resource(MovieInfoResource, '/api/v1/movie')
# api.add_resource(MovieSearchResource, '/api/v1/movie/search')
api.add_resource(MovieReviewResource, '/api/v1/review')
api.add_resource(FavoriteResource, '/api/v1/favorit/<int:movie_id>')
api.add_resource(FavoriteListResource, '/api/v1/favorit')
# # api.add_resource(MovieRecommandResource, '/api/v1/movie/recommendation')
# api.add_resource(MovieRealtimeRecommandResource, '/api/v1/movie/recommendation') # 실시간 추천

if __name__ == '__main__' : app.run()