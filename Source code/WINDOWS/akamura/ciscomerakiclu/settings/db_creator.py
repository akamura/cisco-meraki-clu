#**************************************************************************
#   App:         Cisco Meraki CLU                                         *
#   Version:     1.4                                                      *
#   Author:      Matia Zanella                                            *
#   Description: Cisco Meraki CLU (Command Line Utility) is an essential  *
#                tool crafted for Network Administrators managing Meraki  *
#   Github:      https://github.com/akamura/cisco-meraki-clu/             *
#                                                                         *
#   Icon Author:        Cisco Systems, Inc.                               *
#   Icon Author URL:    https://meraki.cisco.com/                         *
#                                                                         *
#   Copyright (C) 2024 Matia Zanella                                      *
#   https://www.matiazanella.com                                          *
#                                                                         *
#   This program is free software; you can redistribute it and/or modify  *
#   it under the terms of the GNU General Public License as published by  *
#   the Free Software Foundation; either version 2 of the License, or     *
#   (at your option) any later version.                                   *
#                                                                         *
#   This program is distributed in the hope that it will be useful,       *
#   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#   GNU General Public License for more details.                          *
#                                                                         *
#   You should have received a copy of the GNU General Public License     *
#   along with this program; if not, write to the                         *
#   Free Software Foundation, Inc.,                                       *
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
#**************************************************************************


# ==================================================
# IMPORT various libraries and modules
# ==================================================
import os
import sqlite3
from getpass import getpass
from termcolor import colored
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode

def generate_fernet_key(password):
    return Fernet(urlsafe_b64encode(password.encode('utf-8').ljust(32)[:32]))

# ==================================================
# CREATE the Database (Not encrypted by itself, encryption handled at data level)
# ==================================================
def create_cisco_meraki_clu_db(db_path):
    try:
        if not os.path.exists(os.path.dirname(db_path)):
            os.makedirs(os.path.dirname(db_path))

        # SQLite connection
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS sensitive_data (id INTEGER PRIMARY KEY, data TEXT)")
        print("Database and table created successfully.")
    except Exception as e:
        print(colored("\nFailed to create or access the database.\n", "red") + str(e))
        input("\nPress Enter to retry")
        return False
    finally:
        if conn:
            conn.close()
    return True

def database_exists(db_path):
    db_path = 'db/cisco_meraki_clu_db.db'
    return os.path.exists(db_path)

def verify_database_password():
    db_path = 'db/cisco_meraki_clu_db.db'
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT count(*) FROM sensitive_data")
        conn.close()
        return True
    except Exception as e:
        print(colored("\nError: The provided database password is incorrect.\n", "red"))
        return False


# ==================================================
# CREATE a new Database table for IPinfo token
# ==================================================
def prompt_create_database():
    db_path = 'db/cisco_meraki_clu_db.db'
    create_db = input("The program needs a database to store sensitive data like Cisco Meraki API key.\nDo you want to create the DB? [yes/no]: ").strip().lower()
    if create_db == 'yes':
        print(colored("\nRemember to save your database encryption key in a safe place!", "red"))
        print(colored("You will need it to access the application!\n", "red"))
        if create_cisco_meraki_clu_db(db_path):
            print(colored("Database created successfully.", "green"))
            return True
    elif create_db == 'no':
        print(colored("\nNo database created. Exiting the program.\n", "red"))
        return False
    else:
        print(colored("\nInvalid input. Please try again.\n", "red"))
        return prompt_create_database()

def update_database_schema(db_path, password):
    db_path = 'db/cisco_meraki_clu_db.db'
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(f"PRAGMA key = '{password}'")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tools_ipinfo (
                id INTEGER PRIMARY KEY, 
                access_token TEXT
            );
        """)
        conn.commit()
        conn.close()
        print(colored("Database schema updated successfully.", "green"))
    except Exception as e:
        print(colored(f"Failed to update database schema: {e}", "red"))

def store_tools_ipinfo_access_token(access_token, password):
    db_path = 'db/cisco_meraki_clu_db.db'
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(f"PRAGMA key = '{password}'")
        conn.execute("INSERT INTO tools_ipinfo (access_token) VALUES (?)", (access_token,))
        conn.commit()
        conn.close()
        print(colored("Access token stored successfully.", "green"))
    except Exception as e:
        print(colored(f"Failed to store access token: {e}", "red"))

def get_tools_ipinfo_access_token(password):
    db_path = 'db/cisco_meraki_clu_db.db'
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(f"PRAGMA key = '{password}'")
        cursor = conn.cursor()
        cursor.execute("SELECT access_token FROM tools_ipinfo LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
        return None
    except Exception as e:
        print(f"Failed to retrieve access token: {e}")
        return None