"""
Ingest PDFs from Azure Blob Storage into a Chroma vector database.

This script:
- Connects to Azure Blob Storage using credentials from the .env file
- Downloads all PDFs from a specified container
- Parses and chunks the PDF content using LangChain
- Embeds each chunk using Azure OpenAI `text-embedding-3-small`
- Stores the resulting vectors in a hosted Chroma vector database

Required environment variables:
- AZURE_STORAGE_ACCOUNT_NAME
- AZURE_STORAGE_ACCOUNT_KEY
- AZURE_STORAGE_CONTAINER_NAME
- AZURE_OPENAI_EMBEDDING_KEY
- AZURE_OPENAI_EMBEDDING_ENDPOINT
- AZURE_OPENAI_EMBEDDING_DEPLOYMENT
- CHROMA_API_KEY
- CHROMA_TENANT
- CHROMA_DATABASE
- CHROMA_COLLECTION
"""

import os
import tempfile
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
import chromadb
from utils.pdf_cleaner import filter_pdf_text

# Load environment variables
load_dotenv()

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

def ingest_pdfs_from_blob():
    blob_service = BlobServiceClient(
        account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
        credential=AZURE_STORAGE_ACCOUNT_KEY
    )
    container_client = blob_service.get_container_client(AZURE_STORAGE_CONTAINER_NAME)
    blob_list = container_client.list_blobs()

    for blob in blob_list:
        try:
            print(f"📄 Processing: {blob.name}")
            downloader = container_client.download_blob(blob.name)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(downloader.readall())
                tmp_path = tmp_file.name

            loader = PyPDFLoader(tmp_path)
            raw_docs = loader.load()
            for doc in raw_docs:
                doc.page_content = filter_pdf_text(doc.page_content)

            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = splitter.split_documents(raw_docs)
            chunks = [chunk for chunk in chunks if chunk.page_content.strip()] # Filter out empty or whitespace-only chunks
            print(f"✂️  Chunked into {len(chunks)} sections")

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

            collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION)

            vectorstore = Chroma(
                client=chroma_client,
                collection_name=CHROMA_COLLECTION,
                embedding_function=embeddings
            )

            vectorstore.add_documents(chunks)
            print(f"✅ Embedded {len(chunks)} chunks into Chroma for {blob.name}")

        except Exception as e:
            print(f"[ERROR] Failed to process {blob.name}: {e}")

        finally:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == "__main__":
    ingest_pdfs_from_blob()
