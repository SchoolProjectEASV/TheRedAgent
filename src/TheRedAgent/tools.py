import os
from typing import List, Dict
import panel as pn

from VectorStore import VectorStoreComponent
from api_factory import APIFactory

pn.extension(design="material")

if "vector_store" not in pn.state.cache:
    pn.state.cache["vector_store"] = VectorStoreComponent(collection_name="PDFAbout")


class Tools:
    """Encapsulates the Tools functionality. Using the APIWrapper, so one can use the both the mock API and the real API."""

    @staticmethod
    def get_top_gainers_tool(limit: int = 5, use_mock: bool = False) -> List[Dict]:
        api_key = os.getenv("API_FINANCIAL_KEY")
        if api_key is not None:
            api_key = api_key.strip()

        api_instance = APIFactory.get_api_wrapper(use_mock=use_mock, api_key=api_key)

        losers = api_instance.get_top_gainers(limit=limit)
        if not losers:
            return []
        return losers

    @staticmethod
    def get_losers_gainers_tool(limit: int = 5, use_mock: bool = False) -> List[Dict]:
        api_key = os.getenv("API_FINANCIAL_KEY")
        if api_key is not None:
            api_key = api_key.strip()

        api_instance = APIFactory.get_api_wrapper(use_mock=use_mock, api_key=api_key)

        gainers = api_instance.get_top_losers(limit=limit)
        if not gainers:
            return []
        return gainers

    @staticmethod
    def get_vector_context_tool(query: str) -> str:
        """Retrieve relevant financial trading context from the vector store for the given query."""
        limit = 5
        results = pn.state.cache["vector_store"].retrieve_relevant(
            query=query, limit=limit
        )
        context_text = "\n".join(r["text"] for r in results if r["score"] != 0.0)
        if not context_text.strip():
            context_text = "No relevant financial trading information found."
        return context_text
