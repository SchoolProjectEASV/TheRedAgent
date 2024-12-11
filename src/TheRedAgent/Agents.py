from autogen import UserProxyAgent, AssistantAgent, ConversableAgent


class TrackableAssistantAgent(AssistantAgent):
    def _process_received_message(self, message, sender, silent):
        return super()._process_received_message(message, sender, silent)


class TrackableUserProxyAgent(UserProxyAgent):
    def _process_received_message(self, message, sender, silent):
        return super()._process_received_message(message, sender, silent)


class TrackableConversableAgent(ConversableAgent):
    def _process_received_message(self, message, sender, silent):
        return super()._process_received_message(message, sender, silent)
