### (AbUserIPDB) Abnormal User IPDB - Project KillChain
A automated script to help new SOC Teams make informed decicions on malicious IPs observed over SIEM by saving efforts and time. 

Made with :heart: by [Shrefa Ashour](https://www.linkedin.com/in/shrefa-salem-37b876290) + [Kamran Saifullah](https://linkedin.com/in/KamranSaifullah)

![PKC](https://img.shields.io/badge/Project-%20Killchain-357441)
![Language](https://img.shields.io/badge/Language-%20Python-357441?style=flat-square)

<img src="https://img1.wsimg.com/blobby/go/1cf5bcbc-aad3-42e4-a7e0-6c0149aec441/downloads/BG%20Gradient%20(2).png" width="125" height="125">

----
## Overview

The purpose of this script is to help new and small SOC Teams make informed decisions for the blocked/malicious IP addresses on SIEM by taking them out and checking their reputation against **AbuseIPDB** and **VirusTotal**. Thus, helping them save time + efforts to perform rapid investigations.

The script does the following:

- **AbuseIPDB**
  - Domain Name
  - Abuse Condifence Score
  - Country Code
  - Internet Service Provider
  - Total Reports
  - Last Reported Date
- **VirusTotal**
  - Subnet
  - Harmless Score
  - Malicious Score
  - Suspicious Score
  - Undetected Score

---

## Instructions for using the tool

### Installing Dependencies
In order for the script to work properly, there are few dependencies which are required to be installed. Do it with the following from within the folder or as you like. 

```pip install -r requirements.txt```

or you can install the dependecies one by one. 

### Getting the API Keys
Two API keys are required for the tool to be in full action. 

1. AbuseIPDB - https://www.abuseipdb.com/
2. VirusTotal - https://www.virustotal.com/

Create a personal account/professional account on both website and grab the API keys from your profile.

Place the keys for the following variables at the following.

- Line 8 
  - `AbuseIPDB_KEY = "<API KEY HERE>"`
- Line 9 
  - `VT_KEY = "<API KEY HERE>"`

### Begin The Hunt

Execute the `AbUserIPDB.py` by doing simply as 
```python3 AbUserIPDB.py```. 

The scripts supports 3 parameters.

1. For help `AbUserIPDB.py -h`.
2. For single IP `AbUserIPDB.py -ip`.
3. for multiple IPs from a file `AbUserIPDB.py -file`.

Finally, the script created a `File.csv` in the program directory in which all the data reflecting on the terminal is appended for later use. 

The results saved in the CSV file includes the following. 

1. IP Address
2. Domain Name
3. Abuse Confidence Score
4. Country Code
5. Internet Service Provider
6. Total Reports
7. Last Reported Date
8. VT Harmless Score
9. VT Undetected Score
10. VT Malicious Score
11. VT Suspicious Score

### Other Scripts

- **VTExplorer.py** - This scans the single IP and IPs from file only via VirusTotal.
- **AbuseIPDB.py** - This scans the single IP and IPs from file only via AbuseIPDB.  

## Feedback & Issues

Please, submit any feedback or issues to our **GitHub:** https://github.com/CyDefOps/project-killchain

Many Thanks

[Shrefa Ashour](https://www.linkedin.com/in/shrefa-salem-37b876290) + [Kamran Saifullah](https://linkedin.com/in/KamranSaifullah)

----

### Updates Coming...
- Securing API Keys - OS ENV
- More Integrations
- Dashboarding 
- Many more..

----

### Contributions
Project Killchain values and appreciates contributions from the cybersecurity community. Feel free to contribute code, share new tools, update our knowledge base, or expand the IOC database. 

Please review the contributing guidelines before making any contributions.

https://github.com/CyDefOps/project-killchain#contributions

----
