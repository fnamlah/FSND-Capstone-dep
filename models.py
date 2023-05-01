import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


database_path = os.environ['DATABASE_URL']
if database_path.startswith("postgres://"):
  database_path = database_path.replace("postgres://", "postgresql://", 1)

db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    with app.app_context():

        db.app = app

        db.init_app(app)
        db.create_all()



# Drops the database tables and starts fresh
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

class Store(db.Model):
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(100), unique=True)

    products = db.relationship('Product', back_populates='store')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, store_name):
        self.store_name = store_name

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'store_name': self.store_name,
            'created_at': self.created_at
        }
    
    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    store = db.relationship('Store', back_populates='products')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, quantity, price, store_id):
        self.name = name
        self.quantity = quantity
        self.price = price
        self.store_id = store_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'price': self.price,
            'store_id': self.store_id,
            'created_at': self.created_at
        }
    
    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
