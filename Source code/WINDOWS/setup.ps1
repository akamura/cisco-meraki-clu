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
# Define System Paths and identify Desktop location
# ==================================================
$utilitiesFolder = "$env:USERPROFILE\Utilities"
$akamuraFolder = ".\akamura"
$WScriptShell = New-Object -ComObject WScript.Shell
$desktopPath = $WScriptShell.SpecialFolders("Desktop")


# ==================================================
# MOVE akamura folder and subfolders in Utilities
# ==================================================
if (Test-Path -Path $akamuraFolder) {
    $installFolder = Join-Path -Path $utilitiesFolder -ChildPath "akamura"

    # Create "Utilities" folder if it doesn't exist
    if (-not (Test-Path -Path $utilitiesFolder)) {
        New-Item -Path $utilitiesFolder -ItemType Directory
    }

    # Check if "akamura" already exists in "Utilities", prompt for action
    if (Test-Path -Path $installFolder) {
        Write-Host "The 'akamura' folder already exists in '$utilitiesFolder'."
    } else {
        try {
            Move-Item -Path $akamuraFolder -Destination $utilitiesFolder -Force
        } catch {
            Write-Error "Error moving akamura folder: $_"
        }
    }
}

$targetFolder = $installFolder


# ==================================================
# CREATE the Application shortcut on Desktop
# ==================================================
if (Test-Path -Path $targetFolder) {
    $Shortcut = $WScriptShell.CreateShortcut("$desktopPath\Cisco Meraki CLU.lnk")
    $Shortcut.TargetPath = "C:\Windows\System32\cmd.exe"
    $Shortcut.Arguments = "/c python `"$targetFolder\ciscomerakiclu\main.py`""
    $Shortcut.IconLocation = "$targetFolder\ciscomerakiclu\icons\cisco-meraki-icon.ico"
    $Shortcut.WorkingDirectory = "$targetFolder\ciscomerakiclu"

    try {
        $Shortcut.Save()
    } catch {
        Write-Error "Unable to save shortcut: $_"
    }
    
} else {
    Write-Host "The 'akamura' folder was not moved successfully. Shortcut creation is skipped."
}