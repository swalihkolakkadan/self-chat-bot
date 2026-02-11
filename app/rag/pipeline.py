"""
RAG Pipeline using LangChain with Google Gemini and Chroma.
"""
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from app.config import get_settings
from app.prompts.system import SYSTEM_PROMPT
from app.services.chat_history import ChatHistoryManager

settings = get_settings()

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=settings.google_api_key
)

# Initialize vector store
vectorstore = Chroma(
    persist_directory=settings.chroma_persist_dir,
    embedding_function=embeddings
)

# Initialize LLM
# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=settings.google_api_key,
    temperature=0.7,
    max_output_tokens=150,
    convert_system_message_to_human=True
)


# Create prompt template
prompt_template = PromptTemplate(
    template=SYSTEM_PROMPT,
    input_variables=["context", "chat_history", "question"]
)


def get_retriever():
    """Get the vector store retriever."""
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )


async def get_rag_response(question: str, session_id: str = None) -> str:
    """
    Get a complete response from the RAG pipeline with chat history.
    """
    from app.utils.timer import timer
    
    retriever = get_retriever()
    
    # Get chat history
    with timer("Get Chat History"):
        chat_history_str = ChatHistoryManager.get_formatted_history(session_id) if session_id else ""
    
    search_query = question

    # Retrieve relevant documents using the raw question
    with timer("Retrieve Documents (Vector DB)"):
        docs = retriever.invoke(search_query)
        context = "\n\n".join([doc.page_content for doc in docs])
    
    # Format prompt with history
    formatted_prompt = prompt_template.format(
        context=context,
        chat_history=chat_history_str,
        question=question
    )
    
    # Get response
    with timer("Generate Answer (LLM)"):
        response = await llm.ainvoke(formatted_prompt)
        response_text = response.content
    
    # Update history
    if session_id:
        ChatHistoryManager.add_user_message(session_id, question)
        ChatHistoryManager.add_ai_message(session_id, response_text)
        
    return response_text

