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
from getpass import getpass
from termcolor import colored
from pysqlcipher3 import dbapi2 as sqlite

# ==================================================
# CREATE the encrypted Database
# ==================================================
def create_cisco_meraki_clu_db(password):
    db_path = '/opt/akamura/ciscomerakiclu/db/cisco_meraki_clu_db.db'
    conn = None
    
    try:
        if not os.path.exists(os.path.dirname(db_path)):
            os.makedirs(os.path.dirname(db_path))

        conn = sqlite.connect(db_path)
        conn.execute(f"PRAGMA key = '{password}'")
        conn.execute("CREATE TABLE IF NOT EXISTS sensitive_data (id INTEGER PRIMARY KEY, data TEXT)")
        print("Database and table created successfully.")
        conn.close()
        return True
    except Exception as e:
        print(colored("\nFailed to create or access the encrypted database.\n", "red") + str(e))
        input("\nPress Enter to retry")
        return False
    
    finally:
        if conn:
            conn.close()

def database_exists():
    db_path = '/opt/akamura/ciscomerakiclu/db/cisco_meraki_clu_db.db'
    return os.path.exists(db_path)

def verify_database_password(password):
    db_path = '/opt/akamura/ciscomerakiclu/db/cisco_meraki_clu_db.db'
    try:
        conn = sqlite.connect(db_path)
        conn.execute(f"PRAGMA key = '{password}'")
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
    create_db = input("The program need a SQLCipher encrypted database to store sensitive data like Cisco Meraki API key.\nDo you want to create the DB? [yes - no]]: ").strip().lower()
    if create_db == 'yes':
        print(colored("\nREMEMBER TO SAVE YOUR DATABASE PASSWORD IN A SAFE PLACE!", "red"))
        print(colored("YOU WILL NEED IT TO ACCESS THE APPLICATION!\n", "red"))
        db_password = getpass("Enter the encryption password for the database: ")
        create_cisco_meraki_clu_db(db_password)
        return db_password
    elif create_db == 'no':
        print(colored("\nNo database created. Exiting the program.\n", "red"))
        input("\n to close the program")
        return False
    else:
        print(colored("\nInvalid input. Please try again.\n", "red"))
        input("\nPress Enter to retry")
        return False

def update_database_schema(password):
    db_path = '/opt/akamura/ciscomerakiclu/db/cisco_meraki_clu_db.db'
    try:
        conn = sqlite.connect(db_path)
        conn.execute(f"PRAGMA key = '{password}'")
        conn.execute("CREATE TABLE IF NOT EXISTS tools_ipinfo (id INTEGER PRIMARY KEY, access_token TEXT)")
        conn.close()
        print("Database schema updated successfully.")
    except Exception as e:
        print(f"Failed to update database schema: {e}")

def store_tools_ipinfo_access_token(password, access_token):
    db_path = '/opt/akamura/ciscomerakiclu/db/cisco_meraki_clu_db.db'
    try:
        conn = sqlite.connect(db_path)
        conn.execute(f"PRAGMA key = '{password}'")
        conn.execute("INSERT INTO tools_ipinfo (access_token) VALUES (?)", (access_token,))
        conn.commit()
        conn.close()
        print("Access token stored successfully.")
    except Exception as e:
        print(f"Failed to store access token: {e}")

def get_tools_ipinfo_access_token(password):
    db_path = '/opt/akamura/ciscomerakiclu/db/cisco_meraki_clu_db.db'
    try:
        conn = sqlite.connect(db_path)
        conn.execute(f"PRAGMA key = '{password}'")
        cursor = conn.cursor()
        cursor.execute("SELECT access_token FROM tools_ipinfo LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
        else:
            return None
    except Exception as e:
        print(f"Failed to retrieve access token: {e}")
        return None