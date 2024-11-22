# -*- coding: utf-8 -*-
import sqlite3
import config
from datetime import datetime

def add_user_from_database(user_id, registered_from_bot):
    if get_user_from_database(user_id) == False:
        conn, cursor = get_cursor_database()
        cursor.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?);", (user_id, 0, datetime(2000, 1, 1, 0, 0, 0).isoformat(), 'main_menu', registered_from_bot) )
        conn.commit()
        return True


def get_all_user_from_database():
    conn, cursor = get_cursor_database()
    cursor.execute("SELECT * FROM users")
    exists = cursor.fetchall()
    conn.commit()
    if not exists:
        return False
    else:
        return exists


def get_user_from_database(user_id):
    conn, cursor = get_cursor_database()
    cursor.execute("SELECT * FROM users WHERE user_id=?",(user_id,))
    exists = cursor.fetchone()
    conn.commit()
    if not exists:
        return False
    else:
        return exists


def set_user_last_percent(user_id, percent):
    conn, cursor = get_cursor_database()
    cursor.execute("SELECT * FROM users WHERE user_id=?",(user_id,))
    exists = cursor.fetchall()
    if exists:
        cursor.execute("UPDATE users SET user_last_result=? WHERE user_id=?", (percent, user_id,))
    conn.commit()

def get_user_last_percent(user_id):
    return get_user_from_database(user_id)[1]


def set_user_saved_time(user_id):
    conn, cursor = get_cursor_database()
    cursor.execute("SELECT * FROM users WHERE user_id=?",(user_id,))
    exists = cursor.fetchall()
    if exists:
        cursor.execute("UPDATE users SET user_result_saved_time=? WHERE user_id=?", (datetime.now().isoformat(), user_id,))
    conn.commit()

def get_user_saved_time(user_id):
    is_saved_time = get_user_from_database(user_id)[2]
    if is_saved_time:
        return datetime.fromisoformat(is_saved_time)
    else:
        return False


def set_user_menu(user_id, menu):
    conn, cursor = get_cursor_database()
    cursor.execute("SELECT * FROM users WHERE user_id=?",(user_id,))
    exists = cursor.fetchall()
    if exists:
        cursor.execute("UPDATE users SET user_menu=? WHERE user_id=?", (menu, user_id,))
    conn.commit()


def get_user_menu(user_id):
    return get_user_from_database(user_id)[3]


def get_cursor_database():
    conn = sqlite3.connect(config.DATABASE)
    cursor = conn.cursor()
    return conn, cursor


def create_database():
    conn, cursor = get_cursor_database()
    cursor.execute("""CREATE TABLE if not exists users(
            user_id INTEGER,
            user_last_result INTEGER,
            user_result_saved_time TEXT,
            user_menu TEXT,
            user_registered_from_bot BOOL
        )""")
    conn.commit()

create_database()
