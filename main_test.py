from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from llm import ask_llm

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
client = QdrantClient(url="http://localhost:6333")

COLLECTION_NAME = "code_chunks"

# def search(query, top_k=3):
#     query_vector = model.encode(query).tolist()
#     results = client.query_points(
#         collection_name=COLLECTION_NAME,
#         query=query_vector,
#         limit=top_k,
#     )
#     return [point.payload for point in results.points]

def search(query, top_k=3):
    query_vector = model.encode(query).tolist()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
    )
    output = []
    for point in results.points:
        chunk = point.payload.copy()
        chunk["score"] = point.score
        output.append(chunk)
    return output


if __name__ == "__main__":
    question = input("Ask something about the code: ")

    chunks = search(question, top_k=2)
    answer = ask_llm(question, chunks)

    print("\n--- Answer ---")
    print(answer)