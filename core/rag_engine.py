import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_mistralai import ChatMistralAI

from core.vector_store import (
    build_vector_store,
    load_vector_store,
    get_retriever,
)


def get_llm():
    api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        raise RuntimeError(
            "MISTRAL_API_KEY not found in .env"
        )

    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=api_key,
        temperature=0.3,
    )


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


SYSTEM_PROMPT = """
You are an expert meeting assistant.

Answer ONLY using the meeting transcript context.

If the answer is not present, reply:

"I could not find this information in the meeting transcript."

Context:
{context}
"""


def build_rag_chain(transcript: str):
    vector_store = build_vector_store(transcript)

    retriever = get_retriever(vector_store, k=4)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{question}"),
        ]
    )

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | get_llm()
        | StrOutputParser()
    )

    return rag_chain


def load_rag_chain():
    vector_store = load_vector_store()

    retriever = get_retriever(vector_store, k=4)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{question}"),
        ]
    )

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | get_llm()
        | StrOutputParser()
    )

    return rag_chain


def ask_question(rag_chain, question: str):
    print(f"\nQuestion: {question}")

    answer = rag_chain.invoke(question)

    print(f"\nAnswer:\n{answer}")

    return answer