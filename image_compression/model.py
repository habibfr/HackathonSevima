from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ImageMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=True)
    mimetype = db.Column(db.String(50), nullable=True)
    size = db.Column(db.Integer, nullable=True)
    hash = db.Column(db.String(64), nullable=True)