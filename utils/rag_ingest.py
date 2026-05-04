import os
import tempfile
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
import chromadb
from utils.pdf_cleaner import filter_pdf_text

# Load environment variables
# load_dotenv()
load_dotenv(override=True)

# Env variables
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")

AZURE_OPENAI_EMBEDDING_KEY = os.getenv("AZURE_OPENAI_EMBEDDING_KEY")
AZURE_OPENAI_EMBEDDING_ENDPOINT = os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION")


# -----------------------------
# Shared helpers
# -----------------------------
def get_vectorstore():
    print(f"🔗 Writing to collection: {CHROMA_COLLECTION}")

    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        api_key=AZURE_OPENAI_EMBEDDING_KEY,
        azure_endpoint=AZURE_OPENAI_EMBEDDING_ENDPOINT,
    )

    chroma_client = chromadb.HttpClient(
        ssl=True,
        host="api.trychroma.com",
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE,
        headers={"x-chroma-token": CHROMA_API_KEY}
    )

    # Ensure collection exists
    chroma_client.get_or_create_collection(name=CHROMA_COLLECTION)

    return Chroma(
        client=chroma_client,
        collection_name=CHROMA_COLLECTION,
        embedding_function=embeddings
    )


def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1800, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    return [c for c in chunks if c.page_content.strip()]


# -----------------------------
# Blob ingestion (existing)
# -----------------------------
def ingest_pdfs_from_blob():
    blob_service = BlobServiceClient(
        account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
        credential=AZURE_STORAGE_ACCOUNT_KEY
    )

    container_client = blob_service.get_container_client(AZURE_STORAGE_CONTAINER_NAME)
    blob_list = container_client.list_blobs()

    vectorstore = get_vectorstore()

    for blob in blob_list:
        try:
            print(f"📄 Processing: {blob.name}")

            downloader = container_client.download_blob(blob.name)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(downloader.readall())
                tmp_path = tmp_file.name

            loader = PyPDFLoader(tmp_path)
            docs = loader.load()

            for doc in docs:
                doc.page_content = filter_pdf_text(doc.page_content)

            chunks = chunk_documents(docs)

            print(f"✂️ Chunked into {len(chunks)} sections")

            vectorstore.add_documents(chunks)
            print(f"✅ Embedded {len(chunks)} chunks into Chroma for {blob.name}")

        except Exception as e:
            print(f"[ERROR] Failed to process {blob.name}: {e}")

        finally:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)


# -----------------------------
# Local ingestion (NEW)
# -----------------------------
def ingest_local_files():
    base_path = os.getenv("LOCAL_RAG_PATH")

    if not base_path or not os.path.exists(base_path):
        raise ValueError(f"Invalid LOCAL_RAG_PATH: {base_path}")

    docs = []

    for file in os.listdir(base_path):
        path = os.path.join(base_path, file)

        try:
            if file.endswith(".txt"):
                print(f"📄 Loading TXT: {file}")
                docs.extend(TextLoader(path).load())

            elif file.endswith(".pdf"):
                print(f"📄 Loading PDF: {file}")
                pdf_docs = PyPDFLoader(path).load()

                for doc in pdf_docs:
                    doc.page_content = filter_pdf_text(doc.page_content)

                docs.extend(pdf_docs)

        except Exception as e:
            print(f"[ERROR] Failed to load {file}: {e}")

    chunks = chunk_documents(docs)
    print(f"✂️ Chunked into {len(chunks)} sections")

    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)

    print(f"✅ Embedded {len(chunks)} chunks into Chroma (local files)")


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    source = os.getenv("INGEST_SOURCE", "blob")

    print(f"🔧 Ingest mode: {source}")
    print(f"📦 DB: {CHROMA_DATABASE}")
    print(f"📚 Collection: {CHROMA_COLLECTION}")

    if source == "local":
        ingest_local_files()
    else:
        ingest_pdfs_from_blob()