import streamlit as st
import logging
import time
from VectorStore import VectorStoreComponent
import ollama
from alpha_vantage.timeseries import TimeSeries

# Set up logging
logging.basicConfig(level=logging.INFO)

API_KEY = "N3J457GUET9DGQK2"

def get_top_stock_gainers():
    """Fetch the top 5 stock gainers based on percentage change."""
    try:
        ts = TimeSeries(key=API_KEY, output_format='pandas')
        
        stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK.B", "JPM", "V"]
        gainers = []

        for stock in stocks:
            data, meta_data = ts.get_daily(symbol=stock, outputsize='compact')
            latest_close = data['4. close'].iloc[0]
            previous_close = data['4. close'].iloc[1]
            percent_change = ((latest_close - previous_close) / previous_close) * 100
            gainers.append({
                "symbol": stock,
                "latest_close": latest_close,
                "percent_change": percent_change
            })

        top_gainers = sorted(gainers, key=lambda x: x["percent_change"], reverse=True)[:5]
        return top_gainers

    except Exception as e:
        logging.error(f"Error fetching stock gainers: {str(e)}")
        return [{"error": "Unable to fetch stock gainers at this time."}]

if 'vector_store' not in st.session_state:
    st.session_state.vector_store = VectorStoreComponent(collection_name="PDFAbout")
if 'messages' not in st.session_state:
    st.session_state.messages = []
    

def getTestDataFromAPISTUFFLOL():
    return "This is a test"

MODEL = "llama3.1:latest"

def query_llama(model, query, context):
    """Query the Llama model synchronously."""
    try:
        messages = [
            {
                "role": "system",
                "content": "You are an AI assistant. Use the provided context to answer questions accurately and concisely."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }
                
        ] 
    
        tools = [
            {
                'type': 'function',
                'function': {
                    'name': 'getTestDataFromAPISTUFFLOL',
                    'description': 'Get test data from API',
                    'parameters': {
                        'type': 'object',
                        'properties': {},
                        'required': [],
                    },
                },
            }
        ]
        
        
        response = ollama.chat(model=model, messages=messages)
        return response.get("message", {}).get("content", "").strip() 
    except Exception as e:
        logging.error(f"Error querying Llama: {str(e)}")
        return "An error occurred while processing your query."

def process_query_with_llama(query: str):
    """Retrieve relevant chunks from vector store and use Llama to generate a response."""
    try:
        results = st.session_state.vector_store.retrieve_relevant(query=query, limit=5)
        if not results or all(r['score'] == 0.0 for r in results):
            return "No relevant information found for your query."

        context = "\n".join(f"{result['text']}" for result in results)

        response_message = query_llama(MODEL, query, context)
        return response_message
    except Exception as e:
        logging.error(f"Error processing query with Llama: {str(e)}")
        return "An error occurred while processing your query."


def main():
    st.title("Financial advisor bot")
    logging.info("App started")

    if prompt := st.chat_input("Enter your query here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        logging.info(f"User input: {prompt}")

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                start_time = time.time()
                logging.info("Processing query with Llama and vector store results")

                with st.spinner("Processing query with Llama..."):
                    try:
                        response_message = process_query_with_llama(query=prompt)
                        duration = time.time() - start_time
                        response_message_with_duration = f"{response_message}\n\nDuration: {duration:.2f} seconds"

                        st.session_state.messages.append({"role": "assistant", "content": response_message_with_duration})
                        st.write(response_message_with_duration)
                        logging.info(f"Response: {response_message}, Duration: {duration:.2f} s")

                    except Exception as e:
                        st.session_state.messages.append({"role": "assistant", "content": str(e)})
                        st.error("An error occurred while processing your query.")
                        logging.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
