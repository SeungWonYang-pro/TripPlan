GOOGLE_API_KEY="API_KEY"
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
import os
os.environ["OPENAI_PROXY"] = "http://127.0.0.1:8000"
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
    query =  "I want to go to "+country+" for " + duration + " days.  I am interested in "+ style +". Please provide a detailed day-by-day itinerary without any bonuses, tips and Note."
    print(query)
    plans =  getPlan(query)
    return {'plan': plans}

def getPlan(query):
    import google.generativeai as genai
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    plans = model.generate_content(query).candidates[0].content.parts[0].text
    return plans

