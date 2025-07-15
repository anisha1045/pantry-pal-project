from flask import Flask, render_template, request, jsonify
import base64
from PIL import Image
from io import BytesIO

@app.route('/camera')
def camera():
    return render_template('camera.html')  # serve the camera page

@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    data = request.get_json()
    image_data = data['image'].split(',')[1]
    img_bytes = base64.b64decode(image_data)

    image = Image.open(BytesIO(img_bytes))
    image.save('user_upload.png')  # or save to a Clarifai upload endpoint

    return jsonify({'status': 'success'})
