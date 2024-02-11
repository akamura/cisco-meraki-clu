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


from pathlib import Path
from datetime import datetime
from termcolor import colored
from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE
from rich.text import Text


# ==================================================
# IMPORT custom modules
# ================================================== 
from modules.meraki import meraki_api 
from settings import term_extra


# ==================================================
# DISPLAY Firewall Rules in a Beautiful Table Format
# ==================================================
def display_firewall_rules(api_key, network_id, organization_id):
    rules = meraki_api.get_l3_firewall_rules(api_key, network_id)
    policy_objects = meraki_api.get_organization_policy_objects(api_key, organization_id)
    policy_objects_groups = meraki_api.get_organization_policy_objects_groups(api_key, organization_id)

    # Create mappings for objects and groups
    obj_mapping = {str(obj['id']): obj['name'] for obj in policy_objects}
    group_mapping = {str(group['id']): group['name'] for group in policy_objects_groups}

    term_extra.clear_screen()
    term_extra.print_ascii_art()
    
    if rules:
        table = Table(show_header=True, header_style="green", box=SIMPLE)
        priority_columns = ['policy', 'protocol', 'srcPort', 'srcCidr', 'destPort', 'destCidr']
        excluded_columns = ['syslogEnabled']
        other_columns = [key for key in rules[0].keys() if key not in priority_columns and key not in excluded_columns]

        for key in priority_columns + other_columns:
            table.add_column(key.upper(), no_wrap=False)

        for rule in rules:
            for cidr_field in ['srcCidr', 'destCidr']:
                original_cidr = rule[cidr_field]

                if original_cidr.startswith("OBJ(") or original_cidr.startswith("GRP("):
                    obj_or_grp_id = original_cidr[4:-1]
                    rule[cidr_field] = obj_mapping.get(obj_or_grp_id, group_mapping.get(obj_or_grp_id, original_cidr))

            row_data = [str(rule.get(key, "")) for key in priority_columns + other_columns]
            policy = rule.get("policy", "").lower()
            row_style = "green" if policy == "allow" else "red" if policy == "deny" else ""
            styled_row_data = [Text(cell, style=row_style) for cell in row_data]
            table.add_row(*styled_row_data)

        console = Console()
        console.print(table)
    else:
        print(colored("No firewall rules found in the selected network.", "red"))
    input(colored("\nPress Enter to return to the previous menu...", "green"))




# ==================================================
# PROCESS Data Inside Networks (MX Firewall Rules)
# ==================================================
def select_mx_network(api_key, organization_id):
    selected_network = meraki_api.select_mx_network(api_key, organization_id)
    if selected_network:
        network_name = selected_network['name']
        network_id = selected_network['id']

        display_firewall_rules(api_key, network_id, organization_id)
        
        downloads_path = str(Path.home() / "Downloads")
        current_date = datetime.now().strftime("%Y-%m-%d")
        meraki_dir = os.path.join(downloads_path, f"Cisco-Meraki-CLU-Export-{current_date}")
        os.makedirs(meraki_dir, exist_ok=True)

        while True:
            term_extra.clear_screen()
            term_extra.print_ascii_art()
            header = "MX Firewall Rules Menu"
            options = [
                "List Firewall Rules",
                "Download Firewall Rules CSV",
                "Status (under dev)",
                "Return to Main Menu"
            ]
            term_extra.print_header(header)
            term_extra.print_menu(options)
            
            columns, _ = term_extra.get_terminal_size()
            print("-" * columns)

            choice = input(colored("\nChoose a menu option [1-4]: ", "cyan"))
            
            if choice == '1':
                display_firewall_rules(api_key, network_id)
            
            elif choice == '2':
                firewall_rules = meraki_api.get_l3_firewall_rules(api_key, network_id)
                
                if firewall_rules:
                    meraki_api.export_firewall_rules_to_csv(firewall_rules, network_name, meraki_dir)
                else:
                    print("No firewall rules to download.")
                choice = input(colored("\nPress Enter to return to the precedent menu...", "green"))

            elif choice == '4':
                break