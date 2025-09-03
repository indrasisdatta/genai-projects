import base64
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Convert uploaded image file to base64 string
def get_base64_image_data(uploaded_file):
    if uploaded_file is not None:
        file_buffer = uploaded_file.getvalue()
        base64_encoded = base64.b64encode(file_buffer)
        base64_string = base64_encoded.decode('utf8')
        extension = 'png'
        if '.' in uploaded_file.name: 
            extension = uploaded_file.name.split('.')[-1].lower()
        if extension == 'jpg':  
            extension = 'jpeg'
        return f"data:image/{extension};base64,{base64_string}"

    else: 
        raise FileNotFoundError("No file uploaded")
    
# Get final response from LLM
def get_response(llm, input_prompt, user_input, image_data):
    prompt = ChatPromptTemplate.from_messages([
        ('system', input_prompt),
        ("human", [
            {
                "type": "text",
                "text": user_input,
            },
            {
                "type": "image_url", 
                "image_url": {
                    "url": image_data
                }
            }
        ])
    ])
    parser = StrOutputParser()

    chain = prompt | llm | parser 

    response = chain.invoke({
        "image_data": image_data
    })
    return response