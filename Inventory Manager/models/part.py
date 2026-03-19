from .users import db

class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    cost_per_unit = db.Column(db.Float, nullable=True)

    inventory_items = db.relationship('Inventory', back_populates='part', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Part {self.id}: '{self.name}'>"