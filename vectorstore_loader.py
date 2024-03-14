from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from config import settings
import PyPDF2
import os


os.environ["PINECONE_API_KEY"] = settings.pinecone_api_key


def extract_text_from_pdf(pdf_file_path):
    '''This function extract the texts from all the pages of a specified PDF.'''
    text = ""
    with open(pdf_file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        print(f"Number of pages: {num_pages}")
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text += page.extract_text()
    print(f"Number of characters: {len(text)}")
    return text


def split_text_into_chunks(text, words_per_chunk):
    '''This function takes in the text extracted from the PDF and splits it into chunks.'''
    words = text.split()
    print(f"Number of words: {len(words)}")
    chunks = [' '.join(words[i:i+words_per_chunk]) for i in range(0, len(words), words_per_chunk)]
    return chunks


def vectorstore_loader():
    '''This function responsible for parsing a pdf and loading it's contents into the 
    Vector Store in chunks.'''
    
    pdf_file_path = "EUR_GDPR_Guidelines.pdf"  # Path to your PDF file
    words_per_chunk = 50  # Number of words per chunk

    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_file_path)

    # Split text into chunks based on word count
    chunks = split_text_into_chunks(pdf_text, words_per_chunk)

    embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_apikey)
    vectordb = PineconeVectorStore.from_texts(chunks, embeddings, index_name="virtual-assistant")
    print("Successfully loaded pinecone vector store!")



if __name__ == "__main__":
    vectorstore_loader()