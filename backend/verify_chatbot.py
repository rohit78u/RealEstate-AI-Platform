import os
import sys
import types

os.chdir(r"C:\Users\rohit\Desktop\Project A\backend")
sys.path.insert(0, os.getcwd())

chromadb = types.ModuleType("chromadb")

class PersistentClient:
    def __init__(self, *args, **kwargs):
        pass

    def get_or_create_collection(self, *args, **kwargs):
        return types.SimpleNamespace(count=lambda: 0, query=lambda *args, **kwargs: {"documents": [[]], "metadatas": [[]], "distances": [[]]})

chromadb.PersistentClient = PersistentClient
sys.modules["chromadb"] = chromadb

groq = types.ModuleType("groq")

class Groq:
    def __init__(self, *args, **kwargs):
        pass

groq.Groq = Groq
sys.modules["groq"] = groq

from app.services.rag_service import RAGService

service = RAGService()
queries = [
    "Show me the biggest property in Bangalore",
    "Find the minimum price in Delhi",
    "What should I look for before buying a property?",
    "Compare the best options in Pune",
]

for query in queries:
    response, _ = service.generate_response(
        query,
        [{
            "document": "Property ID: 1\nTitle: Green Villa\nCity: Bangalore\nLocation: Whitefield\nPrice: ₹1,200,000\nArea: 1800 sqft\nBedrooms: 3\nBathrooms: 2\nYear Built: 2022\nParking: Yes\nParking spaces: 2\nDescription: Spacious family apartment\nFeatures: balcony: yes, furnished: yes"
        }],
    )
    print(query)
    print(response.splitlines()[0])
    print("---")
