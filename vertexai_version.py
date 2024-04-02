import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content
from google.oauth2 import service_account

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def generate_text():
    credentials_path = 'magicweb-solution-62f543e62c62.json'

    # Create credentials using google-auth
    credential = service_account.Credentials.from_service_account_file(credentials_path)

    # Initialize Vertex AI
    vertexai.init(project='magicweb-solution', location='us-central1', credentials=credential)
    # Load the model
    multimodal_model = GenerativeModel("gemini-pro")
    # Query the model
    messages = [Content(
                  role="user",
                  parts=[
                      Part.from_text("Who is the president of US?"),
                  ],
                ),
                Content(
                  role="model",
                  parts=[
                      Part.from_text("Joe Biden"),
                  ],
                ),
                Content(
                  role="user",
                  parts=[
                      Part.from_text("What was the first question I asked?"),
                  ],
                )
              ]
    response = multimodal_model.generate_content(messages)
    print(response.text)


if __name__ == "__main__":
    generate_text()
