from consolemenu import ConsoleMenu
from consolemenu.items import MenuItem

  
def print_ascii_art():
    ascii_art = """
  ____ _                 __  __                _    _    ____ _    _   _ 
 / ___(_)___  ___ ___   |  \/  | ___ _ __ __ _| | _(_)  / ___| |  | | | |
| |   | / __|/ __/ _ \  | |\/| |/ _ \ '__/ _` | |/ / | | |   | |  | | | |
| |___| \__ \ (_| (_) | | |  | |  __/ | | (_| |   <| | | |___| |__| |_| |
 \____|_|___/\___\___/  |_|  |_|\___|_|  \__,_|_|\_\_|  \____|_____\___/ 
"""
    print(ascii_art)


# Define a function to do nothing (for header and footer simulation)
def dummy_function():
    pass

# Create the menu
menu = ConsoleMenu("Main Menu", prologue_text="is an essential tool crafted for Network Administrators managing Cisco Meraki networks. ",
                   epilogue_text="Disclaimer\nThis utility is not an official Cisco Meraki product but is based on the official Cisco Meraki API.\nIt is intended to provide Network Administrators with an easy daily companion in the swiss army knife. \n☕️ Fuel me a coffee if you found it useful: https://www.paypal.com/paypalme/matiazanella/")

# Add body items (actual menu items or functions)
body_item_1 = MenuItem("Security Appliance", menu)
body_item_2 = MenuItem("Switches and Access Points", menu)
body_item_3 = MenuItem("Sensors [Under Dev]", menu)
body_item_4 = MenuItem("Swiss Army Knife", menu)
body_item_5 = MenuItem("Meraki Platform Tools [Under Dev]", menu)
body_item_6 = MenuItem("Manage API Keys", menu)
menu.append_item(body_item_1)
menu.append_item(body_item_2)
menu.append_item(body_item_3)
menu.append_item(body_item_4)
menu.append_item(body_item_5)
menu.append_item(body_item_6)

# Show the menu
menu.show()
