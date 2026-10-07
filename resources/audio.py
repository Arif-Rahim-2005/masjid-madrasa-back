from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import User, AudioRecording, AudioCategory, AudioSeries, AudioSeriesTranslation, AudioRecordingTranslation  ,db
import os
import cloudinary
import cloudinary.uploader

class GetAudioCategories(Resource):
    def get(self):
        categories = AudioCategory.query.all()

        if not categories:
            return [], 200

        return [
            {
                "id": category.id,
                "name": category.name
            }
            for category in categories
        ], 200

class CreateAudioCategory(Resource):
    @jwt_required()
    def post(self):
        current_user = User.query.get(int(get_jwt_identity()))

        if not current_user or current_user.role != "admin":
            return {"message": "Admin access required"}, 403

        parser = reqparse.RequestParser()
        parser.add_argument(
            "name",
            type=str,
            required=True,
            help="Name is required"
        )

        data = parser.parse_args()
        name = data["name"].strip()

        if not name:
            return {"message": "Name cannot be empty"}, 400

        existing_category = AudioCategory.query.filter_by(name=name).first()

        if existing_category:
            return {"message": "Category already exists"}, 409

        category = AudioCategory(name=name)

        db.session.add(category)
        db.session.commit()

        return {
            "id": category.id,
            "name": category.name
        }, 201
class UpdateAudioCategory(Resource):
    @jwt_required()
    def patch(self, category_id):
        current_user = User.query.get(int(get_jwt_identity()))

        if not current_user or current_user.role != "admin":
            return {"message": "Admin access required"}, 403

        category = AudioCategory.query.get(category_id)

        if not category:
            return {"message": "Category not found"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, required=True)

        data = parser.parse_args()
        name = data["name"].strip()

        if not name:
            return {"message": "Name cannot be empty"}, 400

        existing_category = AudioCategory.query.filter(
            AudioCategory.name == name,
            AudioCategory.id != category_id
        ).first()

        if existing_category:
            return {"message": "Category already exists"}, 409

        category.name = name
        db.session.commit()

        return {
            "id": category.id,
            "name": category.name
        }, 200

class DeleteAudioCategory(Resource):
    @jwt_required()
    def delete(self, category_id):
        current_user = User.query.get(int(get_jwt_identity()))

        if not current_user or current_user.role != "admin":
            return {"message": "Admin access required"}, 403

        category = AudioCategory.query.get(category_id)

        if not category:
            return {"message": "Category not found"}, 404

        if category.series:
            return {
                "message": "Cannot delete category because it has series attached. Delete the series first before deleting the category."
            }, 409

        if category.recordings:
            return {
                "message": "Cannot delete category because it has recordings attached. Delete or move the recordings first before deleting the category."
            }, 409

        db.session.delete(category)
        db.session.commit()

        return {
            "message": "Category deleted successfully"
        }, 200

class CreateAudioSeries(Resource):
    @jwt_required()
    def post(self):
        current_user = User.query.get(int(get_jwt_identity()))

        if not current_user or current_user.role != "admin":
            return {"message": "Admin access required"}, 403

        parser = reqparse.RequestParser()
        parser.add_argument(
            "category_id",
            type=int,
            required=True,
            help="Category ID is required"
        )
        parser.add_argument("name_en", type=str, required=True)
        parser.add_argument("description_en", type=str)
        parser.add_argument("name_sw", type=str, required=True)
        parser.add_argument("description_sw", type=str)
        parser.add_argument("name_ar", type=str, required=True)
        parser.add_argument("description_ar", type=str)

        data = parser.parse_args()

        category = AudioCategory.query.get(data["category_id"])

        if not category:
            return {"message": "Category not found"}, 404

        series = AudioSeries(category_id=category.id)

        db.session.add(series)
        db.session.flush()

        translations = [
            AudioSeriesTranslation(
                series_id=series.id,
                name=data["name_en"].strip(),
                description=data["description_en"],
                language="en"
            ),
            AudioSeriesTranslation(
                series_id=series.id,
                name=data["name_sw"].strip(),
                description=data["description_sw"],
                language="sw"
            ),
            AudioSeriesTranslation(
                series_id=series.id,
                name=data["name_ar"].strip(),
                description=data["description_ar"],
                language="ar"
            )
        ]

        db.session.add_all(translations)
        db.session.commit()

        return {
            "id": series.id,
            "category_id": series.category_id,
            "translations": [
                {
                    "name": translation.name,
                    "description": translation.description,
                    "language": translation.language
                }
                for translation in translations
            ]
        }, 201

class GetAudioSeries(Resource):
    def get(self, category_id):
        language = request.args.get("language")

        if language not in ["en", "sw", "ar"]:
            return {"message": "Invalid language"}, 400

        category = AudioCategory.query.get(category_id)

        if not category:
            return {"message": "Category not found"}, 404

        series_list = AudioSeries.query.filter_by(
            category_id=category_id
        ).all()

        if not series_list:
            return [], 200

        result = []

        for series in series_list:
            translation = next(
                (
                    translation
                    for translation in series.translations
                    if translation.language == language
                ),
                None
            )

            if translation:
                result.append({
                    "id": series.id,
                    "category_id": series.category_id,
                    "name": translation.name,
                    "description": translation.description,
                    "language": translation.language
                })

        return result, 200

class UpdateAudioSeries(Resource):
    @jwt_required()
    def patch(self, series_id):
        current_user = User.query.get(int(get_jwt_identity()))

        if not current_user or current_user.role != "admin":
            return {"message": "Admin access required"}, 403

        series = AudioSeries.query.get(series_id)

        if not series:
            return {"message": "Series not found"}, 404

        parser = reqparse.RequestParser()

        parser.add_argument("category_id", type=int)
        parser.add_argument("name_en", type=str)
        parser.add_argument("description_en", type=str)

        parser.add_argument("name_sw", type=str)
        parser.add_argument("description_sw", type=str)

        parser.add_argument("name_ar", type=str)
        parser.add_argument("description_ar", type=str)

        data = parser.parse_args()

        # Update category if provided
        if data["category_id"] is not None:
            category = AudioCategory.query.get(data["category_id"])

            if not category:
                return {"message": "Category not found"}, 404

            series.category_id = category.id

        # Update translations
        language_data = {
            "en": {
                "name": data["name_en"],
                "description": data["description_en"]
            },
            "sw": {
                "name": data["name_sw"],
                "description": data["description_sw"]
            },
            "ar": {
                "name": data["name_ar"],
                "description": data["description_ar"]
            }
        }

        for language, values in language_data.items():
            if values["name"] is not None or values["description"] is not None:

                translation = next(
                    (
                        translation
                        for translation in series.translations
                        if translation.language == language
                    ),
                    None
                )

                if not translation:
                    return {
                        "message": f"{language} translation not found"
                    }, 404

                if values["name"] is not None:
                    name = values["name"].strip()

                    if not name:
                        return {
                            "message": "Series name cannot be empty"
                        }, 400

                    translation.name = name

                if values["description"] is not None:
                    translation.description = values["description"]

        db.session.commit()

        return {
            "message": "Series updated successfully",
            "id": series.id,
            "category_id": series.category_id,
            "translations": [
                {
                    "name": translation.name,
                    "description": translation.description,
                    "language": translation.language
                }
                for translation in series.translations
            ]
        }, 200

class DeleteAudioSeries(Resource):
    @jwt_required()
    def delete(self, series_id):
        current_user = User.query.get(int(get_jwt_identity()))

        if not current_user or current_user.role != "admin":
            return {"message": "Admin access required"}, 403

        series = AudioSeries.query.get(series_id)

        if not series:
            return {"message": "Series not found"}, 404

        if series.recordings:
            return {
                "message": "Cannot delete series because it has recordings attached. Delete or move the recordings first before deleting the series."
            }, 409

        db.session.delete(series)
        db.session.commit()

        return {
            "message": "Series deleted successfully"
        }, 200