from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from PIL import Image
import os
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['COMPRESSED_FOLDER'] = 'compressed'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['COMPRESSED_FOLDER']):
    os.makedirs(app.config['COMPRESSED_FOLDER'])

@app.route('/')
def index():
    compressed_image_url = request.args.get('compressed_image_url')
    return render_template('index.html', compressed_image_url=compressed_image_url)

@app.route('/compress', methods=['POST'])
def compress():
    if 'image' not in request.files:
        return 'No image uploaded!', 400

    image = request.files['image']

    if image.filename == '':
        return 'No selected file', 400

    compression_level = request.form.get('compression_level', 'medium')

    # Define quality based on compression level
    quality_map = {
        'low': 30,
        'medium': 50,
        'high': 80
    }
    quality = quality_map.get(compression_level, 50)

    if image:
        # Open the uploaded image
        img = Image.open(image)
        img = img.convert('RGB')  # Ensure it's in RGB mode for JPEG compatibility
        img_io = BytesIO()

        # Compress the image
        img.save(img_io, 'JPEG', quality=quality)
        img_io.seek(0)

        # Save the compressed image
        compressed_filename = os.path.join(app.config['COMPRESSED_FOLDER'], 'compressed_image.jpg')
        with open(compressed_filename, 'wb') as f:
            f.write(img_io.getbuffer())

        return redirect(url_for('index', compressed_image_url=url_for('send_compressed_file', filename='compressed_image.jpg')))

@app.route('/compressed/<filename>')
def send_compressed_file(filename):
    return send_from_directory(app.config['COMPRESSED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
