# security-onion-install-tutorial
This is a tutorial for installing Security Onion 2.4 Standalone instance with Virtualbox, and with a Linux Mint VM to access the SOC interface.

- Security Onion minimum hardware recommendation: 200GB, 16GB RAM, 4 cores of CPU.


## Content
[Downloading Security Onion ISO](https://github.com/borelli28/security-onion-install-tutorial?tab=readme-ov-file#downloading-security-onion-iso)

[Settings Linux Mint VM](https://github.com/borelli28/security-onion-install-tutorial?tab=readme-ov-file#settings-linux-mint-vm)

[Settings of Security Onion VM in VirtualBox](https://github.com/borelli28/security-onion-install-tutorial?tab=readme-ov-file#settings-of-security-onion-vm-in-virtualbox)

[Security Onion instance setup](https://github.com/borelli28/security-onion-install-tutorial?tab=readme-ov-file#security-onion-instance-setup)

[Access Security Onion SOC Portal](https://github.com/borelli28/security-onion-install-tutorial?tab=readme-ov-file#access-security-onion-soc-portal)


#### Downloading Security Onion ISO
- Visit the repo releases page and download the latest version of Security Onion 2.4: https://github.com/Security-Onion-Solutions/securityonion/releases

- Check the hash of the downloaded file.


#### Settings Linux Mint VM

- Go to the link and download the Linux Mint Desktop ISO: https://linuxmint.com/download.php

- Once downloaded we can press "New" to create the VM.

- For the Memory I will be using 6000MB but it does not matter that much for this VM.

![alt text](./images/mint0.png)

- And I will be using 2 Processors.

- In the Network tab I selected 1 adapter NatNetwork, the same one that I will be using for the Security Onion instance, so they can communicate.

![alt text](./images/mint1.png)

- For Storage I selected 30GB.

- Now we select the Linux Mint instance and press "Start".

- When the VM loads, click on "Install Linux Mint".

![alt text](./images/mint2.png)

- Select language and Keyboard.

- You can press "Continue" here.

![alt text](./images/mint3.png)

- Select "Erase disk and Install Linux Mint" and press "Install Now".

- Press "Continue" and select your location.

- Now pick you username, name for the PC, and password. Press "Continue".

![alt text](./images/mint4.png)

- At the end of the installation we need to press "Restart Now" and then press enter.

![alt text](./images/mint5.png)

- Enter password to login.

- Now open the Terminal.

![alt text](./images/mint6.png)

- Run update in the terminal, when prompted enter your password: `sudo apt update`.

![alt text](./images/mint7.png)

- Now type `ip addr` in order to get the IPv4 of this instance, which we will use when setting up Security Onion.

![alt text](./images/mint8.png)

- Now you can leave the Ubuntu instance running while we start the security onion instance.


#### Settings of Security Onion VM in VirtualBox

- Now we can start creating the VM for Security Onion:

- For Hardware, we are selecting 17000MB of Memory and 4 Processors.

![alt text](./images/so0.png)

- For Storage, we are selecting 200GB which is the minimum recommended.

- For Network, we will have two adapters; the first one will be a NatNetwork for the interface & the second one will be another NatNetwork with Promiscuous Mode to "Allow VMs" for monitoring.

![alt text](./images/so1.png)

![alt text](./images/so2.png)


#### Security Onion instance setup

- Now we start the Security Onion instance.

- Type "Yes" on the first screen.

![alt text](./images/so3.png)

- Enter an username: `admin`.

- Enter a password.

- Now a bunch of packages will be installed so just wait.

![alt text](./images/so4.png)

- When it's done we will press enter to reboot and continue the setup.

![alt text](./images/so5.png)

- Login, and press "Yes" to continue with the setup.

- Select Install.

![alt text](./images/so6.png)

- Select "STANDALONE".

- Type "agree" and press "OK".

- Select "Standard".

![alt text](./images/so7.png)

- Enter a hostname for the instance and press "OK".

- You can leave the description blank.

![alt text](./images/so8.png)

- In this screen we select the Network Adapter for management, this adapter is the one that is NOT in promiscous mode. Verify the MAC address to pick the correct one.

![alt text](./images/so9.png)

- Select "DHCP" and then press "OK".

- Press "Yes" to continue with a DHCP.

- Press "OK" to setup the networking.

- Select "Direct".

![alt text](./images/so10.png)

- Select "Yes".

- Select the network adapter for Monitoring.

- Enter an email, this email will be used to login into the SOC portal on the Linux Mint machine. It can be a fake email.

![alt text](./images/so11.png)

- Enter password, again, this password will be used to login into the SOC portal.

- Select IP.

![alt text](./images/so12.png)

- Select "Yes" to add our Linux Mint IP to the analyst's list of Security Onion. This would allow us to access the SOC portal.

![alt text](./images/so13.png)

-  Enter the IP of the Linux Mint machine with the subnet mask of 24.

![alt text](./images/so14.png)

- Select "Yes".

![alt text](./images/so15.png)

- Now we will be waiting for a while until Security Onion finish the setup.

- Once its done, we can go to our Linux Mint machine to access the SOC portal.

![alt text](./images/so16.png)


#### Access Security Onion SOC Portal

- Login into the Linux Mint VM.

- In the firefox browser, type the IP of the Security Onion instance in the search bar.

- Click "Advanced" and "Accept the Risk and Continue".

![alt text](./images/mint9.png)

- Login with the email and password. Now you should see the SOC portal.

![alt text](./images/mint10.png)

