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


def _context(*rows):
    return [{"document": row} for row in rows]


HOME_BLR = (
    "Property ID: 1\nTitle: Whitefield Home\nCity: Bangalore\nLocation: Whitefield\n"
    "Price: ₹8,000,000\nArea: 1800 sqft\nBedrooms: 3\nBathrooms: 2\nFloors: 2\n"
    "Year Built: 2022\nParking: Yes\nParking spaces: 3\nDescription: Home\n"
    "Features: furnished: yes, balcony: yes"
)
HOME_PUNE = (
    "Property ID: 2\nTitle: Pune Home\nCity: Pune\nLocation: Baner\n"
    "Price: ₹9,000,000\nArea: 1600 sqft\nBedrooms: 2\nBathrooms: 2\nFloors: 1\n"
    "Year Built: 2021\nParking: Yes\nParking spaces: 1\nDescription: Home\n"
    "Features: furnished: yes, balcony: no"
)


def test_parser_handles_indian_prices_and_multiple_cities():
    service = RAGService()
    parsed = service.parse_query("Properties in Whitefield under ₹1 crore")
    assert parsed["location"] == "whitefield"
    assert parsed["max_price"] == 10_000_000

    parsed = service.parse_query("Compare properties in Bangalore and Pune")
    assert parsed["cities"] == ["bangalore", "pune"]
    assert parsed["compare"] is True

    for phrase, expected in (("₹80 lakh", 8_000_000), ("80 lakhs", 8_000_000), ("₹80L", 8_000_000), ("1 crore", 10_000_000), ("₹1.5 crore", 15_000_000)):
        assert service.parse_query(f"properties under {phrase}")["max_price"] == expected


def test_furnished_balcony_requires_both_explicit_features():
    service = RAGService()
    response, sources = service.generate_response(
        "Furnished + balcony", _context(HOME_BLR, HOME_PUNE)
    )
    assert "Whitefield Home" in response
    assert "Pune Home" not in response
    assert [source["metadata"]["property_id"] for source in sources] == [1]


def test_multi_city_comparison_and_most_parking_are_deterministic():
    service = RAGService()
    response, sources = service.generate_response(
        "Compare properties in Bangalore and Pune", _context(HOME_BLR, HOME_PUNE)
    )
    assert "Bangalore:" in response
    assert "Pune:" in response
    assert {source["metadata"]["property_id"] for source in sources} == {1, 2}

    response, sources = service.generate_response(
        "Which property has the most parking?", _context(HOME_BLR, HOME_PUNE)
    )
    assert "Whitefield Home" in response
    assert "Pune Home" not in response
    assert sources[0]["metadata"]["property_id"] == 1


def test_no_match_and_off_topic_queries_return_no_sources():
    service = RAGService()
    response, sources = service.generate_response(
        "Find a 10 BHK property in Antarctica under ₹1 lakh",
        _context(HOME_BLR, HOME_PUNE),
    )
    assert "couldn't find" in response.lower()
    assert sources == []

    response, sources = service.generate_response("What is the weather today?", _context(HOME_BLR))
    assert "real estate" in response.lower()
    assert sources == []
