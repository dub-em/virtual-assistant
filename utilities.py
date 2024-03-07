from langchain.llms.openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains.summarize import load_summarize_chain
from langchain_pinecone import PineconeVectorStore
from openai import OpenAI
from config import settings


def gpt_punctuator(messages):
    '''Function is responsible for querying the GPT-3.5 model for analysis of a given content.'''

    client = OpenAI(
        # This is the default and can be omitted
        api_key=settings.openai_apikey,)

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
        temperature=0.0,)
    
    #Response is extracted
    response = chat_completion.choices[0].message.content
    return (response)

    
def vectorstore_similaritysearch(user_input):

    embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_apikey)
    vectorstore = PineconeVectorStore(index_name="virtual-assistant", embedding=embeddings)

    docs = vectorstore.similarity_search(user_input, k=1)
    information = docs[0].page_content

    return information