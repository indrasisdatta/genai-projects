from helper import dataRetrieval, dataIndexingVectorDB, augmentPrompt, generation

retriever = dataRetrieval()
prompt = augmentPrompt()
# response = generation(prompt, retriever, 'chat1', "Suggest some places to visit in Goa")

# Step 1: run a query with session_id="user1"
response1 = generation(prompt, retriever, session_id="user1", question="Hi, I am 33 years old male, who's planning a trip to Goa.")
print("Bot:", response1.content)

# Step 2: ask a follow-up without repeating context
response2 = generation(prompt, retriever, session_id="user1", question="Suggest me some offbeat destinations.")
print("Bot:", response2.content)

# Step 3: check if it remembers
response3 = generation(prompt, retriever, session_id="user1", question="What was the first state I said I want to travel?")
print("Bot:", response3.content)

