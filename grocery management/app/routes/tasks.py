from flask import Blueprint,jsonify,request,current_app
from app.models.models import Products,User,Store
from app import db
import jwt 

tasks_bp = Blueprint("tasks",__name__)

# route for viewing store.. (for user -> all stores , for owner -> the stores they own)
@tasks_bp.route("/get_stores", methods = [ "GET"])
def view_all_stores():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401
    token = auth_header.split(" ")[1]
    try:
        secret = current_app.config["SECRET_KEY"]
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        email = payload.get("email")  # ✅ Get email from JWT
        role = payload.get("role")
        user = User.query.filter_by(email=email).first()
        user_id = user.user_id
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        if user:
            if role == "user":
                stores = Store.query.all()
                store_list = [{
                    "store_name": s.store_name,
                    "store_add": s.store_add,
                    "store_description": s.store_description
                } for s in stores]
                return jsonify(store_list), 200
            
            elif role == "owner":
                    stores = Store.query.filter_by(user_id=user_id).all()
                    store_list = [{
                        "store_id": s.store_id,
                        "store_name": s.store_name,
                        "store_add": s.store_add,
                        "store_description": s.store_description
                    } for s in stores]
                    return jsonify(store_list), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired , Login again"}), 401
    
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token, Login again"}), 401

#route for adding another store for the owner 
@tasks_bp.route("/add_store", methods = ["POST"])
def Add_store():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = auth_header.split(" ")[1]

    try:
        secret = current_app.config["SECRET_KEY"]
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        email = payload.get("email")
        role = payload.get("role")

        if role != "owner":
            return jsonify({"error": "Only owners can Add Stores"}), 403
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"message": "User not found"}), 404
        store_name = request.form.get('store_name')
        store_add = request.form.get('store_address')
        store_description = request.form.get('store_description')
        if not all ([store_name,store_add,store_description]):
            return jsonify({"message" : 'Please fill all the fields'}),400

        new_store = Store(store_name = store_name, store_add = store_add, store_description = store_description,user_id = user.user_id)
        db.session.add(new_store)
        db.session.commit()
        return jsonify({
            "message": "Store registered successfully",
            "store_id": new_store.store_id,
            "store_name": new_store.store_name,
            "store_description" : new_store.store_description,
            "store_address" : new_store.store_add
        }), 201
        
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired, login again"}), 401

    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token, login again"}), 401


# route for viewing products for the particular store.. (same for all )
@tasks_bp.route("/get_products/<int:store_id>",methods = ["GET"])
def veiw_products_of_store(store_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401
    token = auth_header.split(" ")[1]
    try:
        secret = current_app.config["SECRET_KEY"]
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        email = payload.get("email")
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        product_list = Products.query.filter_by(store_id=store_id).all()
        names = [product.product_name for product in product_list]
        return jsonify({"product_names": names}), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired , Login again"}), 401
    
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token, Login again"}), 401


# Route for adding a product to a specific store (only by the owner of that store)
@tasks_bp.route("/add_product/<int:store_id>", methods=["POST"])
def add_product(store_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = auth_header.split(" ")[1]

    try:
        secret = current_app.config["SECRET_KEY"]
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        email = payload.get("email")
        role = payload.get("role")

        if role != "owner":
            return jsonify({"message": "Only owners can add products"}), 403

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        # ✅ Check that the store belongs to the logged-in owner
        store = Store.query.filter_by(store_id=store_id, user_id=user.user_id).first()
        if not store:
            return jsonify({"error": "You do not own this store"}), 403

        # ✅ Get form data
        product_name = request.form.get('Product_name')
        product_quantity = request.form.get('Quantity')
        product_price = request.form.get('Price')

        if not all([product_name, product_quantity, product_price]):
            return jsonify({"message": "Please provide product_name, quantity, and price"}), 400

        try:
            product_price = float(product_price)
        except ValueError:
            return jsonify({"message": "Price must be a valid number"}), 400

        # ✅ Create and save the product
        new_product = Products(
            product_name=product_name,
            quantity=product_quantity,
            price=product_price,
            store_id=store_id
        )
        db.session.add(new_product)
        db.session.commit()

        return jsonify({"message": f"Product '{product_name}' added successfully"}), 201

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired, login again"}), 401

    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token, login again"}), 401


# route for viewing products_info for the product.. (same for all )
@tasks_bp.route("/get_product_info/<int:product_id>", methods=["GET"])
def get_product_info(product_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401
    token = auth_header.split(" ")[1]
    try:
        secret = current_app.config["SECRET_KEY"]
        jwt.decode(token, secret, algorithms=["HS256"])

        product = Products.query.get(product_id)
        if not product:
            return jsonify({"message": "Product not found"}), 404
        product_data = {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "quantity": product.quantity,
            "price": product.price,
            "store_id": product.store_id
        }
        return jsonify({"product_info": product_data}), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired , Login again"}), 401
    
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token, Login again"}), 401


# route for delete a product from the store (only for owners)
@tasks_bp.route("/remove_product/<int:product_id>", methods=["DELETE"])
def remove_product(product_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401
    token = auth_header.split(" ")[1]

    try:
        secret = current_app.config["SECRET_KEY"]
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        email = payload.get("email")  # ✅ Get email from JWT
        role = payload.get("role")
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        if user:
            if role == "owner":
                product = Products.query.get(product_id)
                if product:
                    store = Store.query.get(product.store_id)
                    
                    if store and store.user_id == user.user_id:
                        db.session.delete(product)
                        db.session.commit()
                        return jsonify({"message": f"Product '{product.product_name}' deleted successfully"}), 200
                    else:
                        return jsonify({"error": "You do not have permission to delete this product"}), 403
                else:
                    return jsonify({"error": "Product not found"}), 404
                
            else :
                return jsonify({"error ": "only owners can delete a product"})
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired , Login again"}), 401
    
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token, Login again"}), 401


#route for editing a product of the owners's store
@tasks_bp.route("/edit_product/<int:product_id>", methods=["POST"])
def edit_product(product_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = auth_header.split(" ")[1]

    try:
        secret = current_app.config["SECRET_KEY"]
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        email = payload.get("email")
        role = payload.get("role")

        if role != "owner":
            return jsonify({"error": "Only owners can edit products"}), 403

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        product = Products.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        store = Store.query.filter_by(store_id=product.store_id, user_id=user.user_id).first()
        if not store:
            return jsonify({"error": "You do not have permission to edit this product"}), 403

        # ✅ Optional input fields
        product_name = request.form.get('Product_name')
        product_quantity = request.form.get('Quantity')
        product_price = request.form.get('Price')

        # ✅ Update only if provided
        if product_name:
            product.product_name = product_name
        if product_quantity:
            product.quantity = product_quantity
        if product_price:
            try:
                product.price = float(product_price)
            except ValueError:
                return jsonify({"message": "Price must be a valid number"}), 400
        db.session.commit()
        return jsonify({"message": f"Product '{product.product_name}' updated successfully"}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired, login again"}), 401

    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token, login again"}), 401
    





