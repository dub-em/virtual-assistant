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

    #Creates the prompt to punctuate the subtitle extracted from the given video
    messages = [
        {"role":"system","content":"you are a virtual assistant"}]
    
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
            print(f"Apologies, my current version isn't capable of carrying out commands.")

            user_input = input('Message VA: ')


if __name__ == "__main__":
    virtual_assistant()