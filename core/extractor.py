import os

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def get_llm():
    api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        raise RuntimeError(
            "MISTRAL_API_KEY not found. Check your .env file."
        )

    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=api_key,
        temperature=0.2,
    )


def build_chain(system_prompt: str):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{text}"),
        ]
    )

    return prompt | get_llm() | StrOutputParser()


def extract_action_items(transcript: str) -> str:
    if not transcript.strip():
        return "No transcript available."

    chain = build_chain(
        """
You are an expert meeting analyst.

Extract every action item.

For each action item provide:
- Task
- Owner
- Deadline (or "Not specified")

Return a numbered list.

If none exist, return:
No action items found.
"""
    )

    return chain.invoke({"text": transcript})


def extract_key_decisions(transcript: str) -> str:
    if not transcript.strip():
        return "No transcript available."

    chain = build_chain(
        """
You are an expert meeting analyst.

Extract every key decision made during the meeting.

Return a numbered list.

If none exist, return:
No key decisions found.
"""
    )

    return chain.invoke({"text": transcript})


def extract_questions(transcript: str) -> str:
    if not transcript.strip():
        return "No transcript available."

    chain = build_chain(
        """
You are an expert meeting analyst.

Extract unresolved questions or follow-up topics.

Return a numbered list.

If none exist, return:
No open questions found.
"""
    )

    return chain.invoke({"text": transcript})