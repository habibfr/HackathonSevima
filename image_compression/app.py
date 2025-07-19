# app.py
from PIL import Image
from flask import Flask, request, jsonify, render_template, send_from_directory
from model import db, ImageMeta
from kmeans.kmeans import compress_image, gen_thumbnail, hash_filename_thumbnail
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import jwt as pyjwt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sevima:sevima@localhost:5433/image_compression'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SECRET_KEY'] = 'sayatidaktahusecretkeysaya'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files['file']
    filename = secure_filename(file.filename)
    img = Image.open(file)
    
    # Pastikan folder upload ada
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

  # Simpan file asli ke disk sementara untuk cek ukuran
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}_original")
    file.seek(0)
    file.save(original_path) if hasattr(file, "save") else open(original_path, "wb").write(file.read())
    original_size = os.path.getsize(original_path)

    # Compress
    compressed = compress_image(img, n_colors=16)
    thumb = gen_thumbnail(img)

    hashed = hash_filename_thumbnail(filename)
    img_path = f"{hashed}_compressed.png"
    thumb_path = f"{hashed}_thumb.png"

    compressed.save(os.path.join(app.config['UPLOAD_FOLDER'], img_path))
    thumb.save(os.path.join(app.config['UPLOAD_FOLDER'], thumb_path))

    compressed_size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], img_path))

    # Save to DB
    meta = ImageMeta(
        filename=filename,
        mimetype=file.mimetype,
        size=compressed_size,
        hash=hashed
    )
    db.session.add(meta)
    db.session.commit()

    # Create signed URL
    token = pyjwt.encode({
        'hash': hashed,
        'exp': datetime.utcnow() + timedelta(minutes=10)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    os.remove(original_path)

    return jsonify({
        "compressed_url": f"/image/{token}",
        "thumb_url": f"/static/uploads/{thumb_path}",
        "original_size": original_size,
        "compressed_size": compressed_size
    })

@app.route("/image/<token>")
def access_image(token):
    try:
        payload = pyjwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        hashed = payload["hash"]
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            if file.startswith(hashed) and "compressed" in file:
                return send_from_directory(app.config['UPLOAD_FOLDER'], file)
        return "Not found", 404
    except pyjwt.ExpiredSignatureError:
        return "URL expired", 403
