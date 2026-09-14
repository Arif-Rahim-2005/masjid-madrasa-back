from app import app
from models import db, User

with app.app_context():
    email = input("Admin email: ").strip()

    user = User.query.filter_by(email=email).first()

    if not user:
        print("User not found.")
        print("Create the account through /signup first.")
    else:
        user.role = "admin"
        db.session.commit()

        print(f"{user.email} is now an admin.")