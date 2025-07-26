<<<<<<< HEAD
from sentence_transformers import SentenceTransformer

# ✅ This ensures it downloads full model with pytorch_model.bin
model = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L6-v2")

# ✅ Save to ./local_model
model.save("./local_model")

print("✅ local_model downloaded and saved with pytorch_model.bin")
=======
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
model.save('./local_model')

print("local_model saved — ready for Docker!")
>>>>>>> 444671027836fcd32718b71f681fded2782fa008
