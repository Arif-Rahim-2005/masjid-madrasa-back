from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from models import User, MadrasaProgramCategories, MadrasaProgramCategoriesTranslation, db

class AddCategory(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("name_en",required=True)
    parser.add_argument("name_sw",required=True)
    parser.add_argument("name_ar",required=True)

    @jwt_required()
    def post(self):

        # get the current logged in user
        current_user_id= get_jwt_identity()
        current_user=User.query.get(current_user_id)

# checking whether the JWT corresponds to a valid user
        if not current_user:
            return {"message":"invalid user"},  404

# only admins can add programs
        if current_user.role != "admin":
            return {"message":"access denied"}

        data = self.parser.parse_args()


        try:
            new_category = MadrasaProgramCategories()

            db.session.add(new_category)
            db.session.flush()


            english = MadrasaProgramCategoriesTranslation(
                category_id= new_category.id,
                name = data["name_en"],
                language = "en"

            )
            swahili = MadrasaProgramCategoriesTranslation(
                category_id= new_category.id,
                name = data["name_sw"],
                language = "sw"

            )
            arabic = MadrasaProgramCategoriesTranslation(
                category_id= new_category.id,
                name = data["name_ar"],
                language = "ar"

            )

            db.session.add_all(
                [english, swahili, arabic]
            )
            db.session.commit()


            return {
                "message": "Category added successfully",
                "category_id": new_category.id
            }, 201

        except IntegrityError as e:
            db.session.rollback()

            return {
                    "message":"error adding program", 
                    "error":str(e)
                    }, 400

class GetCategories(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("language", required=True, location = "args")

    def get(self):
        categories = MadrasaProgramCategories.query.all()

        if not categories:
            return {"message": "No categories found"}, 404

        data = self.parser.parse_args()
        language = data["language"]

        if language not in ["en", "sw", "ar"]:
            return {"message": "Invalid language"}, 400

        result = []

        for category in categories:
            translation = next(
                (
                    translation
                    for translation in category.translations
                    if translation.language == language
                ),
                None
            )

            if translation:
                result.append({
                    "category_id": category.id,
                    "category_name": translation.name,
                    "category_language": translation.language
                })

        if not result:
            return {"message": "No categories found for this language"}, 404

        return result, 200

    
class UpdateCategory(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("name_en", required=False)
    parser.add_argument("name_sw", required=False)
    parser.add_argument("name_ar", required=False)

    @jwt_required()
    def patch(self, category_id):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user:
            return {"message": "Invalid user"}, 404

        if current_user.role != "admin":
            return {"message": "Access denied"}, 403

        category = MadrasaProgramCategories.query.get(category_id)

        if not category:
            return {"message": "Category not found"}, 404

        data = self.parser.parse_args()

        translations = {
            "en": data["name_en"],
            "sw": data["name_sw"],
            "ar": data["name_ar"]
        }

        for language, name in translations.items():
            if name is not None:
                translation = next(
                    (
                        translation
                        for translation in category.translations
                        if translation.language == language
                    ),
                    None
                )

                if translation:
                    translation.name = name

        db.session.commit()

        return {
            "message": "Category updated successfully"
        }, 200



class DeleteCategory(Resource):

    @jwt_required()
    def delete(self, category_id):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user:
            return {"message": "Invalid user"}, 404

        if current_user.role != "admin":
            return {"message": "Access denied"}, 403

        category = MadrasaProgramCategories.query.get(category_id)

        if not category:
            return {"message": "Category not found"}, 404

        db.session.delete(category)
        db.session.commit()

        return {
            "message": "Category deleted successfully"
        }, 200