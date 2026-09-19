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