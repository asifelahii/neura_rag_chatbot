from typing import List, Optional

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
- Do not pretend that general model knowledge is official Neura company data.
"""


class GeminiService:
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )
        self.model = settings.gemini_model

    def build_system_instruction(
        self,
        context: Optional[str],
    ) -> str:

        if not context:
            return SYSTEM_PROMPT

        return f"""
{SYSTEM_PROMPT}

VERIFIED NEURA KNOWLEDGE BASE CONTEXT:

{context}

When answering Neura-specific factual questions:
- Use the verified knowledge-base context above.
- Do not invent information missing from the context.
- If the context does not contain enough information, say so clearly.
"""

    async def generate_response(
        self,
        message: str,
        history: List[dict],
        context: Optional[str] = None,
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
                system_instruction=self.build_system_instruction(
                    context
                ),
                temperature=0.4,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text.strip()
