from autogen import UserProxyAgent, AssistantAgent


class TrackableAssistantAgent(AssistantAgent):
    def _process_received_message(self, message, sender, silent):
        return super()._process_received_message(message, sender, silent)


class TrackableUserProxyAgent(UserProxyAgent):
    def _process_received_message(self, message, sender, silent):
        return super()._process_received_message(message, sender, silent)
