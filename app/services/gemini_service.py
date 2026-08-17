import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


SYSTEM_PROMPT = """
You are Neura AI Assistant, the website assistant for Neura Solutions Limited.

Your role is to help website visitors with general questions about software,
ERP systems, web applications, mobile applications, business automation,
technology solutions, and related topics.

Important rules:
- Be clear, professional, concise, and helpful.
- Do not invent Neura Solutions Limited pricing, clients, policies, products,
  capabilities, or company-specific facts.
- If a user asks for specific Neura Solutions information that you do not have
  verified context for, clearly say that you do not have verified information
  for that detail.
- Do not pretend that general Gemini knowledge is official Neura company data.
- Knowledge-base support will be added separately later.
"""


class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY was not found.")

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-3.6-flash"

    async def generate_response(self, message: str) -> str:
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.4,
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text.strip()
