import pandas as pd
import chromadb
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import os


# ============================================================
# CONFIG
# ============================================================

CSV_FILE = "pico8_games_100.csv"
DB_PATH = "./rag_database"
COLLECTION_NAME = "pico8_games"


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 70)
print("PICO-8 RAG DATABASE")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(CSV_FILE)

print(f"Loaded {len(df)} games.")


# ============================================================
# PREPARE DOCUMENTS
# ============================================================

documents = []
metadata = []

for index, row in df.iterrows():

    document = f"""
Game Name: {row.get('Name of game', '')}
Author: {row.get('Name of author', '')}
License: {row.get('License', '')}
Like Count: {row.get('Like count', '')}

Game Description:
{row.get('Game description', '')}

Top Comments:
{row.get('Top-5 comments', '')}

Game Code:
{row.get('Game code', '')}
"""

    documents.append(document)

    metadata.append({
        "game_name": str(row.get("Name of game", "")),
        "author": str(row.get("Name of author", "")),
        "license": str(row.get("License", "")),
        "likes": str(row.get("Like count", "")),
        "game_code": str(row.get("Game code", ""))
    })


# ============================================================
# TF-IDF VECTOR DATABASE
# ============================================================

print("\nCreating vector embeddings...")

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=10000
)

embeddings = vectorizer.fit_transform(documents).toarray()

print("Embeddings created.")
print("Embedding dimensions:", embeddings.shape[1])


# ============================================================
# CHROMA DATABASE
# ============================================================

print("\nCreating Chroma vector database...")

client = chromadb.PersistentClient(
    path=DB_PATH
)

# Delete old collection if it exists
try:
    client.delete_collection(COLLECTION_NAME)
except Exception:
    pass

collection = client.create_collection(
    name=COLLECTION_NAME
)


# ============================================================
# STORE DATA
# ============================================================

collection.add(
    ids=[f"game_{i}" for i in range(len(documents))],
    embeddings=embeddings.tolist(),
    documents=documents,
    metadatas=metadata
)

print("Games stored in vector database:", collection.count())


# ============================================================
# SAVE VECTORIZER
# ============================================================

import pickle

with open("rag_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)


# ============================================================
# SEARCH FUNCTION
# ============================================================

def search_games(query, top_k=5):

    query_vector = vectorizer.transform(
        [query]
    ).toarray().tolist()

    results = collection.query(
        query_embeddings=query_vector,
        n_results=top_k
    )

    return results


# ============================================================
# PICO-8 CODE GENERATION PROMPT
# ============================================================

def create_code_generation_prompt(query, results):

    retrieved_games = results["documents"][0]

    context = "\n\n".join(retrieved_games)

    prompt = f"""
You are an expert PICO-8 game developer.

The user wants to create:

{query}

Use the following retrieved PICO-8 game examples
as inspiration:

{context}

Create a complete PICO-8 Lua game.

Requirements:
- Use valid PICO-8 Lua syntax.
- Include _init(), _update(), and _draw().
- Keep the game simple enough to run on PICO-8.
- Do not copy an existing game exactly.
- Use the retrieved games only as design inspiration.

Return only the PICO-8 Lua code.
"""

    return prompt


# ============================================================
# INTERACTIVE RAG SYSTEM
# ============================================================

print("\n" + "=" * 70)
print("RAG DATABASE READY")
print("=" * 70)

print("""
Example queries:

1. platformer game
2. space shooter
3. puzzle game
4. racing game
5. game with enemies
6. platformer with coins

Type 'exit' to stop.
""")


while True:

    query = input("\nEnter your game idea: ")

    if query.lower() == "exit":
        break

    results = search_games(
        query,
        top_k=5
    )

    print("\n" + "-" * 70)
    print("TOP 5 RETRIEVED GAMES")
    print("-" * 70)

    for i in range(5):

        game = results["metadatas"][0][i]

        print(
            f"\n{i + 1}. {game['game_name']}"
        )

        print(
            f"   Author: {game['author']}"
        )

        print(
            f"   Likes: {game['likes']}"
        )

    # Create generation prompt
    generation_prompt = create_code_generation_prompt(
        query,
        results
    )

    # Save prompt
    with open(
        "pico8_generation_prompt.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(generation_prompt)

    print("\n" + "-" * 70)
    print("RAG CODE-GENERATION CONTEXT CREATED")
    print("-" * 70)

    print(
        "\nSaved to: pico8_generation_prompt.txt"
    )


print("\nRAG system finished.")