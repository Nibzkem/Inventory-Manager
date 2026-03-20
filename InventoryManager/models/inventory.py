from models import db

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    warehouse = db.relationship('Warehouse', back_populates='inventory_items')
    part = db.relationship('Part', back_populates='inventory_items')

    def __repr__(self):
        return f"<Inventory {self.id}: '{self.name}'>"