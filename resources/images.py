from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import User, Image, db
import cloudinary
import cloudinary.uploader
import os

class AddImage(Resource):

    @jwt_required()
    def post(self):
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

        file = request.files.get("image")

        if not file:
            return {
                "message": "No image uploaded"
            }, 400

        allowed_extensions = [".jpg", ".jpeg", ".png", ".webp"]

        filename = file.filename
        extension = os.path.splitext(filename)[1].lower()

        if extension not in allowed_extensions:
            return {
                "message": "Only JPG, JPEG, PNG and WEBP images are allowed"
            }, 400
        title = request.form.get("title")

        if not title:
            return {
                "message": "Title is required"
            }, 400

        uploaded_image = cloudinary.uploader.upload(
            file,
            resource_type="image"
        )

        new_image = Image(
            title=title,
            filename=file.filename,
            url=uploaded_image["secure_url"],
            public_id=uploaded_image["public_id"],
        )

        db.session.add(new_image)
        db.session.commit()

        return {
            "message": "Image uploaded successfully",
            "image_id": new_image.id,
            "title": title
        }, 201

class GetImages(Resource):

    def get(self):
        images = Image.query.all()

        if not images:
            return {
                "message": "No images found"
            }, 404

        result = []

        for image in images:
            result.append({
                "id": image.id,
                "title": image.title,
                "filename": image.filename,
                "url": image.url,
                "uploaded_at": image.uploaded_at.isoformat()
            })

        return result, 200


class DeleteImage(Resource):
    @jwt_required()
    def delete (self, image_id):
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

        image = Image.query.get(image_id)

        if not image:
            return{
                "message":"Image not found"
            }, 404


        cloudinary.uploader.destroy(image.public_id, resource_type = "image")

        db.session.delete(image)
        db.session.commit()

        return{
            "message":"Image deleted successfully"
        }, 200