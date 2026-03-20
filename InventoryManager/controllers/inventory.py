from models import db, Inventory

def add_part_to_warehouse(warehouse_id, part_id, quantity):
    item = Inventory.query.filter_by( warehouse_id=warehouse_id, part_id=part_id).first()

    if item:
        item.quantity += quantity
    else:
        item = Inventory(
            warehouse_id=warehouse_id,
            part_id=part_id,
            quantity=quantity
        )
        db.session.add(item)

    db.session.commit()
    return item

def get_parts_in_warehouse(warehouse_id):
    return Inventory.query.filter_by(warehouse_id=warehouse_id).all()


def update_inventory(warehouse_id, part_id, new_quantity):
    item = Inventory.query.filter_by(
        warehouse_id=warehouse_id,
        part_id=part_id
    ).first()

    if not item:
        return None

    item.quantity = new_quantity
    db.session.commit()
    return item

def remove_part_from_warehouse(warehouse_id, part_id):
    item = Inventory.query.filter_by(
        warehouse_id=warehouse_id,
        part_id=part_id
    ).first()

    if not item:
        return False

    db.session.delete(item)
    db.session.commit()
    return True