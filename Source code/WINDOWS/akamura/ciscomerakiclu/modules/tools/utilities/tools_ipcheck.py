
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
import ipinfo
from settings import db_creator
from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE
from settings import term_extra

def get_ip_details(ip_address, handler):
    def safe_get_attr(object, attr, subattr=None, default='N/A'):
        """
        Safely gets a nested attribute from an object, or returns 'N/A' if not found.
        If 'subattr' is provided, it fetches a nested attribute.
        """
        result = getattr(object, attr, default)
        if subattr and result != default:
            return getattr(result, subattr, default)
        return result

    try:
        details = handler.getDetails(ip_address)

        ip_info = [
            ['IP', safe_get_attr(details, 'ip')],
            ['Hostname', safe_get_attr(details, 'hostname')],
            ['Anycast', 'Yes' if safe_get_attr(details, 'anycast', default=False) else 'No'],
            ['City', safe_get_attr(details, 'city')],
            ['Region', safe_get_attr(details, 'region')],
            ['Country', safe_get_attr(details, 'country')],
            ['Location', safe_get_attr(details, 'loc')],
            ['Organisation', safe_get_attr(details, 'org')],
            ['Postal', safe_get_attr(details, 'postal')],
            ['Timezone', safe_get_attr(details, 'timezone')],
            ['ASN', safe_get_attr(details, 'asn', 'asn')],
            ['ASN Name', safe_get_attr(details, 'asn', 'name')],
            ['ASN Domain', safe_get_attr(details, 'asn', 'domain')],
            ['ASN Route', safe_get_attr(details, 'asn', 'route')],
            ['ASN Type', safe_get_attr(details, 'asn', 'type')],
            ['Company Name', safe_get_attr(details, 'company', 'name')],
            ['Company Domain', safe_get_attr(details, 'company', 'domain')],
            ['Company Type', safe_get_attr(details, 'company', 'type')],
            ['VPN', 'Yes' if safe_get_attr(details, 'privacy', 'vpn', default=False) else 'No'],
            ['Proxy', 'Yes' if safe_get_attr(details, 'privacy', 'proxy', default=False) else 'No'],
            ['Tor', 'Yes' if safe_get_attr(details, 'privacy', 'tor', default=False) else 'No'],
            ['Relay', 'Yes' if safe_get_attr(details, 'privacy', 'relay', default=False) else 'No'],
            ['Hosting', 'Yes' if safe_get_attr(details, 'privacy', 'hosting', default=False) else 'No'],
            ['Abuse Address', safe_get_attr(details, 'abuse', 'address')],
            ['Abuse Country', safe_get_attr(details, 'abuse', 'country')],
            ['Abuse Email', safe_get_attr(details, 'abuse', 'email')],
            ['Abuse Name', safe_get_attr(details, 'abuse', 'name')],
            ['Abuse Network', safe_get_attr(details, 'abuse', 'network')],
            ['Abuse Phone', safe_get_attr(details, 'abuse', 'phone')],
            ['Total Domains', str(safe_get_attr(details, 'domains', 'total'))]
        ]

        domains = safe_get_attr(details, 'domains', 'domains', default=[])
        if domains != 'N/A':
            for domain in domains:
                ip_info.append(['Domain', domain])

        return ip_info
    except Exception as e:
        return [['Error', str(e)]]

def main(fernet):
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    access_token = db_creator.get_tools_ipinfo_access_token(fernet)
    if not access_token:
        print("IPinfo access token not found. Please ensure it is set correctly.")
        return

    handler = ipinfo.getHandler(access_token)

    ip_address = input("Please enter an IP address: ")

    ip_details = get_ip_details(ip_address, handler)
    console = Console()
    
    table = Table(show_header=False, header_style="bold green", box=SIMPLE)
    table.add_column("Name", style="cyan", width=12)
    table.add_column("Result", style="green")
    
    for detail in ip_details:
        table.add_row(*detail)

    console.print(table)
    
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()