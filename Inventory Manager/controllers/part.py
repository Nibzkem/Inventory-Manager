from models import db, Part

def get_part_by_id(part_id):
    return db.session.get(Part, part_id)


def create_part(name, description=None, cost_per_unit=None):
    new_part = Part(
        name=name,
        description=description,
        cost_per_unit=cost_per_unit
    )
    db.session.add(new_part)
    db.session.commit()
    return new_part


def update_part(part_id, new_name=None, new_description=None, new_cost_per_unit=None):
    part = db.session.get(Part, part_id)
    
    if part is None:
        return None

    if new_name is not None:
        part.name = new_name
    if new_description is not None:
        part.description = new_description
    if new_cost_per_unit is not None:
        part.cost_per_unit = new_cost_per_unit

    db.session.commit()
    return part


def delete_part(part_id):
    part = db.session.get(Part, part_id)
    
    if part is None:
        return False

    db.session.delete(part)
    db.session.commit()
    return True