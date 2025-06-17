from DB_setup import Item, User, Category
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DB_setup import PATH

# creating an engine to the SQL database
engine = create_engine('sqlite:///' + PATH + 'ItemCatalogDB.db',
                       connect_args={'check_same_thread': False})

# Bind the db engine to a session to interact with the database.
Session = sessionmaker(bind=engine)

# Create a DataBase Session object.
session = Session()

# Fake user data
fake_user = User(
    name='Hossam Doma',
    email='conancode96@gmail.com',
    picture='''http://icons.iconarchive.com
               /icons/aha-soft/free-large-boss/512/Caucasian-Boss-icon.png'''
)
# Adding then committing
session.add(fake_user)
session.commit()

# Fake category data
fake_category1 = Category(
    name='MEWOs',
    user=fake_user
)
# Adding then committing
session.add(fake_category1)
session.commit()

# Fake category data
fake_category2 = Category(
    name='SewSew',
    user=fake_user
)
# Adding then committing
session.add(fake_category2)
session.commit()

# Fake Item data
item1 = Item(
    name='Cat',
    description='meow! meow! can you recognize me now?!',
    category=fake_category1,
    user=fake_user
)
# Adding then committing
session.add(item1)
session.commit()

# Fake Item data
item2 = Item(
    name='Birdy',
    description='sewsew! sewsew! can you recognize me now?!',
    category=fake_category2,
    user=fake_user
)
# Adding then committing
session.add(item2)
session.commit()

# Fake Item data
item3 = Item(
    name='OWL',
    description='AWWWWW! can you recognize me now?!',
    category=fake_category2,
    user=fake_user
)
# Adding then committing
session.add(item3)
session.commit()


# Voila!!! ^_^
print('Finished populating the database!')
