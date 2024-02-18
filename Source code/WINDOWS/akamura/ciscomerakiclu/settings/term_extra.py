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
import shutil


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
# CLEAR the screen and present the main menu
# ==================================================
def clear_screen():
    os.system('cls')

def print_ascii_art():
    ascii_art = """
  ____ _                 __  __                _    _    ____ _    _   _ 
 / ___(_)___  ___ ___   |  \/  | ___ _ __ __ _| | _(_)  / ___| |  | | | |
| |   | / __|/ __/ _ \  | |\/| |/ _ \ '__/ _` | |/ / | | |   | |  | | | |
| |___| \__ \ (_| (_) | | |  | |  __/ | | (_| |   <| | | |___| |__| |_| |
 \____|_|___/\___\___/  |_|  |_|\___|_|  \__,_|_|\_\_|  \____|_____\___/ 
"""
    print(ascii_art)
                    
def get_terminal_size():
    columns, rows = shutil.get_terminal_size()
    return columns, rows