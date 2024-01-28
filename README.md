# Cisco Meraki Command Line Utility

![Cisco Meraki CLU Screenshot](Preview.png)

**Cisco Meraki CLU** (Command Line Utility) is an essential tool crafted for Network Administrators managing Cisco Meraki networks. It streamlines and accelerates your workflow, offering quick access to vital information—especially crucial during intensive troubleshooting sessions where time is of the essence and web dashboard accessibility is limited.

<br><br>
# 🌟 Features

- **API Key Management**: Securely 256-bit AES store and effortlessly manage your Cisco Meraki API key in an encrypted local DB.
- **Device Listing**: Instantly retrieve detailed lists of APs and switches.
- **Meraki MX Status Monitoring**: Keep a pulse on the status of your Meraki MX appliances. (under development)
- **Organization & Network Management**: Efficiently navigate through organizations and networks. (under development)
- **Data Export**: Conveniently export device data into well-organized CSV files.
- **Network Diagnostics Toolkit**: Includes additional third-party open-source tools troubleshoot network issues. (under development)

<br><br>
# 🚀 Installation


## Clone the repository
    git clone https://github.com/akamura/cisco-meraki-clu.git

## Navigate to the repository and install libraries
    cd /opt/akamura/ciscomerakiclu

you will find the **setup.py** file which contain a list of libraries and modules needed to run the program.


## Install from a Package
At the moment I released the first package for Ubuntu and tested under OS release 22.04.3 LTS.
Download the package and execute.

    sudo apt install ./cisco-meraki-clu.deb

## Uninstall from a Package
If you want to uninstall the Ubuntu .deb package execute this command

    sudo apt remove ciscomerakiclu


<br><br>
# 🎬 Getting Started
First of all you need to generate a Cisco Meraki API key from your account, for this you can refer to this [Cisco Meraki Dashboard API](https://documentation.meraki.com/General_Administration/Other_Topics/Cisco_Meraki_Dashboard_API) Knowledge Base.


<br><br>
# 🛠 Usage
From the Ubuntu Application Launcher click on Cisco Meraki CLU.

The application at first start will promting you to create the encrypted database that will need to safely store your API key
Initialize your Cisco Meraki API key with the utility.
Access a range of features from device listing to MX status monitoring.
Experience a more streamlined approach to network management!

From the terminal

    cd /opt/akamura/ciscomerakiclu
    python3 main.py


<br><br>
# 👐 Contributing
Your contributions make this project thrive. Feel free to report issues, suggest features, or submit pull requests.
Every bit of help is valued!


<br><br>
# 💖 Acknowledgments
Cisco Systems Inc. to provide such robust API, you can find more [clicking here](https://developer.cisco.com/meraki/).

Open-Source Community: For the valuable libraries that enhance this project.

<br><br>
# 📬 Contact
Got questions or suggestions? Join the conversation on the Discussions panel.

Let's make Network Management seamless with Cisco Meraki CLU! 🚀