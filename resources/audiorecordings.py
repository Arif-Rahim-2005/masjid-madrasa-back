from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import User, AudioRecording, AudioCategory, AudioSeries, AudioSeriesTranslation, AudioRecordingTranslation  ,db
import os
import cloudinary
import cloudinary.uploader


class CreateAudioRecording(Resource):
    @jwt_required()
    def post(self):
        current_user = User.query.get(int(get_jwt_identity()))

        if not current_user or current_user.role != "admin":
            return {"message": "Admin access required"}, 403

        category_id = request.form.get("category_id")
        series_id = request.form.get("series_id")

        name_en = request.form.get("title_en")
        description_en = request.form.get("description_en")

        name_sw = request.form.get("title_sw")
        description_sw = request.form.get("description_sw")

        name_ar = request.form.get("title_ar")
        description_ar = request.form.get("description_ar")

        speaker = request.form.get("speaker")
        recorded_at = request.form.get("recorded_at")

        audio_file = request.files.get("audio")

        if not category_id:
            return {"message": "Category ID is required"}, 400

        if not audio_file:
            return {"message": "Audio file is required"}, 400

        try:
            category_id = int(category_id)
        except ValueError:
            return {"message": "Invalid category ID"}, 400

        category = AudioCategory.query.get(category_id)

        if not category:
            return {"message": "Category not found"}, 404

        if series_id:
            try:
                series_id = int(series_id)
            except ValueError:
                return {"message": "Invalid series ID"}, 400

            series = AudioSeries.query.get(series_id)

            if not series:
                return {"message": "Series not found"}, 404

            if series.category_id != category_id:
                return {
                    "message": "Series does not belong to this category"
                }, 400

        titles = [name_en, name_sw, name_ar]

        if any(not title or not title.strip() for title in titles):
            return {
                "message": "English, Swahili and Arabic titles are required"
            }, 400

        try:
            upload_result = cloudinary.uploader.upload(
                audio_file,
                resource_type="video",
                folder="madrasa/audio"
            )

            audio_url = upload_result["secure_url"]
            public_id = upload_result["public_id"]

            recording = AudioRecording(
                category_id=category_id,
                series_id=series_id if series_id else None,
                audio_url=audio_url,
                public_id=public_id,
                speaker=speaker,
                recorded_at=recorded_at if recorded_at else None
            )

            db.session.add(recording)
            db.session.flush()

            translations = [
                AudioRecordingTranslation(
                    recording_id=recording.id,
                    title=name_en.strip(),
                    description=description_en,
                    language="en"
                ),
                AudioRecordingTranslation(
                    recording_id=recording.id,
                    title=name_sw.strip(),
                    description=description_sw,
                    language="sw"
                ),
                AudioRecordingTranslation(
                    recording_id=recording.id,
                    title=name_ar.strip(),
                    description=description_ar,
                    language="ar"
                )
            ]

            db.session.add_all(translations)
            db.session.commit()

            return {
                "id": recording.id,
                "category_id": recording.category_id,
                "series_id": recording.series_id,
                "audio_url": recording.audio_url,
                "public_id": recording.public_id,
                "speaker": recording.speaker,
                "recorded_at": recording.recorded_at.isoformat() if recording.recorded_at else None,
                "translations": [
                    {
                        "title": translation.title,
                        "description": translation.description,
                        "language": translation.language
                    }
                    for translation in translations
                ]
            }, 201

        except Exception as error:
            db.session.rollback()
            return {
                "message": "Failed to upload audio",
                "error": str(error)
            }, 500
        
class GetAudioRecordings(Resource):
    def get(self):
        language = request.args.get("language")
        category_id = request.args.get("category_id")
        series_id = request.args.get("series_id")

        if language not in ["en", "sw", "ar"]:
            return {"message": "Invalid language"}, 400

        query = AudioRecording.query

        if category_id:
            try:
                category_id = int(category_id)
            except ValueError:
                return {"message": "Invalid category ID"}, 400

            category = AudioCategory.query.get(category_id)

            if not category:
                return {"message": "Category not found"}, 404

            query = query.filter_by(category_id=category_id)

        if series_id:
            try:
                series_id = int(series_id)
            except ValueError:
                return {"message": "Invalid series ID"}, 400

            series = AudioSeries.query.get(series_id)

            if not series:
                return {"message": "Series not found"}, 404

            query = query.filter_by(series_id=series_id)

        recordings = query.all()

        if not recordings:
            return [], 200

        result = []

        for recording in recordings:
            translation = next(
                (
                    translation
                    for translation in recording.translations
                    if translation.language == language
                ),
                None
            )

            if translation:
                result.append({
                    "id": recording.id,
                    "category_id": recording.category_id,
                    "series_id": recording.series_id,
                    "title": translation.title,
                    "description": translation.description,
                    "language": translation.language,
                    "audio_url": recording.audio_url,
                    "speaker": recording.speaker,
                    "recorded_at": recording.recorded_at.isoformat() if recording.recorded_at else None,
                    "uploaded_at": recording.uploaded_at.isoformat() if recording.uploaded_at else None
                })

        return result, 200

class UpdateAudioRecording(Resource):
    @jwt_required()
    def patch(self, recording_id):
        current_user = User.query.get(int(get_jwt_identity()))

        if not current_user or current_user.role != "admin":
            return {"message": "Admin access required"}, 403

        recording = AudioRecording.query.get(recording_id)

        if not recording:
            return {"message": "Recording not found"}, 404

        category_id = request.form.get("category_id")

        series_id = request.form.get("series_id")
        series_id_provided = "series_id" in request.form

        title_en = request.form.get("title_en")
        description_en = request.form.get("description_en")

        title_sw = request.form.get("title_sw")
        description_sw = request.form.get("description_sw")

        title_ar = request.form.get("title_ar")
        description_ar = request.form.get("description_ar")

        speaker = request.form.get("speaker")
        recorded_at = request.form.get("recorded_at")

        audio_file = request.files.get("audio")

        # -------------------------
        # Validate category
        # -------------------------

        if category_id:
            try:
                category_id = int(category_id)
            except ValueError:
                return {"message": "Invalid category ID"}, 400

            category = AudioCategory.query.get(category_id)

            if not category:
                return {"message": "Category not found"}, 404

        # -------------------------
        # Validate series
        # -------------------------

        if series_id:
            try:
                series_id = int(series_id)
            except ValueError:
                return {"message": "Invalid series ID"}, 400

            series = AudioSeries.query.get(series_id)

            if not series:
                return {"message": "Series not found"}, 404

            selected_category_id = (
                category_id
                if category_id
                else recording.category_id
            )

            if series.category_id != selected_category_id:
                return {
                    "message": "Series does not belong to this category"
                }, 400

        # -------------------------
        # Save old Cloudinary file
        # -------------------------

        old_public_id = recording.public_id

        # -------------------------
        # Upload new audio if provided
        # -------------------------

        new_public_id = None

        if audio_file:
            try:
                upload_result = cloudinary.uploader.upload(
                    audio_file,
                    resource_type="video",
                    folder="madrasa/audio"
                )

                recording.audio_url = upload_result["secure_url"]
                recording.public_id = upload_result["public_id"]

                new_public_id = upload_result["public_id"]

            except Exception as error:
                return {
                    "message": "Failed to upload new audio",
                    "error": str(error)
                }, 500

        # -------------------------
        # Update category
        # -------------------------

        if category_id:
            recording.category_id = category_id

        # -------------------------
        # Update/remove series
        # -------------------------

        if series_id_provided:
            if series_id == "":
                recording.series_id = None
            else:
                recording.series_id = series_id

        # -------------------------
        # Update speaker
        # -------------------------

        if speaker is not None:
            recording.speaker = speaker

        # -------------------------
        # Update recorded date
        # -------------------------

        if recorded_at is not None:
            recording.recorded_at = recorded_at

        # -------------------------
        # Update translations
        # -------------------------

        language_data = {
            "en": {
                "title": title_en,
                "description": description_en
            },
            "sw": {
                "title": title_sw,
                "description": description_sw
            },
            "ar": {
                "title": title_ar,
                "description": description_ar
            }
        }

        for language, values in language_data.items():

            if (
                values["title"] is not None
                or values["description"] is not None
            ):

                translation = next(
                    (
                        translation
                        for translation in recording.translations
                        if translation.language == language
                    ),
                    None
                )

                if not translation:
                    if new_public_id:
                        cloudinary.uploader.destroy(
                            new_public_id,
                            resource_type="video"
                        )

                    db.session.rollback()

                    return {
                        "message": f"{language} translation not found"
                    }, 404

                if values["title"] is not None:
                    title = values["title"].strip()

                    if not title:
                        if new_public_id:
                            cloudinary.uploader.destroy(
                                new_public_id,
                                resource_type="video"
                            )

                        db.session.rollback()

                        return {
                            "message": f"{language} title cannot be empty"
                        }, 400

                    translation.title = title

                if values["description"] is not None:
                    translation.description = values["description"]

        # -------------------------
        # Commit database changes
        # -------------------------

        try:
            db.session.commit()

        except Exception as error:
            db.session.rollback()

            # Delete newly uploaded file if database update failed
            if new_public_id:
                try:
                    cloudinary.uploader.destroy(
                        new_public_id,
                        resource_type="video"
                    )
                except Exception:
                    pass

            return {
                "message": "Failed to update recording",
                "error": str(error)
            }, 500

        # -------------------------
        # Delete old audio
        # -------------------------

        if new_public_id and old_public_id:
            try:
                cloudinary.uploader.destroy(
                    old_public_id,
                    resource_type="video"
                )
            except Exception as error:
                return {
                    "message": "Recording updated, but old audio could not be deleted",
                    "error": str(error)
                }, 500

        # -------------------------
        # Return updated recording
        # -------------------------

        return {
            "id": recording.id,
            "category_id": recording.category_id,
            "series_id": recording.series_id,
            "audio_url": recording.audio_url,
            "public_id": recording.public_id,
            "speaker": recording.speaker,
            "recorded_at": (
                recording.recorded_at.isoformat()
                if recording.recorded_at
                else None
            ),
            "uploaded_at": (
                recording.uploaded_at.isoformat()
                if recording.uploaded_at
                else None
            ),
            "translations": [
                {
                    "title": translation.title,
                    "description": translation.description,
                    "language": translation.language
                }
                for translation in recording.translations
            ]
        }, 200

class DeleteAudioRecording(Resource):
    @jwt_required()
    def delete(self, recording_id):
        current_user = User.query.get(int(get_jwt_identity()))

        if not current_user or current_user.role != "admin":
            return {"message": "Admin access required"}, 403

        recording = AudioRecording.query.get(recording_id)

        if not recording:
            return {"message": "Recording not found"}, 404

        try:
            cloudinary.uploader.destroy(
                recording.public_id,
                resource_type="video"
            )

            db.session.delete(recording)
            db.session.commit()

            return {
                "message": "Audio recording deleted successfully"
            }, 200

        except Exception as error:
            db.session.rollback()

            return {
                "message": "Failed to delete audio recording",
                "error": str(error)
            }, 500