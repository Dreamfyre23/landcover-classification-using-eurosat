from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import rasterio
from tensorflow.keras.models import load_model
import tempfile
import os
from collections import Counter
from google.cloud import storage

app = Flask(__name__)
CORS(app)

# Initialize Google Cloud Storage
storage_client = storage.Client()
bucket_name = os.getenv('GCLOUD_STORAGE_BUCKET')

# Load model from Cloud Storage
def load_model_from_gcs():
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob('models/6bands_v5-5_SC.h5')
    local_path = '/tmp/model.h5'
    blob.download_to_filename(local_path)
    return load_model(local_path)

model = load_model_from_gcs()

class_labels = {
    0: 'AnnualCrop',
    1: 'Forest',
    2: 'HerbaceousVegetation',
    3: 'Highway',
    4: 'Industrial',
    5: 'Pasture',
    6: 'PermanentCrop',
    7: 'Residential',
    8: 'River',
    9: 'SeaLake'
}

def preprocess_image(image_path):
    """Preprocess the satellite image"""
    with rasterio.open(image_path) as src:
        selected_bands = [1, 2, 3, 4, 5, 6]
        selected_bands = [b for b in selected_bands if b <= src.count]
        img = src.read(selected_bands)
    
    img = np.moveaxis(img, 0, -1)
    img = img.astype(np.float32) / 10000.0
    
    if img.shape[-1] < 6:
        diff = 6 - img.shape[-1]
        extra_bands = np.repeat(img[..., -1:], diff, axis=-1)
        img = np.concatenate([img, extra_bands], axis=-1)
    
    return img

def predict_landcover(image_path, patch_size=64):
    """Predict land cover for an image"""
    image = preprocess_image(image_path)
    h, w, c = image.shape
    
    patches = []
    coords = []
    for i in range(0, h - patch_size + 1, patch_size):
        for j in range(0, w - patch_size + 1, patch_size):
            patch = image[i:i+patch_size, j:j+patch_size, :]
            patches.append(patch)
            coords.append((i, j))
    
    patches = np.array(patches)
    predictions = model.predict(patches)
    predicted_classes = np.argmax(predictions, axis=1)
    
    return coords, predicted_classes

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.tif'):
        return jsonify({'error': 'File must be a .tif'}), 400
    
    try:
        # Save uploaded file to temp location
        temp_dir = tempfile.mkdtemp()
        upload_path = os.path.join(temp_dir, file.filename)
        file.save(upload_path)
        
        # Process the image
        coords, predicted_classes = predict_landcover(upload_path)
        
        # Prepare results
        predictions = [
            {"patch": f"{x},{y}", "class": class_labels[cls]}
            for (x, y), cls in zip(coords[:10], predicted_classes[:10])  # Show first 10 for demo
        ]
        
        # Calculate class distribution
        total = len(predicted_classes)
        class_dist = {
            class_labels[cls]: count/total
            for cls, count in Counter(predicted_classes).items()
        }
        
        # Clean up
        os.remove(upload_path)
        os.rmdir(temp_dir)
        
        return jsonify({
            'status': 'success',
            'predictions': predictions,
            'class_distribution': class_dist
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
