
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
model.save('./local_model')

print("local_model saved — ready for Docker!")

