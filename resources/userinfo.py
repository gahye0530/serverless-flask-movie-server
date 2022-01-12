from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from http import HTTPStatus

from mysql_userinfo import get_connection

# 내 정보 가져오기(GET)

class UserInfoResource(Resource) :
    @jwt_required()
    def get(self) :
        user_id = get_jwt_identity()
        try :
            connection = get_connection()
            # user정보 가져오기
            query = '''select email, name, gender from user where id = %s;'''
            param = (user_id, )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()
            # review 가져오기
            user_info = record_list[0]
            query = '''select r.id, m.title, r.rating
                        from rating r
                        join movie m
                        on r.user_id =%s and r.movie_id = m.id;
                        '''
            record = (user_id, )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)
            record_list = cursor.fetchall()
            print(record_list)
            review_list = record_list
        except Error as e :
            print('Error', e)
            return {'error' : e}, HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected() :
                cursor.close()
                connection.close()

        return {'user_info' : user_info, 'review_list' : review_list}, HTTPStatus.OK