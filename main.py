GOOGLE_API_KEY="APIKEY"
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

from fastapi import FastAPI, Depends, Request, Response, WebSocket
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from fastapi.security import OAuth2PasswordRequestForm

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException

from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session


from schema import InfoSchema
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
        
def run():
    import uvicorn
    uvicorn.run(app)

templates = Jinja2Templates(directory="templates")

if __name__ == "__main__":
    run()
    
@app.get("/")
def get_root(request: Request):
    return templates.TemplateResponse("home.html",{"request":request})


@app.post('/token')
def makePlan(response: Response, data: InfoSchema):
    country= data.country
    duration= data.duration
    style = data.style
    query =  "I want to go to " + country +". And I'm interesting in " + style + " Can you make some plan for "+duration+" days? "

    plans =  getPlan(query)
    return {'plan': plans}

def getPlan(query):
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
            "You are a great chatbot planning detail things that client needs with some urls for making some reservation or getting information."
    ),
        HumanMessagePromptTemplate.from_template("{question}")
        ]
    )

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
    plans = []
    for chunk in rag_chain.stream(query):
        plans.append(str(chunk))
    return plans

