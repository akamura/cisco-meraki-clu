## Version 1.4 (2024-03-24)

### New Features
- **[DNSBL Check Tool]** Check your IP reputation agains more than 300 lists.
- **[IP Check Tool]** Based on the powerful IPinfo database this tool gives you precise data about an IP when you need it most.
- **[Password Generator Tool]** Generate infinite complex passwords and export them in CSV format.
- **[Subnet Calculator Tool]** An assistant to help you create, manipulate and export subnets.

### Minor improvements
- Refactored and redesigned submenus across the application.

### Bug Fixes
- No fixes from the previous release.

### Documentation Updates
- Updated documentation.



## Version 1.3 (2024-02-18)

### New Features
- **[Microsoft Windows]** The application has undergone a comprehensive code refactor, enabling it to run seamlessly on Microsoft Windows. Understanding the importance of not compromising on security, I maintained SQLCipher for its robust encryption on Linux and MacOS. For Windows users, I've adapted by rewriting the database layer to incorporate Fernet encryption, ensuring security standards across Windows platform.
- **[Main Menu]** Refactored main menu to align it to the web version. This evolution is aimed at enhancing your network management experience, making it more accessible especially during critical troubleshooting tasks.

### Bug Fixes
- No fixes from the previous release.

### Documentation Updates
- Updated for Microsoft Windows.



## Version 1.2 (2024-02-11)

### New Features
- **[MS Switches and MR Access Points]** Implemented the new feature "Get Organization Devices Statuses".

### Bug Fixes
- No fixes from the previous release.

### Enhancements
- Refactored the entire project to organize the code into different subfolders to accommodate future enhancements.

### Documentation Updates
- Nothing to change.

### Contributors
- [Stefano Bettini](https://www.linkedin.com/in/stefano-bettini-97904918a/) for providing great optimization suggestions to show management interface details such as if a device has a statically or dynamically assigned IP.




## Version 1.1 (2024-02-04)

### New Features
- **[MX Appliance]** List firewall rules and fetch (if any) Organization policy objects and groups.
- **[MX Appliance]** Download firewall rules to the %User% system Download folder for convenience.
- **[MS Switches]** Retrieve Switch Ports data and their status based on a timespan, including useful information such as in/out traffic and PoE power metrics. Currently, a value of 1800 seconds, equivalent to 30 minutes, is set on line 230 of Module "meraki.py." Feel free to adjust the value.

### Bug Fixes
- No fixes from the previous release.

### Enhancements
- Refactored the "GET a list of Networks in an Organization" function on line 153 of Module "meraki.py" to improve the listing of large networks within an Organization.

### Documentation Updates
- Updated installation instructions in the README.

### Contributors
- [David Mallen](https://www.linkedin.com/in/david-mallen-64a679a/) for providing great optimization suggestions for retrieving large Network Lists within an Organization.