## Scenario

A SOC analyst took a memory dump from a machine infected with a meterpreter malware. As a Digital Forensicators, your job is to analyze the dump, extract the available indicators of compromise (IOCs) and answer the provided questions.

## Tool used

- Volatility2


## Question

### Q1. What is the SHA1 hash of Triage-Memory.mem (memory dump)?

Using sha1sum or any HASH calculating tool.

**Answer: C95E8CC8C946F95A109EA8E47A6800DE10A27ABD**

### Q2. What volatility profile is the most appropriate for this machine? (ex: Win10x86_14393)

Using the `imageinfo` plugin in Volatility2 to determine the appropriate profile.

![{18F8C6A1-3100-43CB-B5B7-457553C2921F}](https://github.com/user-attachments/assets/9fe1a390-88e8-4edc-9a2d-c9624100c250)

**Answer: Win7SP1x64**

### Q3. What was the process ID of notepad.exe?

Using the `pslist` plugin in Volatility2 to list all processes and their IDs.

![{9C0382A1-4EEE-424F-B221-653AC30042BE}](https://github.com/user-attachments/assets/5eaea51b-c5b3-453a-ae9f-aea6f0b7808f)

**Answer: 3032**

### Q4. Name the child process of wscript.exe.

Using `pstree` plugin in Volatility2 to visualize the parent-child relationships between processes.

![image](https://github.com/user-attachments/assets/a6d2e2b1-8ce6-43a7-abb9-da45046e3561)

**Answer: UWkpjFjDzM.exe**

### Q5. What was the IP address of the machine at the time the RAM dump was created?

Using the `netscan` plugin in Volatility2 to enumerate the active network connections, including the machine’s IP address.

![{DDDACCFD-25A7-45EC-A163-149AC521A8A9}](https://github.com/user-attachments/assets/fe7d7737-0b43-4020-afcf-7c389a6768d7)

The machine’s IP address is under the Local Address column.

**Answer: 10.0.0.101**

### Q6. Based on the answer regarding the infected PID, can you determine the IP of the attacker?

In the pstree result, the process with PID 3496 named UwKpjFjDzM.exe is suspicious due to its unusual name. Its child process is `cmd.exe`, and its parent process is `wscript.exe` - the Windows Script Host (WSH) executable, is a crucial component of the Windows operating system that allows the execution of scripts written in various scripting languages, most commonly VBScript (.vbs) and JScript (.js). Cross-referencing with the netscan table, the corresponding PID shows that the victim machine is establishing a connection to another system with IP and port `10.0.0.106:4444` - port 4444 is commonly used by the Metasploit framework for exploitation, possibly a reverse shell attack.

**Answer: 10.0.0.106**

### Q7. How many processes are associated with VCRUNTIME140.dll?

Using `dlllist` plugin in Volatility2 and grep `VCRUNTIME140.dll` to know how many processes there are.

I do not know why there are only 1 process when I use volatility2 (also volatility3).

![{67FFEA95-E366-4AAD-A0B5-F98F30BCC6BC}](https://github.com/user-attachments/assets/fb0db771-8a62-412b-bb52-013858cfd30b)


**Answer: 5**

### Q8. After dumping the infected process, what is its md5 hash?

Using `procdump` plugin in Volatility2 to dump VCRUNTIME140.dll.

**Answer: 690ea20bc3bdfb328e23005d9a80c290**

### Q9. What is the LM hash of Bob's account?

Using `hashdump` plugin in Volatility2 to retrieve LM password hashes on Windows. The LM (LAN Manager) hash was one of the first password hashing algorithms to be used by Windows operating systems, and the only version to be supported up until the advent of NTLM used in Windows 2000, XP, Vista, and 7.

![{B76BB1F9-2FB0-4C64-B5F0-84A011C5977A}](https://github.com/user-attachments/assets/2305f37e-f404-49d7-868f-c3e7542e4aa3)

LM hash format: `<User_name>:<User_ID>:<LM_hash>:<NTLM hash>:<Comment>:<Home Dir>:`

The string "aad3b435b51404eeaad3b435b51404ee" is the LM hash for an empty password, and "31d6cfe0d16ae931b73c59d7e0c089c0" is the NTLM hash for an empty password too.

**Answer: aad3b435b51404eeaad3b435b51404ee**

### Q10. What memory protection constants does the VAD node at 0xfffffa800577ba10 have?

Using `vadinfo` plugin in Volatility2 to inspect VAD details. Virtual Address Descriptor – is used by the Windows memory manager to describe memory ranges used by a process as they are allocated. When a process allocates memory with VirtualAlloc, the memory manager creates an entry in the VAD tree.

![{EE421684-D70A-4D06-947C-5AAA198BCE3E}](https://github.com/user-attachments/assets/c2f1b76d-3a8c-4d52-be2e-29334977afd1)


**Answer: PAGE_READONLY**

### Q11. What memory protection did the VAD starting at 0x00000000033c0000 and ending at 0x00000000033dffff have?

Search the output for the VAD range starting at `0x00000000033c0000` and ending at `0x00000000033dffff` to find the memory protection information.

![{BAA63B1E-BEC2-44C5-847E-AFB5D6D6448D}](https://github.com/user-attachments/assets/b5de6cf6-fd9e-4e6b-9a84-61071b52ff09)

**Answer: PAGE_NOACCESS**

### Q12. There was a VBS script that ran on the machine. What is the name of the script? (submit without file extension)

Base on Question 6, find **wscript.exe** in by using `cmdline` plugin in Volatility2.

![{38018C4F-B1E5-4A37-A646-D59215F619DE}](https://github.com/user-attachments/assets/fa7f71f4-d8ab-46cd-a904-d6bc6bad53d8)

**Answer: vhjReUDEuumrX**

### Q13. An application was run at 2019-03-07 23:06:58 UTC. What is the name of the program? (Include extension)

The `shimcache` plugin in Volatility logs executed programs, including timestamps. ShimCache (Application Compatibility Cache) is a Windows feature designed to provide backward compatibility for older applications running on newer systems. The caching information is stored in memory and written to the registry upon system shutdown. Entries are generally added to the cache if the file was executed or visible in the Windows File Explorer.

![{9FB2E816-E437-4BD8-8E64-EDB0934F53A3}](https://github.com/user-attachments/assets/7e5a5678-8649-4aa6-b02e-69881842d865)

**Answer: Skype.exe**

### Q14. What was written in notepad.exe at the time when the memory dump was captured?

First, we need to use memdump to dump everything that is loaded in the notepad.exe’s memory space. Then, using `strings.exe` in [Sysinternals Suite](https://learn.microsoft.com/en-us/sysinternals/downloads/sysinternals-suite), pipe the output directly into PowerShell's Select-String to filter only the strings that match exact answer format.

Running the following command: `strings.exe -n 17 .\3032.dmp | Select-String -Pattern "^.{4}<.{7}_.{2}_.{4}>$"`

**Answer: flag<REDBULL_IS_LIFE>**

### Q15. What is the short name of the file at file record 59045?

Examine the Master File Table (MFT) to retrieve the short name of the file. Using `mftparser` plugin in Volatility2 to analyze the MFT entries. MFT - can be considered one of the most important files in the NTFS files system. It keeps records of all files in a volume, the file's location in the directory, the physical location of the files in on the drive and the file metadata. There is at least on entry in the MFT for every file on an NTFS file system volume, including the MFT itself. All information about a file, including its size, time and data stamps, permissions, and data content is stored either in MFT entries, or in space outside the MFT that is described by MFT entries.

`mftparser` plugin will return huge amount of information as it prints all the file in the MFT entries, so the best use is to extract the output and dump to disk as a .txt file for better analysis.

Run the following commanđ: `vol2.exe -f .\Triage-Memory.mem --profile=Win7SP1x64 mftparser --output-file=mftparser_vol2.txt`

![{23FFB7E2-3265-459B-B83E-070E76CB7229}](https://github.com/user-attachments/assets/78d08592-b6ef-43a1-8c98-94fb4b33a459)

**Answer: EMPLOY~1.XLS**

### Q16. This box was exploited and is running meterpreter. What was the infected PID?

**Answer: 3496**


## References

- [1] Shimcache: https://www.youtube.com/watch?v=7byz1dR_CLg
- [2] Virtual Address Descriptor: https://www.infosecinstitute.com/resources/penetration-testing/finding-enumerating-processes-within-memory-part-2/
- [3] Sysinternals Suite: https://learn.microsoft.com/en-us/sysinternals/downloads/sysinternals-suite
