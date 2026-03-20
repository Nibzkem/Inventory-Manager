from models import db, Warehouse

def get_warehouse_by_id(warehouse_id):
    return db.session.get(Warehouse, warehouse_id)


def create_warehouse(name, location=None, capacity=None):
    new_warehouse = Warehouse(
        name=name,
        location=location,
        capacity=capacity
    )
    db.session.add(new_warehouse)
    db.session.commit()
    return new_warehouse


def update_warehouse(warehouse_id, new_name=None, new_location=None, new_capacity=None):
    warehouse = db.session.get(Warehouse, warehouse_id)

    if warehouse is None:
        return None

    if new_name is not None:
        warehouse.name = new_name
    if new_location is not None:
        warehouse.location = new_location
    if new_capacity is not None:
        warehouse.capacity = new_capacity

    db.session.commit()
    return warehouse


def delete_warehouse(warehouse_id):
    warehouse = db.session.get(Warehouse, warehouse_id)

    if warehouse is None:
        return False

    db.session.delete(warehouse)
    db.session.commit()
    return True