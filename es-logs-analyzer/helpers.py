import json 

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

def extract_json(text):
    text = text.replace("\n", "").replace(" ", "").strip()
    try:
        # Try direct parsing
        return json.loads(text)
    except json.JSONDecodeError:
        # Extract substring between curly braces {} 
        try:
            json_part = text[text.index('{'):text.rindex('}')+1]
            print("JSON part extracted:", json_part)
            return json.loads(json_part)
        except Exception as e:
            print("Failed to extract JSON:", e)
            return None
        
def is_valid_es_query(es_obj):
    if not isinstance(es_obj, dict):
        return False 
    return "query" in es_obj