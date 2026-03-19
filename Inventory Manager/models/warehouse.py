from .users import db

class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    capacity = db.Column(db.Integer, nullable=True)

    inventory_items = db.relationship('Inventory', back_populates='warehouse', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Warehouse {self.id}: '{self.name}'>"