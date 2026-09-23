from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import User, Document, db
import os
import cloudinary
import cloudinary.uploader

class AddDocument(Resource):

    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user:
            return{
                "message":"Invalid User"
            }, 404

        if current_user.role !="admin":
            return{
                "message":"Access denied"
            }, 403

        file = request.files.get("document")

        if not file:
            return{
                "message":"No file uploaded. Please uplaod a file"
            } , 400

        file_name = file.filename    

        filename, file_extension = os.path.splitext(file_name)

        if file_extension.lower() != ".pdf":
            return{
                "message":"Only pdf files are allowed"
            }, 400

       
        title = request.form.get("title")

        if not title:
            return{
                "message":"Title is required"
            }, 400
                

        document_type = request.form.get("document_type")

        if not document_type:
            return{
                "message":"document_type is required"
            }, 400

        uploaded_doc = cloudinary.uploader.upload(file, resource_type="raw")

        
        # language = request.form.get("language")

        # if not language:
        #     return{
        #         "message":"language is required"
        #     }, 400

        new_document = Document(
            title = title,
            filename=file.filename,
            url= uploaded_doc["secure_url"],
            public_id = uploaded_doc["public_id"],
            document_type = document_type,

        )

        db.session.add(new_document)
        db.session.commit()

        return{
            "message":"Document uploaded successfully",
            "document_id": new_document.id,
            "title" : title,
        }, 200

class GetDocuments(Resource):

    def get(self):
        documents = Document.query.all()

        if not documents:
            return {
                "message": "No documents found"
            }, 404        

        result = []
        for document in documents:
            result.append({
            "id": document.id,
            "title":document.title,
            "filename":document.filename,
            "url":document.url,
            "document_type":document.document_type,
            "language":document.language,
            "uploaded_at": document.uploaded_at.isoformat()
     }) 

            return result, 200


class DeleteDocuments(Resource):

    @jwt_required()
    def delete(self, document_id):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user:
            return{
                "message":"Invalid user"
            }, 404

        if current_user.role !="admin":
            return{
                "message":"Access denied"
            }, 403

        document = Document.query.get(document_id)

        if not document:
            return{
                "message":"Document not found"
            }, 404

        cloudinary.uploader.destroy(
            document.public_id,
            resource_type = "raw"
        )

        db.session.delete(document)
        db.session.commit()

        return{
            "message":"Document deleted successfully"
        }, 200