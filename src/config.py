from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")
# llm = ChatGroq(model="llama-3.3-70b-versatile")


# from langchain_ollama import ChatOllama

# llm = ChatOllama(model="llama3.1:8b", base_url="http://localhost:11434")