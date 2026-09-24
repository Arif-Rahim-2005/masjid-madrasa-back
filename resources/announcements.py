from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Announcement, AnnouncementTranslation
from datetime import datetime
from sqlalchemy.exc import IntegrityError

class AddAnnouncement(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("title_en", required=True)
    parser.add_argument("content_en", required=True)

    parser.add_argument("title_sw", required=True)
    parser.add_argument("content_sw", required=True)

    parser.add_argument("title_ar", required=True)
    parser.add_argument("content_ar", required=True)


    @jwt_required()
    def post (self):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user:
            return{
                "message":"Invalid User"
            } , 404

        if current_user.role !="admin":
            return{
                "message":"Access denied"
            }, 403

        data = self.parser.parse_args()

        print("DATA:", data)


        try:
            # Create the new announcement
            new_announcement = Announcement(
                created_at=datetime.utcnow()
                )

            db.session.add(new_announcement)
            db.session.flush() # Flush to get the new_announcement id


            english = AnnouncementTranslation(
                announcement_id=new_announcement.id,
                title=data["title_en"],
                content=data["content_en"],
                language="en"            )

            swahili = AnnouncementTranslation(
                announcement_id=new_announcement.id,
                title=data["title_sw"],
                content=data["content_sw"],
                language="sw"
            )

            arabic = AnnouncementTranslation(
                announcement_id=new_announcement.id,
                title=data["title_ar"],
                content=data["content_ar"],
                language="ar"           
            )

            db.session.add_all([english, swahili, arabic])
            db.session.commit()

            return {
                "message": "Announcement added successfully",
                "announcement_id": new_announcement.id
            }, 201

        except IntegrityError as e:
            db.session.rollback()

            return {
                "message": "Announcement already exists",
                "error": str(e)
            }, 400


class GetAnnouncements(Resource):

    parser = reqparse.RequestParser()

    parser.add_argument(
        "language",
        required=True,
        location="args"
    )

    def get (self):
        data = self.parser.parse_args()
        language = data["language"]

        if language not in ["en", "sw", "ar"]:
            return{
                "message":"Invalid Language"
            }, 400

        announcements = Announcement.query.all()

        if not announcements:
            return{
                "message":"No announcements found"
            }, 404

        result = []

        for announcement in announcements:
            translation = next(
                (
                    translation
                    for translation in announcement.translations
                    if translation.language == language
                ),
                None
            )

            if translation:
                result.append({
                    "announcement_id": announcement.id,
                    "title": translation.title,
                    "content": translation.content,
                    "image_id": announcement.image_id,
                    "language": translation.language
                })

        return result, 200

class DeleteAnnouncement(Resource):
    @jwt_required()
    def delete (self, announcement_id):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user:
            return{
                "message":"Invalid User"
            }, 404

        if current_user.role != "admin":
            return{
                "message":"Access denied"
            }, 403

        announcement  = Announcement.query.get(announcement_id)

        if not announcement:
            return{
                "message":"No such announcement found"
            }, 404

        try:
            db.session.delete(announcement)
            db.session.commit()

            return{
                "message": "Announcement deleted successfully",
                "announcement_id": announcement_id
            }, 200

        except IntegrityError as e:
            db.session.rollback()

            return{
                "message":"Error deleting announcement",
                "Error":str(e)
            }, 400