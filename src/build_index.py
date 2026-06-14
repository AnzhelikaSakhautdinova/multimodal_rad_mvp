import pandas as pd
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer

CAPTIONS_PATH = "data/captions.csv"
INDEX_PATH = "data/video_index.faiss"
META_PATH = "data/video_metadata.pkl"

df = pd.read_csv(CAPTIONS_PATH)

df = df.dropna(subset=["description"])
df = df[df["description"].str.strip() != ""]

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

embeddings = model.encode(
    df["description"].tolist(),
    convert_to_numpy=True,
    normalize_embeddings=True
)

embeddings = embeddings.astype("float32")

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

faiss.write_index(index, INDEX_PATH)

metadata = df.to_dict(orient="records")
with open(META_PATH, "wb") as f:
    pickle.dump(metadata, f)

print(f"Indexed {len(df)} scenes/frames")
print(f"Saved index to {INDEX_PATH}")