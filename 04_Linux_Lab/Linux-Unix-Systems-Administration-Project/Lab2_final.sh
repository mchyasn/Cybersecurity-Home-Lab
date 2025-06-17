# Owner: mchyasn
# Date: 6 I 2018

#!/bin/bash

PASSWD_FILE=/etc/passwd

addUser()
{
# PASSWD_FILE=/etc/passwd
echo -n "Enter username: "
read username
# try to locate username in /etc/passwd
# use /dev/null to send any unwanted output from program/command
# store exit status of grep
# if found grep will return 0 exit stauts
# if not found, grep will return a nonzero exit stauts
grep "^$username" $PASSWD_FILE > /dev/null
status=$?
if test $status -eq 0
then
    echo "$username exists in passwd file."
else
    echo "$username not fount in passwd file"
    echo -n "Enter full name: "
    read fullname
    echo -n "Enter home directory: "
    read home_directory
    echo -n "Enter shell: "
    read shell
    echo -n "Enter password: "
    read password
    echo "creating user $username"
    sudo useradd -c $fullname   -d $home_directory    -m   -p $password    -s $shell    $username
fi
}

delUser()
{
echo " Enter username to delete: "
read username
grep "^$username" $PASSWD_FILE > /dev/null
status=$?
if test $status -eq 0
then
    echo "$username exists in passwd file."

    echo " delete home directory? (y or n): "
    read delete_dir
    case $delete_dir in
    y) echo "Delete home directory: "
    sudo userdel -r $username
    ;;
    n) echo "Keep home directory: "
    sudo userdel $username
    ;;
    *) echo "[unrecognised value]"
    exit
    esac
else
    echo "$username not found in passwd file"
fi
}

modUser()
{
echo " Enter username to modify: "
read username
grep "^$username" $PASSWD_FILE > /dev/null
status=$?
if test $status -eq 0
then
    echo "$username exists in passwd file."
    echo "---------------------------------"
    echo "What do you want to be changed?"
    echo " 1. Full Name."
    echo ""
    echo " 2. Shell."
    echo ""
    echo " 3. Home Directory."
    echo ""
    echo " 4. Set new Password."
    echo ""
    echo " 5. Expire the Password."
    echo ""
    echo " 6. Add user to group."
    echo ""
    echo " 7. Remove user from group."
    echo "---------------------------------"
    read -p "Please enter your choice: " mod
    case $mod in
    1) echo "Enter new full name: "
       read fullname
       sudo usermod -c $fullname $username
    ;;
    2) echo "Enter new shell: "
       read shell
       sudo usermod -s $shell $username
    ;;
    3) echo "Enter new home directory: "
       read home_directory
       sudo usermod -d $home_directory $username
    ;;
    4) echo "Enter new password: "
       read password
       sudo usermod -p $password $username
    ;;
    5) echo "Enter new pasword expiration: "
       read exp
       sudo usermod -e $exp $username
    ;;
    6) echo "Enter new group for this username: "
       read group
       sudo usermod -g $group $username
    ;;
    7) echo "Enter the group that this username leaves: "
       read group
       sudo deluser $username $group $username
    ;;
    *) echo "[unrecognised value]"
       exit
    esac
else
    echo "$username not fount in passwd file"
fi
}

while :;
do
echo "============================================"
echo "Welcome to the User Management Application"
echo " 1. Create a new user."
echo ""
echo " 2. Delete a user."
echo ""
echo " 3. Modify a user."
echo ""
echo " 4. See last 10 created users."
echo ""
echo " 5. Quit."
echo "============================================"
read -p "Please enter your choice: " choice
case $choice in
1) echo "new_user"
   addUser
;;
2) echo "delete_user"
   delUser
;;
3) echo "modify_user"
   modUser
;;
4) echo "List of the last 10 users: "
   tail /etc/passwd
;;
5) exit
;;
*) echo "[unrecognised value]"
   exit
esac
sleep 2
clear
done
