import re
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from functools import lru_cache
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from tqdm import tqdm

# Load kamus alay dari CSV
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
kamus_path = os.path.join(BASE_DIR, "data", "resources", "colloquial-indonesian-lexicon.csv")

kamus_df = pd.read_csv(kamus_path)
kamus_alay = dict(zip(kamus_df['slang'], kamus_df['formal']))

# Normalisasi tambahan
norm = {
    "aku":"saya","ak":"saya", "aq":"saya", "gue":"saya","gua":"saya","gw":"saya","sy":"saya","sya":"saya","saya":"saya",
    "kamu":"kamu","lu":"kamu","elo":"kamu",
    "dia":"dia","doi":"dia","ia":"dia",
    "gk":"tidak","ga":"tidak","gak":"tidak","nggak":"tidak","enggak":"tidak","engga":"tidak",
    "klo":"kalau","kalo":"kalau","yg":"yang","utk":"untuk","bgt":"sangat", "banget":"sangat",
    "pengin":"ingin", "pengen":"ingin", "mau":"ingin", "mo":"ingin", "mw":"ingin",
    "bye":"selamat tinggal",  "kayak":"seperti", "aja":"saja",
    "jambakin":"menjambak", "nyekek":"mencekik", "bikin":"membuat", "asik":"asyik", "capek":"lelah",
    "udah":"sudah", "udh":"sudah", "gitu":"begitu", "cuma":"hanya",
    "bundir":"bunuh diri", "suicide":"bunuh diri", "suicidal":"bunuh diri",
    "ngiket":"mengikat", "nabrakin":"menabrakkan", "jedotin":"membenturkan", 
    "jedot":"bentur", "benturin":"membenturkan", "kejedot":"terbentur", 
    "dijedotin":"dibenturkan", "dijedotkan":"dibenturkan",
    "sih":"","deh":"","dong":"","nih":"","lah":"","kok":"","kan":"","ya":"","yah":"","nya":"",
}

phrases = [
    (r"\bself\s*harm\b", "selfharm"),
    (r"\b(nyakiti|nyakitin|sakiti)\b", "menyakiti"),
    (r"\b(melukai|ngelukai|lukai)\b", "melukai"),
    (r"\b(nyilet|sayat|iris|gores|barcode)\s+(tangan|pergelangan)\b", "sayat_tangan"),
]

stemmer = StemmerFactory().create_stemmer()
factory = StopWordRemoverFactory()
stopwords = set(factory.get_stop_words())
tqdm.pandas()

@lru_cache(maxsize=10000)
def cached_stem(word):
    return stemmer.stem(word)

def preprocess(content, custom_norm=False):
    content = re.sub(r"http\S+|www\S+|https\S+", '', content)
    content = re.sub(r'@\w+|\#\w+', '', content)
    content = re.sub(r"[^a-zA-Z\s]", " ", content)
    content = content.lower()
    tokens = content.split()
    tokens = [kamus_alay.get(word, word) for word in tokens]
    if custom_norm:
        tokens = [norm.get(word, word) for word in tokens]
        text = " ".join(tokens)
        for pattern, repl in phrases:
            text = re.sub(pattern, repl, text)
        tokens = text.split()
    tokens = [w for w in tokens if w not in stopwords]
    stemmed = [cached_stem(word) for word in tokens]
    return ' '.join(stemmed)

def plot_label_distribution(df, label_column):
    jumlah_kelas = df[label_column].value_counts()
    persen_kelas = df[label_column].value_counts(normalize=True) * 100
    distribusi = pd.DataFrame({'Jumlah': jumlah_kelas, 'Persentase (%)': persen_kelas.round(2)})
    print("\n📊 Distribusi Kelas:\n", distribusi)

    plt.figure(figsize=(6, 4))
    ax = sns.countplot(x=label_column, data=df)
    plt.title("Distribusi Kelas (Imbalance Check)")
    plt.xlabel("Label")
    plt.ylabel("Jumlah")

    total = len(df)
    for p in ax.patches:
        jumlah = int(p.get_height())
        persentase = 100 * jumlah / total
        ax.annotate(f'{persentase:.1f}%', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    return plt

def run_preprocessing(input_path, output_file, save_img_path, custom_norm=False):
    print(f"Membaca dataset dari: {input_path}")
    df = pd.read_csv(input_path, encoding='utf-8', on_bad_lines='skip')
    
    # FIXED: Tidak rename dari 'komentar', karena dataset sudah memiliki 'clean_text'
    # df = df.rename(columns={'komentar': 'clean_text'})  # ❌ DIHAPUS
    # FIXED: Pastikan kolom clean_text ada
    if 'clean_text' not in df.columns:
        raise ValueError("Kolom 'clean_text' tidak ditemukan di dataset! Harap cek struktur CSV.")  # FIXED

    print("🔧 Melakukan preprocessing...")
    df['clean_text'] = df['clean_text'].astype(str)
    df['clean_text'] = df['clean_text'].progress_apply(lambda x: preprocess(x, custom_norm))
    print("✅ Preprocessing selesai!")

    df['id'] = range(1, len(df) + 1)
    df[['id', 'clean_text', 'label']].to_csv(output_file, index=False)
    print(f"💾 Hasil disimpan di: {output_file}")
    
    plt_obj = plot_label_distribution(df, 'label')
    plt_obj.savefig(save_img_path)
    plt_obj.show()
    
    return df

if __name__ == "__main__":
    input_file = os.path.join(BASE_DIR, "data", "raw", "fix_data.csv") 
    output_file = os.path.join(BASE_DIR, "data", "processed", "nc_preprocessed_dataset.csv")
    save_img_path = os.path.join(BASE_DIR, "data", "processed", 'nc_distribution.png')

    run_preprocessing(input_file, output_file, save_img_path, custom_norm=False)
