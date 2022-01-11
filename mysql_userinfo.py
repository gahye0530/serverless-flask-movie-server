import mysql.connector

def get_connection() :
    connection = mysql.connector.connect(
        host = 'database-1.cibdadxvyc3i.us-east-2.rds.amazonaws.com',
        database = 'movie_db',
        user = 'movie_user',
        password = '1234'
    )
    return connection