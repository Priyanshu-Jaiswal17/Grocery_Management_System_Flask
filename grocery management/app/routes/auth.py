from flask import Blueprint,jsonify,request,current_app
from app.models.models import User
from app import db
import jwt,datetime

auth_bp = Blueprint("auth",__name__)

@auth_bp.route("/login", methods = ["POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        registerd_user = User.query.filter_by(email=email).first()

        if not registerd_user:
            return jsonify({"message" : "Please register first"}),404
        
        if registerd_user.password == password :
            role = registerd_user.role
            payload = {
            "email": email,
            "role": role,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=90)
            }
            SECRET_KEY = current_app.config['SECRET_KEY']
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return jsonify({"message" : "Login success",'token':token}),200
        
        else:
            return jsonify({"message": f"wrong password try again"}) , 401


@auth_bp.route("/user_register",methods = ["POST"])
def register():
    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('username')
        password = request.form.get('password')
        role = "user"

        registered_user = User.query.filter_by(email=email).first()

        if registered_user:
            return jsonify({"message" : f"this {email} is already registerd"}),401
        if len(password) < 8:
            return jsonify({"message": f"please use strong password"}) , 401
        else:
            
            new_user = User(name = name,email=email,password=password,role = role)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"message" : "registerd successfully"}),200
        

@auth_bp.route("/owner_register",methods = ["POST"])
def register_owner():
    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('username')
        password = request.form.get('password')
        role= "owner"

        registered_user = User.query.filter_by(email=email).first()

        if registered_user:
            return jsonify({"message" : f"this {email} is already registerd"}),401
        if len(password) < 8:
            return jsonify({"message": f"please use strong password"}) , 401
        else:
            new_user = User(name = name,email=email,password=password,role=role)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"message" : "registerd successfully"}),200


@auth_bp.route("/logout")
def logout():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401
    token = auth_header.split(" ")[1]
    try:
        secret = current_app.config["SECRET_KEY"]
        jwt.decode(token, secret, algorithms=["HS256"])
        return jsonify({"message": "Logout successful"}), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401