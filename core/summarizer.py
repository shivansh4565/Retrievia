import os

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_llm():
    api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        raise RuntimeError(
            "MISTRAL_API_KEY not found. Please check your .env file."
        )

    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=api_key,
        temperature=0.3,
    )


def split_transcript(transcript: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200,
    )
    return splitter.split_text(transcript)


def summarize(transcript: str) -> str:
    if not transcript.strip():
        return "No transcript available."

    llm = get_llm()

    chunks = split_transcript(transcript)

    map_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Summarize this meeting transcript section concisely."),
            ("human", "{text}"),
        ]
    )

    map_chain = map_prompt | llm | StrOutputParser()

    partial_summaries = [
        map_chain.invoke({"text": chunk})
        for chunk in chunks
    ]

    combined_text = "\n\n".join(partial_summaries)

    reduce_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Combine these partial summaries into one professional meeting summary using bullet points.",
            ),
            ("human", "{text}"),
        ]
    )

    reduce_chain = reduce_prompt | llm | StrOutputParser()

    return reduce_chain.invoke({"text": combined_text})


def generate_title(transcript: str) -> str:
    if not transcript.strip():
        return "Untitled Meeting"

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Generate a professional meeting title (maximum 8 words). "
                "Return only the title.",
            ),
            ("human", "{text}"),
        ]
    )

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({"text": transcript[:2000]}).strip()