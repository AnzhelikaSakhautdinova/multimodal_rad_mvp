import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

import matplotlib.pyplot as plt
from PIL import Image

INDEX_PATH = "data/video_index.faiss"
META_PATH = "data/video_metadata.pkl"

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

index = faiss.read_index(INDEX_PATH)

with open(META_PATH, "rb") as f:
    metadata = pickle.load(f)

def search(query, top_k=3):
    query_emb = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    scores, indices = index.search(query_emb, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        item = metadata[idx]
        results.append({
            "score": float(score),
            "timestamp": item.get("timestamp"),
            "timestamp_sec": item.get("timestamp_sec"),
            "frame_path": item.get("frame_path"),
            "description": item.get("description"),
        })

    return results

if __name__ == "__main__":
    while True:
        query = input("\nEnter query: ")

        if query.lower() in ["exit", "quit"]:
            break

        # results = search(query)

        # for i, result in enumerate(results, 1):
        #     print(f"\nResult {i}")
        #     print(f"Score: {result['score']:.3f}")
        #     print(f"Timestamp: {result['timestamp']}")
        #     print(f"Frame: {result['frame_path']}")
        #     print(f"Description: {result['description']}")

        results = search(query)

        for i, result in enumerate(results, 1):
            print(f"\nResult {i}")
            print(f"Score: {result['score']:.3f}")
            print(f"Timestamp: {result['timestamp']}")
            print(f"Description: {result['description']}")

            image = Image.open(result["frame_path"])

            plt.figure(figsize=(6, 4))
            plt.imshow(image)
            plt.title(
                f"Rank {i} | {result['timestamp']} | Score={result['score']:.3f}"
            )
            plt.axis("off")
            plt.show()