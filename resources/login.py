# 로그인(POST)
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from flask import request
from mysql.connector.errors import Error
from http import HTTPStatus

from mysql_userinfo import get_connection
from utils import check_password

class UserLoginResource(Resource) :
    def post(self) :
        data = request.get_json()
        try :
            connection = get_connection()
            query = '''select * from user where email = %s;'''
            param = (data['email'], )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()
            i = 0
            for record in record_list:
                record_list[i]['created_at'] = record['created_at'].isoformat()                
                i = i + 1
        except Error as e :
            print('Error', e)
            return {'error' : e}, HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected() :
                cursor.close()
                connection.close()

        if len(record_list) == 0 :
            return {'error' : '회원가입이 되어있지 않은 사람입니다.'}, HTTPStatus.UNAUTHORIZED
        # if check_password(data['password'], record_list[0]['password']) == False :
        #     return {'error' : '비번이 다릅니다.'}, HTTPStatus.UNAUTHORIZED

        user_id = record_list[0]['id']
        access_token = create_access_token(user_id)
        return {'result' : record_list, 'access_token' : access_token}
