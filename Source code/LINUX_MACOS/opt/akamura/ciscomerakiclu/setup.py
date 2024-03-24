#**************************************************************************
#   App:         Cisco Meraki CLU                                         *
#   Version:     1.4                                                     *
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
from setuptools import setup, find_packages


# ==================================================
# SETUP the environment with needed libraries
# ==================================================
setup(
    name='Cisco Meraki CLU',
    version='1.4',
    packages=find_packages(),
    install_requires=[
        'tabulate',
        'pathlib',
        'datetime',
        'termcolor',
        'requests',
        'pysqlcipher3',
        'rich',
        'dnspython',
        'setuptools',
        'dnspython',
        'ipinfo',
        'scapy',
        'secrets',
        'numpy',
        'ipaddress'
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'ciscomerakiclu = ciscomerakiclu.main:main'
        ]
    }
)