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
# EXPORT firewall rules in a beautiful table format
# ==================================================
def export_firewall_rules_to_csv(firewall_rules, network_name, base_folder_path):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{network_name}_{current_date}_MX_Firewall_Rules.csv"
    file_path = os.path.join(base_folder_path, filename)

    if firewall_rules:
        # Priority columns, adjust these based on your data
        priority_columns = ['policy', 'protocol', 'srcport', 'srccidr', 'destport','destcidr','comments']

        # Gather all columns from the firewall rules
        all_columns = set(key for rule in firewall_rules for key in rule.keys())
        
        # Reorder columns so that priority columns come first
        ordered_columns = priority_columns + [col for col in all_columns if col not in priority_columns]

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            # Convert fieldnames to uppercase
            fieldnames = [col.upper() for col in ordered_columns]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for rule in firewall_rules:
                # Convert keys to uppercase to match fieldnames
                row = {col.upper(): rule.get(col, '') for col in ordered_columns}
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
def get_meraki_networks(api_key, organization_id, per_page=5000):
    url = f"https://api.meraki.com/api/v1/organizations/{organization_id}/networks"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    params = {
        "perPage": per_page
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        networks = response.json()
        # Sort the networks by name
        networks.sort(key=lambda x: x['name'])
        return networks
    else:
        print("Failed to fetch networks")
        return None, None


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
# GET a list of Switch Ports and their Status
# ==================================================
def get_switch_ports(api_key, serial):
    url = f"https://api.meraki.com/api/v1/devices/{serial}/switch/ports"
    headers = {"X-Cisco-Meraki-API-Key": api_key, "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch switch ports for serial {serial}, status code: {response.status_code}")
        return None 
    
def get_switch_ports_statuses_with_timespan(api_key, serial, timespan=1800):
    url = f"https://api.meraki.com/api/v1/devices/{serial}/switch/ports/statuses"
    headers = {"X-Cisco-Meraki-API-Key": api_key, "Content-Type": "application/json"}
    # Assuming the API supports a 'timespan' query parameter for this endpoint
    params = {'timespan': timespan}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch switch ports for serial {serial}, status code: {response.status_code}")
        return None 


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
    

# ==================================================
# SELECT a Network in an Organization
# ==================================================
def select_mx_network(api_key, organization_id):
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
# GET Layer 3 Firewall Rules for a Network
# ==================================================
def get_l3_firewall_rules(api_key, network_id):
    url = f"https://api.meraki.com/api/v1/networks/{network_id}/appliance/firewall/l3FirewallRules"
    headers = {"X-Cisco-Meraki-API-Key": api_key, "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["rules"]
    else:
        print("Failed to fetch L3 firewall rules")
        return None


# ==================================================
# DISPLAY Firewall Rules in a Table Format
# ==================================================
def display_firewall_rules(firewall_rules):
    if firewall_rules:
        print("\nLayer 3 Firewall Rules:")
        print(tabulate(firewall_rules, headers="keys", tablefmt="pretty"))
    else:
        print("No firewall rules found in the selected network.")


# ==============================================================
# FETCH Organization policy and group objects for Firewall Rules
# ==============================================================
def get_organization_policy_objects(api_key, organization_id):
    url = f"https://api.meraki.com/api/v1/organizations/{organization_id}/policyObjects"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("Policy Objects:", data[:5])
        return data
    else:
        print(f"Failed to fetch organization policy objects: {response.text}")
        return []

def get_organization_policy_objects_groups(api_key, organization_id):
    url = f"https://api.meraki.com/api/v1/organizations/{organization_id}/policyObjects/groups"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("Policy Objects Groups:", data[:5])
        return data
    else:
        print(f"Failed to fetch organization policy objects groups: {response.text}")
        return []


# ==============================================================
# FETCH Organization Devices Statuses
# ==============================================================
def get_organization_devices_statuses(api_key, organization_id):
    url = f"https://api.meraki.com/api/v1/organizations/{organization_id}/devices/statuses"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch organization devices statuses. Status code: {response.status_code}")
        return []