from langchain.llms.openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains.summarize import load_summarize_chain
from langchain_pinecone import PineconeVectorStore
from openai import OpenAI
from config import settings
import utilities
import variable


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
            
            # Adds the custom knowledge and user input to the chat memory
            messages.append({"role": "system", "content": custom_knowledge},)
            messages.append({"role": "user", "content": user_input},)

            # Sends the chat memory to GPT to generate a response
            reply = utilities.conversation_component(messages)

            messages.append({"role": "assistant", "content": reply},) #adds reposne to chat memory

            print(f"\nVirtual Assistant: {reply}\n")

            user_input = input('Message VA: ') #prompts more user input
        else:
            #if user input is for a command execution, identify the feature linked to the user input
            feature_type = utilities.identify_features(user_input)

            if feature_type in ['Web Analyzer']:
                #if identified feature is in list of user inputs extract the parameters needed to execute that feature from the user input
                print(feature_type)
                params = [variable.feature_param,
                          variable.feature_param_extract_prompt,
                          variable.feature_param_request,
                          feature_type,
                          user_input
                          ] #creates list of prompt dictionaries and other variables
                
                # Extracts the needed arguments for the identified function, including prompting user to input any arguments not provided in their original input.
                param_value = utilities.feature_param_extract(params)

                # Dictionary containing function titles and their respective methods
                funct_dict = {'Web Analyzer':utilities.web_crawler_feature}

                # Automatically executes the identfied function and the extracted arguments
                # analysis_result = utilities.execute_function_wrapper(funct_dict[feature_type], param_value)

                # return analysis_result
            else:
                #if feature being asked for by user isn't in list of functions then, outputs the message below.
                print(f"Apologies, my current version isn't capable of carrying out this specific commands.")

            user_input = input('Message VA: ')


if __name__ == "__main__":
    virtual_assistant()