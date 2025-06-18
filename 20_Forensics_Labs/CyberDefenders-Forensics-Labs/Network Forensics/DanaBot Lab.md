## Scenario

The SOC team has detected suspicious activity in the network traffic, revealing that a machine has been compromised. Sensitive company information has been stolen. Your task is to use Network Capture (PCAP) files and Threat Intelligence to investigate the incident and determine how the breach occurred.

## Tools used:
- [Wireshark](https://www.wireshark.org/download.html)
- [NetworkMiner](https://www.netresec.com/?page=NetworkMiner)
- [CyberChef](https://gchq.github.io/CyberChef)

## MITRE ATT&CK and D3FEND

### MITRE ATT&CK:




### MITRE D3FEND: 

Updating...

## Questions

### Q1. Which IP address was used by the attacker during the initial access?

When viewing the HTTP Stream, we see an obfuscated code.

![{ABD0AAF0-4367-41EE-8D46-1BA4ED5FC967}](https://github.com/user-attachments/assets/2a5ee742-5a68-4ef7-a0e3-e24454b3d049)
<p></p>

Take note of the following:
- Public IP: 62.173.142.148
- Private IP: 10.2.14.101

It appears that the device with IP 10.2.14.101 was previously compromised, and the attacker is using it to send requests to their Command & Control (C&C) server. This is indicative of a reverse_tcp attack, where the infected device initiates a connection back to the attacker's server, allowing them to remotely control it.

![{43E17FD9-D2E3-45FB-843F-FCA6F559BAD3}](https://github.com/user-attachments/assets/85e7ac89-ddf7-472e-abb4-e8905414f41f)
<p></p>

**Answer: 62.173.142.148**

### Q2. What is the name of the malicious file used for initial access?

According to the HTTP Stream in question 1.

**Answer: allegato_708.js**

### Q3. What is the SHA-256 hash of the malicious file used for initial access?

#### Method 1

Open the pcap file with NetworkMiner, navigate to the **File** tab, and double-click on the file name mentioned in question 2.

<img src=https://github.com/user-attachments/assets/880c8d69-b2e7-4342-b7aa-d30d67a38e82 width=100%>

#### Method 2

Choose File --> Export Objects --> HTTP...

<img src=https://github.com/user-attachments/assets/acb56bc9-8403-499b-b96e-893f8b8ec19e width=100%>

<p></p>

<img src=https://github.com/user-attachments/assets/61827933-923f-48e6-9446-6554894ae629 width=100%>
<p></p>

**Answer: 847b4ad90b1daba2d9117a8e05776f3f902dda593fb1252289538acf476c4268**

### Q4. Which process was used to execute the malicious file?

Analysis from the AnyRun sandbox indicates that *wscript.exe* is the process used to execute this malicious file.

<img src=https://github.com/user-attachments/assets/eaceefda-7fec-4c6b-93af-3a4935b79b30 width=100%>
<p></p>

**Answer: wscript.exe**

### Q5. What is the file extension of the second malicious file utilized by the attacker?

![{9C6B094D-653E-404B-832D-437579CF3D1E}](https://github.com/user-attachments/assets/c43b360c-1969-424b-9fa0-769f5314dcc6)
<p></p>

- Private IP: 10.2.14.101
- Public IP: 188.114.97.3

At this point, the hacker is using a different IP address than the one initially observed.

The second malicious file used by the hacker is resources.dll. This is because it is an executable file, identified by its MZ file signature, indicating that it follows the Portable Executable (PE) format.

![{F0F30305-729A-4C8E-8E65-A175728BB21E}](https://github.com/user-attachments/assets/3667f158-238a-411c-9124-4aa843563214)
<p></p>

![{630144F3-468E-4E9D-A116-ECBE5CDE306E}](https://github.com/user-attachments/assets/163960ab-f7b9-4170-a86b-31dc0934cd0b)
<p></p>

Check VirusTotal

![{BD320840-464A-48B3-B139-2F642FB7AD02}](https://github.com/user-attachments/assets/95a2dd05-087d-49c7-a068-f38e081a338a)
<p></p>

**Answer: .dll**

### Q6. What is the MD5 hash of the second malicious file?

AnyRun: https://app.any.run/tasks/9c91e420-2515-437e-a60b-ea0aff0050dc

**Answer: e758e07113016aca55d9eda2b0ffeebe**


## References
- [1] File Signature: https://www.garykessler.net/library/file_sigs.html
- [2] AnyRun Submission: https://app.any.run/submissions
- [3] VirusTotal: https://www.virustotal.com/
- [4] CyberChef: https://gchq.github.io/CyberChef
