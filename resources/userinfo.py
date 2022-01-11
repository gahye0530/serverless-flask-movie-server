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
            query = '''select email, name, gender from user where id = %s;'''
            param = (user_id, )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, param)
            record_list = cursor.fetchall()

            # gender 정보를 문자로 바꾸어주자
            gender = record_list[0]['gender']
            if  gender == 0 : 
                gender =  "Agender"                
            elif gender == 1: 
                gender = "Bigender"  
            elif gender ==  2:
                gender = "Female"
            elif gender == 3 :
                gender = "Genderfluid"
            elif gender == 4 :
                gender = "Genderqueer"
            elif gender == 5 :
                gender = "Male"
            elif gender == 6 :
                gender = "Non-binary"
            elif gender == 7 :
                gender = "Polygender"
            else :
                gender = "성별"
            record_list[0]['gender'] = gender
            user_info = record_list[0]
            # i = 0
            # for record in record_list:
            #     record_list[i]['created_at'] = record['created_at'].isoformat()                
            #     i = i + 1


            # 다시 데이터를 가져오자.
            query = '''select r.id, m.title, r.rating
                        from rating r
                        join movie m
                        on r.user_id =%s and r.movie_id = m.id;
                        '''

            record = (user_id, )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)
            # select 문은 아래 내용이 필요하다.
            # 커서로 부터 실행한 결과 전부를 받아와라.
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