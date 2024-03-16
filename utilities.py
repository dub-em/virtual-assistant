from langchain.llms.openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains.summarize import load_summarize_chain
from langchain_pinecone import PineconeVectorStore
from openai import OpenAI
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from wrapt_timeout_decorator import timeout
import concurrent.futures
from config import settings


def conversation_or_command(information):
    '''Function is responsible for querying the GPT-3.5 model for analysis of a given content.'''
    from openai import OpenAI

    client = OpenAI(
        # This is the default and can be omitted
        api_key=settings.openai_apikey,)

    #Prompt engineering message to be fed to the GPT model.
    messages_1 = [{"role":"system","content":"you are a text analyst assistant. Given a text input, respond with only 'Conversation' or 'Command'."}]

    #Creates the prompt to check for the most similar column
    prompt_1 = f"{information}"
    prompt_2 = f"Given this input above from the user, would you classify this request under 'Conversation' or 'Command'"

    #Adds the prompts to the chat memory
    messages_1.append({"role": "user", "content": prompt_1},)
    messages_1.append({"role": "user", "content": prompt_2},)

    
    #GPT model is triggered and response is generated.
    chat_completion = client.chat.completions.create(
        messages=messages_1,
        model="ft:gpt-3.5-turbo-1106:personal:conv-or-comm:92lF8Njb",
        # model="gpt-3.5-turbo-1106",
        temperature=0.0,) 

    #Response is extracted
    response = chat_completion.choices[0].message.content
    return (response)


#Conversation related features
def conversation_component(messages):
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
    '''This function conducts a similarity search in a Vector Store using the user input in order to 
    aid the GPT model gain access to custom knowledge'''

    embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_apikey)
    vectorstore = PineconeVectorStore(index_name="virtual-assistant", embedding=embeddings)

    docs = vectorstore.similarity_search(user_input, k=1)
    information = docs[0].page_content

    return information


#Command related features
def identify_features(information):
    '''Function is responsible for querying the GPT-3.5 model for analysis of a given content.'''
    from openai import OpenAI

    client = OpenAI(
        # This is the default and can be omitted
        api_key=settings.openai_apikey,)

    #Prompt engineering message to be fed to the GPT model.
    messages_1 = [{"role":"system","content":"You are a text analyst assistant. Given a text input from a user, categorize the input under one of the following features [Web Analyzer, None]"}]

    #Creates the prompt to check for the most similar column
    prompt_1 = f"{information}"
    prompt_2 = f"Given this input above from the user, please classify this request under one of the given given features in this list [Web Analyzer, None]."

    #Adds the prompts to the chat memory
    messages_1.append({"role": "user", "content": prompt_1},)
    messages_1.append({"role": "user", "content": prompt_2},)

    
    #GPT model is triggered and response is generated.
    chat_completion = client.chat.completions.create(
        messages=messages_1,
        model="ft:gpt-3.5-turbo-1106:personal:identify-features:93RqU9Ph",
        # model="gpt-3.5-turbo-1106",
        temperature=0.0,) 

    #Response is extracted
    response = chat_completion.choices[0].message.content
    return (response)


def content_extractor(url_link):
    '''This function extracts all the content from a given page in a website.'''
    
    #Creates a fake user agent to prevent websites from blocking the bot
    options = Options()
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-cookies")
    #options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(r'C:/Users/hp/Documents/Our Documents/Personal Development/Projects/Client Projects/Honordex (Upwork)/honordex-dei-project/chromedriver-win64_119/chromedriver.exe',options=options)

    print(url_link)
    driver.get(url_link)

    #Extract all elements on the company home page
    all_elements = driver.find_elements(By.XPATH, '//*')
    print(len(all_elements))

    #Extracts specific properties of the elements extracted
    element_content, element_tag = [], []
    for element in all_elements:
        try:
            element_content.append(element.get_attribute('innerText')) #Extracts the text associated with the element
        except:
            element_content.append('')
        try:
            element_tag.append(element.get_attribute('tagName')) #Extracts the tag associated with the element for filtering
        except:
            element_tag.append('')
    #print(len(element_content), len(element_tag))       

    driver.quit()
    print('All contents extracted!')
    return element_content, element_tag
    

def etl_extrct_mthd(url_link):
    '''This first method extracts all the contents of the website and analyses them indivdually.
    This takes more time but is more accurate in result.'''

    #Contents, links and element tage name extraction from the given url or page
    content, tag_names = content_extractor(url_link)
    
    #list of tag names to remove from the set of elements to analyse to reduce computation time.
    tag_name_list = ['HEAD', 'HTML', 'META', 'LABEL', 'SCRIPT', 'STYLE', 'FORM', 'TIME', 'BR',
                     'INPUT', 'BODY', 'NOSCRIPT', 'IMG', 'H1','DIV','HEADER','SPAN','LINK','FOOTER',
                     'BUTTON','TITLE','NAV'
                    ]
    
    #The indices with these tag names are identified along with element with no content
    index_to_drop = []
    for i in range(len(tag_names)):
        if (tag_names[i] in tag_name_list) | (content[i] == '') | ('NoneType' in str(type(content[i]))):# | (len(set(content[i].split())) <= 1):
            index_to_drop.append(i)

    #Using the marked indices, elements are filtered from the set of elements
    content_1 = [content[i] for i in range(len(content)) if i not in index_to_drop]
    tag_names_1 = [tag_names[i] for i in range(len(tag_names)) if i not in index_to_drop]
    print(len(content_1), len(tag_names_1))
    return content_1


@timeout(5)  #Sets the timeout duration in seconds (e.g., 5 seconds)
def gpt_analyst(information):
    '''Function is responsible for querying the GPT-3.5 model for analysis of a given content.'''
    from openai import OpenAI

    client = OpenAI(
        # This is the default and can be omitted
        api_key=settings.openai_apikey,)
    
    #Prompt engineering message to be fed to the GPT model.
    messages_1 = []

    #Creates the prompt to check for the most similar column
    prompt_1 = f"{information[1]}"
    prompt_2 = f"{information[0]}"

    #Adds the prompts to the chat memory
    messages_1.append({"role": "user", "content": prompt_1},)
    messages_1.append({"role": "user", "content": prompt_2},)

    
    #GPT model is triggered and response is generated.
    chat_completion = client.chat.completions.create(
        messages=messages_1,
        model="gpt-3.5-turbo",
        temperature=0.0,) 

    #Response is extracted
    response = chat_completion.choices[0].message.content
    return (information[1], response)


def web_crawler_feature(user_input):
    '''This function executes a kind of overview analysis of the content to filter which contents should be
    analysed and which should be discarded.
    
    Parameters
    ----------
    url link (string): The url link of the website that the user want to have analysed.
    prompt (string): The user input regarding what the analysis is about.

    Returns
    ----------
    Returns the result of the analysis conducted by the LLM model.'''

    url_link = user_input['url_link']
    prompt = user_input['prompt']

    web_contents = etl_extrct_mthd(url_link)
    web_contents = [(prompt, content) for content in web_contents]
    
    #In-function dictionary created to hold the needed contents to be return to the overall global dictionary.
    gpt3_responses, content_lists = [], []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        arguments = web_contents
        futures = [executor.submit(gpt_analyst, arg) for arg in arguments]

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if "yes" in result[1].lower():
                    gpt3_responses.append(result[1])
                    content_lists.append(result[0])
            except:
                continue

    #Remaining elements are appended to the temporary dictionary to sent to the global dictionary.
    for i in range(len(gpt3_responses)):
        print(f"{gpt3_responses[i]}: {content_lists[i]}")
            
    print(f"Website analysis done!")
    #return extracted_analysed_element