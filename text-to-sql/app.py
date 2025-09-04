from helpers import connect_db, get_gemini_response, get_prompt
import google.generativeai as genai
import os
import streamlit as st

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

db = connect_db()

print(db)

st.set_page_config(page_title="SQL Chat")
st.header("Retrieve data from SQL using Gemini")
question = st.text_input("Input: ", key="input")
submit = st.button("Submit")

if submit:
    response = get_gemini_response(question, get_prompt()[0])
    print(response)
    st.subheader("Response: ")
    st.write(response)