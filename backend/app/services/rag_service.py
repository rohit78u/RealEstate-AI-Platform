import chromadb
import google.generativeai as genai
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Property


class RAGService:
    COLLECTION_NAME = "properties"

    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.collection = self.client.get_or_create_collection(name=self.COLLECTION_NAME)
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    def _property_document(self, prop: Property) -> str:
        return (
            f"Property ID: {prop.id}\n"
            f"Title: {prop.title}\n"
            f"City: {prop.city}\n"
            f"Location: {prop.location}\n"
            f"Price: ₹{float(prop.price):,.0f}\n"
            f"Area: {prop.area_sqft} sqft\n"
            f"Bedrooms: {prop.bedrooms}\n"
            f"Bathrooms: {prop.bathrooms}\n"
            f"Floors: {prop.floors}\n"
            f"Year Built: {prop.year_built}\n"
            f"Parking: {prop.parking}\n"
            f"Description: {prop.description or 'N/A'}\n"
            f"Features: {prop.features or {}}"
        )

    def index_property(self, prop: Property):
        self.collection.upsert(
            ids=[str(prop.id)],
            documents=[self._property_document(prop)],
            metadatas=[{"property_id": prop.id, "city": prop.city, "title": prop.title}],
        )

    def remove_property(self, property_id: int):
        self.collection.delete(ids=[str(property_id)])

    def reindex_all(self, db: Session):
        properties = db.query(Property).all()
        if not properties:
            return 0
        self.collection.upsert(
            ids=[str(p.id) for p in properties],
            documents=[self._property_document(p) for p in properties],
            metadatas=[
                {"property_id": p.id, "city": p.city, "title": p.title} for p in properties
            ],
        )
        return len(properties)

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        if self.collection.count() == 0:
            return []
        results = self.collection.query(query_texts=[query], n_results=min(top_k, self.collection.count()))
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved = []
        for doc, meta, distance in zip(documents, metadatas, distances):
            retrieved.append({"document": doc, "metadata": meta, "distance": distance})
        return retrieved

    def generate_response(self, query: str, retrieved: list[dict]) -> tuple[str, list[dict]]:
        if not retrieved:
            return (
                "I don't have any property listings indexed yet. Please check back after properties are added.",
                [],
            )

        context = "\n\n---\n\n".join(item["document"] for item in retrieved)

        if not self.model:
            return (
                "Gemini API key is not configured. Here are the most relevant listings I found:\n\n"
                + context,
                retrieved,
            )

        prompt = f"""You are a real estate assistant. Answer ONLY using the property context below.
If the answer is not in the context, say "I don't have that information in our listings."
Do not invent prices, locations, or property details.
Be concise and helpful. Use ₹ for prices.

Context:
{context}

User question: {query}
"""
        response = self.model.generate_content(prompt)
        return response.text.strip(), retrieved


rag_service = RAGService()
