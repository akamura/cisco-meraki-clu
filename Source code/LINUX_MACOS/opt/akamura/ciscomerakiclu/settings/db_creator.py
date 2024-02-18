#**************************************************************************
#   App:         Cisco Meraki CLU                                         *
#   Version:     1.3                                                      *
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
    try:
        db_path = os.path.join('/opt/akamura/ciscomerakiclu/db', 'cisco_meraki_clu_db.db')
        conn = sqlite.connect(db_path)
        conn.execute(f"PRAGMA key = '{password}'")
        conn.execute("SELECT count(*) FROM sensitive_data")
        conn.close()
    except Exception as e:
        print(colored("\nError: The provided database password is incorrect.\n", "red"))
        input("\nPress Enter to close the program")
        return False

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