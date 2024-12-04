import streamlit as st
import asyncio
from autogen import ConversableAgent, UserProxyAgent, AssistantAgent

class TrackableAssistantAgent(AssistantAgent):
    def _process_received_message(self, message, sender, silent):
        # Process the message without rendering it in the UI
        return super()._process_received_message(message, sender, silent)


class TrackableUserProxyAgent(UserProxyAgent):
    def _process_received_message(self, message, sender, silent):
        # Process the message without rendering it in the UI
        return super()._process_received_message(message, sender, silent)