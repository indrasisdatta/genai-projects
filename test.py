from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
import json

# Example template for each few-shot sample
example_prompt = PromptTemplate(
    input_variables=["question", "query"],
    template="Question: {question}\nES Query: {query}"
)

# Few-shot examples
examples = [
    {
        "question": "Show me the cart details for Cart123",
        "query": """{{ "query": {{ "match": {{ "cartId": "Cart123" }} }} }}"""
    },
    {
        "question": "What are the orders placed between June 20 to June 25 2025?",
        "query": """{{ "query": {{ "bool": {{ "must": [
            {{ "range": {{ "@timestamp": {{ "gte": "2025-06-20T00:00:00Z", "lte": "2025-06-25T23:59:59Z" }} }} }},
            {{ "exists": {{ "field": "orderNum" }} }}
        ] }} }} }}"""
    }
]


# Create the FewShotPromptTemplate
prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="You are an Elasticsearch DSL generator.",
    suffix="Question: {question}\nES Query:",
    input_variables=["question"]
)

# Format with new input (no query passed!)
# final_prompt = prompt.format(
#     question="Show me the details of cart id CART-A1F7"
# )

final_prompt = prompt.invoke({
    "question": "Show me the details of cart id CART-A1F7"
})
print(final_prompt)
