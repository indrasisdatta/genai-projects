from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
from langchain_google_genai import ChatGoogleGenerativeAI

from helper import get_base64_image_data, get_response

load_dotenv()

# Initialize Gemini 
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=500,
    timeout=None,
    max_retries=1
)

# Streamlit initialize
st.set_page_config(page_title="Invoice Extractor")
st.header("Invoice Extractor")

# Text input
user_input = st.text_input("Input Prompt: ", key="input")
# File upload
uploaded_file = st.file_uploader("Choose Invoice Image", type=['jpg', 'jpeg', 'png'])
image = ""
# Image preview once uploaded
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded image", 
            #  use_column_width=True
            )
# Submit button
submit = st.button('Submit')    

input_prompt = """
You're an expert in understanding invoices. We will upload an invoice image so that you can answer any questions based on the uploaded image.
"""

if submit:
    image_data = get_base64_image_data(uploaded_file)
    response = get_response(llm, input_prompt, user_input, image_data)
    
    print(response)
    # Display response in UI
    st.subheader("Response:")
    st.write(response)