# === Imports ===
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from utils.logger import get_logger
from utils.sanitize import sanitize_input

# Local modules
from utils.yaml_loader import load_faq
from utils.match_faq import find_best_match

# === Load environment variables ===
load_dotenv()

# === System Prompt ===
system_prompt = "You are a helpful banking assistant. Answer questions clearly and concisely."

# === Initialize logger ===
logger = get_logger()

# === Initialize AzureOpenAI client ===
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Get deployment name from env
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# === Load FAQ Data ===
client_id = os.getenv("CLIENT_ID", "demobank")
faq_data = load_faq(client_id)

# === Simulated User Input ===
raw_input = "What are your hours of operation?"  # TODO: Replace with input from frontend
user_question = sanitize_input(raw_input) # Sanitize the input for security and consistency
logger.info(f"Client: {client_id} | Raw Input: {raw_input}")
logger.debug(f"Sanitized input: {user_question}")

# === First try to match FAQ (using RapidFuzz) ===
answer = find_best_match(user_question, faq_data)

# === If an answer is found in the FAQ, return it; otherwise, query GPT ===
if answer:
    logger.info("[FAQ MATCH] Answer returned from FAQ.")
    logger.debug(f"Answer: {answer}")
    print(answer)
else:
    logger.info("[NO FAQ MATCH] Querying GPT...")
    # If no FAQ match, query the GPT model
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]
    )
    # If GPT returns an invalid response, guard against it
    if response.choices and response.choices[0].message:
        answer = response.choices[0].message.content
        logger.debug(f"GPT Answer: {answer}")
        print(answer)
    else:
        logger.warning("GPT returned no response.")
        answer = "Sorry, I couldn’t retrieve a response at the moment."
        print(answer)

