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
from pathlib import Path
from datetime import datetime
from termcolor import colored


# ==================================================
# IMPORT custom modules
# ==================================================
from modules.meraki import meraki_api 
from modules.meraki import meraki_ms_mr
from modules.meraki import meraki_mx
from modules.tools.dnsbl import dnsbl_check
from modules.tools.utilities import tools_ipcheck
from modules.tools.utilities import tools_passgen
from modules.tools.utilities import tools_subnetcalc

from settings import term_extra


# ==================================================
# VISUALIZE submenus for Appliance, Switches and APs
# ==================================================
def select_organization(api_key):
    selected_org = meraki_api.select_organization(api_key)
    return selected_org

def submenu_sw_and_ap(api_key):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        options = ["Select an Organization", "Return to Main Menu"]
        
        # Description header over the menu
        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│".ljust(59) + "│")
        for index, option in enumerate(options, start=1):
            print(f"│ {index}. {option}".ljust(59) + "│")
        print("│".ljust(59) + "│")
        print("└" + "─" * 58 + "┘")

        choice = input(colored("\nChoose a menu option [1-2]: ", "cyan"))

        if choice == '1':
            selected_org = select_organization(api_key)
            if selected_org:
                term_extra.clear_screen()
                term_extra.print_ascii_art()
                print(colored(f"\nYou selected {selected_org['name']}.\n", "green"))
                select_network(api_key, selected_org['id'])
        elif choice == '2':
            break

def submenu_mx(api_key):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        options = ["Select an Organization", "Return to Main Menu"]

        # Description header over the menu
        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│".ljust(59) + "│")
        for index, option in enumerate(options, start=1):
            print(f"│ {index}. {option}".ljust(59) + "│")
        print("│".ljust(59) + "│")
        print("└" + "─" * 58 + "┘")

        choice = input(colored("\nChoose a menu option [1-2]: ", "cyan"))

        if choice == '1':
            selected_org = select_organization(api_key)
            if selected_org:
                term_extra.clear_screen()
                term_extra.print_ascii_art()
                print(colored(f"\nYou selected {selected_org['name']}.\n", "green"))
                meraki_mx.select_mx_network(api_key, selected_org['id'])
        elif choice == '2':
            break


# ==================================================
# DEFINE how to process data inside Networks
# ==================================================
def select_network(api_key, organization_id):
    selected_network = meraki_api.select_network(api_key, organization_id)
    if selected_network:
        network_name = selected_network['name']
        network_id = selected_network['id']

        downloads_path = str(Path.home() / "Downloads")
        current_date = datetime.now().strftime("%Y-%m-%d")
        meraki_dir = os.path.join(downloads_path, f"Cisco-Meraki-CLU-Export-{current_date}")
        os.makedirs(meraki_dir, exist_ok=True)

        while True:
            term_extra.clear_screen()
            term_extra.print_ascii_art()

            options = [
                "Get Switches",
                "Get Access Points",
                "Get Switch Ports",
                "Get Devices Statuses",
                "Download Switches CSV",
                "Download Access Points CSV",
                "Download Devices Statuses CSV (under dev)",
                "Return to Main Menu"
            ]
            
            # Description header over the menu
            print("\n")
            print("┌" + "─" * 58 + "┐")
            print("│".ljust(59) + "│")
            for index, option in enumerate(options, start=1):
                print(f"│ {index}. {option}".ljust(59) + "│")
            print("│".ljust(59) + "│")
            print("└" + "─" * 58 + "┘")

            choice = input(colored("\nChoose a menu option [1-8]: ", "cyan"))

            if choice == '1':
                meraki_ms_mr.display_devices(api_key, network_id, 'switches')
            elif choice == '2':
                meraki_ms_mr.display_devices(api_key, network_id, 'access_points')
            elif choice == '3':
                serial_number = input("\nEnter the switch serial number: ")
                if serial_number:
                    print(f"Fetching switch ports for serial: {serial_number}")
                    meraki_ms_mr.display_switch_ports(api_key, serial_number)
                else:
                    print("[red]Invalid input. Please enter a valid serial number.[/red]")
            elif choice == '4':
                meraki_ms_mr.display_organization_devices_statuses(api_key, organization_id, network_id)
            elif choice == '5':
                switches = meraki_api.get_meraki_switches(api_key, network_id)
                if switches:
                    meraki_api.export_devices_to_csv(switches, network_name, 'switches', meraki_dir)
                else:
                    print("No switches to download.")
                choice = input(colored("\nPress Enter to return to the precedent menu...", "green"))
                
            elif choice == '6':
                access_points = meraki_api.get_meraki_access_points(api_key, network_id)
                if access_points:
                    meraki_api.export_devices_to_csv(access_points, network_name, 'access_points', meraki_dir)
                else:
                    print("No access points to download.")
                choice = input(colored("\nPress Enter to return to the precedent menu...", "green"))

            elif choice == '8':
                break
    else:
        print("[red]No network selected or invalid organization ID.[/red]")


# ==================================================
# DEFINE the Swiss Army Knife submenu
# ==================================================
def swiss_army_knife_submenu(fernet):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()

        options = [
            "DNSBL Check",
            "IP Check",
            "MTU Correct Size Calculator [under dev]",
            "Password Generator",
            "Subnet Calculator",
            "WiFi Spectrum Analyzer [under dev]",
            "WiFi Adapter Info [under dev]",
            "WiFi Neighbors [under dev]",
            "Return to Main Menu"
        ]

        # Description header over the menu
        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│".ljust(59) + "│")
        for index, option in enumerate(options, start=1):
            print(f"│ {index}. {option}".ljust(59) + "│")
        print("│".ljust(59) + "│")
        print("└" + "─" * 58 + "┘")

        choice = input(colored("Choose a menu option [1-9]: ", "cyan"))

        if choice == '1':
            dnsbl_check.main()
        elif choice == '2':
            tools_ipcheck.main(fernet)
        elif choice == '3':
            pass
        elif choice == '4':
            tools_passgen.main()
        elif choice == '5':
            tools_subnetcalc.main()
        elif choice == '6':
            pass
        elif choice == '7':
            pass
        elif choice == '8':
            pass
        elif choice == '9':
            break
        else:
            print(colored("Invalid input. Please enter a number between 1 and 9.", "red"))