import streamlit as st
import logging
import asyncio
from VectorStore import VectorStoreComponent
from Agents import TrackableAssistantAgent, TrackableUserProxyAgent
from FinAPIWrapper import FinancialModelingPrepAPI
from typing import List, Dict
from autogen import register_function

logging.basicConfig(level=logging.INFO)

config_list = [
    {
        "model": "llama3.1:latest",
        "api_type": "ollama",
        "client_host": "http://localhost:11434/",
    }
]

llm_config = {
    "seed": 42,
    "config_list": config_list,
    "temperature": 0,
}

if 'vector_store' not in st.session_state:
    st.session_state.vector_store = VectorStoreComponent(collection_name="PDFAbout")
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Tool function with proper annotations
def get_top_gainers_tool(limit: int = 5) -> List[Dict]:
    """
    Fetch the top gainers from the stock market.
    Args:
        limit: Number of top gainers to fetch (default is 5).
    Returns:
        A list of dictionaries containing top gainers' data.
    """
    api_instance = FinancialModelingPrepAPI(api_key = "MTihNQIqwXoMaKQO3UyHWO9oFuiJ58TQ".strip())
    gainers = api_instance.get_top_gainers(limit=limit)
    if not gainers:
        raise ValueError("Failed to fetch top gainers.")
    return gainers

async def query_autogen(llm_config, query, context):
    assistant = TrackableAssistantAgent(
        name="assistant",
        llm_config=llm_config,
        system_message=f"""You are a knowledgeable AI assistant specializing in finance.
        Answer financial questions based on the Context:{context} provided, offering detailed explanations, insights, and accurate information.
        You have the tool "GetTopGainers" avaiable, if you wanna retrieve the top stock gainers.
        REPLY 'TERMINATE' at the very end of your response.
        """
    )

    user_proxy = TrackableUserProxyAgent(
        name="user",
        max_consecutive_auto_reply=5,
        human_input_mode="NEVER",
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    )

    register_function(
        get_top_gainers_tool,
        caller=assistant,  # The assistant agent can suggest calls to the calculator.
        executor=user_proxy,  # The user proxy agent can execute the calculator calls.
        name="TopGainers",  # By default, the function name is used as the tool name.
        description="Gets the stock markets top gainers.",  # A description of the tool.
    )

    try:
        chat_response = await user_proxy.a_initiate_chat(assistant, message=query)
        for msg in chat_response.chat_history:
            if msg.get("name") == "assistant":
                return msg.get("content", "").replace("TERMINATE", "").strip()
        return "No response generated."
    except Exception as e:
        logging.error(f"Error in query_autogen: {str(e)}")
        raise


async def process_query_with_llama(query: str):
    """Retrieve relevant chunks from vector store and use Llama to generate a response."""
    try:
        results = st.session_state.vector_store.retrieve_relevant(query=query, limit=5)

        if not results or all(r['score'] == 0.0 for r in results):
            return "No relevant information found for your query."

        context = "\n".join(f"{result['text']}" for result in results)
        response = await query_autogen(llm_config, query, context)
        return response

    except Exception as e:
        error_message = f"Error processing query with Llama: {str(e)}"
        logging.error(error_message)
        return error_message

def main():
    st.title("Financial Advisor Bot")
    logging.info("App started")

    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        st.chat_message(role).write(content)

    if user_input := st.chat_input("Enter your query here..."):
        with st.spinner("Processing query with Llama..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                response = loop.run_until_complete(
                    process_query_with_llama(query=user_input)
                )
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response
                })

                st.chat_message("user").write(user_input)
                st.chat_message("assistant").write(response)
                
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                st.error(error_message)
                logging.error(error_message)
            finally:
                loop.close()

if __name__ == "__main__":
    main()
