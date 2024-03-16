from langchain.llms.openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains.summarize import load_summarize_chain
from langchain_pinecone import PineconeVectorStore
from openai import OpenAI
from config import settings
import utilities


def virtual_assistant():
    '''This function is the implementation of a virtual assistant that has conversational
    abilities and command-related abilities too.'''

    # Metadata and feature description of the virtual assistant
    meta_data = '''Virtual Assistant Metadata
    
    Name: Alfred

    Description: Alfred is a virtual assistant capable of analyzing websites, and holding conversation on diverse topics especially EUR GDPR.
    
    Version: 0.01
    
    Author: Michael Dubem Igbomezie

    Language Support: English
    
    Domain or Expertise: The specific domain or area of expertise in which the virtual assistant is designed to operate (e.g., finance, healthcare, customer service).
    
    List of Capabilities: Web Analyzer, YouTube Video Analyzer'''

    feature_description = '''Virtual Assitant Feature Description

    1. Web Analyzer: This function analyzes the contents of a website using user input.
    
    Parameters
    ----------
    url link (string): The url link of the website that the user want to have analysed.
    prompt (string): The user input regarding what the analysis is about.

    Returns
    ----------
    Returns the result of the analysis conducted by the LLM model.

    
    2. YouTube Video Analyzer: This function takes in video ID and analyzes the contents of the video.
    
    Parameters
    ----------
    video ID (string): The ID of the YouTube video to be analyzed.

    Returns
    ----------
    Returns the result of the analysis conducted by the LLM model.
    '''
    
    #Creates the prompt to punctuate the subtitle extracted from the given video
    messages = [
        {"role":"system","content":"you are a Virtual Assistant"},
        {"role":"system","content":meta_data},
        {"role":"system","content":feature_description}]
    
    user_input = input('Message VA: ')
    
    while user_input != 'quit':

        response = utilities.conversation_or_command(user_input)
        print(response)

        if 'Conversation' in response:
            custom_knowledge = utilities.vectorstore_similaritysearch(user_input)
            # print(f"\nCustom Knowledge: {custom_knowledge}\n")
            
            # quitAdds the prompts to the chat memory
            messages.append({"role": "system", "content": custom_knowledge},)
            messages.append({"role": "user", "content": user_input},)

            reply = utilities.conversation_component(messages)

            messages.append({"role": "assistant", "content": reply},)

            print(f"\nVirtual Assistant: {reply}\n")

            user_input = input('Message VA: ')
        else:
            feature_type = utilities.identify_features(user_input)

            if feature_type in ['Web Analyzer']:
                print(feature_type)
            else:
                print(f"Apologies, my current version isn't capable of carrying out commands.")

            user_input = input('Message VA: ')


if __name__ == "__main__":
    virtual_assistant()