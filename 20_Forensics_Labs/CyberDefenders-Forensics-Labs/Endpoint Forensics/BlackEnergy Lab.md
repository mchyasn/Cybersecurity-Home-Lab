## Scenario

A multinational corporation has suffered a cyber attack, resulting in the theft of sensitive data. The attack employed a previously unseen variant of the BlackEnergy v2 malware. The company's security team has obtained a memory dump from the infected machine and is seeking your expertise as a SOC analyst to analyze the dump in order to understand the scope and impact of the attack.

## Tools used

- Volatility2


## MITRE ATT&CK & D3FEND

### MITRE ATT&CK



### MITRE D3FEND




## Question

### Q1. Which volatility profile would be best for this machine?

Using volatility2 with `imageinfo` plugin to know the profile would be best for this machine.

![{D9875737-FDFB-4761-A0B1-18E14801E97E}](https://github.com/user-attachments/assets/577ac208-f09b-426b-877f-1a383d9c1171)


**Answer: WinXPSP2x86**

### Q2. How many processes were running when the image was acquired?

First of all, we wanted to determine how many processes were running. We used pstree to view the processes in a tree-like structure.

I prefer using `pstree` because it presents process relationships in a structured that means easy to identify parent and child processes.

![{D0D87515-A2C4-459D-9476-81DFD51105C3}](https://github.com/user-attachments/assets/b4d8c312-2cf2-4859-b956-049bac99061a)

We can see that there are totally 25 processes but there are only 19 running processes. They are 6 processes have not been handled.

**Answer: 19**

### Q3. What is the process ID of cmd.exe?

See at Question 2.

**Answer: 1960**

### Q4. What is the name of the most suspicious process?

The most suspicious process in that list is `rootkit.exe`. Because this process is a child process of `explorer.exe`, which typically only spawns GUI-related child processes, and it has `cmd.exe` child process.

**Answer: rootkit.exe**

### Q5. Which process shows the highest likelihood of code injection?

In Volatility 2, `malfind` plugin is used to detect and extract suspicious code segments (injected malware, DLL injection, ...) hidden within a process’s memory regions.

![{1E6ACE74-C4F8-4AB3-84C7-01A54F7FECA0}](https://github.com/user-attachments/assets/68e45ef8-3f70-419d-8639-dc84a9ad147b)


Windows allocated a memory region with PAGE_EXECUTE_READWRITE for the svchost.exe process, and the "MZ" header (4D 5A in Hex) shows that a PE file (such as EXE, DLL,...) has been directly embedded into this memory region. Learn about file signatures [here](https://filesig.search.org/).

![{BFD645AF-C7C7-44A6-BD4B-8B8800F12648}](https://github.com/user-attachments/assets/3370c3f3-7d11-4b15-bc8c-76bdf14568b3)


Running following command to dump process to check it on VirusTotal: `vol2.exe -f .\CYBERDEF-567078-20230213-171333.raw --profile=WinXPSP2x86 malfind -p 880 -D .`

![{58142905-958C-41E3-A24A-FD290FB6560C}](https://github.com/user-attachments/assets/305a34c6-14f7-44a3-9764-c37eb12806a0)

**Answer: svchost.exe**

### Q6. There is an odd file referenced in the recent process. Provide the full path of that file.

To identify the recent process and investigate its behavior, we can use `handles` plugin - which is used to print list of open handles for each process, and from there determine whether the analyzed process references any odd file.

![{CA054AD1-56F6-40F9-B941-942BDFB7446F}](https://github.com/user-attachments/assets/61177dd8-2e13-4e9e-9298-bcef8a9a9bb4)

`svchost.exe` is a process that operates in **user-mode**, while the file `str.sys` is located in the `\Windows\System32\drivers` directory — a folder that contains hardware and system service drivers which run in **kernel-mode**. This means they have the highest level of access in the OS and can deeply interact with the system. In addition, the driver name “str.sys” is unusual and meaningless. The legitimate process `svchost.exe` was injected with code to exploit it for executing or accessing the `str.sys` file in order to gain kernel-mode privileges.

**Answer: C:\WINDOWS\system32\drivers\str.sys**

### Q7. What is the name of the injected DLL file loaded from the recent process?

We can use `dlllist` plugin to extract the process’s loaded modules. But one thing, during an investigation, it is a good practice to compare both **dlllist** and **ldrmodules** results to see if there is any unlinking between the process loaded modules. Because some sample have the ability to unlink themselves from other modules, and if the sample has this capability when you run dlllist plugin, that module won’t appear on the result.

![{20A0ED72-1B4B-4B52-A41D-BE398455E63A}](https://github.com/user-attachments/assets/5a1b9e9c-16a3-488f-8766-13b0229bdeac)

![{29B0448C-7264-45C0-8A15-5EFA1ADCD811}](https://github.com/user-attachments/assets/84d34855-128f-4ad8-bf8b-d474e462aae1)

The DLL file `msxml3r.dll` is loaded by svchost.exe but is marked False in all three columns InLoad, InInit, and InMem. Note also that the name msxml3r.dll is unusual and differs from the original Windows file named msxml3.dll. This is highly suspicious because a legitimate DLL loaded by the Windows loader through the normal mechanism will have all three of these values set to True. This DLL is not fully recognized in these lists indicates it has been injected into the process.

DLL injection is a common technique used by attackers to execute malicious code within the context of a legitimate process. By doing so, they can hide their activities and exploit the privileges of the targeted process.

**Answer: msxml3r.dll**

### Q8. What is the base address of the injected DLL?

See at Question 5.

**Answer: 0x980000**

## References

- [1] Pavel Yosifovich, Alex Ionescu, Mark Russinovich and David Solomon, *Windows Internals: System architecture, processes, threads, memory management, and more* (7th ed). Microsoft Press, May 5, 2017.
- [2] File Signature: https://filesig.search.org/
