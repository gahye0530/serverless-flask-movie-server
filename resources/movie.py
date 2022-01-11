# # 영화목록(GET), 검색(GET), 추천(GET)

# from flask_jwt_extended import get_jwt_identity
# from flask_restful import Resource
# from flask import request
# from mysql.connector.errors import Error
# from flask_restful import Resource
# from flask import request
# from mysql.connector.errors import Error
# from mysql_userinfo import get_connection
# from http import HTTPStatus
# from flask_jwt_extended import jwt_required
# import pandas as pd

# class MovieInfoResource(Resource) :
#     def get(self) :
#         # data = request.get_json()
        
#         # 1. 쿼리 스트링의 정보를 가져오기.

#         # 방법 1) 키, 밸류로 가져오기
#         offset = request.args.get('offset')
#         limit = request.args.get('limit')
#         order = request.args.get('order')

#         # 방법 2) 딕셔너리로 전부 받아서 가져오는 방법
#         # query_params = request.args.to_dict()
#         # query_params['offset']
        
#         # 2. 디비에 쿼리한다. 
#         try :
#             connection = get_connection()

#             if order == 'count' : 
#                 query = '''select movie.title as title, count(rating.user_id) as 'count', avg(rating.rating) as 'average' 
#                             from movie left join rating on movie.id = rating.movie_id 
#                             group by movie.title
#                             order by count desc limit ''' + offset + ''', '''+ limit + ''';'''
#             elif order == 'average' :
#                 query = '''select movie.title as title, count(rating.user_id) as 'count', avg(rating.rating) as 'average' 
#                             from movie left join rating on movie.id = rating.movie_id 
#                             group by movie.title
#                             order by average desc limit ''' + offset + ''', '''+ limit + ''';'''

#             cursor = connection.cursor(dictionary = True)
#             cursor.execute(query)
#             record_list = cursor.fetchall()

#             i=0
#             for record in record_list :
#                 record_list[i]['count'] = str(record['count'])
#                 record_list[i]['average'] = str(record['average'])
#                 i=i+1

#         except Error as e:
#             print('Error', e)
#             return {'error' : e}, HTTPStatus.BAD_REQUEST
#         finally :
#             if connection.is_connected() :
#                 cursor.close()
#                 connection.close()

#         return {'count' : len(record_list), 'result' : record_list}, HTTPStatus.OK


# class MovieSearchResource(Resource) :
#     def get(self):
#         # data = request.get_json()
#         offset = request.args.get('offset')
#         limit = request.args.get('limit')
#         keyword = request.args.get('keyword') # 'star'
#         search_word = '%' + keyword + '%'
#         print(offset, limit, search_word)
#         try :
#             connection = get_connection()
            
#             query = '''select movie.title as title, count(rating.user_id) as 'count', avg(rating.rating) as 'average' 
#                         from movie left join rating on movie.id = rating.movie_id 
#                         group by movie.title
#                         having movie.title like %s
#                         order by count desc limit ''' + offset + ''', '''+ limit + ''';'''
#             record = (search_word, )
#             cursor = connection.cursor(dictionary = True)
#             cursor.execute(query, record)
#             record_list = cursor.fetchall()

#             i=0
#             for record in record_list :
#                 record_list[i]['count'] = str(record['count'])
#                 record_list[i]['average'] = str(record['average'])
#                 i=i+1

#         except Error as e:
#             print('Error', e)
#             return {'error' : e}, HTTPStatus.BAD_REQUEST
#         finally :
#             if connection.is_connected() :
#                 cursor.close()
#                 connection.close()

#         return {'result' : record_list}, HTTPStatus.OK


# class MovieRecommandResource(Resource) :
#     @jwt_required()
#     def get(self) :
#         # /data/~~ 라고 하면 안된다.
#         corr_df = pd.read_csv('data/movie_correlations.csv', index_col = 'title')
#         user_id = get_jwt_identity()

#         try :
#             connection = get_connection()
#             query = '''select r.id, r.user_id, r.movie_id, r.rating, m.title
#                         from rating r
#                         join movie m 
#                         on r.user_id = %s and r.movie_id = m.id;'''
#             param = (user_id, )
#             cursor = connection.cursor(dictionary = True)
#             cursor.execute(query, param)
#             record_list = cursor.fetchall()
#             print(record_list[0]['title'])


#         except Error as e :
#             print('error' , e)
#             return {'error' : str(e)}, HTTPStatus.BAD_REQUEST
#         finally :
#             if connection.is_connected() :
#                 cursor.close()
#                 connection.close()

#         #유저의 정보를 pandas dataframe으로 만들어준다.
#         my_rating = pd.DataFrame(data = record_list)
#         print(my_rating)
#         similar_movies_list = pd.DataFrame()
#         for i in range( len(my_rating) ) :
#             similar_movie = corr_df[my_rating['title'][i]].dropna().sort_values(ascending=False).to_frame()
#             similar_movie.columns = ['Correlation']
#             similar_movie['Weight'] = my_rating['rating'][i] * similar_movie['Correlation']
#             similar_movies_list = similar_movies_list.append(similar_movie)

#         similar_movies_list.reset_index(inplace=True)
#         similar_movies_list = similar_movies_list.groupby('title')['Weight'].max().sort_values(ascending=False)
#         ### 중요!  위의 결과는, 유저가 본 영화 제목도 포함되어있다. 따라서
#         ### 유저가 본 영화는 제거 해야 한다!!!
#         ### 힌트 pandas isin() 함수와 ~ (not) 기호 사용
#         similar_movies_list = similar_movies_list.reset_index()
#         title_list = my_rating['title'].tolist()
#         recommand_movie_list = similar_movies_list.loc[~similar_movies_list['title'].isin(title_list), ].head(10)
        
#         # result = recommand_movie_list.to_json(orient="columns")
#         # parsed = json.loads(result)
#         # result_json = json.dumps(parsed, indent=4)  
#         # print(result_json)

#         return {'movie_list' : recommand_movie_list.to_dict('records')}, HTTPStatus.OK


# class MovieRealtimeRecommandResource(Resource) :
#     @jwt_required()
#     def get(self) :
#         user_id = get_jwt_identity()

#         try :
#             connection = get_connection()

#             # 상관계수를 위한 데이터프레임을 데이터베이스로부터 조인해서 가지고 올거야
#             # 실시간으로 상관계수를 측정하기 위해, 먼저 테이블로부터 정보를 가져온다. 
#             query = '''select user_id, movie_id, rating, title
#                         from rating r
#                         join movie m
#                         on r.movie_id = m.id;'''
#             cursor = connection.cursor(dictionary = True)
#             cursor.execute(query)
#             record_list = cursor.fetchall()
#             movies_rating_df = pd.DataFrame(data = record_list)
#             userid_movietitle_matrix = movies_rating_df.pivot_table(index='user_id', columns='title', values='rating')
#             corr_df = userid_movietitle_matrix.corr(min_periods=50)

#             query = '''select r.id, r.user_id, r.movie_id, r.rating, m.title
#                         from rating r
#                         join movie m 
#                         on r.user_id = %s and r.movie_id = m.id;'''
#             param = (user_id, )
#             cursor = connection.cursor(dictionary = True)
#             cursor.execute(query, param)
#             record_list = cursor.fetchall()
#             print(record_list[0]['title'])
#         except Error as e :
#             print('error' , e)
#             return {'error' : str(e)}, HTTPStatus.BAD_REQUEST
#         finally :
#             if connection.is_connected() :
#                 cursor.close()
#                 connection.close()

#         my_rating = pd.DataFrame(data = record_list)
#         print(my_rating)
#         similar_movies_list = pd.DataFrame()
#         for i in range( len(my_rating) ) :
#             similar_movie = corr_df[my_rating['title'][i]].dropna().sort_values(ascending=False).to_frame()
#             similar_movie.columns = ['Correlation']
#             similar_movie['Weight'] = my_rating['rating'][i] * similar_movie['Correlation']
#             similar_movies_list = similar_movies_list.append(similar_movie)

#         similar_movies_list.reset_index(inplace=True)
#         similar_movies_list = similar_movies_list.groupby('title')['Weight'].max().sort_values(ascending=False)
#         similar_movies_list = similar_movies_list.reset_index()
#         title_list = my_rating['title'].tolist()
#         recommand_movie_list = similar_movies_list.loc[~similar_movies_list['title'].isin(title_list), ].head(10)

#         return {'movie_list' : recommand_movie_list.to_dict('records')}, HTTPStatus.OK