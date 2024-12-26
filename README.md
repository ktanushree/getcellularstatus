# Prisma SD-WAN Get Cellular Status
This utility is used to retrieve cellular module status across a single site or all sites. 

### Synopsis
For Prisma SD-WAN ION devices that are cellular capable, this script can be used to retrieve cellular module status.


### Requirements
* Active Prisma SDWAN Account
* Python >=3.6
* Python modules:
    * Prisma SASE (prisma_sase) Python SDK >= 6.5.1b1 - <https://github.com/PaloAltoNetworks/prisma-sase-sdk-python>

### License
MIT

### Installation:
 - **Github:** Download files to a local directory, manually run `getcellularstatus.py`. 

### Authentication:
 - Create a Service Account via the Identity & Access menu on Strata Cloud Manager
 - Save Service account details in the prismasase_settings.py file

### Examples of usage:
1. Get status from a single site
```angular2html
./getcellularstatus.py -S "<sitename>"
```
2. Get status from all sites
```angular2html
./getcellularstatus.py -S ALL_SITES
```

### Help Text:
```angular2
TanushreePro:getcellularstatus tanushreekamath$ ./getcellularstatus.py -h
usage: getcellularstatus.py [-h] [--site_name SITE_NAME] [--tprod TPROD]

Prisma SD-WAN Cellular Port Details.

options:
  -h, --help            show this help message and exit

Config:
  Details for the Sites you wish to retrieve status from

  --site_name SITE_NAME, -S SITE_NAME
                        Source Site Name. Provide site name or use keyword ALL_SITES
  --tprod TPROD, -T TPROD
                        TPROD Env
TanushreePro:getcellularstatus tanushreekamath$ 
```

#### Version
| Version | Build | Changes |
| ------- | ----- | ------- |
| **1.0.0** | **b1** | Initial Release. |


#### For more info
 * Get help and additional Prisma SDWAN Documentation at <https://docs.paloaltonetworks.com/prisma/prisma-sd-wan.html>
