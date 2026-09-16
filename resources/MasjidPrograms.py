from gettext import translation

from flask import request
from flask_restful import Resource
from models import MasjidPrograms, MasjidProgramsTranslation, db, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask_restful import reqparse


class AddProgram(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("program_name_en", required=True)
    parser.add_argument("program_schedule_en", required=True)
    parser.add_argument("book_en", required=True)

    parser.add_argument("program_name_sw", required=True)
    parser.add_argument("program_schedule_sw", required=True)
    parser.add_argument("book_sw", required=True)

    parser.add_argument("program_name_ar", required=True)
    parser.add_argument("program_schedule_ar", required=True)
    parser.add_argument("book_ar", required=True)

    
    @jwt_required()
    def post(self):
        # Get the currently logged-in user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user:
            return {"message": "Invalid user"}, 404

        # Only admins can add programs
        if current_user.role != "admin":
            return {"message": "Access denied"}, 403

        data = self.parser.parse_args()

        print("DATA:", data)

        if not data:
            return {"message": "Request body is required"}, 400

        try:
            # Create the main program
            new_program = MasjidPrograms(
                created_at=datetime.utcnow()
                )

            db.session.add(new_program)
            db.session.flush() # Flush to get the new_program.id

            # Create translations for the program
            # for translation in translations:
            #     new_translation = MasjidProgramsTranslation(
            #         program_id=new_program.id,
            #         program_name=translation.get("program_name"),
            #         program_schedule=translation.get("program_schedule"),
            #         language=translation.get("language"),
            #         book=translation.get("book")
            #     )

            #     db.session.add(new_translation)
            english = MasjidProgramsTranslation(
                program_id=new_program.id,
                program_name=data["program_name_en"],
                program_schedule=data["program_schedule_en"],
                language="en",
                book=data["book_en"]
            )

            swahili = MasjidProgramsTranslation(
                program_id=new_program.id,
                program_name=data["program_name_sw"],
                program_schedule=data["program_schedule_sw"],
                language="sw",
                book=data["book_sw"]
            )

            arabic = MasjidProgramsTranslation(
                program_id=new_program.id,
                program_name=data["program_name_ar"],
                program_schedule=data["program_schedule_ar"],
                language="ar",
                book=data["book_ar"]
            )

            db.session.add_all([english, swahili, arabic])
            db.session.commit()

            return {
                "message": "Program added successfully",
                "program_id": new_program.id
            }, 201

        except IntegrityError as e:
            db.session.rollback()

            return {
                "message": "Program already exists",
                "error": str(e)
            }, 400


# class GetPrograms(Resource):
    def get(self):
        language = request.args.get("language", "en")

        if language not in ["en", "sw", "ar"]:
            return {"message": "Invalid language"}, 400

        programs = MasjidPrograms.query.all()

        result = []

        for program in programs:
            translation = MasjidProgramsTranslation.query.filter_by(
                program_id=program.id,
                language=language
            ).first()

            if translation:
                program_data = {
                    "id": program.id,
                    "created_at": program.created_at.isoformat(),
                    "translation": {
                        "program_name": translation.program_name,
                        "program_schedule": translation.program_schedule,
                        "language": translation.language,
                        "book": translation.book
                    }
                }

                result.append(program_data)

        return result, 200

class UpdateProgram(Resource):

    parser = reqparse.RequestParser()

    parser.add_argument("program_name_en")
    parser.add_argument("program_schedule_en")
    parser.add_argument("book_en")

    parser.add_argument("program_name_sw")
    parser.add_argument("program_schedule_sw")
    parser.add_argument("book_sw")

    parser.add_argument("program_name_ar")
    parser.add_argument("program_schedule_ar")
    parser.add_argument("book_ar")

    @jwt_required()
    def patch(self, program_id):
        # Get the currently logged-in user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user:
            return {"message": "Invalid user"}, 404

        # Only admins can update programs
        if current_user.role != "admin":
            return {"message": "Access denied"}, 403

        data = self.parser.parse_args()

        program = MasjidPrograms.query.get(program_id)

        if not program:
            return {"message": "Program not found"}, 404

        try:
            # Update translations for the program
            translations = {
                "en": {
                    "program_name": data["program_name_en"],
                    "program_schedule": data["program_schedule_en"],
                    "book": data["book_en"]
                },
                "sw": {
                    "program_name": data["program_name_sw"],
                    "program_schedule": data["program_schedule_sw"],
                    "book": data["book_sw"]
                },
                "ar": {
                    "program_name": data["program_name_ar"],
                    "program_schedule": data["program_schedule_ar"],
                    "book": data["book_ar"]
                }
            }

            for lang, translation_data in translations.items():
                translation = MasjidProgramsTranslation.query.filter_by(
                    program_id=program.id,
                    language=lang
                ).first()

                if translation:
                    if translation_data["program_name"] is not None:
                        translation.program_name = translation_data["program_name"]

                    if translation_data["program_schedule"] is not None:
                        translation.program_schedule = translation_data["program_schedule"]

                    if translation_data["book"] is not None:
                        translation.book = translation_data["book"]
                else:
                    new_translation = MasjidProgramsTranslation(
                        program_id=program.id,
                        program_name=translation_data["program_name"],
                        program_schedule=translation_data["program_schedule"],
                        language=lang,
                        book=translation_data["book"]
                    )
                    db.session.add(new_translation)

            db.session.commit()

            return {"message": "Program updated successfully", "program_id": program.id}, 200

        except IntegrityError as e:
            db.session.rollback()
            return {
                "message": "Error updating program",
                "error": str(e)
            }, 400

class DeleteProgram(Resource):

    @jwt_required()
    def delete(self, program_id):
        # Get the currently logged-in user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user:
            return {"message": "Invalid user"}, 404

        # Only admins can delete programs
        if current_user.role != "admin":
            return {"message": "Access denied"}, 403

        # Find the program
        program = MasjidPrograms.query.get(program_id)

        if not program:
            return {"message": "Program not found"}, 404

        try:
            db.session.delete(program)
            db.session.commit()

            return {
                "message": "Program deleted successfully",
                "program_id": program_id
            }, 200

        except IntegrityError as e:
            db.session.rollback()

            return {
                "message": "Error deleting program",
                "error": str(e)
            }, 400
        