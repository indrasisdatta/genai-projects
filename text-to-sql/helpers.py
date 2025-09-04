from langchain.sql_database import SQLDatabase 
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import google.generativeai as genai
from sql_mapping import sql_mapping_list

load_dotenv(override=True)

def connect_db():
    print("DB connection string:") 
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    conn_str = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"
    print(conn_str)
    
    return SQLDatabase(create_engine(conn_str))

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content([prompt, question])
    return response.text

def get_prompt():
    sql_str = ''
    n = 1
    for dict in sql_mapping_list:
        print(dict)
        sql_str += f"Question {str(n)}: {dict['Question']}, SQL: {dict['SQL']}\n"
    prompt = [
        f"""
        You are an expert in converting English questions to SQL Query. 
        Consider the following tables from SQL Database to answer the questions:
        1. sites 
        2. site_subscription
        3. site_manager 
        4. site_payment_history
        {sql_str}
        If you're unable to answer, please mention "Couldn't find any relevant data".
        """
    ]
    return prompt
