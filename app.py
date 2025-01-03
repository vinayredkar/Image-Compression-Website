import os
from PIL import Image
from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Compress function
@app.route('/')
def index():
    return render_template('index.html', compressed_image_url=None, shrink_percentage=None)

@app.route('/compress', methods=['POST'])
def compress():
    if 'image' not in request.files:
        return "No file part"
    file = request.files['image']
    
    if file.filename == '':
        return "No selected file"
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the uploaded file
        file.save(filepath)
        
        # Open the image using PIL
        img = Image.open(filepath)
        
        # Check if the image is in RGBA mode (transparency) and convert to RGB if necessary
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Get original file size
        original_size = os.path.getsize(filepath)
        
        # Compress the image with the chosen quality
        quality = 75  # Example of medium quality (you can adjust based on user input)
        compressed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'compressed_{filename}')
        img.save(compressed_filepath, 'JPEG', quality=quality)
        
        # Get compressed file size
        compressed_size = os.path.getsize(compressed_filepath)
        
        # Calculate shrink percentage
        shrink_percentage = ((original_size - compressed_size) / original_size) * 100
        
        # Get the compressed image URL
        compressed_image_url = f'/uploads/{os.path.basename(compressed_filepath)}'
        
        # Return the compressed image URL and shrink percentage to the front-end
        return render_template('index.html', compressed_image_url=compressed_image_url, shrink_percentage=shrink_percentage)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)
