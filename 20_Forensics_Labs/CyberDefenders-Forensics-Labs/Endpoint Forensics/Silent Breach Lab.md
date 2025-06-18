## Scenario

The IMF is hit by a cyber attack compromising sensitive data. Luther sends Ethan to retrieve crucial information from a compromised server. Despite warnings, Ethan downloads the intel, which later becomes unreadable. To recover it, he creates a forensic image and asks Benji for help in decoding the files.

Resources:
[Windows Mail Artifacts: Microsoft HxStore.hxd (email) Research](https://boncaldoforensics.wordpress.com/2018/12/09/microsoft-hxstore-hxd-email-research/)

## Tools used

- FTK Imager
- DB Browser for SQLite
- CyberChef

## Question

### Q1. What is the MD5 hash of the potentially malicious EXE file the user downloaded?

Using FTK Imager, then go to Downloads directory, we can see an exe file named "IMF-Info.pdf.exe". This file shows clear malicious because its name is intentionally made to look like a regular PDF file in order to deceive users.

**Answer: 336A7CF476EBC7548C93507339196ABB**


### Q2. What is the URL from which the file was downloaded?

If we click to that mentioned file in Evidence tree, we can see a Zone.Identifier in File List. So, what is Zone.Identifier?

Zone.Identifier is a small Alternate Data Stream (ADS) that the Windows system automatically adds to files downloaded from the Internet or from untrusted sources. It contains information about the Security Zone of the file's origin, helping Windows determine the risk level and display security warnings when open the file. [1]

Files with an ADS Zone.Identifier that contains ZoneID, by default as follow [2][3]

```
ZoneId: 0 - My Computer
        1 - Local Intranet
        2 - Trusted Sites
        3 - Internet
        4 - Restricted Sites
```

![{78839CC9-C4A5-482A-BE13-406119E0312C}](https://github.com/user-attachments/assets/01074da4-d7c1-4a06-8bf8-c50e0a911292)

**Answer: http://192.168.16.128:8000/IMF-Info.pdf.exe**


### Q3. What application did the user use to download this file?

First, we should to know the history of browser. Go to `C:\Users\ethan\AppData\Local\Microsoft\Edge\User Data\Default\`, export History file, then load it to DB Browser for SQLite tool.

![{6770C4B2-29C9-4ADF-B8CE-55C711C2AE41}](https://github.com/user-attachments/assets/bb657683-6bf7-461d-9846-7b28667072ee)

**Answer: Microsoft Edge**


### Q4. By examining Windows Mail artifacts, we found an email address mentioning three IP addresses of servers that are at risk or compromised. What are the IP addresses?

Following the link mentioned in the Scenario section, we need to export the `HxStore.hxd` file. This file can be found at the path: `Users\<user>\Appdata\Local\Packages\microsoft.windowscommunicationsapps_8wekyb3d8bbwe\LocalState\`

Then, use the `strings.exe` tool from Sysinternals Suite to extract readable text from the file.

![{337C08A0-46D4-4210-834E-83D04BEC1F4D}](https://github.com/user-attachments/assets/c56981b2-b648-4c11-ab72-dd227c63609d)

**Answer: 145.67.29.88, 212.33.10.112, 192.168.16.128**


### Q5. By examining the malicious executable, we found that it uses an obfuscated PowerShell script to decrypt specific files. What predefined password does the script use for encryption?

Search for the MD5 hash of the executable file in Q1 on VirusTotal. Then, navigate to the Relations tab — we can see that a PowerShell script was dropped.
Using the SHA256 hash `f1768084b830d07820b39dac6ac0ecc6807a1caf7e011a61d1b3bf9dc105de5a`, I found an AnyRun analysis of that file. [4]

Below is the content of the PowerShell script `Gz3m6mG3j2TyAqF2Zx4v.ps1`

![{DAD60291-4298-4635-AF06-760FFA88D23C}](https://github.com/user-attachments/assets/8974038b-4317-4b26-bb68-5258fb977544)

The PowerShell script is obfuscated. It stores a Base64 encoded string in the variable $wy7qIGPnm36HpvjrL2TMUaRbz.

This string is first converted into a character array and then reversed using [array]::Reverse(). After reversing, it is converted back to a string and decoded from Base64 using [System.Convert]::FromBase64String(), followed by [System.Text.Encoding]::UTF8.GetString() to get the actual payload.

The decoded content is then executed using Invoke-Expression, which is aliased as "pwn" in this script.

Using CyberChef, to reverse and decode that Base64

![{FBC8CABB-C8A7-4F9D-BD8F-47775C827E8E}](https://github.com/user-attachments/assets/274a226b-74f3-4275-888a-ee9e0db623f1)

**Answer: Imf!nfo#2025Sec$**


### Q6. After identifying how the script works, decrypt the files and submit the secret string.

We can run the following script in local to get key and iv for decrypting AES.

```
$password = "Imf!nfo#2025Sec$"
$salt = [Byte[]](0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08)
$iterations = 10000
$keySize = 32   
$ivSize = 16 

$deriveBytes = New-Object System.Security.Cryptography.Rfc2898DeriveBytes($password, $salt, $iterations)
$key = $deriveBytes.GetBytes($keySize)
$iv = $deriveBytes.GetBytes($ivSize)
```
*Note: key and iv need to be changed from decimal to hex before decrypting*

![{711B5161-75A2-48DB-B787-BAF7BD1C6D8C}](https://github.com/user-attachments/assets/d82654cc-cfaf-419a-b18e-feb1604c7c9e)

Download that pdf file and get the secret string.

**Answer: CyberDefenders{N3v3r_eX3cuTe_F!l3$_dOwnL0ded_fr0m_M@lic10u5_$erV3r}**


## References

- [1] Russinovich, Mark E.; Solomon, David A.; Ionescu, Alex (2009). "File Systems". Windows Internals (5th ed.). Microsoft Press. p. 836. ISBN 978-0-7356-2530-3.
- [2] Security Zones: https://learn.microsoft.com/en-us/previous-versions/troubleshoot/browsers/security-privacy/ie-security-zones-registry-entries#zones
- [3] Zone.Identifier: https://windowsforensics.net/database/file-download/ads-zone-identifier.html
- [4] AnyRun: https://app.any.run/tasks/5b98b97e-114a-4f6d-9907-4ac0c2d15f84
