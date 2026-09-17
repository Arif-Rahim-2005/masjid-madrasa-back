import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api
# from flask_sqlalchemy import SQLAlchemy
from models import db
from resources.users import SignupResource, LogInResource, UserResource, AdminResource
from resources.MasjidPrograms import AddProgram, DeleteProgram, UpdateProgram
from resources.MadrasaProgramCategories import AddCategory, GetCategories, UpdateCategory, DeleteCategory



load_dotenv()

app = Flask(__name__)

# -------------------------
# Configuration
# -------------------------

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# -------------------------
# Extensions
# -------------------------

# db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
api = Api(app)

db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)

CORS(app)

# -------------------------
# Routes
# -------------------------

@app.route("/")
def home():
    return jsonify({
        "message": "Madrasatul Kheirat API is running"
    })


api.add_resource(SignupResource, "/signup")
api.add_resource(LogInResource, "/login")
api.add_resource(UserResource, "/users", "/users/<int:user_id>")
api.add_resource(AdminResource, "/me")
api.add_resource(AddProgram, "/masjid-programs")
api.add_resource(UpdateProgram, "/masjid-programs/<int:program_id>")
api.add_resource(DeleteProgram, "/masjid-programs/<int:program_id>")
api.add_resource(AddCategory, "/madrasa-program-categories")
api.add_resource(GetCategories, "/madrasa-program-categories")
api.add_resource(UpdateCategory, "/madrasa-program-categories/<int:category_id>")
api.add_resource(DeleteCategory, "/madrasa-program-categories/<int:category_id>")

if __name__ == "__main__":
    app.run(debug=True)