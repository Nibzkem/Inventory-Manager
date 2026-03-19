from models import db, Users

def get_all_users():
    return Users.query.all()

def get_user_by_id(user_id):
    return Users.query.get(user_id)

def create_user(firstname, lastname, username, password, admin):
    new_user = Users(
        firstname=firstname,
        lastname=lastname,
        username=username,
        password=password,
        admin=admin
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return new_user


def update_user(user_id, new_firstname=None, new_lastname=None, new_username=None, new_password=None, new_admin=None):
    user = db.session.get(Users, user_id)
    
    if user is None:
        return None

    if new_firstname is not None:
        user.firstname = new_firstname
    if new_lastname is not None:
        user.lastname = new_lastname
    if new_username is not None:
        user.username = new_username
    if new_password is not None:
        user.hashPassword = new_password
    if new_admin is not None:
        user.admin = new_admin

    db.session.commit()
    return user


def delete_user(user_id):
    user = db.session.get(Users, user_id)
    
    if user is None:
        return False

    db.session.delete(user)
    db.session.commit()
    return True