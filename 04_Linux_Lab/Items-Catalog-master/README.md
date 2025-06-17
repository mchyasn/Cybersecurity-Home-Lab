# Item Catalog Project
Udacity's Full Stack Web Development Nanodegree 2nd Project

## Goal
Developing a web application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Why this project?
Modern web applications perform a variety of functions and provide amazing features and utilities to their users; but deep down, it’s really all just creating, reading, updating and deleting data. In this project, you’ll combine your knowledge of building dynamic websites with persistent data storage to create a web application that provides a compelling service to your users.

### Features
- [x] Google OAuth2 Sign-in authentication and authorisation check.
- [x] Full Create/Read/Update/Delete (CRUD) support using Python, SQLAlchemy and Flask.
- [x] JSON endpoints support.

## Requirements

* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/downloads.html)
* [Git](https://git-scm.com/download)
* [Python 3.6](https://www.python.org/downloads/)
* [Pip 3.6](https://pip.pypa.io/en/stable/installing/)
* [Flask](https://palletsprojects.com/p/flask/)
* [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy/)

## Steps to reproduce

1) Download and install [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
2) Download and install [Vagrant](https://www.vagrantup.com/downloads.html)
3) Download [this](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip) file that configures Vagrant to download an Ubuntu box, PostgreSQL, Python 3 and other dependecies...
4) Unzip this file, navigate to the `vagrant` folder
5) Open a shell terminal inside the folder and run
    ```bash 
    vagrant up
    ```
6) After the process is finished, run the following command to login to Ubuntu box
    ```bash
    vagrant ssh
    ```
7) Now, you are inside the Ubuntu box terminal shell, go to `\vagrant` using the command `cd \vagrant`, this folder is synced with the same vagrant folder in the configuration file you downloaded above

8) Download or clone this repository, and navigate to it.

9) Install or upgrade Python 3.6 / Pip 3.6:
    ```bash
    sudo apt-get install software-properties-common python-software-properties
    sudo add-apt-repository ppa:jonathonf/python-3.6
    apt-get update
    apt-get install python3.6
    python3.6 -V
    
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3.6 get-pip.py --user
    sudo pip3.6 install -upgrade pip
    pip -V
    ```
10) Run the `requirements.txt` file to install any other dependency package not properly installed 
    ```bash
    sudo pip3.6 install -r requirements.txt
    ```
11. Set up the database schema running:
    ```bash
    python3.6 DB_setup.py
    ```
12. Insert fake data to jump-start the app with some data
    ```bash
    python3.6 dummy_data.py
    ```
13. Run this application:
    ```bash
    python3.6 catalogApp.py
    ```
14. Open `http://localhost:8000/` in your Web browser and wonder :grin:

## Category Routers

* `@app.route("/catalog/category/new/", methods=['GET', 'POST'])` Adds a Category
* `@app.route('/catalog/category/<int:category_id>/edit/', methods=['GET', 'POST'])` Edits a specific Category
* `@app.route('/catalog/category/<int:category_id>/delete/', methods=['GET', 'POST'])` Deletes a specific Category

## Item Routers

* `@app.route("/catalog/item/new/", methods=['GET', 'POST'])` - Creates new item from scratch
* `@app.route("/catalog/category/<int:category_id>/item/new/", methods=['GET', 'POST'])` - Creates a new item given a specific category 
* `@app.route('/catalog/item/<int:item_id>/')` - Views an item
* `@app.route("/catalog/item/<int:item_id>/edit/", methods=['GET', 'POST'])` - Updates a given item
* `@app.route("/catalog/item/<int:item_id>/delete/", methods=['GET', 'POST'])` - Deletes a given item
* `@app.route('/catalog/category/<int:category_id>/items/')` - Lists all items for a given category

## JSON Endpoints
* **`/api/v1/categories/JSON`** Returns a JSON of all the categories in the catalog.
* **`/api/v1/catalog/JSON`** Return a JSON of all the items in the catalog.
* **`/api/v1/categories/<int:category_id>/item/<int:item_id>/JSON`** Return a JSON of a particular item in the catalog.

## Tests
- [x] PEP 8 Compatible code
- [x] Accessing endpoints that require authorization without so produces a useful message about the invalid request along with redirection to the suitable resource (most probably homepage)

## TroubleShooting
In case the app doesn't run, follow the following possible solutions:
- Make sure you have `python3.6` installed along with the requirements in **step 10**
- Feeling stuck? Follow this [tutorial](https://www.rosehosting.com/blog/how-to-install-python-3-6-on-ubuntu-16-04/) to install `python3.6` on `Ubuntu 16.04`
- Open an issue ASAP, I will see to it within one day at most, Cheers! :grin:
