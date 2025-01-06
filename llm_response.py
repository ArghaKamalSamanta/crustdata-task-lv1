import faiss
import json
from create_vectorDB import model
from huggingface_hub import InferenceClient

# Load the FAISS Vector Database
index = faiss.read_index("notion_vector_index.faiss")

# Load metadata (retrieved chunks)
with open("notion_metadata.json", "r", encoding="utf-8") as meta_file:
    metadata = json.load(meta_file)

# Huggingface api
client = InferenceClient(api_key="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")

# Function to Retrieve Relevant Chunks
def retrieve_chunks(query, top_k=5):
    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)
    results = [metadata["chunks"][idx] for idx in indices[0]]
    return results

# Generate Output with LLaMA
def generate_response(query):
    # Retrieve relevant chunks
    retrieved_chunks = retrieve_chunks(query)
    context = " ".join(retrieved_chunks)

    # Prepare the input for LLaMA
    input_text = f"""
        CONTEXT: {context}
        
        QUESTION: {query}

        THINGS TO BE NOTED:
        1. ADD PROPER CODES OR COMMANDS IF NECESSARY.
        2. IF NOTHING IS SPECIFIED, AND YOU FIND BOTH THE PYTHON CODE AND CURL COMMANDS ARE EQUALLY APPLICABLE, PREFER CURL COMMANDS OVER THE PYTHON CODE.
        3. IF IMPORTANT LINKS ARE AVAILABLE TO LOOK INTO, ATTACH THEM.
        
        Answer:
        """
    
    messages = [
	    {
	    	"role": "user",
	    	"content": input_text
	    }
    ]

    completion = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3", 
    	messages=messages, 
    	max_tokens=500
    )

    return completion.choices[0].message.content

# Example Query
# if __name__ == "__main__":
#     user_query = "How do I authenticate using the API?"
#     response = generate_response(user_query)
#     print("Generated Response:")
#     print(response)
