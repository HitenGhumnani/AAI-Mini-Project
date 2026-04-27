import io
import os
import threading

import numpy as np
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from PIL import Image
from tensorflow.keras.layers import Conv2DTranspose
from tensorflow.keras.models import load_model


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "pix2pix_generator_50.h5")

app = Flask(__name__)
CORS(app)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")

class LegacyConv2DTranspose(Conv2DTranspose):
    @classmethod
    def from_config(cls, config):
        # Some older pix2pix .h5 exports store "groups" for Conv2DTranspose.
        # Keras in this environment may reject it, so we ignore that key.
        config.pop("groups", None)
        return super().from_config(config)


model = None
_model_lock = threading.Lock()


def get_model():
    global model
    if model is None:
        with _model_lock:
            if model is None:
                print("Loading model...")
                model = load_model(
                    MODEL_PATH,
                    compile=False,
                    custom_objects={"Conv2DTranspose": LegacyConv2DTranspose},
                )
                print("Model loaded.")
    return model


def preprocess_image(file_storage):
    image = Image.open(file_storage).convert("RGB").resize((256, 256))
    image_array = np.array(image).astype(np.float32)
    image_array = (image_array / 127.5) - 1.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array


def postprocess_output(prediction):
    output = prediction[0]
    output = (output + 1.0) / 2.0
    output = np.clip(output * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(output)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model_loaded": model is not None})


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file uploaded. Use field name 'image'."}), 400

    file_storage = request.files["image"]
    if file_storage.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    try:
        loaded_model = get_model()
        input_tensor = preprocess_image(file_storage)
        prediction = loaded_model.predict(input_tensor, verbose=0)
        output_image = postprocess_output(prediction)

        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")
        buffer.seek(0)
        return send_file(buffer, mimetype="image/png")
    except Exception as error:
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
