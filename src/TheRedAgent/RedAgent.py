import logging
import panel as pn
import autogen
from autogen import register_function
from typing import List, Dict
from VectorStore import VectorStoreComponent
from Agents import TrackableAssistantAgent
from FinAPIWrapper import FinancialModelingPrepAPI

logging.basicConfig(level=logging.INFO)

pn.extension(design="material")

if "vector_store" not in pn.state.cache:
    pn.state.cache["vector_store"] = VectorStoreComponent(collection_name="PDFAbout")

conversation_terminated = False
initiate_chat_task_created = False

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


def get_top_gainers_tool(limit: int = 5) -> List[Dict]:
    api_instance = FinancialModelingPrepAPI(
        api_key="PROVIDEAPIKEYHERE".strip()
    )
    gainers = api_instance.get_top_gainers(limit=limit)
    if not gainers:
        return []
    return gainers

def get_vector_context_tool(query: str) -> str:
    """Retrieve relevant context from the vector store for the given query."""
    limit = 5
    results = pn.state.cache["vector_store"].retrieve_relevant(query=query, limit=limit)
    context_text = "\n".join(r["text"] for r in results if r["score"] != 0.0)
    if not context_text.strip():
        context_text = "No relevant information found."
    return context_text


SYSTEM_MESSAGE_TEMPLATE_PLANNER = """You are the planner.
You have these tools available via the assistant:
1. VectorContext(query:str) -> returns relevant context from the vector store.
2. TopGainers(limit:int=5) -> returns the top stock gainers.

Rules:
- If the user wants stock gainers and also wants advice from the context, instruct the assistant to:
  1. Call the VectorContext tool first to get relevant advice context.
  2. Call the TopGainers tool once to get stock gainers.
  3. Combine both results into a final answer and terminate.
- If the user only wants context-based advice (no stock gainers), instruct the assistant to call VectorContext and then finalize.
- If the user only wants stock gainers without context, instruct the assistant to call TopGainers once and finalize.
- Do not repeat the same instruction multiple times. Once you have given a sequence of instructions, do not give new or repeated instructions.
- If the assistant doesn't follow correctly, do not cause loops. Either wait or finalize by saying "No further actions needed."
"""

SYSTEM_MESSAGE_TEMPLATE_ASSISTANT = """You are a knowledgeable AI assistant specializing in finance.
You have two tools available:
- VectorContext(query:str) -> returns relevant context text.
- TopGainers(limit:int=5) -> returns a list of top gaining stocks.

Rules:
- Follow the planner's instructions exactly.
- If instructed to call VectorContext, do so exactly once per request and store the result.
- If instructed to call TopGainers, do so exactly once per request and store the result.
- After obtaining the required tool results, combine them into a final answer. If you have context and gainers, integrate them together into helpful advice.
- Always end your final message with 'TERMINATE'.
- If the planner asks for repeated actions already done, simply state you've done it and finalize with 'TERMINATE'.
- Do not loop or wait indefinitely. Execute instructions once and finalize.
"""

SYSTEM_MESSAGE_TEMPLATE_TOOL_AGENT = """You are the tool agent.
You execute tools only when asked by the assistant.
Return results directly to the assistant.
If asked again for a completed request, state that it has been done and you cannot repeat.
"""

SYSTEM_MESSAGE_TEMPLATE_USER = """You are the human user.
Provide a query and wait for a response. Once you receive a final answer ending with 'TERMINATE', consider the conversation complete.
"""

user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message=SYSTEM_MESSAGE_TEMPLATE_USER,
    code_execution_config={
        "last_n_messages": 2,
        "work_dir": "groupchat",
        "use_docker": False
    },
    human_input_mode="ALWAYS",
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
)

planner = TrackableAssistantAgent(
    name="planner",
    llm_config=llm_config,
    system_message=SYSTEM_MESSAGE_TEMPLATE_PLANNER,
)

assistant = TrackableAssistantAgent(
    name="assistant",
    llm_config=llm_config,
    system_message=SYSTEM_MESSAGE_TEMPLATE_ASSISTANT,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
)

tool_agent = TrackableAssistantAgent(
    name="tool_agent",
    llm_config=llm_config,
    system_message=SYSTEM_MESSAGE_TEMPLATE_TOOL_AGENT,
    human_input_mode="NEVER",
)

register_function(
    get_top_gainers_tool,
    caller=assistant,
    executor=tool_agent,
    name="TopGainers",
    description="Gets the top gaining stocks from the market."
)

register_function(
    get_vector_context_tool,
    caller=assistant,
    executor=tool_agent,
    name="VectorContext",
    description="Retrieves relevant context from the vector store based on the query."
)

groupchat = autogen.GroupChat(
    agents=[user_proxy, planner, assistant, tool_agent], 
    messages=[], 
    max_round=20
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

chat_interface = pn.chat.ChatInterface()
chat_interface.send("Send a message!", user="System", respond=False)

avatar = {
    "assistant": "🤖",
    "User_proxy": "👨‍💼",
    "planner": "🗓",
    "tool_agent": "🛠",
    "System": "💻",
}

def print_messages(recipient, messages, sender, config):
    msg = messages[-1]
    message_user = msg.get("name", msg.get("role", "System"))
    message_content = msg.get("content", "")
    user_avatar = avatar.get(message_user, "")
    chat_interface.send(
        message_content,
        user=message_user,
        avatar=user_avatar,
        respond=False,
    )
    return False, None

for ag in [user_proxy, planner, assistant, tool_agent]:
    ag.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages,
        config={"callback": None},
    )

def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    global initiate_chat_task_created, conversation_terminated

    if conversation_terminated:
        chat_interface.send("The conversation has ended.", user="System", respond=False)
        return

    if not initiate_chat_task_created:
        initiate_chat_task_created = True
        user_proxy.initiate_chat(manager, message=contents)
    else:
        chat_interface.send("Waiting for the conversation to proceed...", user="System", respond=False)

chat_interface.callback = callback
chat_interface.servable()
