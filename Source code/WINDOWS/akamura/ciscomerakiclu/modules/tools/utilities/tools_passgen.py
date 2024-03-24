
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
import secrets
import string
import os
import csv

from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from csv import writer
from rich.box import SIMPLE
from settings import term_extra

def get_user_input(prompt, input_type=str, condition=lambda x: True):
    """Utility function to get user input and validate it."""
    while True:
        user_input = input(prompt)
        try:
            value = input_type(user_input)
            if condition(value):
                return value
            else:
                raise ValueError
        except ValueError:
            print(f"Invalid input. Please enter a valid {input_type.__name__}.")

def generate_passwords(length, characters, quantity, case_option, allow_repeats):
    """Generate a specified quantity of secure passwords and apply case transformation."""
    if not allow_repeats:
        if length > len(characters):
            raise ValueError("Password length exceeds unique characters available without repeats.")
        passwords = [''.join(secrets.SystemRandom().sample(characters, length)) for _ in range(quantity)]
    else:
        passwords = [''.join(secrets.choice(characters) for _ in range(length)) for _ in range(quantity)]
    
    if case_option == 'uppercase':
        passwords = [pwd.upper() for pwd in passwords]
    elif case_option == 'lowercase':
        passwords = [pwd.lower() for pwd in passwords]
    return passwords

base_folder_path = str(Path.home() / "Downloads" / "Cisco-Meraki-CLU-Tools-Passgen-Export")

def export_passwords_to_csv(passwords):
    term_extra.clear_screen()
    term_extra.print_ascii_art()

    if not passwords:
        print("No passwords data to export.")
        return

    os.makedirs(base_folder_path, exist_ok=True)

    # Format the filename using current date and number of passwords
    current_date = datetime.now().strftime("%Y-%m-%d")
    number_of_passwords = len(passwords)
    filename = f"passwords_{current_date}_{number_of_passwords}.csv"
    full_filename = os.path.join(base_folder_path, filename)

    priority_columns = ['Password list']

    with open(full_filename, 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        csv_writer.writerow(priority_columns)

        for password in passwords:
            csv_writer.writerow([password])
            
    print(f"Passwords have been exported to {full_filename}. Press Enter to continue.")
    input()

def main():
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    console = Console()
    print("Welcome to the Secure Password Generator!")
    
    length = get_user_input("Enter the desired password length (at least 8): ", int, lambda x: x >= 8)
    include_symbols = get_user_input("Include symbols (e.g., @#$%)? (yes/no): ", str, lambda x: x.lower() in ['yes', 'no']) == 'yes'
    include_numbers = get_user_input("Include numbers? (yes/no): ", str, lambda x: x.lower() in ['yes', 'no']) == 'yes'
    include_special_characters = get_user_input("Include special characters (e.g. !%^&*())? (yes/no): ", str, lambda x: x.lower() in ['yes', 'no']) == 'yes'
    exclude_chars = get_user_input("Enter any characters to exclude (leave blank if none): ", str)
    quantity = get_user_input("How many passwords to generate? ", int, lambda x: x > 0)
    case_option = get_user_input("Should the password be in uppercase, lowercase, or mixed? (Enter: uppercase/lowercase/mixed): ", str, lambda x: x.lower() in ['uppercase', 'lowercase', 'mixed'])
    allow_repeats = get_user_input("Allow characters to repeat? (yes/no): ", str, lambda x: x.lower() in ['yes', 'no']) == 'yes'
    
    characters = string.ascii_letters
    if include_numbers:
        characters += string.digits
    if include_symbols:
        characters += string.punctuation
    if include_special_characters:
        characters += "!%^&*()"
    characters = ''.join(ch for ch in characters if ch not in exclude_chars)
    
    try:
        passwords = generate_passwords(length, characters, quantity, case_option, allow_repeats)
        
        table = Table(title="Generated Passwords", header_style="bold green", box=SIMPLE)
        table.add_column("Index", style="dim", width=12)
        table.add_column("Password", justify="left")
        for idx, pwd in enumerate(passwords, start=1):
            table.add_row(str(idx), pwd)
        console.print(table)

    except ValueError as e:
        print(e)
        return
    
    export_csv = get_user_input("Do you want to export the passwords to a CSV file? (yes/no): ", str, lambda x: x.lower() in ['yes', 'no']) == 'yes'
    if export_csv:
        export_passwords_to_csv(passwords)

if __name__ == "__main__":
    main()