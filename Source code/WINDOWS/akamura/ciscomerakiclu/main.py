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
import sys
import logging
import traceback

required_packages = {
    "tabulate": "tabulate",
    "pathlib": "pathlib",
    "datetime": "datetime",
    "termcolor": "termcolor",
    "requests": "requests",
    "rich": "rich",
    "setuptools": "setuptools",
    "cryptography": "cryptography"
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

from getpass import getpass
from datetime import datetime
from termcolor import colored 


# ==================================================
# IMPORT custom modules
# ==================================================
from api import meraki_api_manager
from settings import term_extra
from settings import db_creator
from utilities import submenu


# ==================================================
# ERROR logging
# ==================================================
logger = logging.getLogger('ciscomerakiclu')
logger.setLevel(logging.ERROR)

log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = os.path.join(log_directory, 'error.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
   

# ==================================================
# VISUALIZE the Main Menu
# ==================================================
def main_menu(fernet):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()

        api_key = meraki_api_manager.get_api_key(fernet)
        ipinfo_token = db_creator.get_tools_ipinfo_access_token(fernet)
        options = [
            "Network wide [under dev]",
            "Security & SD-WAN", 
            "Switch and wireless",
            "Environmental [under dev]", 
            "Organization [under dev]", 
            "The Swiss Army Knife", 
            f"{'Edit Cisco Meraki API Key' if api_key else 'Set Cisco Meraki API Key'}",
            f"{'Edit IPinfo Token' if ipinfo_token else 'Set IPinfo Token'}",
            "Exit the Command Line Utility"
        ]
        current_year = datetime.now().year
        footer = f"\033[1mPROJECT PAGE\033[0m\n© {current_year} Matia Zanella\nhttps://developer.cisco.com/codeexchange/github/repo/akamura/cisco-meraki-clu/\n\n\033[1mSUPPORT ME\033[0m\n☕️ Fuel me with a coffee if you found it useful https://www.paypal.com/paypalme/matiazanella/\n\n\033[1mDISCLAIMER\033[0m\nThis utility is not an official Cisco Meraki product but is based on the official Cisco Meraki API.\nIt is intended to provide Network Administrators with an easy daily companion in the swiss army knife."
        
        # Description header over the menu
        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│".ljust(59) + "│")
        for index, option in enumerate(options, start=1):
            print(f"│ {index}. {option}".ljust(59) + "│")
        print("│".ljust(59) + "│")
        print("└" + "─" * 58 + "┘")

        term_extra.print_footer(footer)
        choice = input(colored("Choose a menu option [1-9]: ", "cyan"))
        
        if choice.isdigit() and 1 <= int(choice) <= 9:
            if choice == '1':
                pass
            elif choice == '2':
                if api_key:
                    submenu.submenu_mx(api_key)
                else:
                    print("Please set the Cisco Meraki API key first.")
                input(colored("\nPress Enter to return to the main menu...", "green"))

            elif choice == '3':
                if api_key:
                    submenu.submenu_sw_and_ap(api_key)
                else:
                    print("Please set the Cisco Meraki API key first.")
                input(colored("\nPress Enter to return to the main menu...", "green"))
            elif choice == '4':
                pass
            elif choice == '5':
                pass
            elif choice == '6':
                submenu.swiss_army_knife_submenu(fernet)
            elif choice == '7':
                manage_api_key(fernet)
            elif choice == '8':
                manage_ipinfo_token(fernet)
            elif choice == '9':
                term_extra.clear_screen()
                term_extra.print_ascii_art()

                print("\nThank you for using the Cisco Meraki Command Line Utility!")
                print("Exiting the program. Goodbye, and have a wonderful day!")
                print("\n🚀 \033[1mCONTRIBUTE\033[0m\nThis is not just a project; it's a community effort.\nI'm inviting you to be a part of this journey.\nStar it, fork it, contribute, or just play around with it.\nEvery feedback, issue, or pull request is an opportunity for us to make this tool even more amazing.\nYou are more than welcome to discuss it on GitHub https://github.com/akamura/cisco-meraki-clu/discussions")
                print("\n" * 2)

                break
            else:
                print(colored(f"You selected: {options[int(choice) - 1]}", "green"))
        else:
            print(colored("Invalid choice. Please try again.", "red"))

def manage_api_key(fernet):
    term_extra.clear_screen()
    api_key = input("\nEnter the Cisco Meraki API Key: ")
    meraki_api_manager.save_api_key(api_key, fernet)

def manage_ipinfo_token(fernet):
    term_extra.clear_screen()
    current_token = db_creator.get_tools_ipinfo_access_token(fernet)
    if current_token:
        print(colored(f"Current IPinfo Token: {current_token}", "yellow"))
        change = input("Do you want to change it? [yes/no]: ").lower()
        if change != 'yes':
            return
    
    new_token = input("\nEnter the new IPinfo access token: ")
    if new_token:
        db_creator.store_tools_ipinfo_access_token(new_token, fernet)
        print(colored("\nIPinfo access token saved successfully.", "green"))
    else:
        print(colored("No token entered. No changes made.", "red"))

# ==================================================
# ERROR handling and logging
# ==================================================
if __name__ == "__main__":
    try:
        db_path = 'db/cisco_meraki_clu_db.db'
        if not db_creator.database_exists(db_path):
            os.system('cls')  # Clears the terminal screen.
            term_extra.print_ascii_art()
            if db_creator.prompt_create_database():
                db_password = getpass(colored("\nEnter a password for encrypting the database: ", "green"))
                fernet = db_creator.generate_fernet_key(db_password)
                db_creator.update_database_schema(db_path, db_password)  # Update the database schema after creation.
            else:
                print(colored("Database creation cancelled. Exiting program.", "yellow"))
                exit()
        else:
            os.system('cls')  # Clears the terminal screen.
            term_extra.print_ascii_art()
            db_password = getpass(colored("\n\nWelcome to Cisco Meraki Command Line Utility!\nThis program contains sensitive information. Please insert your password to continue: ", "green"))
            fernet = db_creator.generate_fernet_key(db_password)

        # At this point, the database exists, so update the schema as needed.
        db_creator.update_database_schema(db_path, db_password)  # Ensure the schema is updated for existing databases too.
        
        main_menu(fernet)

    except Exception as e:
        logger.error("An error occurred", exc_info=True)
        print("An error occurred:")
        print(e)
        traceback.print_exc()
        input("\nPress Enter to exit.\n")