# 리뷰가져오기(GET), 리뷰(별점) 작성(POST)

from flask_jwt_extended import get_jwt_identity
from flask_restful import Resource
from flask import request
from mysql.connector.errors import Error
from http import HTTPStatus
from mysql_userinfo import get_connection
from flask_jwt_extended import jwt_required


class MovieReviewResource(Resource) :
    # 영화선택하면 리뷰가져오기
    def get(self) :
        movie_id = request.args.get('movie_id')
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        try :
            connection = get_connection()
            # query = '''select user.name as 'name', user.gender as 'gender', rating.rating as 'rating'
            #             from movie 
            #             join rating on movie.id = rating.movie_id
            #             join user on rating.user_id = user.id
            #             where movie.id = '''+ movie_id + '''
            #             limit '''+ offset + ''', ''' + limit + ''';'''

            query = '''select r.id as rating_id, r.user_id, r.movie_id, u.name, u.gender, r.rating 
                        from rating r
                        join user u
                        on r.user_id = %s
                        where r.movie_id=1
                        limit ''' + offset + ''', ''' + limit +''';'''
            param = (movie_id, )
            cursor = connection.cursor(dictionary = True)
            # cursor.execute(query)
            cursor.execute(query, param)
            record_list = cursor.fetchall()
        except Error as e :
            print('error', e)
            return {'error' : str(e)}, HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected() :
                cursor.close()
                connection.close()
        return {'result' : record_list}, HTTPStatus.OK
    # 리뷰(별점) 작성
    @jwt_required()
    def post(self) :
        data = request.get_json()
        user_id = get_jwt_identity()
        try :
            connection = get_connection()
            query = '''insert into rating(user_id, movie_id, rating, contents) value(%s, %s, %s, %s);'''
            record = (user_id, data['movie_id'], data['rating'], data['contents'])
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
        except Error as e:
            print('error', e)
            return {'error' : str(e)}, HTTPStatus.BAD_REQUEST
        finally:
            if connection.is_connected() :
                cursor.close()
                connection.close()
        return {'result' : '리뷰작성 완료'}, HTTPStatus.OK
