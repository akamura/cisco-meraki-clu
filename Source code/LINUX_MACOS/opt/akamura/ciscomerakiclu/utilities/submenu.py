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
from pathlib import Path
from datetime import datetime
from termcolor import colored


# ==================================================
# IMPORT custom modules
# ==================================================
from modules.meraki import meraki_api 
from modules.meraki import meraki_ms_mr
from modules.meraki import meraki_mx
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
        header = ""
        options = ["Select an Organization", "Return to Main Menu"]
        term_extra.print_header(header)
        term_extra.print_menu(options)
        choice = input(colored("\nChoose a menu option [1-2]: ", "cyan"))

        if choice == '1':
            selected_org = select_organization(api_key)
            if selected_org:
                term_extra.clear_screen()
                term_extra.print_ascii_art()
                term_extra.print_header(header)
                print(colored(f"\nYou selected {selected_org['name']}.\n", "green"))
                select_network(api_key, selected_org['id'])
        elif choice == '2':
            break

def submenu_mx(api_key):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        header = ""
        options = ["Select an Organization", "Return to Main Menu"]
        term_extra.print_header(header)
        term_extra.print_menu(options)
        choice = input(colored("\nChoose a menu option [1-2]: ", "cyan"))

        if choice == '1':
            selected_org = select_organization(api_key)
            if selected_org:
                term_extra.clear_screen()
                term_extra.print_ascii_art()
                term_extra.print_header(header)
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
            header = "Network Menu"
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
            term_extra.print_header(header)
            term_extra.print_menu(options)

            columns, _ = term_extra.get_terminal_size()
            print("-" * columns)

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