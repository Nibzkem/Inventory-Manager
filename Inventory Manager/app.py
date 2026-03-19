import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Users, Part, Warehouse, Inventory
from sqlalchemy import func


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret')
db.init_app(app)


@app.before_request
def require_login():
    # Allow access to the login page and static files without being logged in
    allowed_endpoints = ('login', 'register', 'about','static')
    if request.endpoint in allowed_endpoints:
        return
    # If the user is not logged in, redirect to login
    if 'username' not in session:
        return redirect(url_for('login'))

#------------------------------------------
# Login
#------------------------------------------





#------------------------------------------
# Read
#------------------------------------------




@app.route('/parts', methods=['GET'])
def index():
    # Load all parts
    parts = Part.query.all()
    # aggregate current stock totals directly from the Inventory table to avoid any stale relationship state
    totals = db.session.query(Inventory.part_id, func.coalesce(func.sum(Inventory.quantity), 0)).group_by(Inventory.part_id).all()
    totals_map = {part_id: total for part_id, total in totals}

    # determine if current user is admin
    is_admin = False
    if 'user_id' in session:
        user = Users.query.get(session['user_id'])
        try:
            is_admin = int(getattr(user, 'admin', 0)) == 1
        except Exception:
            is_admin = False

    return render_template('parts.html', parts=parts, totals_map=totals_map, is_admin=is_admin)


@app.route('/parts/<int:part_id>')
def part_detail(part_id):
    # Get part or 404
    part = Part.query.get_or_404(part_id)
    # total stock across all warehouses
    total_stock = sum(item.quantity for item in part.inventory_items) if part.inventory_items else 0
    # per-warehouse breakdown
    warehouses = []
    for item in part.inventory_items:
        wh = item.warehouse
        warehouses.append({
            'name': wh.name if wh else '-',
            'location': wh.location if wh else '-',
            'quantity': item.quantity
        })
    # also provide full warehouse list for the update form
    warehouses_all = Warehouse.query.all()
    return render_template('part_detail.html', part=part, total_stock=total_stock, warehouses=warehouses, warehouses_all=warehouses_all)


@app.route('/parts/<int:part_id>/update_stock', methods=['POST'])
def update_stock(part_id):
    part = Part.query.get_or_404(part_id)
    warehouse_id = request.form.get('warehouse_id')
    quantity_raw = request.form.get('quantity')
    try:
        quantity = int(quantity_raw)
    except (TypeError, ValueError):
        quantity = 0

    if not warehouse_id:
        return redirect(url_for('part_detail', part_id=part_id))

    warehouse = Warehouse.query.get(warehouse_id)
    if not warehouse:
        return redirect(url_for('part_detail', part_id=part_id))

    # find existing inventory item and update directly
    item = Inventory.query.filter_by(warehouse_id=warehouse.id, part_id=part.id).first()
    if item:
        item.quantity = quantity
    else:
        item = Inventory(warehouse_id=warehouse.id, part_id=part.id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    return redirect(url_for('part_detail', part_id=part_id))


@app.route('/parts/add', methods=['GET', 'POST'])
def add_part():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        description = (request.form.get('description') or '').strip()
        cost_raw = (request.form.get('cost_per_unit') or '').strip()

        errors = []
        if not name:
            errors.append('Name is required.')
        if len(name) > 100:
            errors.append('Name must be 100 characters or fewer.')
        if description and len(description) > 500:
            errors.append('Description must be 500 characters or fewer.')

        cost = None
        if cost_raw:
            try:
                cost = float(cost_raw)
                if cost < 0:
                    errors.append('Cost per unit cannot be negative.')
            except (ValueError, TypeError):
                errors.append('Cost per unit must be a number.')

        if errors:
            return render_template('add_part.html', error=' '.join(errors), name=name, description=description, cost_per_unit=cost_raw)

        # Valid — create and commit
        new_part = Part(name=name, description=description, cost_per_unit=cost)
        db.session.add(new_part)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_part.html')

@app.route('/manage-account', methods=['GET', 'POST'])
def manage_account():
    # require logged-in user (before_request already enforces this)
    user = None
    if 'user_id' in session:
        user = Users.query.get(session['user_id'])
    if user is None:
        return redirect(url_for('login'))

    message = None
    if request.method == 'POST':
        new_password = (request.form.get('new_password') or '').strip()
        if not new_password:
            message = 'Password cannot be empty.'
        else:
            user.hashPassword = new_password
            db.session.commit()
            message = 'Password updated successfully.'

    return render_template('manage_account.html', user=user, message=message)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/parts/<int:part_id>/edit', methods=['GET', 'POST'])
def edit_part(part_id):
    part = Part.query.get_or_404(part_id)
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        description = (request.form.get('description') or '').strip()
        cost_raw = (request.form.get('cost_per_unit') or '').strip()

        errors = []
        if not name:
            errors.append('Name is required.')
        if len(name) > 100:
            errors.append('Name must be 100 characters or fewer.')
        if description and len(description) > 500:
            errors.append('Description must be 500 characters or fewer.')

        cost = None
        if cost_raw:
            try:
                cost = float(cost_raw)
                if cost < 0:
                    errors.append('Cost per unit cannot be negative.')
            except (ValueError, TypeError):
                errors.append('Cost per unit must be a number.')

        if errors:
            # Do NOT commit; show form with error and submitted values
            return render_template('edit_part.html', part=part, error=' '.join(errors), name=name, description=description, cost_per_unit=cost_raw)

        # Valid — apply and commit
        part.name = name
        part.description = description
        part.cost_per_unit = cost
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_part.html', part=part)


@app.route('/parts/<int:part_id>/delete')
def delete_part(part_id):
    # only allow admins to delete parts
    user = None
    if 'user_id' in session:
        user = Users.query.get(session['user_id'])
    # Interpret admin as integer (works if stored as int or string '1')
    try:
        is_admin = int(getattr(user, 'admin', 0)) == 1
    except Exception:
        is_admin = False
    if not user or not is_admin:
        # do not flash; simply redirect
        return redirect(url_for('index'))

    part = Part.query.get_or_404(part_id)
    db.session.delete(part)
    db.session.commit()
    return redirect(url_for('index'))

#------------------------------------------
# Authentication
#------------------------------------------

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = (request.form.get('password') or '')
        user = Users.query.filter_by(username=username).first()
        if user and user.hashPassword == password:
            session['username'] = user.username
            session['user_id'] = user.id
            return redirect(url_for('index'))
        error = 'Invalid username or password.'
        return render_template('login.html', error=error, username=username)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = (request.form.get('firstname') or '').strip()
        lastname = (request.form.get('lastname') or '').strip()
        username = (request.form.get('username') or '').strip()
        password = (request.form.get('password') or '')
        admin_checked = request.form.get('admin')

        errors = []
        if not firstname:
            errors.append('First name is required.')
        if not lastname:
            errors.append('Last name is required.')
        if not username:
            errors.append('Username is required.')
        else:
            # ensure username is unique
            if Users.query.filter_by(username=username).first():
                errors.append('Username already exists.')
        if not password:
            errors.append('Password is required.')

        admin_value = 1 if admin_checked else 0

        if errors:
            return render_template('register.html', error=' '.join(errors), firstname=firstname, lastname=lastname, username=username, admin=admin_checked)

        # create user (store password as plain text to match existing project style)
        new_user = Users(firstname=firstname, lastname=lastname, username=username, hashPassword=password, admin=admin_value)
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Failed to create user: ' + str(e))
            return render_template('register.html', error='Failed to create user.', firstname=firstname, lastname=lastname, username=username, admin=admin_checked)

        flash('Registration successful. You can now log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/warehouses/add', methods=['GET', 'POST'])
def add_warehouse():
    # only admins may add warehouses
    user = None
    if 'user_id' in session:
        user = Users.query.get(session['user_id'])
    try:
        is_admin = int(getattr(user, 'admin', 0)) == 1
    except Exception:
        is_admin = False
    if not is_admin:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        location = (request.form.get('location') or '').strip()
        capacity_raw = (request.form.get('capacity') or '').strip()

        errors = []
        if not name:
            errors.append('Name is required.')
        if len(name) > 100:
            errors.append('Name must be 100 characters or fewer.')
        if location and len(location) > 100:
            errors.append('Location must be 100 characters or fewer.')

        capacity = None
        if capacity_raw:
            try:
                capacity = int(capacity_raw)
                if capacity < 0:
                    errors.append('Capacity cannot be negative.')
            except (ValueError, TypeError):
                errors.append('Capacity must be an integer.')

        if errors:
            return render_template('add_warehouse.html', error=' '.join(errors), name=name, location=location, capacity=capacity_raw)

        # create and commit
        wh = Warehouse(name=name, location=location or None, capacity=capacity)
        db.session.add(wh)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_warehouse.html')

#------------------------------------------
# Execute Application
#------------------------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)