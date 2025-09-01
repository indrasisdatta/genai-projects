import pandas as pd 
from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_ollama import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain_community.chat_models import ChatOllama
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time 

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# STEP 1: Indexing (Store vector embedding of CSV file in local Vector store file)
def dataIndexingVectorDB(type):
    # Load CSV file 
    loader = CSVLoader(file_path="travel-dataset.csv", csv_args={"delimiter": ","})
    documents = loader.load()

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    # Create Embedding and store in Vector store 
    vectorstore = None
    if type == 'faiss':
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local("./vectordb_faiss")
    elif type == 'chroma':
        vectorstore = Chroma.from_documents(chunks, embedding=embeddings, persist_directory="./vectordb_chroma")    

    return vectorstore

# STEP 2: Retrieval
def dataRetrieval(type):
    vectorstore = None
    if type == 'faiss':
        vectorstore = FAISS.load_local(
            "./vectordb_faiss", 
            embeddings=embeddings, 
            allow_dangerous_deserialization=True
        )
    elif type == 'chroma':
        vectorstore = Chroma(
            persist_directory="./vectordb_chroma", 
            embedding_function=embeddings
        )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    # print(retriever.invoke("Suggest some places to visit in Goa"))
    return retriever

# STEP 3: Augmentation
def augmentPrompt():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You're a helpful travel planner assistant. Answer the user's queries to the best of your ability using the following context: \n {context}"),
        MessagesPlaceholder(variable_name="messages")
    ])
    return prompt    

# STEP 4: Generation 
def generation(prompt, retriever, session_id: str, question: str):
    config = {"configurable": {"session_id": session_id}}

    context = get_context_from_retriever(retriever, question)

    model = ChatOllama(model="llama3.1")
    chain = prompt | model
    with_message_history = RunnableWithMessageHistory(chain, get_session_history, input_messages_key="messages")
    response = with_message_history.invoke(
        {
            "messages": [HumanMessage(content=question)],
            "context": context
        },
        config=config
    )  
    return response


# ----------------------------------------------------------
# Other helper functions
# ----------------------------------------------------------
store = {}
def get_session_history(session_id: str)->BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def get_context_from_retriever(retriever, question):
    docs = retriever.invoke(question)
    context = "\n".join([doc.page_content for doc in docs])
    return context

def benchmark_latency(store, queries, k=5):
    times = []
    for q in queries:
        start = time.time()
        _ = store.similarity_search(q, k=k)
        times.append(time.time() - start)
    return sum(times)/len(times)

# Since FAISS Flat = ground truth, use its results as baseline.
def recall_at_k(faiss_store, store, queries, k=5):
    total = 0
    for q in queries:
        faiss_res = faiss_store.similarity_search(q, k=k)
        faiss_ids = [d.page_content for d in faiss_res]

        test_res = store.similarity_search(q, k=k)
        test_ids = [d.page_content for d in test_res]

        # Intersection / k
        overlap = len(set(faiss_ids) & set(test_ids)) / k
        total += overlap
    return total/len(queries)

# Compare performance metrics
def comparePerformanceMetrics(querytexts):

    faiss_vectorstore = dataIndexingVectorDB('faiss')
    chroma_vectorstore = dataIndexingVectorDB('chroma')

    faiss_latency = benchmark_latency(faiss_vectorstore, querytexts)
    print(f"FAISS Latency = {faiss_latency}")
    chroma_latency = benchmark_latency(chroma_vectorstore, querytexts)
    print(f"Chroma Latency = {chroma_latency}")

    chroma_recall = benchmark_latency(faiss_latency, querytexts)
    print(f"Chroma Recall = {chroma_recall}")


comparePerformanceMetrics([
    "Places to visit in Goa",
    "What are the best sea beaches?",
    "What are some budget friendly tour plans in Goa?"
])