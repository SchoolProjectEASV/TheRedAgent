import logging
import panel as pn
import autogen
from autogen import register_function
from VectorStore import VectorStoreComponent
from Agents import TrackableAssistantAgent, TrackableConversableAgent
from tools import Tools
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

pn.extension(design="material")

if "vector_store" not in pn.state.cache:
    pn.state.cache["vector_store"] = VectorStoreComponent(collection_name="PDFAbout")

conversation_terminated = False
initiate_chat_task_created = False

config_list = [
    {
        "model": os.getenv("MODEL"),
        "api_type": os.getenv("API_TYPE"),
        "client_host": os.getenv("CLIENT_HOST"),
    }
]

llm_config = {
    "seed": 42,
    "config_list": config_list,
    "temperature": 0,
}


SYSTEM_MESSAGE_TEMPLATE_ASSISTANT = """You are a highly knowledgeable AI assistant specializing in finance.
You have access to three tools via a tool agent:

VectorContext(query: str) - Retrieves relevant financial context based on a query.
TopGainers(limit: int = 5) - Provides a list of top gaining stocks.
TopLosers(limit: int = 5) - Provides a list of top losing stocks.

You are not allowed to answer back, before you can see that the tool agent have answered. Do not pretend you are calling the tools, with bogus information.
Rules for Using Tools:
Delegation: You cannot execute tools directly. Always call the tool agent to execute tools on your behalf.
Single Use: Call each tool exactly once per request. Avoid multiple or duplicate calls.
Combination of Results: Integrate results logically into a cohesive response when multiple tools are used. For example:
If you retrieve context and top gainers, use both to provide a relevant and actionable response.
Final Response: Always conclude your final message with TERMINATE.
Interaction Guidelines:
No Redundancy: If a tool request has already been completed, do not re-request it.
Execution Only: Avoid loops or indefinite waits. Execute instructions once and finalize.
"""

SYSTEM_MESSAGE_TEMPLATE_TOOL_AGENT = """You are the tool agent.
You execute tools only when asked by the assistant.
Return results directly to the assistant.
If asked again for a completed request, state that it has been done and you cannot repeat.
"""

SYSTEM_MESSAGE_TEMPLATE_USER = """You are the human user.
Provide a query and wait for a response from the assistant.
Once you receive a final answer ending with 'TERMINATE', consider the conversation complete.
"""

user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message=SYSTEM_MESSAGE_TEMPLATE_USER,
    code_execution_config={
        "last_n_messages": 2,
        "work_dir": "groupchat",
        "use_docker": False,
    },
    human_input_mode="ALWAYS",
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
)


assistant = TrackableConversableAgent(
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
    Tools.get_top_gainers_tool,
    caller=assistant,
    executor=tool_agent,
    name="TopGainers",
    description="Gets the top gaining stocks from the market.",
)

register_function(
    Tools.get_losers_gainers_tool,
    caller=assistant,
    executor=tool_agent,
    name="TopLosers",
    description="Gets the top 5 losing stocks from the market.",
)

register_function(
    Tools.get_vector_context_tool,
    caller=assistant,
    executor=tool_agent,
    name="VectorContext",
    description="Retrieves relevant financial trading context from the vector store based on the query.",
)


groupchat = autogen.GroupChat(
    agents=[user_proxy, assistant, tool_agent], messages=[], max_round=8
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

chat_interface = pn.chat.ChatInterface()
chat_interface.send("Send a message!", user="System", respond=False)

avatar = {
    "assistant": "🤖",
    "User_proxy": "👨‍💼",
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


for ag in [user_proxy, assistant, tool_agent]:
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
        chat_interface.send(
            "Waiting for the conversation to proceed...", user="System", respond=False
        )


chat_interface.callback = callback
chat_interface.servable()
