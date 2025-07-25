import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings
import chromadb

# Load environment variables
load_dotenv()

# Debug query
query = "What is the routing number for Regent Bank?"

# Set up embedding model
embedding_model = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_EMBEDDING_KEY"),
)

# Chroma Client Setup
chroma_client = chromadb.HttpClient(
    ssl=True,
    host="api.trychroma.com",
    tenant=os.getenv("CHROMA_TENANT"),
    database=os.getenv("CHROMA_DATABASE"),
    headers={"x-chroma-token": os.getenv("CHROMA_API_KEY")}
)

# Load collection
vectorstore = Chroma(
    client=chroma_client,
    collection_name=os.getenv("CHROMA_COLLECTION"),
    embedding_function=embedding_model
)

# Reusable function for top-k chunk retrieval
def get_top_chunks(query: str, k: int = 4):
    """
    Retrieve top-k most relevant chunks from Chroma DB.
    Returns list of (text, metadata) tuples.
    """
    results = vectorstore.similarity_search_with_score(query, k=k)
    return [(doc.page_content, doc.metadata) for doc, _ in results]

# Optional debug/test block
if __name__ == "__main__":
    # Test query can be entered interactively if desired
    query = input("Enter a test query: ")
    top_chunks = get_top_chunks(query)

    print(f"\n🔍 Top chunks for: '{query}'\n")
    for i, (content, metadata) in enumerate(top_chunks, 1):
        print(f"Result {i}:\n{content}\n--- Metadata: {metadata}\n{'-'*40}")

# ------------
# # Search
# results = vectorstore.similarity_search(query, k=3)

# # Display results
# print(f"\n🔍 Top matches for: '{query}'\n")
# for i, doc in enumerate(results, 1):
#     print(f"Result {i}:\n{doc.page_content}\n{'-'*40}")
