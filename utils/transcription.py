import uvicorn
import cohere
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser
import base64
from utils.custom_types import ImageAnalysis

load_dotenv()
IMAGES_FOLDER = "images"


os.makedirs(IMAGES_FOLDER, exist_ok=True)

# Initialize Supabase client
supabase_client: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))


openai_model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
gemini_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.5)

def generate_llm_response(prompt: str, context: str, model: str = "openai") -> str:
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are a helpful assistant that provides information based on the given context."),
        HumanMessage(content=f"Context: {context}\n\nQuestion: {prompt}\n\nPlease provide an answer based on the given context:")
    ])

    try:
        if model == "openai":
            response = openai_model.invoke(chat_prompt.format_messages())
        elif model == "gemini":
            response = gemini_model.invoke(chat_prompt.format_messages())
        else:
            return "Invalid model specified. Please use 'openai' or 'gemini'."

        return response.content

    except Exception as e:
        print(f"Error with {model} API: {e}")
        return f"I'm sorry, but I couldn't generate a response using the {model} model at this time."



def create_image_analyzer(api_key: str):
    # Initialize the model
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0
    )

    # Create parser
    parser = PydanticOutputParser(pydantic_object=ImageAnalysis)

    format_instructions = parser.get_format_instructions()

    def analyze_image(image_bytes: bytes) -> ImageAnalysis:
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            # Create the analysis prompt
            prompt = f"""
            Analyze this image and provide the following information:
            1. All visible text in the image
            2. Your confidence level in the transcription (High, Medium, or Low)
            3. Approximate locations of text in the image
            4. Languages detected in the text
            5. Rate the overall OCR quality on a scale of 1-10

            {format_instructions}
            """

            # Create a message with the image
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    },
                ]
            )

            # Get response from model
            response = model.invoke([message])
            print(response.content)

            # Parse the response into our structured format
            result = parser.parse(response.content)
            return result

        except Exception as e:
            print(e)
            raise Exception(f"Error analyzing image: {str(e)}")

    return analyze_image