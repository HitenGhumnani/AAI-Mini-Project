# Pix2Pix Image-to-Image Translation (Mini Project)

This project has:
- `backend/`: Flask API that loads your Pix2Pix `.h5` model and runs inference.
- `frontend/`: Simple Vite web UI to upload an image and show generated output.

## 1) Project structure

- `pix2pix_generator_50.h5` (your trained model in project root)
- `samples/` (sample input images)
- `backend/app.py`
- `backend/requirements.txt`
- `frontend/` (UI)

## 2) Backend setup (Flask + TensorFlow)

Open terminal in project root and run:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend runs at: `http://127.0.0.1:5000`

Note: model loading is lazy (on first prediction). So backend starts fast, and the first `/predict` call may take longer while the `.h5` model loads.

### API endpoint

- `POST /predict`
- Form-data key: `image`
- Returns: generated image (`image/png`)

## 3) Frontend setup (Vite)

Open a second terminal in project root:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://127.0.0.1:5173`

## 4) How it works

### Preprocessing (input)
- Image is resized to `256x256`
- Normalized exactly as:
  - `(image / 127.5) - 1`

### Postprocessing (output)
- Model output is denormalized exactly as:
  - `(output + 1) / 2`
- Then converted to PNG and sent back to frontend.

## 5) Use the app

1. Open frontend URL in browser.
2. Upload a blueprint/label-map image.
3. Click **Generate Output**.
4. See generated facade image in output panel.
