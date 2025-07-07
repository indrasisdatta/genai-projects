# Import necessary libraries

from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_groq import ChatGroq 

from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv(override=True)

import os 
import json
import pandas as pd
from helpers import examples, extract_json, is_valid_es_query

# This function creates a prompt template using Few shot prompting
# Passes the prompt to the LLM (Groq) to generate an Elasticsearch query
def initialize_llm(input_text):
    example_prompt = PromptTemplate(
        input_variables=["question", "query"],
        template="Question: {question}\nES Query: {query}"
    )
    prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix="You are an Elastisearch DSL generator. In the output, display only the ES query in a valid JSON format. Do not include any additional text or explanations.\n",
        suffix="User input: {question}\n ES Query:",
        input_variables=["question"]
    )
    # Format the prompt with the user input
    final_prompt = prompt.format(question=input_text)
    # Initialize the LLM with the Groq API key and model
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model="Llama3-8b-8192"
    )
    # Invoke the LLM with the formatted prompt
    response = llm.invoke(final_prompt)
    return response

# This function extracts the Elasticsearch query from the LLM response
# Validates it, and then queries Elasticsearch to retrieve logs
def get_es_logs(response):
    es_query = extract_json(response.content)
    if es_query and is_valid_es_query(es_query):
        print("Valid Elasticsearch query:", es_query)
    else: 
        print("Invalid Elasticsearch query.")
        return []

    # Pass the parsed ES query to Elasticsearch
    es = Elasticsearch(
        os.getenv("ES_URL"), 
        basic_auth=(os.getenv("ES_USERAME"), os.getenv("ES_PASSWORD"))
    )
    response = es.search(index=os.getenv("ES_INDEX"), body=json.dumps(es_query))
    # print(res['hits']['hits'])
    hits = response.get("hits", {}).get("hits", [])

    # Format the logs for display
    logs = []
    for i,doc in enumerate(hits, 1):
        source = doc['_source']
        logs.append({
            "#": i,
            "Message": source.get("message", "-"), 
            "Timestamp": source.get("@timestamp", "-"), 
            "Session ID": source.get("sessionId", "-"),
            "Cart ID": source.get("cartId", "-"), 
            "Order No.": source.get("orderNum", "-")  
        })
        print(f"{i}. {source}")
    return logs

import streamlit as st 

st.set_page_config(page_title="Order Logs Analyzer")
st.title("Order Logs Analyzer")

with st.form("user_form"):
    text = st.text_area("Enter your question", placeholder="e.g. List all orders which were placed on 1st July 2025")
    submitted = st.form_submit_button("Submit")
    if submitted:
        if text:
            with st.spinner("Processing your request..."):
                # Call LLM
                response = initialize_llm(text)
                # Get Elasticsearch logs
                logs = get_es_logs(response)
                # Display the logs in a table format
                print('Logs', logs)
                if logs:
                    st.dataframe(pd.DataFrame(logs).set_index("#"), use_container_width=True)
                else:
                    st.warning("No data found for the given query.")
        else:
            st.warning("Please enter a question")