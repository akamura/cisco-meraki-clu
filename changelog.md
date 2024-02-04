## Version 1.1 (2024-02-04)

### New Features
- **[MX Appliance]** List firewall rules and fetch (if any) Organization policy objects and groups.
- **[MX Appliance]** Download firewall rules to the %User% system Download folder for convenience.
- Retrieve Switch Ports data and their status based on a timespan, including useful information such as in/out traffic and PoE power metrics. Currently, a value of 1800 seconds, equivalent to 30 minutes, is set on line 230 of Module "meraki.py." Feel free to adjust the value.

### Bug Fixes
- No fixes from the previous release.

### Enhancements
- Refactored the "GET a list of Networks in an Organization" function on line 153 of Module "meraki.py" to improve the listing of large networks within an Organization.

### Documentation Updates
- Updated installation instructions in the README.

### Contributors
- [David Mallen](https://www.linkedin.com/in/david-mallen-64a679a/) for providing great optimization suggestions for retrieving large Network Lists within an Organization.