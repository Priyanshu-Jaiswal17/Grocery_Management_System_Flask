from app import db

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Products(db.Model):  # Capitalize class name
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'), nullable=False)

class Store(db.Model):
    store_id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(100), nullable=False)
    store_add = db.Column(db.String(200), nullable=False)
    store_description = db.Column(db.String(200), nullable=False)
    user_id =  db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)




