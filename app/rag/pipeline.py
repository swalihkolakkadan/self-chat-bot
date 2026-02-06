"""
RAG Pipeline using LangChain with Google Gemini and Chroma.
"""
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from app.config import get_settings
from app.prompts.system import SYSTEM_PROMPT

settings = get_settings()

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=settings.google_api_key
)

# Initialize vector store
vectorstore = Chroma(
    persist_directory=settings.chroma_persist_dir,
    embedding_function=embeddings
)

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=settings.google_api_key,
    temperature=0.7,
    convert_system_message_to_human=True
)


# Create prompt template
prompt_template = PromptTemplate(
    template=SYSTEM_PROMPT,
    input_variables=["context", "question"]
)


def get_retriever():
    """Get the vector store retriever."""
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )


async def get_rag_response(question: str) -> str:
    """
    Get a complete response from the RAG pipeline.
    """
    retriever = get_retriever()
    
    # Retrieve relevant documents
    docs = retriever.get_relevant_documents(question)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Format prompt
    formatted_prompt = prompt_template.format(
        context=context,
        question=question
    )
    
    # Get response
    response = await llm.ainvoke(formatted_prompt)
    return response.content

