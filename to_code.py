# /// script
# requires-python = ">=3.11"
# dependencies = [
#  "sentence-transformers",
#  "scikit-learn",
# ]
# ///

import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Step 1: Ensure ./data/ directory exists
os.makedirs('./data/', exist_ok=True)

# Step 2: Read comments from the file
with open('./data/comments.txt', 'r') as f:
    comments = [line.strip() for line in f if line.strip()]  # Ignore empty lines

# Step 3: Generate embeddings for comments
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(comments)

# Step 4: Calculate cosine similarities
similarity_matrix = cosine_similarity(embeddings)

# Step 5: Find the most similar pair
most_similar_pair = np.unravel_index(np.argmax(similarity_matrix - np.eye(len(similarity_matrix))), similarity_matrix.shape)

# Step 6: Write the most similar comments to a file
with open('./data/comments-similar.txt', 'w') as f:
    f.write(comments[most_similar_pair[0]] + '\n')
    f.write(comments[most_similar_pair[1]] + '\n')