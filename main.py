import bs4
from operator import itemgetter
from langchain import hub
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings import GooglePalmEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.chat_models import ChatGooglePalm
from langchain.schema.runnable.history import RunnableWithMessageHistory
from langchain.prompts import ChatPromptTemplate,SystemMessagePromptTemplate,HumanMessagePromptTemplate


loader = WebBaseLoader(web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",), bs_kwargs=dict(parse_only=bs4.SoupStrainer(class_=("post-content", "post-title", "post-header"))),)
raw_documents = loader.load()

# Text Split
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

splits = text_splitter.split_documents(raw_documents)

# Embedding
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=GooglePalmEmbeddings(google_api_key=GOOGLE_API_KEY)
)

# Retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k":6}
)


# Generate
llm = ChatGooglePalm(google_api_key=GOOGLE_API_KEY)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

from langchain.prompts import (ChatPromptTemplate,SystemMessagePromptTemplate,HumanMessagePromptTemplate)
prompt = ChatPromptTemplate(
messages=[
    SystemMessagePromptTemplate.from_template(
        "You are a great chatbot planning detail things that client needs. And you have to give some url for making some reservation or getting information."
  ),
    HumanMessagePromptTemplate.from_template("{question}")
    ]
)

country = input("Where are you want to visit? ")
days = input("How many days do you travel? ")
preference = input("What are your travel preferences? (Ex. Activity, Food, History) ")
query =  "I want to go to " + country +". And I'm interesting in " + preference + " Can you make some plan for "+days+" days? "
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()    }
    | prompt
    | llm
    | StrOutputParser()
)
# ===========================================

print("## Generated string ##")
for chunk in rag_chain.stream(query):
    print(chunk, end="", flush=True)

