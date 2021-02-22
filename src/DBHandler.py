import sqlite3
from datetime import datetime


def get_db():
    # Open/Create db file
    conn = sqlite3.connect('server.db')
    conn.text_factory = bytes
    return conn


def create_users_tab():
    # Create the table if not exists
    conn = get_db()
    clients_table = """ CREATE TABLE IF NOT EXISTS clients (
                                            id varchar(16) PRIMARY KEY,
                                            name varchar(255) NOT NULL,
                                            publicKey varchar(160) NOT NULL,
                                            lastSeen text
                                        ); """
    conn.executescript(clients_table)
    conn.commit()
    conn.close()


def create_messages_tab():
    # Create the table if not exists
    conn = get_db()
    messages_table = """ CREATE TABLE IF NOT EXISTS messages (
                                                id integer NOT NULL,
                                                toClient varchar(16) NOT NULL,
                                                fromClient varchar(16) NOT NULL,
                                                type char NOT NULL,
                                                content text NOT NULL,
                                                PRIMARY KEY (id, toClient)
                                            ); """
    conn.executescript(messages_table)
    conn.commit()
    conn.close()


def save_user_to_db(uid, name, public_key):
    last_seen = datetime.now()
    conn = get_db()
    clients_table = """ INSERT INTO clients VALUES (?, ?, ?, ?); """
    conn.execute(clients_table, [uid.hex, name, public_key.decode('utf-8', errors='ignore'), last_seen])
    conn.commit()
    conn.close()


def save_message_to_db(mid, to_client, from_client, m_type, content):
    conn = get_db()
    messages_table = """ INSERT INTO messages VALUES (?, ?, ?, ?, ?); """
    conn.execute(messages_table, [mid, to_client.hex, from_client.hex, m_type, content])
    conn.commit()
    conn.close()


def update_last_seen(uid):
    last_seen = datetime.now()
    conn = get_db()
    clients_table = """ UPDATE clients SET last_seen = ? WHERE id = ? """
    conn.execute(clients_table, [last_seen, uid])
    conn.commit()
    conn.close()
