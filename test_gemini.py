from google import genai
from config import GEMINI_API_KEY
from gemini_helper import generate_workload_analysis

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello in one sentence."
)

print(response.text)

