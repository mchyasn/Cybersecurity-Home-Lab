#!/usr/bin/env python3


# Main router for the web application.


# used libraries/packages
import requests
import string
import json
import random
import httplib2


from flask import render_template, request, redirect, jsonify, url_for, Flask
from flask import make_response, flash
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DB_setup import User, Item, Category
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets


PATH = '/var/www/FlaskApp/FlaskApp/'


# Main Flask app object
app = Flask(__name__)

app.secret_key = 'super_secret_key_hehe_XD'


# Load the Google Sign-in API Client ID from clinet_secrets JSON.
CLIENT_ID = json.loads(
    open(PATH + 'Google_client_secrets.json', 'r').read())['web']['client_id']


# Connect to the database and create a database session.
db_engine = create_engine('sqlite:///' + PATH + 'ItemCatalogDB.db',
                          connect_args={'check_same_thread': False})


# Bind the database engine to a session.
Session = sessionmaker(bind=db_engine)


# Create a Session object to handle db interaction.
db_session = Session()


# Public JSON Endpoints


# Returns JSON of all the categories in the catalog.
@app.route('/api/v1/categories/JSON')
def categories_json():
    categories = db_session.query(Category).all()
    return jsonify(categories=[i.serialize for i in categories])


# Return JSON of all the items in the catalog.
@app.route('/api/v1/catalog/JSON')
def show_catalog_json():
    items = db_session.query(Item).order_by(Item.id.desc())
    return jsonify(catalog=[i.serialize for i in items])


# Return JSON of a particular item in the catalog.
@app.route('/api/v1/categories/<int:category_id>/item/<int:item_id>/JSON')
def catalog_item_json(category_id, item_id):

    if exists_category(category_id) and exists_item(item_id):
        item = db_session.query(Item) \
            .filter_by(id=item_id, category_id=category_id).first()
        if item is not None:
            return jsonify(item=item.serialize)
        # both exist but item doesn't belong to this category
        else:
            return jsonify(
                error='item {} does not belong to category {}.'
                      .format(item_id, category_id))
    else:
        return jsonify(error='The item or the category does not exist.')


# Helper Functions


# Create new user object, dumps them to the database.
def create_user(local_session):
    new_user = User(
        name=local_session['username'],
        email=local_session['email'],
        picture=local_session['picture']
    )
    db_session.add(new_user)
    db_session.commit()
    user = db_session.query(User).filter_by(email=local_session['email']).one()
    # print(user.id)
    return user.id


# fetches the user_id from a database by an Email (if found)
# else NONE is returned
def get_user_id(email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# fetches the user data object from a database by ID(int)
def get_user_info(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    return user


# Check if the item exists in the database,
def exists_item(item_id):
    item = db_session.query(Item).filter_by(id=item_id).first()
    if item is not None:
        return True
    else:
        return False


# Check if the category exists in the database.
def exists_category(category_id):
    category = db_session.query(Category).filter_by(id=category_id).first()
    if category is not None:
        return True
    else:
        return False


# Revoke Currently Signed in Google Account Access Token.
def gdisconnect():
    # Only disconnect if the user is connected.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps
            ('Failed to revoke access token for current logged in user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Default Router


# Home/Index/catalog-items default router
@app.route('/')
@app.route('/catalog/')
@app.route('/catalog/items/')
def home():
    all_categories = db_session.query(Category).all()
    all_items = db_session.query(Item).all()
    return render_template(
        'home_index.html',
        categories=all_categories,
        items=all_items
    )


# Authentication Routers


# Create anti-forgery (CSRF) state token to identify unique user requests
@app.route('/login/')
def login():
    # Unique random token to identify a user against CSRFs
    STATE = ''.join(
        random.choice(
            string.ascii_uppercase +
            string.ascii_lowercase + string.digits)
        for x in range(64))
    login_session['state'] = STATE
    return render_template("G_login_page.html",
                           state=STATE,
                           client_id=CLIENT_ID
                           )


# Logs out the currently logged-in user.
@app.route('/logout')
def logout():
    if 'username' in login_session:
        gdisconnect()
        del login_session['user_id']
        del login_session['google_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['access_token']

        flash("You have been successfully logged out!")
        return redirect(url_for('home'))
    else:
        flash("You were not logged in!")
        return redirect(url_for('home'))


# Connect to the new Google Sign-in OAuth2 method.
# The Client POST-ed the OTC to this endpoint,
# and now it will validate his state,
# and use the OTC to get the Access Token for him
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # fetch authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object!
        oauth_flow = flow_from_clientsecrets(PATH + 'Google_client_secrets.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    google_id = credentials.id_token['sub']
    if result['user_id'] != google_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_google_id = login_session.get('google_id')
    if stored_access_token is not None and google_id == stored_google_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['google_id'] = google_id

    # Get user info.
    userInfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userInfo_url, params=params)

    data = answer.json()

    # Assign Email as name if User does not have G+ Account
    if "name" in data:
        login_session['username'] = data['name']
    else:
        name_corp = data['email'][:data['email'].find("@")]
        login_session['username'] = name_corp
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if the user exists. If it doesn't, make a new one.
    userID = get_user_id(data["email"])
    if not userID:
        userID = create_user(login_session)
    login_session['user_id'] = userID

    # Show a welcome screen upon successful login.
    output = ''
    output += '<h2>Welcome, '
    output += login_session['username']
    output += '!</h2>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; '
    output += 'border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("You are now logged in as %s!" % login_session['username'])
    print("Voila!")
    return output


# Category Routers


# Adds a new category, supports both [GET, POST] methods
@app.route("/catalog/category/new/", methods=['GET', 'POST'])
def add_category():
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('login'))
    # POST request
    elif request.method == 'POST':
        if request.form['new-category-name'] == '':
            flash('The field cannot be empty.')
            return redirect(url_for('home'))

        category = db_session.query(Category). \
            filter_by(name=request.form['new-category-name']).first()
        if category is not None:
            flash('The entered category already exists.')
            return redirect(url_for('add_category'))

        new_category = Category(
            name=request.form['new-category-name'],
            user_id=login_session['user_id'])
        db_session.add(new_category)
        db_session.commit()
        flash('New category %s successfully created!' % new_category.name)
        return redirect(url_for('home'))
    # GET request
    else:
        return render_template('new_category_form.html')


# Edit a category.
@app.route('/catalog/category/<int:category_id>/edit/',
           methods=['GET', 'POST'])
def edit_category(category_id):

    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('login'))

    if not exists_category(category_id):
        flash("We are unable to process your request right now.")
        return redirect(url_for('home'))

    category = db_session.query(Category).filter_by(id=category_id).first()

    # If the logged in user does not have authorisation to
    # edit the category, redirect to homepage.
    if login_session['user_id'] != category.user_id:
        flash("We are unable to process your request right now.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if request.form['name']:
            category.name = request.form['name']
            db_session.add(category)
            db_session.commit()
            flash('Category successfully updated!')
            return redirect(url_for('show_items_in_category',
                                    category_id=category.id))
    # GET request
    else:
        return render_template('edit_category_form.html', category=category)


# Delete a category.
@app.route('/catalog/category/<int:category_id>/delete/',
           methods=['GET', 'POST'])
def delete_category(category_id):

    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('login'))

    if not exists_category(category_id):
        flash("We are unable to process your request right now.")
        return redirect(url_for('home'))

    category = db_session.query(Category).filter_by(id=category_id).first()

    # If the logged in user does not have authorisation to
    # edit the category, redirect to homepage.
    if login_session['user_id'] != category.user_id:
        flash("We are unable to process your request right now.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        db_session.delete(category)
        db_session.commit()
        flash("Category successfully deleted!")
        return redirect(url_for('home'))
    else:
        return render_template("delete_category_page.html", category=category)


# Item Routers


# Adds a new item.
@app.route("/catalog/item/new/", methods=['GET', 'POST'])
def add_item():
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('login'))
    elif request.method == 'POST':
        # Check if the item already exists in the database.
        # If it does, display an error.
        item = db_session.query(Item).\
                filter_by(name=request.form['name']).first()
        if item:
            if item.name == request.form['name']:
                flash('This item already exists in the database!')
                return redirect(url_for("add_item"))
        new_item = Item(
            name=request.form['name'],
            category_id=request.form['category'],
            description=request.form['description'],
            user_id=login_session['user_id']
        )
        db_session.add(new_item)
        db_session.commit()
        flash('New item created successfully!')
        return redirect(url_for('home'))
    # GET request
    # Fetches the items and categories this user entered
    else:
        items = db_session.query(Item). \
            filter_by(user_id=login_session['user_id']).all()
        categories = db_session.query(Category). \
            filter_by(user_id=login_session['user_id']).all()
        return render_template(
            'new_item_form.html',
            items=items,
            categories=categories
        )


# View an item by its ID.
@app.route('/catalog/item/<int:item_id>/')
def view_item(item_id):
    if exists_item(item_id):
        item = db_session.query(Item).filter_by(id=item_id).first()
        category = db_session.query(Category) \
            .filter_by(id=item.category_id).first()
        owner = db_session.query(User).filter_by(id=item.user_id).first()
        return render_template(
            "view_item_page.html",
            item=item,
            category=category,
            owner=owner
        )
    else:
        flash('Requested Resource not Found! Redirecting...')
        return redirect(url_for('home'))


# Edit an existing item.
@app.route("/catalog/item/<int:item_id>/edit/", methods=['GET', 'POST'])
def edit_item(item_id):

    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('login'))

    if not exists_item(item_id):
        flash('''Requested Resource not found!
              Unable to process your request right now!''')
        return redirect(url_for('home'))

    item = db_session.query(Item).filter_by(id=item_id).first()
    if login_session['user_id'] != item.user_id:
        flash("You were not authorised to access that page.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            item.category_id = request.form['category']
        db_session.add(item)
        db_session.commit()
        flash('Item successfully updated!')
        return redirect(url_for('edit_item', item_id=item_id))
    else:
        categories = db_session.query(Category). \
            filter_by(user_id=login_session['user_id']).all()
        return render_template(
            'update_item_page.html',
            item=item,
            categories=categories
        )


# Delete an existing item.
@app.route("/catalog/item/<int:item_id>/delete/", methods=['GET', 'POST'])
def delete_item(item_id):

    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('login'))

    if not exists_item(item_id):
        flash("We are unable to process your request right now.")
        return redirect(url_for('home'))

    item = db_session.query(Item).filter_by(id=item_id).first()
    if login_session['user_id'] != item.user_id:
        flash("You are not authorised to access that page.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        db_session.delete(item)
        db_session.commit()
        flash("Item successfully deleted!")
        return redirect(url_for('home'))
    else:
        return render_template('delete_item_page.html', item=item)


# Show items in a particular category.
@app.route('/catalog/category/<int:category_id>/items/')
def show_items_in_category(category_id):

    if not exists_category(category_id):
        flash("We are unable to process your request right now.")
        return redirect(url_for('home'))

    category = db_session.query(Category).filter_by(id=category_id).first()
    items = db_session.query(Item).filter_by(category_id=category.id).all()
    total = db_session.query(Item).filter_by(category_id=category.id).count()
    return render_template(
        'catalog_items.html',
        category=category,
        items=items,
        total=total
    )


# Create new item by Category ID.
@app.route("/catalog/category/<int:category_id>/item/new/",
           methods=['GET', 'POST'])
def add_item_by_category(category_id):
    """Create new item by Category ID."""

    if 'username' not in login_session:
        flash("You were not authorised to access that page.")
        return redirect(url_for('login'))
    elif request.method == 'POST':
        # Check if the item already exists in the database.
        # If it does, display an error.
        item = db_session.query(Item).\
                filter_by(name=request.form['name']).first()
        if item:
            if item.name == request.form['name']:
                flash('The item already exists in the database!')
                return redirect(url_for("add_item"))
        new_item = Item(
            name=request.form['name'],
            category_id=category_id,
            description=request.form['description'],
            user_id=login_session['user_id'])
        db_session.add(new_item)
        db_session.commit()
        flash('New item successfully created!')
        return redirect(url_for('show_items_in_category',
                                category_id=category_id))
    else:
        category = db_session.query(Category).filter_by(id=category_id).first()
        return render_template('new_item_predefined_category_form.html',
                               category=category)


if __name__ == "__main__":
    app.secret_key = 'super_secret_key_hehe_XD'
    app.debug = True
    app.run(host='0.0.0.0', port=80)
    # app.run(host="0.0.0.0", port=8000, debug=True)
