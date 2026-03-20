from .users import db, Users
from .part import Part
from .warehouse import Warehouse
from .inventory import Inventory

#loads all data bases from models

__all__ = ['db', 'Users', 'Part', 'Warehouse', 'Inventory']