# 즐겨찾기 설정(POST), 해제(DELETE), 가져오기(GET)
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from mysql.connector.errors import Error
from http import HTTPStatus
from mysql_userinfo import get_connection
from flask import request

class FavoriteResource(Resource) :
    @jwt_required()
    # 즐겨찾기 설정
    def post(self, movie_id) :
        user_id = get_jwt_identity()
        try :
            connection = get_connection()
            query = '''insert into favorite(user_id, movie_id) value(%s, %s);'''
            param = (user_id, movie_id)
            cursor = connection.cursor()
            cursor.execute(query, param)
            connection.commit()
        except Error as e :
            print('Error', e)
            return {'error' : '이미 즐겨찾기 설정 된 영화입니다.'}, HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected() :
                cursor.close()
                connection.close()
        return {'result' : '즐겨찾기 설정'}, HTTPStatus.OK


    @jwt_required()
    # 즐겨찾기 해제
    def delete(self, movie_id) :
        user_id = get_jwt_identity()
        try :
            connection = get_connection()
            query = '''delete from favorite where user_id=%s and movie_id=%s;'''
            param = (user_id, movie_id)
            cursor = connection.cursor()
            cursor.execute(query, param)
            connection.commit()
        except Error as e :
            print('Error', e)
            return {'error' : e}, HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected() :
                cursor.close()
                connection.close()
        return {'result' : '즐겨찾기 해제'}, HTTPStatus.OK


class FavoriteListResource(Resource) :
    @jwt_required()
    # 즐겨찾기 가져오기
    def get(self) :
        user_id = get_jwt_identity()
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        try :
            connection = get_connection()
            # query = '''select id, user_id, movie_id from favorite where user_id = %s limit ''' + offset + ''', ''' + limit + ''';'''
            query = '''select f.id as favorite_id, f.movie_id, f.user_id, m.title, count(r.rating) as cnt, avg(r.rating) as avg
                        from favorite f
                        join movie m
                        on f.user_id = %s and f.movie_id = m.id
                        join rating r
                        on f.movie_id = r.movie_id
                        group by f.movie_id
                        order by f.created_at desc
                        limit ''' + offset + ''',''' + limit + ''';'''
            
            param = (user_id, )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()

            i=0
            for record in record_list :
                record_list[i]['cnt'] = str(record['cnt'])
                record_list[i]['avg'] = str(record['avg'])
                i=i+1

        except Error as e :
            print('Error', e)
            return {'error' : e}, HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected() :
                cursor.close()
                connection.close()
        return {'result' : record_list}, HTTPStatus.OK
