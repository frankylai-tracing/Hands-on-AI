from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel
from dotenv import load_dotenv
import os

load_dotenv()

WORKING_MODEL = str(os.getenv("WORKING_MODEL", "thudm/glm-4-9b-0414"))

PPINFRA_BASE_URL = str(
    os.getenv("PPINFRA_BASE_URL", "https://api.ppinfra.com/v3/openai")
)

PPINFRA_API_KEY = str(os.getenv("PPINFRA_API_KEY", ""))

AGENTS_API_KEY = str(os.getenv("AGENTS_API_KEY", ""))


external_client = AsyncOpenAI(
    api_key=PPINFRA_API_KEY,
    base_url=PPINFRA_BASE_URL,
)
external_model = OpenAIChatCompletionsModel(
    model=WORKING_MODEL, openai_client=external_client
)


# WORKING_MODEL = "deepseek-chat"


# DASHSCOPE_BASE_URL = "https://api.deepseek.com/v1"
# DASHSCOPE_API_KEY = "sk-989c0be6ea404f9982ce391f21c0b563"

# external_client = AsyncOpenAI(
#     api_key=DASHSCOPE_API_KEY,
#     base_url=DASHSCOPE_BASE_URL,
# )
# external_model = OpenAIChatCompletionsModel(
#     model=WORKING_MODEL, openai_client=external_client
# )
