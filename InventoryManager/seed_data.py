"""Seed script for Inventory Manager

This creates tables (if missing) and inserts dummy Users, Parts, Warehouses and Inventory rows.
"""
from app import app
from models import db, Users, Part, Warehouse, Inventory


def seed():
    with app.app_context():
        # Ensure tables exist
        db.create_all()

        # Clear existing data (keeps schema)
        db.session.query(Inventory).delete()
        db.session.query(Part).delete()
        db.session.query(Warehouse).delete()
        db.session.query(Users).delete()
        db.session.commit()

        users = []
        users.append(Users(firstname='Admin', lastname='User', username='admin', hashPassword='password', admin=1))
        for i in range(2, 11):
            users.append(Users(firstname=f'First{i}', lastname=f'Last{i}', username=f'user{i}', hashPassword='pass{i}', admin=0))
        db.session.add_all(users)

        parts = []
        for i in range(1, 11):
            parts.append(Part(name=f'Part {i}', description=f'Description for part {i}', cost_per_unit=round(1.0 + i * 0.5, 2)))
        db.session.add_all(parts)
        
        warehouses = []
        for i in range(1, 11):
            warehouses.append(Warehouse(name=f'Warehouse {i}', location=f'Location {i}', capacity=100 * i))
        db.session.add_all(warehouses)

        db.session.commit()  

        # Create inventory entries (one per part mapped to a warehouse)
        inventory_items = []
        # Map each part to a different warehouse with deterministic quantities
        for idx, p in enumerate(parts):
            wh = warehouses[idx % len(warehouses)]
            qty = (idx + 1) * 10
            inventory_items.append(Inventory(warehouse_id=wh.id, part_id=p.id, quantity=qty))

        inventory_items.append(Inventory(warehouse_id=warehouses[0].id, part_id=parts[1].id, quantity=5))
        inventory_items.append(Inventory(warehouse_id=warehouses[1].id, part_id=parts[2].id, quantity=7))

        db.session.add_all(inventory_items)
        db.session.commit()

        print('Seeding complete:')
        print(f'  Users: {Users.query.count()}')
        print(f'  Parts: {Part.query.count()}')
        print(f'  Warehouses: {Warehouse.query.count()}')
        print(f'  Inventory items: {Inventory.query.count()}')


if __name__ == '__main__':
    seed()
