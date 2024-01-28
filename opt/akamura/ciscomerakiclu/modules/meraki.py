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
import requests
import subprocess
import sys
import csv
import os
try:
    from tabulate import tabulate
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
from datetime import datetime
try:
    from termcolor import colored
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "termcolor"])


# ==================================================
# EXPORT device list in a beautiful table format
# ==================================================
def export_devices_to_csv(devices, network_name, device_type, base_folder_path):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{network_name}_{current_date}_{device_type}.csv"
    file_path = os.path.join(base_folder_path, filename)

    if devices:
        # Priority columns
        priority_columns = ['name', 'mac', 'lanIp', 'serial', 'model', 'firwmare', 'tags']

        # Gather all columns from the devices
        all_columns = set(key for device in devices for key in device.keys())
        
        # Reorder columns so that priority columns come first
        ordered_columns = priority_columns + [col for col in all_columns if col not in priority_columns]

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            # Convert fieldnames to uppercase
            fieldnames = [col.upper() for col in ordered_columns]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for device in devices:
                # Convert keys to uppercase to match fieldnames
                row = {col.upper(): device.get(col, '') for col in ordered_columns}
                writer.writerow(row)
            
        print(f"Data exported to {file_path}")
    else:
        print("No data to export.")


# ==================================================
# GET a list of Organizations
# ==================================================
def get_meraki_organizations(api_key):
    url = "https://api.meraki.com/api/v1/organizations"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch organizations")
        return None

def select_organization(api_key):
    organizations = get_meraki_organizations(api_key)
    if organizations:
        for idx, org in enumerate(organizations, 1):
            print(f"{idx}. {org['name']}")

        choice = input(colored("\nSelect an Organization (enter the number): ", "cyan"))
        try:
            selected_index = int(choice) - 1
            if 0 <= selected_index < len(organizations):
                return organizations[selected_index]
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a number.")

    return None


# ==================================================
# GET a list of Networks in an Organization
# ==================================================
def get_meraki_networks(api_key, organization_id):
    url = f"https://api.meraki.com/api/v1/organizations/{organization_id}/networks"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        networks = response.json()
        # Sort the networks by name
        networks.sort(key=lambda x: x['name'])
        return networks
    else:
        print("Failed to fetch networks")
        return None


# ==================================================
# SELECT a Network in an Organization
# ==================================================
def select_network(api_key, organization_id):
    networks = get_meraki_networks(api_key, organization_id)
    if networks:
        for idx, network in enumerate(networks, 1):
            print(f"{idx}. {network['name']}")

        choice = input(colored("\nSelect an Organization Network (enter the number): ", "cyan"))
        try:
            selected_index = int(choice) - 1
            if 0 <= selected_index < len(networks):
                return networks[selected_index]
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a number.")

    return None


# ==================================================
# GET a list of Switches in an Network
# ==================================================
def get_meraki_switches(api_key, network_id):
    url = f"https://api.meraki.com/api/v1/networks/{network_id}/devices"
    headers = {"X-Cisco-Meraki-API-Key": api_key, "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        devices = response.json()
        switches = [device for device in devices if device['model'].startswith('MS')]
        return switches
    else:
        print("Failed to fetch switches")
        return None

def display_switches(api_key, network_id):
    switches = get_meraki_switches(api_key, network_id)
    if switches:
        print(tabulate(switches, headers="keys", tablefmt="pretty"))
    else:
        print("No switches found in the selected network.")


# ==================================================
# GET a list of Access Points in an Network
# ==================================================
def get_meraki_access_points(api_key, network_id):
    url = f"https://api.meraki.com/api/v1/networks/{network_id}/devices"
    headers = {"X-Cisco-Meraki-API-Key": api_key, "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        devices = response.json()
        # Filter to include only access points (APs)
        access_points = [device for device in devices if device['model'].startswith('MR')]
        return access_points
    else:
        print("Failed to fetch access points")
        return None


# =======================================================================
# [UNDER DEVELOPMENT] GET a list of VLANs and Static Routes in an Network
# =======================================================================
def get_meraki_vlans(api_key, network_id):
    url = f"https://api.meraki.com/api/v1/networks/{network_id}/vlans"
    headers = {"X-Cisco-Meraki-API-Key": api_key, "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch VLANs: {response.status_code}, {response.text}")
        return None

def get_meraki_static_routes(api_key, network_id):
    url = f"https://api.meraki.com/api/v1/networks/{network_id}/staticRoutes"
    headers = {"X-Cisco-Meraki-API-Key": api_key, "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch static routes: {response.status_code}, {response.text}")
        return None