from langchain.llms.openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains.summarize import load_summarize_chain
from langchain_pinecone import PineconeVectorStore
from openai import OpenAI
from config import settings
import utilities, variable, json
import telebot


def manual_virtual_assistant():
    '''This function is the implementation of a virtual assistant that has conversational
    abilities and command-related abilities too.
    
    This version of the virtual assistant is manual mainly because the function calling element
    is manually defined and identified sing customed finetune GPT models'''

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
                analysis_result = utilities.execute_function_wrapper(funct_dict[feature_type], param_value)

                return analysis_result
            else:
                #if feature being asked for by user isn't in list of functions then, outputs the message below.
                print(f"Apologies, my current version isn't capable of carrying out this specific commands.")

            user_input = input('Message VA: ')


def automated_virtual_assistant():
    '''This function is the implementation of a virtual assistant that has conversational
    abilities and command-related abilities too.
    
    This version of the virtual assistant is automated mainly because the function calling element
    is implemented through GPT's in-built function identification feature.'''

    client = OpenAI(
        # This is the default and can be omitted
        api_key=settings.openai_apikey,)
    
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
        {"role":"system","content":"you are a Virtual Assistant. Pleaase do not make any assumption about what value to plug into any function. If it is not explicitly stated, ask the user to input it."},
        {"role":"system","content":meta_data},
        {"role":"system","content":feature_description}]
    
    user_input = input('Message VA: ')
    
    while user_input != 'quit':

        custom_knowledge = utilities.vectorstore_similaritysearch(user_input)
        # print(f"\nCustom Knowledge: {custom_knowledge}\n")
        
        # Adds the custom knowledge and user input to the chat memory
        messages.append({"role": "system", "content": custom_knowledge},)
        messages.append({"role": "user", "content": user_input},)

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo-0125",
            temperature=0.0,
            tools=variable.tools,
            tool_choice="auto",  # auto is default, but we'll be explicit
        )

        #Response is extracted. 
        response_message = chat_completion.choices[0].message
        #If the user input is for a function execution, then tools_call is not None and response is None.
        tool_calls = response_message.tool_calls
        #If the user input is for conversation only, then tools_call is None and response is not None.
        response = response_message.content

        if tool_calls:
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = {
                "web_crawler_feature": utilities.web_crawler_feature,
            }  # only one function in this example, but you can have multiple

            messages.append(response_message)  # extend conversation with assistant's reply
            # print(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                print(function_args)

                #If GPT hallucination gets too much, then append the manual argument extraction here.
                
                # function_response = function_to_call(
                #     location=function_args.get("location"),
                #     unit=function_args.get("unit"),
                # )

                #Appending the response for previously identified functions to the chat memory is important before chat continues so system has the accurate context for the funciton identified, or else it will throw back an error message in the next prompt.
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": "function_response",
                    }
                )  # extend conversation with function response

            second_response = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=messages,
            )  # get a new response from the model where it can see the function response
            # return second_response
        elif response:
            messages.append({"role": "assistant", "content": response},)
            print(response)

        user_input = input('Message VA: ')


#Telegram Bot
BOT_TOKEN = settings.telegram_token
bot = telebot.TeleBot(BOT_TOKEN)


def telegram_bot(messages, user_input):
    '''This function is the implementation of a virtual assistant that has conversational
    abilities and command-related abilities too.
    
    This version of the virtual assistant is automated mainly because the function calling element
    is implemented through GPT's in-built function identification feature.'''

    client = OpenAI(
        # This is the default and can be omitted
        api_key=settings.openai_apikey,)

    custom_knowledge = utilities.vectorstore_similaritysearch(user_input)
    # print(f"\nCustom Knowledge: {custom_knowledge}\n")
    
    # Adds the custom knowledge and user input to the chat memory
    messages.append({"role": "system", "content": custom_knowledge},)
    messages.append({"role": "user", "content": user_input},)

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo-0125",
        temperature=0.0,
        tools=variable.tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )

    #Response is extracted. 
    response_message = chat_completion.choices[0].message
    #If the user input is for a function execution, then tools_call is not None and response is None.
    tool_calls = response_message.tool_calls
    #If the user input is for conversation only, then tools_call is None and response is not None.
    response = response_message.content

    if tool_calls:
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "web_crawler_feature": utilities.web_crawler_feature,
        }  # only one function in this example, but you can have multiple

        chatcompletion_data = {
            "content": response_message.content,
            "role": response_message.role,
            # "function_call": response_message.function_call,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "function": {
                        "arguments": tool_call.function.arguments,
                        "name": tool_call.function.name
                    },
                    "type": tool_call.type
                }
                for tool_call in response_message.tool_calls
            ]
        }
        messages.append(chatcompletion_data)  # extend conversation with assistant's reply
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            print(function_args)

            #If GPT hallucination gets too much, then append the manual argument extraction here.
            
            # function_response = function_to_call(
            #     location=function_args.get("location"),
            #     unit=function_args.get("unit"),
            # )

            #Appending the response for previously identified functions to the chat memory is important before chat continues so system has the accurate context for the funciton identified, or else it will throw back an error message in the next prompt.
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": "function_response",
                }
            )  # extend conversation with function response

        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        response = f"tool_call_id: {tool_call.id}, role: tool, name: {function_name}"
        return messages, response
    elif response:
        messages.append({"role": "assistant", "content": response},)
        return messages, response


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    path = f"messages.json"

    print(message.text)

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        messages = json.load(file)

    messages, response = telegram_bot(messages, str(message.text))

    # Convert dictionary to JSON string
    overall_messages = json.dumps(messages, indent=4)  # Use indent for pretty formatting

    # Save JSON string to a file
    with open(f"messages.json", "w") as json_file:
        json_file.write(overall_messages)

    bot.reply_to(message, response)


if __name__ == "__main__":
    # manual_virtual_assistant()
    # automated_virtual_assistant()
    bot.infinity_polling()