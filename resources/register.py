# 회원가입(POST)

from flask_restful import Resource
from flask import request
from email_validator import validate_email, EmailNotValidError
from http import HTTPStatus
from mysql_userinfo import get_connection
from utils import hash_password
from mysql.connector.errors import Error
from flask_jwt_extended import create_access_token

class UserRegisterResource(Resource) :
    def post(self) :
        data = request.get_json()
        
        try :
            validate_email(data['email'])
        except EmailNotValidError as e :
            print(str(e))
            return {'error' : 'email 주소가 잘못되었습니다.'}, HTTPStatus.BAD_REQUEST
        
        hashed_password = hash_password(data['password'])

        try :
            connection = get_connection()
            query = '''insert into user (email, password, name, gender) values (%s, %s, %s, %s);'''
            record = (data['email'], hashed_password, data['name'], data['gender'])
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            user_id = cursor.lastrowid
        except Error as e :
            print('Error ', e)
            return {'error' : '이미 존재하는 회원입니다.'} , HTTPStatus.BAD_REQUEST
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
        access_token = create_access_token(user_id)
        return {'result' : '회원가입이 잘 되었습니다.', 'access_token' : access_token}