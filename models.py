from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        nullable=False
    )

    password_hash = db.Column(
        db.String(128),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="user"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

class MasjidPrograms(db.Model):
    __tablename__ = "masjid_programs"
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey("images.id"), nullable=True)
    image = db.relationship("Image", backref="masjid_programs")
    # program_name = db.Column(db.String(100), nullable=False)
    # program_schedule = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # book = db.Column(db.String(200), nullable=True)
    translations = db.relationship('MasjidProgramsTranslation', backref='program', cascade = "all, delete-orphan")

class MasjidProgramsTranslation(db.Model):
    __tablename__= "masjid_programs_translations"
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('masjid_programs.id'), nullable=False)
    program_name = db.Column(db.String(100), nullable=False)
    program_schedule = db.Column(db.String(500), nullable=False)
    language = db.Column (db.String(5), nullable=False)
    book = db.Column(db.String(200), nullable=True)
    __table_args__ = (db.UniqueConstraint('program_id', 'language', name='uq_program_language'),)

class MadrasaProgramCategories(db.Model):
    __tablename__ = "madrasa_program_categories"

    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    monthly_fee = db.Column(db.Numeric(10, 2), nullable=False)

    translations = db.relationship(
        "MadrasaProgramCategoriesTranslation",
        backref="category",
        cascade="all, delete-orphan"
    )

class MadrasaProgramCategoriesTranslation(db.Model):
    __tablename__= "madrasa_program_categories_translations"

    id = db.Column(db.Integer, primary_key = True)
    category_id = db.Column(db.Integer, db.ForeignKey("madrasa_program_categories.id"), nullable=False )
    name = db.Column (db.String(100), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    __table_args__ = (
        db.UniqueConstraint(
            "category_id",
            "language",
            name="uq_category_language"
        ),
    )

class MadrasaPrograms(db.Model):
    __tablename__ = "madrasa_programs"

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey("images.id"), nullable=True)
    image = db.relationship("Image", backref="madrasa_programs")
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("madrasa_program_categories.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    translations = db.relationship(
    "MadrasaProgramTranslations",
    backref="program",
    cascade="all, delete-orphan"
    )

class MadrasaProgramTranslations(db.Model):
    __tablename__ = "madrasa_programs_translations"

    id = db.Column(db.Integer, primary_key =True, nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey("madrasa_programs.id"), nullable=False)
    program_name = db.Column(db.String(50), nullable=False)
    subjects=db.Column(db.String(500), nullable=False)
    program_schedule = db.Column(db.String(500), nullable=False)

    language=db.Column(db.String(5), nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "program_id",
            "language",
            name="uq_madrasa_program_language"
        ),
    )


class Document(db.Model):
    __tablename__="documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    filename = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(500), nullable=False)
    document_type = db.Column(db.String(50), nullable=True)
    language = db.Column(db.String(10), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,onupdate=datetime.utcnow, nullable=False)

class Image(db.Model):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

class Announcement(db.Model):
    __tablename__ = "announcements"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    image_id = db.Column(
    db.Integer,
    db.ForeignKey("images.id"),
    nullable=True
    )
    image = db.relationship("Image", backref="announcements")

    translations = db.relationship(
        "AnnouncementTranslation",
        backref="announcement",
        cascade="all, delete-orphan"
    )


class AnnouncementTranslation(db.Model):
    __tablename__ = "announcement_translations"

    id = db.Column(db.Integer, primary_key=True)

    announcement_id = db.Column(
        db.Integer,
        db.ForeignKey("announcements.id"),
        nullable=False
    )

    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(5), nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "announcement_id",
            "language",
            name="uq_announcement_language"
        ),
    )

class AudioCategory(db.Model):
    __tablename__ = "audio_categories"

    id = db.Column(db.Integer, primary_key=True)

    translations = db.relationship(
        "AudioCategoryTranslation",
        backref="category",
        cascade="all, delete-orphan"
    )

    series = db.relationship(
        "AudioSeries",
        backref="category",
        cascade="all, delete-orphan"
    )

class AudioCategoryTranslation(db.Model):
    __tablename__ = "audio_category_translations"

    id = db.Column(db.Integer, primary_key=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("audio_categories.id"),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    language = db.Column(
        db.String(10),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "category_id",
            "language",
            name="uq_audio_category_language"
        ),
    )


class AudioSeries(db.Model):
    __tablename__ = "audio_series"

    id = db.Column(db.Integer, primary_key=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("audio_categories.id"),
        nullable=False
    )

    translations = db.relationship(
        "AudioSeriesTranslation",
        backref="series",
        cascade="all, delete-orphan"
    )

    recordings = db.relationship(
        "AudioRecording",
        backref="series",
        cascade="all, delete-orphan"
    )


class AudioSeriesTranslation(db.Model):
    __tablename__ = "audio_series_translations"

    id = db.Column(db.Integer, primary_key=True)

    series_id = db.Column(
        db.Integer,
        db.ForeignKey("audio_series.id"),
        nullable=False
    )

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(10), nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "series_id",
            "language",
            name="uq_audio_series_language"
        ),
    )


class AudioRecording(db.Model):
    __tablename__ = "audio_recordings"

    id = db.Column(db.Integer, primary_key=True)
    
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("audio_categories.id"),
        nullable=False
    )

    category = db.relationship(
        "AudioCategory",
        backref="recordings"
    )
    series_id = db.Column(
        db.Integer,
        db.ForeignKey("audio_series.id"),
        nullable=True
    )

    audio_url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(500), nullable=False)

    speaker = db.Column(db.String(200), nullable=True)

    recorded_at = db.Column(db.DateTime, nullable=True)

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    translations = db.relationship(
        "AudioRecordingTranslation",
        backref="recording",
        cascade="all, delete-orphan"
    )


class AudioRecordingTranslation(db.Model):
    __tablename__ = "audio_recording_translations"

    id = db.Column(db.Integer, primary_key=True)

    recording_id = db.Column(
        db.Integer,
        db.ForeignKey("audio_recordings.id"),
        nullable=False
    )

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(10), nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "recording_id",
            "language",
            name="uq_audio_recording_language"
        ),
    )