#**************************************************************************
#   App:         Cisco Meraki CLU                                         *
#   Version:     1.2                                                      *
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

from getpass import getpass
from datetime import datetime
from termcolor import colored
from pysqlcipher3 import dbapi2 as sqlite


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
# VISUALIZE the Main Menu
# ==================================================
def main_menu(db_password):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        header = ""

        # Retrieve the API key at the start of each loop iteration
        api_key = meraki_api_manager.get_api_key(db_password)
        options = [
            "Appliances", 
            "Switches and APs", 
            "Meraki Platform Tools (under dev)", 
            "Extra Tools (under dev)", 
            f"{'Edit your Cisco Meraki API Key' if api_key else 'Set your Cisco Meraki API Key'}",
            "Exit the CLU"
        ]
        current_year = datetime.now().year
        footer = f"© {current_year} Matia Zanella\nProject page: https://github.com/akamura/cisco-meraki-clu\nLike? ☕️ Fuel me a coffee: https://www.paypal.com/paypalme/matiazanella/\n\nDisclaimer: This utility is not an official Cisco Meraki product but is based on the official Cisco Meraki API.\nIt is intended to provide Network Administrators with an easy daily companion in the swiss army knife."
        
        term_extra.print_header(header)
        term_extra.print_menu(options)
        term_extra.print_footer(footer)

        choice = input(colored("Choose a menu option [1-6]: ", "cyan"))
        
        if choice.isdigit() and 1 <= int(choice) <= 6:
            if choice == '1':
                if api_key:
                    submenu.submenu_mx(api_key)
                else:
                    print("Please set the Cisco Meraki API key first.")
                choice = input(colored("\nPress Enter to return to the main menu...", "green"))

            elif choice == '2':
                if api_key:
                    submenu.submenu_sw_and_ap(api_key)
                else:
                    print("Please set the Cisco Meraki API key first.")
                choice = input(colored("\nPress Enter to return to the main menu...", "green"))

            elif choice == '5':
                manage_api_key(db_password)
            elif choice == '6':
                term_extra.clear_screen()
                term_extra.print_ascii_art()

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

        term_extra.print_footer(footer)

def manage_api_key(db_password):
    term_extra.clear_screen()
    api_key = input("\nEnter the Cisco Meraki API Key: ")
    meraki_api_manager.save_api_key(db_password, api_key)
    

# ==================================================
# ERROR handling and logging
# ==================================================
if __name__ == "__main__":
    try:
        db_password = ""
        if not db_creator.database_exists():
            os.system('clear')
            term_extra.print_ascii_art()
            db_password = db_creator.prompt_create_database()
        else:
            os.system('clear')
            term_extra.print_ascii_art()
            db_password = getpass(colored("\n\nWelcome to Cisco Meraki Command Line Utility!\nThis program contains sensitive information. Please insert your password to continue: ", "green"))
            db_creator.verify_database_password(db_password)
        main_menu(db_password)
    except Exception as e:
        logger.error("An error occurred", exc_info=True)
        print("An error occurred:")
        print(e)
        traceback.print_exc()
        input("\nPress Enter to exit.\n")