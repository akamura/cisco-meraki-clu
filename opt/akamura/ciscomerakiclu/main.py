#**************************************************************************
#   App:         Cisco Meraki CLU                                         *
#   Version:     1.0                                                      *
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
import shutil
import subprocess
import sys
import logging
import traceback

required_packages = {
    "tabulate": "tabulate",
    "getpass": "getpass",
    "pathlib": "pathlib",
    "datetime": "datetime",
    "termcolor": "termcolor",
    "pysqlcipher3": "pysqlcipher3",
    "rich": "rich"
}

missing_packages = []
for module, package in required_packages.items():
    try:
        __import__(module)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print("Missing required Python packages: " + ", ".join(missing_packages))
    print("Please install them using the following command:")
    print(f"{sys.executable} -m pip install " + " ".join(missing_packages))
    sys.exit(1)

from tabulate import tabulate
from getpass import getpass
from pathlib import Path
from datetime import datetime
from termcolor import colored
from pysqlcipher3 import dbapi2 as sqlite
from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE

# ==================================================
# IMPORT custom modules
# ==================================================
from modules import api_key_manager
from modules import meraki
from modules.meraki import export_devices_to_csv


# ==================================================
# ERROR logging
# ==================================================
# Logging configuration in your Python script
logger = logging.getLogger('ciscomerakiclu')
logger.setLevel(logging.ERROR)

log_directory = '/opt/akamura/ciscomerakiclu/log/'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = os.path.join(log_directory, 'error.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# ==================================================
# CLEAR the screen and present the main menu
# ==================================================
def clear_screen():
    os.system('clear')

def print_ascii_art():
    ascii_art = """
     _____ _                 __  __                _    _    _____ _     _    _ 
    / ____(_)               |  \/  |              | |  (_)  / ____| |   | |  | |
   | |     _ ___  ___ ___   | \  / | ___ _ __ __ _| | ___  | |    | |   | |  | |
   | |    | / __|/ __/ _ \  | |\/| |/ _ \ '__/ _` | |/ / | | |    | |   | |  | |
   | |____| \__ \ (_| (_) | | |  | |  __/ | | (_| |   <| | | |____| |___| |__| |
    \_____|_|___/\___\___/  |_|  |_|\___|_|  \__,_|_|\_\_|  \_____|______\____/ 
    
    """
    print(ascii_art)
                    
def get_terminal_size():
    columns, rows = shutil.get_terminal_size()
    return columns, rows


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
        input("Press Enter to retry")
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
        input("Press Enter to close the program")
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
        input("Press Enter to close the program")
        return False
    else:
        print(colored("\nInvalid input. Please try again.\n", "red"))
        input("Press Enter to retry")
        return False



# ==================================================
# CREATE the application layout
# ==================================================
def print_header(title):
    columns, rows = get_terminal_size()
    print("-" * columns)

def print_menu(options):
    columns, rows = get_terminal_size()
    half = len(options) // 2
    for i in range(half):
        left_option = f"{i+1}. {options[i]}"
        right_option = f"{i+1+half}. {options[i+half]}" if i + half < len(options) else ''
        print(f"{left_option:<{columns//2}}{right_option}")

def print_footer(footer_text):
    columns, _ = get_terminal_size()
    print("-" * columns)
    print("\n")
    lines = footer_text.split('\n')
    for line in lines:
        print(line.ljust(columns))
    print("\n")


# ==================================================
# VISUALIZE the Main Menu
# ==================================================
def main_menu(db_password):
    while True:
        clear_screen()
        print_ascii_art()
        header = ""

        # Retrieve the API key at the start of each loop iteration
        api_key = api_key_manager.get_api_key(db_password)
        options = [
            "Appliance (under dev)", 
            "Switches and APs", 
            "Meraki Platform Tools (under dev)", 
            "Extra Tools (under dev)", 
            f"{'Edit your Cisco Meraki API Key' if api_key else 'Set your Cisco Meraki API Key'}",
            "Exit the CLU"
        ]
        current_year = datetime.now().year
        footer = f"© {current_year} Matia Zanella\nProject page: https://github.com/akamura/cisco-meraki-clu\nLike? ☕️ Fuel me a coffee: https://www.paypal.com/paypalme/matiazanella/\n\nDisclaimer: This utility is not an official Cisco Meraki product but is based on the official Cisco Meraki API.\nIt is intended to provide Network Administrators with an easy daily companion in the swiss army knife."
        
        print_header(header)
        print_menu(options)
        print_footer(footer)

        choice = input(colored("Choose a menu option [1-6]: ", "cyan"))
        
        if choice.isdigit() and 1 <= int(choice) <= 6:
            if choice == '2':
                if api_key:
                    submenu_sw_and_ap(api_key)
                else:
                    print("Please set the Cisco Meraki API key first.")
                choice = input(colored("\nPress Enter to return to the main menu...", "green"))

            elif choice == '5':
                manage_api_key(db_password)
            elif choice == '6':
                clear_screen()
                print_ascii_art()

                print("\n" * 1)
                print("Thank you for using the Cisco Meraki Command Line Utility!")
                print("Exiting the program. Goodbye, and have a wonderful day!")
                print("\nIf you have ideas or want to leave feedback, you are more than welcome to discuss it on GitHub\nhttps://github.com/akamura/cisco-meraki-clu/discussions 🚀")
                print("\n" * 2)

                break
            else:
                
                print(colored(f"You selected: {options[int(choice) - 1]}", "green"))
        else:
            print(colored("Invalid choice. Please try again.", "red"))

        print_footer(footer)

def manage_api_key(db_password):
    clear_screen()
    api_key = input("\nEnter the Cisco Meraki API Key: ")
    api_key_manager.save_api_key(db_password, api_key)


# ==================================================
# VISUALIZE Submenu for Switches and APs
# ==================================================
def submenu_sw_and_ap(api_key):
    while True:
        clear_screen()
        print_ascii_art()
        header = ""
        options = [
            "Select an Organization",
            "Return to Main Menu"
        ] 
        print_header(header)
        print_menu(options)
        choice = input(colored("\nChoose a menu option [1-2]: ", "cyan"))

        if choice == '1':
            select_organization(api_key)
        elif choice == '2':
            break

def select_organization(api_key):
    selected_org = meraki.select_organization(api_key)
    if selected_org:
        clear_screen()
        print_ascii_art()
        header = ""
        print_header(header)
        print(colored(f"\nYou selected {selected_org['name']} and these are the available networks:\n", "green"))
        select_network(api_key, selected_org['id'])


# ==================================================
# VISUALIZE device list in a beautiful table format
# ==================================================
def display_devices(api_key, network_id, device_type):
    devices = None
    if device_type == 'switches':
        devices = meraki.get_meraki_switches(api_key, network_id)
    elif device_type == 'access_points':
        devices = meraki.get_meraki_access_points(api_key, network_id)

    clear_screen()
    print_ascii_art()
    if devices:
        # Sort devices by 'name'
        devices = sorted(devices, key=lambda x: x.get('name', '').lower())

        table = Table(show_header=True, header_style="green", box=SIMPLE)

        # Prioritize specific columns
        priority_columns = ['name', 'mac', 'lanIp', 'serial', 'model']
        excluded_columns = ['networkId', 'details', 'lat', 'lng', 'firmware']
        other_columns = [key for key in devices[0].keys() if key not in priority_columns and key not in excluded_columns]

        # Add priority columns first, allowing text wrap
        for key in priority_columns:
            table.add_column(key.upper(), no_wrap=True)

        # Add other columns, allowing text wrap
        for key in other_columns:
            table.add_column(key.upper(), no_wrap=False)

        # Add rows to the table
        for device in devices:
            row_data = [str(device.get(key, "")) for key in priority_columns + other_columns]
            table.add_row(*row_data)

        console = Console()
        console.print(table)
    else:
        print(colored(f"No {device_type} found in the selected network.", "red"))

    choice = input(colored("\nPress Enter to return to the precedent menu...", "green"))


# ==================================================
# DEFINE how we process data inside Networks
# ==================================================
def select_network(api_key, organization_id):
    selected_network = meraki.select_network(api_key, organization_id)
    if selected_network:
        network_name = selected_network['name']
        network_id = selected_network['id']

        # Define the directory for exports
        downloads_path = str(Path.home() / "Downloads")
        current_date = datetime.now().strftime("%Y-%m-%d")
        meraki_dir = os.path.join(downloads_path, f"Cisco-Meraki-CLU-Export-{current_date}")
        os.makedirs(meraki_dir, exist_ok=True)

        while True:
            clear_screen()
            print_ascii_art()
            header = "Network Menu"
            options = [
                "List Switches",
                "List Access Points",
                "",
                "Download Switches CSV",
                "Download Access Points CSV",
                "Return to Main Menu"
            ]
            print_header(header)
            print_menu(options)
            
            # Print a line separator before the choice prompt
            columns, _ = get_terminal_size()
            print("-" * columns)

            choice = input(colored("\nChoose a menu option [1-6]: ", "cyan"))
            
            if choice == '1':
                display_devices(api_key, network_id, 'switches')
            elif choice == '2':
                display_devices(api_key, network_id, 'access_points')
            elif choice == '4':
                switches = meraki.get_meraki_switches(api_key, network_id)
                if switches:
                    export_devices_to_csv(switches, network_name, 'switches', meraki_dir)
                else:
                    print("No switches to download.")
                choice = input(colored("\nPress Enter to return to the precedent menu...", "green"))
            elif choice == '5':
                access_points = meraki.get_meraki_access_points(api_key, network_id)
                if access_points:
                    export_devices_to_csv(access_points, network_name, 'access_points', meraki_dir)
                else:
                    print("No access points to download.")
                choice = input(colored("\nPress Enter to return to the precedent menu...", "green"))
            elif choice == '6':
                break


# ==================================================
# ERROR handling and logging
# ==================================================
if __name__ == "__main__":
    try:
        db_password = ""
        if not database_exists():
            os.system('clear')
            print_ascii_art()
            db_password = prompt_create_database()
        else:
            os.system('clear')
            print_ascii_art()
            db_password = getpass(colored("\n\nWelcome to Cisco Meraki Command Line Utility!\nThis program contains sensitive information. Please insert your password to continue: ", "green"))
            verify_database_password(db_password)
        main_menu(db_password)
    except Exception as e:
        logger.error("An error occurred", exc_info=True)
        print("An error occurred:")
        print(e)
        traceback.print_exc()
        input("Press Enter to exit...")