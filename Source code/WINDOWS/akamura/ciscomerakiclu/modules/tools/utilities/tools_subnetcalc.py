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
import ipaddress
import math
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

console = Console()

def get_network_from_user():
    while True:
        subnet_input = console.input("[cyan]Enter an IP address with subnet (e.g., 10.0.0.0/15): [/]")
        try:
            return ipaddress.ip_network(subnet_input, strict=False)
        except ValueError:
            console.print("[red]Invalid IP address or subnet. Please try again.[/]")

def divide_network(network, desired_subnets):
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    current_subnet_mask = network.prefixlen
    bits_needed = math.ceil(math.log(desired_subnets, 2))
    new_prefix_length = current_subnet_mask + bits_needed

    if new_prefix_length > 32:
        console.print(f"[yellow]Cannot divide {network} into {desired_subnets} parts due to IPv4 constraints.[/]")
        return [network]

    divided_subnets = list(network.subnets(new_prefix=new_prefix_length))
    return divided_subnets[:desired_subnets]

def display_table(subnets):
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    table = Table(show_header=True, header_style="bold green", box=SIMPLE)
    table.add_column("Subnet Address", style="cyan")
    table.add_column("Netmask", style="magenta")
    table.add_column("Address Range", style="yellow")
    table.add_column("Usable IP Range", style="green")
    table.add_column("Gateway", style="blue")
    table.add_column("Broadcast", style="red")
    table.add_column("Number of Hosts", style="purple")

    for subnet in subnets:
        address_range = f"{subnet.network_address} - {subnet.broadcast_address}"
        usable_range = f"{subnet.network_address + 1} - {subnet.broadcast_address - 1}" if subnet.prefixlen < 31 else "N/A"
        gateway = str(subnet.network_address + 1) if subnet.prefixlen < 31 else "N/A"
        num_hosts = subnet.num_addresses - 2 if subnet.prefixlen < 31 else "N/A"
        table.add_row(
            str(subnet),
            str(subnet.netmask),
            address_range,
            usable_range,
            gateway,
            str(subnet.broadcast_address),
            str(num_hosts)
        )
    
    console.print(table)

base_folder_path = str(Path.home() / "Downloads" / "Cisco-Meraki-CLU-Tools-Subnets-Export")

def export_to_csv(subnets):
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    if not subnets:
        print("No subnets data to export.")
        return

    os.makedirs(base_folder_path, exist_ok=True)

    current_date = datetime.now().strftime("%Y-%m-%d")
    first_subnet_cidr = str(subnets[0]).replace('/', '-') if subnets else 'no-subnets'
    filename = f"{first_subnet_cidr}_{current_date}.csv"
    full_filename = os.path.join(base_folder_path, filename)

    priority_columns = ['Subnet Address', 'Netmask', 'Address Range', 'Usable IP Range', 'Gateway', 'Broadcast', 'Number of Hosts']

    with open(full_filename, 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(priority_columns)

        for subnet in subnets:
            address_range = f"{subnet.network_address} - {subnet.broadcast_address}"
            usable_range = f"{subnet.network_address + 1} - {subnet.broadcast_address - 1}" if subnet.prefixlen < 31 else "N/A"
            gateway = subnet.network_address + 1 if subnet.prefixlen < 31 else "N/A"
            num_hosts = subnet.num_addresses - 2 if subnet.prefixlen < 31 else "N/A"
            csv_writer.writerow([
                str(subnet),
                str(subnet.netmask),
                address_range,
                usable_range,
                str(gateway),
                str(subnet.broadcast_address),
                str(num_hosts)
            ])
            
    print(f"Data is exported to {full_filename}. Press Enter to continue.")
    input()

def main():
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    network = get_network_from_user()
    divided_subnets = []

    while True:
        if not divided_subnets:
            division_input = Prompt.ask("[cyan]Into how many subnets do you want to divide? (default: 2)[/]", default="2")
            try:
                division_number = int(division_input)
                if division_number <= 0:
                    raise ValueError("Division number must be positive.")
                divided_subnets = divide_network(network, division_number)
            except ValueError as e:
                console.print(f"[red]Error: {e}. Please enter a valid positive integer.[/]")
                continue
        
        display_table(divided_subnets)
        
        choices = {
            "1": "edit divide",
            "2": "export to csv",
            "3": "start over",
            "4": "exit"
        }
        choice_prompt = "\n".join([f"[{number}] {action}" for number, action in choices.items()])
        choice = Prompt.ask(f"Choose an option:\n{choice_prompt}\n", default="4")
        
        if choices[choice] == "edit divide":
            division_input = Prompt.ask("[cyan]Into how many subnets do you want to divide?[/]")
            try:
                division_number = int(division_input)
                divided_subnets = divide_network(network, division_number)
           
            except ValueError:
                console.print("[red]Please enter a valid number.[/]")
        elif choices[choice] == "export to csv":
            export_to_csv(divided_subnets)
        elif choices[choice] == "start over":
            divided_subnets = []
            network = get_network_from_user()
        elif choices[choice] == "exit":
            break
        else:
            console.print("[red]Invalid choice. Please try again.[/]")

if __name__ == "__main__":
    main()