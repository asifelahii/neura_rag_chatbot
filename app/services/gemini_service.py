from typing import List

from google import genai
from google.genai import types

from app.core.config import settings


SYSTEM_PROMPT = """
You are Neura AI Assistant, the website assistant for Neura Solutions Limited.

Your role is to help website visitors with general questions about software,
ERP systems, web applications, mobile applications, business automation,
technology solutions, and related topics.

Important rules:
- Be clear, professional, concise, and helpful.
- Use previous messages in the conversation when relevant.
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
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )
        self.model = settings.gemini_model

    async def generate_response(
        self,
        message: str,
        history: List[dict],
    ) -> str:

        contents = []

        for item in history:
            role = "model" if item["role"] == "assistant" else "user"

            contents.append(
                types.Content(
                    role=role,
                    parts=[
                        types.Part(
                            text=item["content"],
                        )
                    ],
                )
            )

        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        text=message,
                    )
                ],
            )
        )

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.4,
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text.strip()
