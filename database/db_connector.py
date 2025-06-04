# Citation for this file:
# Date: 05/05/25
# Adapted from:
# Source URL: https://canvas.oregonstate.edu/courses/1999601/pages/exploration-web-application-technology-2?module_item_id=25352948

import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('DB_HOST')
user = os.getenv('DB_USERNAME')     
passwd = os.getenv('DB_PASSWORD')  
db = os.getenv('DATABASE')

def connectDB(host = host, user = user, passwd = passwd, db = db):
    '''
    connects to a database and returns a database object
    '''
    dbConnection = MySQLdb.connect(host,user,passwd,db)
    return dbConnection

def query(dbConnection = None, query = None, query_params = ()):
    '''
    executes a given SQL query on the given db connection and returns a Cursor object
    dbConnection: a MySQLdb connection object created by connectDB()
    query: string containing SQL query
    returns: A Cursor object as specified at https://www.python.org/dev/peps/pep-0249/#cursor-objects.
    You need to run .fetchall() or .fetchone() on that object to actually acccess the results.
    '''

    if dbConnection is None:
        print("No connection to the database found! Have you called connectDB() first?")
        return None

    if query is None or len(query.strip()) == 0:
        print("query is empty! Please pass a SQL query in query")
        return None

    print("Executing %s with %s" % (query, query_params));
    cursor = dbConnection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query, query_params)
    dbConnection.commit()
    
    return cursor