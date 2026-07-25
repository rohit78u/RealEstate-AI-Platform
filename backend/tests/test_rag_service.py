import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

chromadb = types.ModuleType("chromadb")


class PersistentClient:
    def __init__(self, *args, **kwargs):
        pass

    def get_or_create_collection(self, *args, **kwargs):
        return types.SimpleNamespace(count=lambda: 0, query=lambda *args, **kwargs: {"documents": [[]], "metadatas": [[]], "distances": [[]]})


chromadb.PersistentClient = PersistentClient
sys.modules.setdefault("chromadb", chromadb)

groq = types.ModuleType("groq")


class Groq:
    def __init__(self, *args, **kwargs):
        pass


groq.Groq = Groq
sys.modules.setdefault("groq", groq)

from app.services.rag_service import RAGService


def test_parse_query_detects_large_and_minimum_intent():
    service = RAGService()

    biggest = service.parse_query("Show me the biggest property in Bangalore")
    minimum = service.parse_query("Find the minimum price in Delhi")

    assert biggest["sort_by"] == "area_desc"
    assert minimum["sort_by"] == "price_asc"


def test_general_advice_query_returns_guidance():
    service = RAGService()
    retrieved = [
        {
            "document": "Property ID: 1\nTitle: Green Villa\nCity: Bangalore\nLocation: Whitefield\nPrice: ₹1,200,000\nArea: 1800 sqft\nBedrooms: 3\nBathrooms: 2\nYear Built: 2022\nParking: Yes\nParking spaces: 2\nDescription: Spacious family apartment\nFeatures: balcony: yes, furnished: yes"
        }
    ]

    response, _ = service.generate_response(
        "What should I look for before buying a property?",
        retrieved,
    )

    assert "location" in response.lower() or "budget" in response.lower() or "look for" in response.lower()
