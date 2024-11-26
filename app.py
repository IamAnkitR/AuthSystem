from flask import Flask, request, jsonify
from flask_mail import Mail
from models import db, User, OTP
from config import Config
from utils import generate_otp, send_email, is_otp_valid

app = Flask(__name__)
app.config.from_object(Config)

print(app.config["MAIL_SERVER"])

# Initialize extensions
db.init_app(app)
mail = Mail(app)

@app.before_request
def create_tables():
    db.create_all()

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"error": "User already exists"}), 400

    new_user = User(email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp_code = generate_otp()
    otp_entry = OTP(user_id=user.id, otp=otp_code)
    db.session.add(otp_entry)
    db.session.commit()

    send_email(mail, email, otp_code)

    return jsonify({"message": "OTP sent to email"}), 200

@app.route("/validate-otp", methods=["POST"])
def validate_otp():
    data = request.json
    email = data.get("email")
    otp = data.get("otp")

    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp_entry = OTP.query.filter_by(user_id=user.id, otp=otp).order_by(OTP.created_at.desc()).first()

    if is_otp_valid(otp_entry):
        db.session.delete(otp_entry)
        db.session.commit()
        return jsonify({"message": "OTP validated successfully"}), 200

    return jsonify({"error": "Invalid or expired OTP"}), 400

if __name__ == "__main__":
    app.run(debug=True)
