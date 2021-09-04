import datetime
import os
import traceback
import time
from contextlib import contextmanager

import redis
import pymysql
from dotenv import load_dotenv

from core.utils import generate_hashed_password, stringify_given_datetime_or_current_datetime


# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_password = os.getenv('REDIS_PASSWORD')

redis_store = redis.Redis(host=redis_host, port=redis_port, password=redis_password, 
                decode_responses=True)

db_host_dev = os.getenv('DB_HOST_DEV')
db_host = os.getenv('DB_HOST')
db_port = int(os.getenv('DB_PORT'))
db_user = os.getenv('DB_USERNAME')
db_pw = os.getenv('DB_PASSWORD')
db_dataset = os.getenv('DB_DATABASE')
db_charset = os.getenv('DB_CHARSET')

db_info_kwargs = {
    "host": db_host_dev,
    "port": db_port,
    "user": db_user,
    "password": db_pw,
    "db": db_dataset,
    "charset": db_charset,
    "cursorclass": pymysql.cursors.DictCursor
}

@contextmanager
def get_db():
    try:
        conn = None
        try:
            conn = pymysql.connect(**db_info_kwargs)
        except:
            # print("db host dev connect exception")
            db_info_kwargs["host"] = db_host
            conn = pymysql.connect(**db_info_kwargs)
        yield conn
    except:
        traceback.print_exc()
    finally:
        conn.close()
        pass



def init_db():
    with get_db() as conn:
        from core import schema
        sql_list= schema.schema.split(";")
        for sql in sql_list:
            if sql != '' and sql != '\n':
                try:
                    conn.cursor().execute(sql)
                except:
                    traceback.print_exc()
        conn.commit()
    
    _create_default_users()
    

def _create_default_users():
    
    if not get_user(name='admin'):
        ADMIN_NAME = os.getenv('ADMIN_NAME')
        ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
        ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
        print("Created admin user")
        insert_user(ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD, 0)


def insert_user(user_name, email, password, user_type):
    hashed_password, salt = generate_hashed_password(password)
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = "INSERT into user(name, email, password, salt, user_type) values (%s,%s,%s,%s,%s)"
            cur.execute(sql, (user_name, email, hashed_password, salt, user_type))
            conn.commit()

        return True
    except:
        traceback.print_exc()
        return False

def get_users():
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = """
                SELECT id, name, email, user_type, login_counting, create_datetime, update_datetime
                FROM user
            """
            cur.execute(sql)
            conn.commit()
            res = cur.fetchall()
            return res
    except:
        traceback.print_exc()
        return False

def get_user(id_=None, name=None):
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = """
                SELECT id, name, email, user_type, login_counting, create_datetime, update_datetime
                FROM user
            """
            if id_ is not None:
                sql = add_condition_to_query(sql, "id", id_)
            elif name is not None:
                sql = add_condition_to_query(sql, "name", name)
        
            cur.execute(sql)
            conn.commit()
            res = cur.fetchone()

            return res
    except:
        traceback.print_exc()
        return False


def add_condition_to_query(sql, col, row, is_first_condition=True):
    if is_first_condition:
        sql += " WHERE "
    else:
        sql += " AND "
    if isinstance(row, int):
        sql += f" {col}={row}"
    elif isinstance(row, str):
        sql += f" {col}='{row}'"
    return sql


def insert_photo(type, description, image_id):
    try:
        with get_db() as conn:
            current_datatime = stringify_given_datetime_or_current_datetime()
            cur = conn.cursor()
            sql = "INSERT into photo(type, description, image_id, upload_datetime) values (%s, %s, %s, %s)"
            cur.execute(sql, (type, description.lower(), image_id, current_datatime))
            conn.commit()
            return cur.lastrowid
    except:
        traceback.print_exc()
        return False

def search_photos():
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = """
                SELECT
                    *
                FROM 
                    photo
            """
            cur.execute(sql)
            conn.commit()
            res = cur.fetchall()
        return res
    except:
        traceback.print_exc()
        return None

def get_photo_actions(photo_id):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = f"""
                SELECT
                    a.*
                FROM 
                    photo_action as pa
                Inner Join
                    action as a
                ON
                    a.id = pa.action_id
                Where pa.photo_id={photo_id}
            """
            cur.execute(sql)
            conn.commit()
            res = cur.fetchall()
        return res
    except:
        traceback.print_exc()
        return None

def get_photo_locations(photo_id):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = f"""
                SELECT
                    l.*
                FROM 
                    photo_location as pl
                Inner Join
                    location as l
                ON
                    l.id = pl.location_id
                Where pl.photo_id={photo_id}
            """
            cur.execute(sql)
            conn.commit()
            res = cur.fetchall()
        return res
    except:
        traceback.print_exc()
        return None

def update_photo(id_, type, desc, image_id):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = f"""
                UPDATE 
                    photo
                SET
                    type={type}
                    desc='{desc.lower}'
                    image_id='{image_id}'
                WHERE
                    id={id_}
            """
            cur.execute(sql)
            conn.commit()
        return True
    except:
        traceback.print_exc()
        return None


def delete_photo(id_):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = f"""
                DELETE FROM 
                    photo
                WHERE 
                    id={id_}
            """
            cur.execute(sql)
            conn.commit()
        return True
    except:
        traceback.print_exc()
        return None


def insert_action(name):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = "INSERT into action(name) values (%s)"
            cur.execute(sql, (name.lower()))
            conn.commit()

        return True
    except:
        traceback.print_exc()
        return False

def get_actions():
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = """
                SELECT
                    *
                FROM action
            """
            cur.execute(sql)
            conn.commit()
            res = cur.fetchall()
        return res
    except:
        traceback.print_exc()
        return None

def update_action(id_, name):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = f"""
                UPDATE 
                    action
                SET
                    name='{name.lower()}'
                WHERE
                    id={id_}
            """
            cur.execute(sql)
            conn.commit()
        return True
    except:
        traceback.print_exc()
        return None


def delete_action(id_):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = f"""
                DELETE FROM 
                    action
                WHERE 
                    id={id_}
            """
            cur.execute(sql)
            conn.commit()
        return True
    except:
        traceback.print_exc()
        return None


def insert_location(name, key=None):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            if key:
                sql = "INSERT into location(key, name) values (%s, %s)"
                cur.execute(sql, (key, name.lower()))
            else:
                sql = "INSERT into location(name) values (%s)"
                cur.execute(sql, (name.lower()))
            conn.commit()

        return True
    except:
        traceback.print_exc()
        return False

def get_locations():
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = """
                SELECT
                    *
                FROM location
            """
            cur.execute(sql)
            conn.commit()
            res = cur.fetchall()
        return res
    except:
        traceback.print_exc()
        return None

def update_location(id_, name):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = f"""
                UPDATE 
                    location
                SET
                    name='{name.lower()}'
                WHERE
                    id={id_}
            """
            cur.execute(sql)
            conn.commit()
        return True
    except:
        traceback.print_exc()
        return None


def delete_location(id_):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = f"""
                DELETE FROM 
                    location
                WHERE 
                    id={id_}
            """
            cur.execute(sql)
            conn.commit()
        return True
    except:
        traceback.print_exc()
        return None

def insert_photo_action(photo_id, actions):
    try:
        rows = [(photo_id, int(action)) for action in actions]
        with get_db() as conn:
            cur = conn.cursor()
            sql = "INSERT into photo_action(photo_id, action_id) values (%s,%s)"
            cur.executemany(sql, rows)
            conn.commit()
    except:
        traceback.print_exc()
        return None

def insert_photo_location(photo_id, locations):
    try:
        rows = [(photo_id, int(location)) for location in locations]
        with get_db() as conn:
            cur = conn.cursor()
            sql = "INSERT into photo_location(photo_id, location_id) values (%s,%s)"
            cur.executemany(sql, rows)
            conn.commit()
    except:
        traceback.print_exc()
        return None
