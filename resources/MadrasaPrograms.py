from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from models import (
    User,
    MadrasaPrograms,
    MadrasaProgramTranslations,
    MadrasaProgramCategories,
    db
)

class AddMadrasaProgram(Resource):
    @jwt_required()
    def post(self):
        parser=reqparse.RequestParser()


        parser.add_argument("category_id", required=True, type=int)

        parser.add_argument("name_en", required=True)
        parser.add_argument("schedule_en", required=True)
        parser.add_argument("subjects_en", required=True)

        parser.add_argument("name_sw", required=True)
        parser.add_argument("schedule_sw", required=True)
        parser.add_argument("subjects_sw", required=True)

        parser.add_argument("name_ar", required=True)
        parser.add_argument("schedule_ar", required=True)
        parser.add_argument("subjects_ar", required=True)

        data = parser.parse_args()

        current_user_id = get_jwt_identity()
        current_user=User.query.get(current_user_id)

        if not current_user:
            return{
                "message":"invalid user"
            }, 404

        if current_user.role != "admin":
            return{
                "message":"access denied"
            }, 403

        new_program = MadrasaPrograms(
            category_id = data["category_id"]
        )

        db.session.add(new_program)
        db.session.flush()

        english = MadrasaProgramTranslations(
            program_id=new_program.id,
            program_name=data["name_en"],
            program_schedule=data["schedule_en"],
            subjects=data["subjects_en"],
            language="en"
        )

        db.session.add(english)

        sawhili = MadrasaProgramTranslations(
            program_id=new_program.id,
            program_name=data["name_sw"],
            program_schedule=data["schedule_sw"],
            subjects=data["subjects_sw"],
            language="sw"
        )

        db.session.add(sawhili)


        arabic = MadrasaProgramTranslations(
            program_id=new_program.id,
            program_name=data["name_ar"],
            program_schedule=data["schedule_ar"],
            subjects=data["subjects_ar"],
            language="ar"
        )

        db.session.add(arabic)

        db.session.commit()

        return{
            "message":"program added successfully",
            "program_id":new_program.id
        }, 201

class GetMadrasaPrograms(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument(
        "language",
        required=True,
        location="args"
    )

    def get(self):
        data = self.parser.parse_args()
        language = data["language"]

        if language not in ["en", "sw", "ar"]:
            return {
                "message": "Invalid language"
            }, 400

        programs = MadrasaPrograms.query.all()

        if not programs:
            return {
                "message": "No programs found"
            }, 404

        result = []

        for program in programs:
            translation = next(
                (
                    translation
                    for translation in program.translations
                    if translation.language == language
                ),
                None
            )

            if translation:
                result.append({
                    "program_id": program.id,
                    "category_id": program.category_id,
                    "program_name": translation.program_name,
                    "subjects": translation.subjects,
                    "schedule": translation.program_schedule,
                    "language": translation.language
                })

                if not result:
                    return {
                        "message": "No programs found for this language"
                    }, 404

                return result, 200


class UpdateMadrasaProgram(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("name_en", required=False)
    parser.add_argument("subjects_en", required=False)
    parser.add_argument("schedule_en", required=False)

    parser.add_argument("name_sw", required=False)
    parser.add_argument("subjects_sw", required=False)
    parser.add_argument("schedule_sw", required=False)

    parser.add_argument("name_ar", required=False)
    parser.add_argument("subjects_ar", required=False)
    parser.add_argument("schedule_ar", required=False)

    @jwt_required()
    def patch(self, program_id):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user:
            return {
                "message": "Invalid user"
            }, 404

        if current_user.role != "admin":
            return {
                "message": "Access denied"
            }, 403

        program = MadrasaPrograms.query.get(program_id)

        if not program:
            return {
                "message": "Program not found"
            }, 404

        data = self.parser.parse_args()

        translations = {
            "en": {
                "program_name": data["name_en"],
                "subjects": data["subjects_en"],
                "program_schedule": data["schedule_en"]
            },
            "sw": {
                "program_name": data["name_sw"],
                "subjects": data["subjects_sw"],
                "program_schedule": data["schedule_sw"]
            },
            "ar": {
                "program_name": data["name_ar"],
                "subjects": data["subjects_ar"],
                "program_schedule": data["schedule_ar"]
            }
        }

        for language, fields in translations.items():
            translation = next(
                (
                    translation
                    for translation in program.translations
                    if translation.language == language
                ),
                None
            )

            if translation:
                if fields["program_name"] is not None:
                    translation.program_name = fields["program_name"]

                if fields["subjects"] is not None:
                    translation.subjects = fields["subjects"]

                if fields["program_schedule"] is not None:
                    translation.program_schedule = fields["program_schedule"]

        db.session.commit()

        return {
            "message": "Madrasa program updated successfully"
        }, 200


class DeleteMadrasaProgram(Resource):

    @jwt_required()
    def delete(self, program_id) :
        
        current_user_id = get_jwt_identity()
        current_user=User.query.get(current_user_id)
# check whether the current user is infact a user
        if not current_user:
            return{
                "message":"Invalid User"
            }, 404

# check whether the current user is an admin
        if current_user.role != "admin":
            return{"message":"Access denied"}, 403

# get the program to be deleted

        program = MadrasaPrograms.query.get(program_id)

        if not program:
            return{
                "message":"Program not found"
            }, 404

# delete the program

        try:
            db.session.delete(program)
            db.session.commit()

            return{
                "message":"Program deleted successfully",
                "program_id": program_id
            }, 200

        except IntegrityError as e:
            db.session.rollback()

            return{"message":"Error deleting program",
                   "error":str(e)
                   } , 400