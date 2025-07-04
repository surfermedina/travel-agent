# Used to interact with the operating system — in our case, to read environment variables from .env
# Example: os.getenv("AZURE_OPENAI_API_KEY") gets your API key from the .env file securely.
import os

# From the python-dotenv package
# Example: load_dotenv() reads the .env file and makes the values available via os.getenv()
# Used to keep secrets out of the source code
from dotenv import load_dotenv

# Imports the new Azure-specific OpenAI SDK client, allowing us to interact with Azure OpenAI services.
#   Set a custom azure_endpoint
#   Use your Azure deployment name instead of the base model name (like gpt-4)
from openai import AzureOpenAI

# Load environment variables from .env
load_dotenv()

# Initialize AzureOpenAI client
# client is an object of the class AzureOpenAI -- defined in the openai SDK with pre-defined methods like, .chat.completions.create(...).
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Get deployment name from env
# Uses os.getenv(...) to access an environment variable from .env file.
# Storing the value in the 'deployment' variable so you can use it in your GPT request.
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT");

# The response will contain the model's reply to the input message.
# Sends a Chat Completion request to the GPT model via your Azure deployment.
# 'create' is a function and it takes 'model' and 'messages' and sends them to the GPT model, and returns a 'response' object.
response = client.chat.completions.create(
    model=deployment,   # Tells Azure which deployed model to use.
    # The core of the chat input. You're giving the model a conversation history in the form of a list of messages.
    # Each message is a dictionary with two keys:
    #   "role" → tells GPT who is speaking ("system", "user", or "assistant")
    #   "content" → the text of the message
    messages=[
        {"role": "system", "content": "You are a helpful banking assistant."},
        {"role": "user", "content": "What are your hours of operation?"}
    ]
)

# Print the model's reply
# GPT responses always return a list of “choices”, even if there's only one.
# Each “choice” is a possible model response.
# So 'choices' is a list, typically with one item unless you request more.
print(response.choices[0].message.content)
