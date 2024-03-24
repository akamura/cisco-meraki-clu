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
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
from termcolor import colored

def generate_fernet_key(password):
    return Fernet(urlsafe_b64encode(password.encode('utf-8').ljust(32)[:32]))

db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'cisco_meraki_clu_db.db')

def save_api_key(api_key, fernet):
    encrypted_api_key = fernet.encrypt(api_key.encode('utf-8'))

    try:
        conn = sqlite3.connect(db_path)
        conn.execute("INSERT OR REPLACE INTO sensitive_data (id, data) VALUES (1, ?)", (encrypted_api_key,))
        conn.commit()
        print("API key saved successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def get_api_key(fernet):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT data FROM sensitive_data WHERE id = 1")
        encrypted_api_key = cursor.fetchone()
        api_key = fernet.decrypt(encrypted_api_key[0]) if encrypted_api_key else None
        return api_key.decode('utf-8') if api_key else None
    except Exception as e:
        print(colored("An error occurred while accessing the database: ", "red") + str(e))
        return None
    finally:
        if conn:
            conn.close()