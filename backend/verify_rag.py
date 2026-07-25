import os
import sys
import types

sys.path.insert(0, os.getcwd())

chromadb = types.ModuleType('chromadb')
class PersistentClient:
    def __init__(self, *args, **kwargs):
        pass
    def get_or_create_collection(self, *args, **kwargs):
        return types.SimpleNamespace(count=lambda: 0, query=lambda *a, **k: {'documents': [[]], 'metadatas': [[]], 'distances': [[]]})
chromadb.PersistentClient = PersistentClient
sys.modules['chromadb'] = chromadb

groq = types.ModuleType('groq')
class Groq:
    def __init__(self, *args, **kwargs):
        pass
groq.Groq = Groq
sys.modules['groq'] = groq

from app.services.rag_service import RAGService

service = RAGService()
print('biggest:', service.parse_query('Show me the biggest property in Bangalore')['sort_by'])
print('largest:', service.parse_query('Find the largest area in Pune')['sort_by'])
print('minimum:', service.parse_query('Find the minimum price in Delhi')['sort_by'])
print('maximum:', service.parse_query('Show me the maximum size in Hyderabad')['sort_by'])
