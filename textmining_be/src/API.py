from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import os
from tqdm import tqdm
from preprocess import preprocess
import joblib
import pandas as pd
import re

app = Flask(__name__)
CORS(app)

# Path model dan vectorizer
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, ".."))
models_dir = os.path.join(project_root, "models")

# =========================
# 1. Home
# =========================

@app.route("/")
def home():
    return render_template("index.html")

# @app.route("/detail/<kategori>")
# def detail(kategori):
#     return render_template("detail.html", kategori=kategori)


# @app.route("/")
# def home():
#     return render_template("home.html")

# @app.route("/detail")
# def detail():
#     return render_template("detail.html")


# =========================
# 2. Halaman Form Input
# =========================
@app.route("/form")
def form():
    return """
    <h2>🎥 Deteksi Komentar TikTok</h2>
    <form action="/detect" method="post" style="margin-top:20px;">
      <label for="video_url">Masukkan URL TikTok:</label><br><br>
      <input type="text" id="video_url" name="video_url" style="width:400px; padding:5px;"><br><br>
      <button type="submit" style="padding:5px 15px;">Deteksi</button>
    </form>
    """

# =========================
# 3. Fungsi Scraper Komentar TikTok
# =========================
def scrape_tiktok_comments(video_url):
    if "vm.tiktok.com" in video_url or "vt.tiktok.com" in video_url:
        videoid = requests.head(video_url, stream=True, allow_redirects=True, timeout=5).url.split("/")[5].split("?", 1)[0]
    else:
        videoid = video_url.split("/")[5].split("?", 1)[0]

    t = 0
    comments = []

    while True:
        try:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
                'referer': f'https://www.tiktok.com/@x/video/{videoid}',
            }

            response = requests.get(
                f"https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={videoid}&count=50&cursor={t}",
                headers=headers
            ).json()

            if "comments" not in response or not response["comments"]:
                break

            for comment in response["comments"]:
                username = comment["user"]["nickname"] if "user" in comment and "nickname" in comment["user"] else "Unknown"
                text = comment["text"]
                comments.append({"username": username, "text": text})

            t += 50
        except Exception as e:
            print(f"Error: {e}")
            break

    return comments

# =========================
# 4. Fungsi Prediksi
# =========================
def predict_texts(texts):
    # 🔹 Ganti ke model 90:20 kamu di sini
    model_path = os.path.join(models_dir, "svm_model9010.pkl")
    vectorizer_path = os.path.join(models_dir, "nc_tfidf_vectorizer.pkl")

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)

    X = vectorizer.transform(texts)
    y_pred = model.predict(X)

    # Mapping label agar lebih jelas
    label_mapping = {
        "abusive": "Non Pelecehan Seksual",
        "pelecehan": "Pelanggaran Seksual"
    }

    y_mapped = [label_mapping.get(label, label) for label in y_pred]
    return y_mapped

# =========================
# 5. Endpoint Deteksi
# =========================
@app.route("/detect", methods=["POST"])
def detect():
    # Cek apakah data dikirim dari JSON (Postman) atau dari Form HTML
    if request.is_json:
        data = request.json
        video_url = data.get("video_url", "").strip()
    else:
        video_url = request.form.get("video_url", "").strip()

    if not video_url:
        return jsonify({"error": "Link TikTok tidak boleh kosong!"}), 400

    print(f"🔍 Mengambil komentar dari: {video_url}")

    comments = scrape_tiktok_comments(video_url)
    if not comments:
        return jsonify({"error": "Tidak ditemukan komentar atau link tidak valid."}), 404

    tqdm.pandas()
    df = pd.DataFrame(comments)
    df['clean_text'] = df['text'].astype(str).progress_apply(lambda x: preprocess(x, custom_norm=True))

    predictions = predict_texts(df['clean_text'].tolist())
    df['prediction'] = predictions

    hasil = []
    for _, row in df.iterrows():
        hasil.append({
            "username": row["username"],
            "text": row["text"],
            "clean_text": row["clean_text"],
            "prediction": row["prediction"]
        })

    return jsonify(hasil)

# =========================
# 6. Run Flask App
# =========================
if __name__ == "__main__":
    app.run(debug=True)
