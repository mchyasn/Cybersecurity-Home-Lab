# Linux-Unix-Systems-Administration-Project

SYSTEM REQUIREMENTS: Linux computer OR Virtual machine.

TO RUN THE APPLICATION:
1. Open the Terminal in sudo mode
2. Type: sh user-crud.sh
3. Press Enter key.

This Bash shell script accomplishes the following:
• Displays the following menu and performs appropriate operation until user selects option 5 (quit):
---------------------------------------------------------------
Welcome to the User Management Application
1. Create a new user.
2. Delete a user.
3. Modify a user.
4. See last 10 created users.
5. Quit.
----------------------------------------------------------------
Please enter your choice:
• Creates a new user
- Ask for the username, Full Name, home directory, Shell, password.
- If the user exists, don’t ask for any of the remaining fields, only display a message that the user exists and go back to the main menu.
- Otherwise go ahead and create the user.
• Deletes a user
- Ask for the username, ask whether to delete home directory.
- If the user doesn’t exist, display a message saying so and go back to the main menu.
- Otherwise delete that user and home directory if entered so.
• Modifies a user
- Ask for username.
- If the user doesn’t exist, say so and go back to the main menu.
- Otherwise ask what you want to be changed:
i. Full Name.
ii. Shell.
iii. Home directory.
iv. Set new Password.
v. Expire the Password.
vi. Add user to group.
vii. Remove user from group.
- After the selection, ask for the appropriate field and set it appropriately.
• Retrieves last 10 created users
- Display a list of the last 10 users that have been created on the system.
• Quits
- Exit the program
