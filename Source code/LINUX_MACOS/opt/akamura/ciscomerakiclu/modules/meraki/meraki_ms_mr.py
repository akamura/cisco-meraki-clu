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
from datetime import datetime
from termcolor import colored
from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE 

 
# ==================================================
# IMPORT custom modules
# ==================================================
from modules.meraki import meraki_api 
from settings import term_extra


# ==================================================
# DEFINE how to retrieve Switch Ports data
# ==================================================
def display_switch_ports(api_key, serial_number):
    port_statuses = []
    
    try:
        switch_ports = meraki_api.get_switch_ports(api_key, serial_number)
    except Exception as e:
        print(f"[red]Failed to fetch switch port configurations: {e}[/red]")
        return

    try:
        port_statuses = meraki_api.get_switch_ports_statuses_with_timespan(api_key, serial_number) or []
    except Exception as e:
        print(f"[red]Failed to fetch real-time port statuses/packets: {e}[/red]")

    if switch_ports:
        table = Table(show_header=True, header_style="bold green", box=SIMPLE)

        columns = [
            ("Port", 5), ("Name", 30), ("Enabled", 5),
            ("PoE", 5), ("Type", 10), ("VLAN", 5),
            ("Allowed VLANs", 8), ("RSTP", 5), ("STP Guard", 10),
            ("Storm Cont", 5), ("In (Gbps)", 8), ("Out (Gbps)", 8),
            ("powerUsageInWh", 8), ("warnings", 30), ("errors", 30)
        ]
        for col_name, col_width in columns:
            table.add_column(col_name, style="dim", width=col_width)

        for port in switch_ports:
            port_id = port.get('portId', 'N/A')
            status = next((item for item in port_statuses if item.get("portId") == port_id), {})

            row_data = [
                port.get('portId', 'N/A'),
                port.get('name', 'N/A'),
                "Yes" if port.get('enabled') else "No",
                "Yes" if port.get('poeEnabled') else "No",
                port.get('type', 'N/A'),
                str(port.get('vlan', 'N/A')),
                port.get('allowedVlans', 'N/A'),
                "Yes" if port.get('rstpEnabled') else "No",
                port.get('stpGuard', 'N/A'),
                "Yes" if port.get('stormControlEnabled') else "No",
                f"{float(status.get('usageInKb', {}).get('recv', 'N/A')) / 1000000:.2f}" if status.get('usageInKb', {}).get('recv', 'N/A') != 'N/A' else 'N/A',
                f"{float(status.get('usageInKb', {}).get('sent', 'N/A')) / 1000000:.2f}" if status.get('usageInKb', {}).get('sent', 'N/A') != 'N/A' else 'N/A',
                str(status.get('powerUsageInWh', 'N/A')),
                str(status.get('warnings', 'N/A')),
                str(status.get('errors', 'N/A'))
            ]
            table.add_row(*row_data)

        console = Console()
        console.print("\nSwitch Ports:")
        console.print(table)
    else:
        print("[red]No ports found for the given serial number or failed to fetch ports.[/red]")

    input("Press Enter to continue...")


# ==================================================
# DISPLAY device list in a beautiful table format
# ==================================================
def display_devices(api_key, network_id, device_type):
    devices = None
    if device_type == 'switches':
        devices = meraki_api.get_meraki_switches(api_key, network_id)
    elif device_type == 'access_points':
        devices = meraki_api.get_meraki_access_points(api_key, network_id)

    term_extra.clear_screen()
    term_extra.print_ascii_art()

    if devices:
        devices = sorted(devices, key=lambda x: x.get('name', '').lower())
        table = Table(show_header=True, header_style="bold green", box=SIMPLE)

        priority_columns = ['name', 'mac', 'lanIp', 'serial', 'model']
        excluded_columns = ['networkId', 'details', 'lat', 'lng', 'firmware']
        other_columns = [key for key in devices[0].keys() if key not in priority_columns and key not in excluded_columns]

        for key in priority_columns:
            table.add_column(key.upper(), no_wrap=True)

        for key in other_columns:
            table.add_column(key.upper(), no_wrap=False)

        for device in devices:
            row_data = [str(device.get(key, "")) for key in priority_columns + other_columns]
            table.add_row(*row_data)

        console = Console()
        console.print(table)
    else:
        print(colored(f"No {device_type} found in the selected network.", "red"))

    choice = input(colored("\nPress Enter to return to the precedent menu...", "green"))


# ==================================================
# DISPLAY organization devices statuses in table
# ==================================================
def display_organization_devices_statuses(api_key, organization_id, network_id):
    devices_statuses = meraki_api.get_organization_devices_statuses(api_key, organization_id)
    term_extra.clear_screen()
    term_extra.print_ascii_art()

    filtered_devices_statuses = [device for device in devices_statuses if device.get('networkId') == network_id]
    filtered_devices_statuses = [device for device in filtered_devices_statuses if device.get('productType') in ["switch", "wireless"]]

    if devices_statuses:
        devices_statuses = [device for device in devices_statuses if device.get('productType') in ["switch", "wireless"]]
        devices_statuses = sorted(devices_statuses, key=lambda x: x.get('name', '').lower())
        table = Table(show_header=True, header_style="bold green", box=SIMPLE)

        priority_columns = ['name', 'serial', 'mac', 'ipType', 'lanIp', 'gateway', 'primaryDns', 'secondaryDns', 'PSU 1', 'PSU 2', 'status', 'lastReportedAt']
        
        for key in priority_columns:
            formatted_key = key if not key.startswith("PSU") else key.replace(" ", "")
            table.add_column(formatted_key.upper(), no_wrap=True)
        
        for device in devices_statuses:
            row_data = []
            for key in priority_columns[:-4]:
                value = str(device.get(key, "N/A"))
                row_data.append(value)

            add_power_supply_statuses(device, row_data)

            status_value = str(device.get('status', "N/A"))
            if status_value.lower() == 'online':
                row_data.append(f"[green]{status_value}[/green]")
            elif status_value.lower() == 'dormant':
                row_data.append(f"[yellow]{status_value}[/yellow]")
            elif status_value.lower() == 'offline' or status_value.lower() == 'alerting':
                row_data.append(f"[red]{status_value}[/red]")
            else:
                row_data.append(status_value)

            last_reported_at = device.get('lastReportedAt')
            if last_reported_at:
                original_datetime = datetime.strptime(last_reported_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_datetime = original_datetime.strftime("%Y-%m-%d %H:%M")
                row_data.append(formatted_datetime)
            else:
                row_data.append("N/A")

            table.add_row(*row_data)

        console = Console()
        console.print(table)

    else:
        print("[red]No 'switch' devices found in the selected network.[/red]")
    choice = input("\nPress Enter to return to the previous menu... ")


# ==================================================
# INTEGRATE additional JSON data for PSU's details
# ==================================================
def add_power_supply_statuses(device, row_data):
    power_statuses = []
    if 'components' in device and 'powerSupplies' in device['components']:
        for slot in [1, 2]:
            power_supply = next((ps for ps in device['components']['powerSupplies'] if ps.get('slot') == slot), None)
            if power_supply:
                status = power_supply.get('status', 'N/A')
                if status.lower() == 'powering':
                    power_statuses.append(f"[green]{status}[/green]")
                elif status.lower() == 'disconnected':
                    power_statuses.append(f"[red]{status}[/red]")
                else:
                    power_statuses.append(status)
            else:
                power_statuses.append("N/A")
    else:
        power_statuses = ["N/A", "N/A"]
    row_data.extend(power_statuses)