from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os
from io import BytesIO
from PIL import Image
import base64

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Database connection
client = MongoClient(MONGO_URI)
db = client['image_database']
collection = db['images']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Save image to MongoDB
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as f:
                img_data = f.read()
                collection.insert_one({'filename': filename, 'image': img_data})
            
            return redirect(url_for('display_images'))
    return render_template('upload.html')

@app.route('/images')
def display_images():
    images = collection.find()
    image_list = []
    for image in images:
        img = Image.open(BytesIO(image['image']))
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        image_list.append({'filename': image['filename'], 'image': img_str})
    return render_template('images.html', images=image_list)

if __name__ == '__main__':
    app.run(debug=True)