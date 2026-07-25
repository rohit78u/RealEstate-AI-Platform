import re
from typing import Any

from sqlalchemy.orm import Session

try:
    import chromadb
except ImportError:  # pragma: no cover - optional dependency
    chromadb = None

try:
    from groq import Groq
except ImportError:  # pragma: no cover - optional dependency
    Groq = None

from app.config import settings
from app.models import Property


class RAGService:
    COLLECTION_NAME = "properties"

    def __init__(self):
        self.client = None
        self.collection = None
        self.client_ai = None

        if chromadb is None:
            return

        try:
            self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
            self.collection = self.client.get_or_create_collection(name=self.COLLECTION_NAME)
        except Exception:
            self.client = None
            self.collection = None

        if settings.groq_api_key and Groq is not None:
            try:
                self.client_ai = Groq(api_key=settings.groq_api_key)
            except Exception:
                self.client_ai = None

    def _property_document(self, prop: Property) -> str:
        features = prop.features or {}
        if isinstance(features, dict):
            allowed_features = {
                key: value
                for key, value in features.items()
                if value is not None and key.lower() not in {"image_url", "imageurl", "images"}
            }
            features_text = ", ".join(
                f"{key}: {value}" for key, value in allowed_features.items()
            )
        else:
            features_text = str(features)

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
            f"Parking: {'Yes' if prop.parking else 'No'}\n"
            f"Parking spaces: {prop.parking}\n"
            f"Description: {prop.description or 'N/A'}\n"
            f"Features: {features_text or 'N/A'}"
        )
    def _contains_any(self, text: str, terms: list[str]) -> bool:
        return any(term in text for term in terms)

    def _infer_sort_preference(self, query: str) -> str | None:
        q = query.lower()

        if self._contains_any(
            q,
            [
                "cheapest",
                "least expensive",
                "lowest price",
                "lowest cost",
                "affordable",
                "cheap",
                "budget",
                "value for money",
                "best value",
                "good deal",
                "low cost",
                "under",
                "within budget",
                "minimum price",
                "minimum budget",
                "cheaper",
                "low",
                "lower",
            ],
        ) and not self._contains_any(q, ["premium", "expensive", "luxury", "high-end", "maximum", "highest"]):
            return "price_asc"

        if self._contains_any(
            q,
            [
                "most expensive",
                "highest price",
                "premium",
                "expensive",
                "luxury",
                "high-end",
                "maximum price",
                "maximum budget",
                "costly",
                "high",
            ],
        ):
            return "price_desc"

        if self._contains_any(
            q,
            [
                "largest",
                "largest area",
                "most spacious",
                "biggest",
                "bigger",
                "larger",
                "maximum area",
                "maximum size",
                "spacious",
                "space",
                "area",
                "size",
                "huge",
                "wide",
            ],
        ) and not self._contains_any(q, ["smallest", "compact", "smaller", "minimum area", "minimum size", "tiny"]):
            return "area_desc"

        if self._contains_any(
            q,
            [
                "smallest",
                "compact",
                "smaller",
                "tiny",
                "minimum area",
                "minimum size",
                "cozy",
            ],
        ):
            return "area_asc"

        if self._contains_any(q, ["newest", "latest", "newly built", "modern", "recent", "new build", "new"]):
            return "year_desc"

        return None

    def parse_query(self, query: str) -> dict:
        q = query.lower()

        filters = {
            "city": None,
            "bedrooms": None,
            "bathrooms": None,
            "floors": None,
            "year_built": None,
            "max_price": None,
            "min_price": None,
            "max_area": None,
            "min_area": None,
            "parking": False,
            "parking_count": None,
            "furnished": False,
            "balcony": False,
            "featured": False,
            "luxury": False,
            "location": None,
            "sort_by": None,
            "compare": False,
            "compare_ids": [],
            "property_id": None,
            "listing_type": None,
            "top_k": 5,
        }

        cities = [
            "mumbai",
            "bangalore",
            "bengaluru",
            "delhi",
            "hyderabad",
            "pune",
            "chennai",
            "kolkata",
            "ahmedabad",
        ]

        for city in cities:
            if city in q:
                filters["city"] = city
                break

        bhk = re.search(r"([1-9])\s*bhk", q)
        if bhk:
            filters["bedrooms"] = int(bhk.group(1))

        bath_match = re.search(r"(\d+)\s*(?:bath|baths|bathroom|bathrooms)\b", q)
        if bath_match:
            filters["bathrooms"] = int(bath_match.group(1))

        floor_match = re.search(r"(\d+)\s*(?:floor|storey|story|storeys|stories)\b", q)
        if floor_match:
            filters["floors"] = int(floor_match.group(1))

        year_match = re.search(r"(?:built in|year built|since)\s*(\d{4})", q)
        if year_match:
            filters["year_built"] = int(year_match.group(1))

        id_match = re.search(r"(?:property|listing)\s*#?\s*(\d+)\b", q)
        if id_match:
            filters["property_id"] = int(id_match.group(1))

        compare_matches = re.findall(r"(?:property|listing)\s*#?\s*(\d+)\b", q)
        if "compare" in q and len(compare_matches) >= 2:
            filters["compare_ids"] = [int(x) for x in compare_matches[:2]]

        price_match = re.search(r"(?:under|up to|max(?:imum)?|budget)\s*([\d,.]+)\s*(crore|cr|lakh|lac)?", q)
        if price_match:
            amount = float(price_match.group(1).replace(",", ""))
            unit = price_match.group(2)
            if unit and unit.startswith("c"):
                filters["max_price"] = int(amount * 10000000)
            elif unit and unit.startswith("l"):
                filters["max_price"] = int(amount * 100000)
            elif amount > 1000:
                filters["max_price"] = int(amount)
            else:
                filters["max_price"] = int(amount * 100000)

        min_price_match = re.search(r"(?:from|at least|minimum|min)\s*([\d,.]+)\s*(crore|cr|lakh|lac)?", q)
        if min_price_match:
            amount = float(min_price_match.group(1).replace(",", ""))
            unit = min_price_match.group(2)
            if unit and unit.startswith("c"):
                filters["min_price"] = int(amount * 10000000)
            elif unit and unit.startswith("l"):
                filters["min_price"] = int(amount * 100000)
            elif amount > 1000:
                filters["min_price"] = int(amount)
            else:
                filters["min_price"] = int(amount * 100000)

        area_max = re.search(r"(?:under|up to|max(?:imum)?)\s*([\d,.]+)\s*(?:sqft|sq ft|sq\.ft)", q)
        if area_max:
            filters["max_area"] = int(area_max.group(1).replace(",", ""))

        area_min = re.search(r"(?:at least|minimum|min|from)\s*([\d,.]+)\s*(?:sqft|sq ft|sq\.ft)", q)
        if area_min:
            filters["min_area"] = int(area_min.group(1).replace(",", ""))

        parking_number = re.search(r"(\d+)\s*parking", q)
        if parking_number:
            filters["parking_count"] = int(parking_number.group(1))
            filters["parking"] = True
        elif "parking" in q:
            filters["parking"] = True

        if "furnished" in q:
            filters["furnished"] = True

        if "balcony" in q:
            filters["balcony"] = True

        if "featured" in q:
            filters["featured"] = True

        if "luxury" in q or "premium" in q or "high-end" in q:
            filters["luxury"] = True

        if "rent" in q and "buy" not in q:
            filters["listing_type"] = "rent"
        elif "buy" in q or "purchase" in q or "sale" in q or "sell" in q:
            filters["listing_type"] = "sale"

        if "top" in q:
            top_match = re.search(r"top\s*(\d+)\b", q)
            if top_match:
                filters["top_k"] = min(int(top_match.group(1)), 10)

        inferred_sort = self._infer_sort_preference(query)
        if inferred_sort:
            filters["sort_by"] = inferred_sort

        if "compare" in q or "comparison" in q:
            filters["compare"] = True

        if "best value" in q or "value" in q:
            filters["sort_by"] = filters["sort_by"] or "price_asc"

        locations = [
            "bandra",
            "thane",
            "malad",
            "jayanagar",
            "hsr layout",
            "electronic city",
            "whitefield",
            "aundh",
            "baner",
            "kukatpally",
            "hitec city",
            "koramangala",
            "whitefield",
            "bellandur",
            "juhu",
        ]

        for loc in locations:
            if loc in q:
                filters["location"] = loc
                break

        return filters
    def _parse_feature_text(self, feature_text: str) -> dict:
        parsed = {}
        for part in feature_text.split(","):
            if ":" in part:
                key, value = part.split(":", 1)
                parsed[key.strip().lower()] = value.strip()
        return parsed

    def _extract_property_fields(self, doc: str) -> dict:
        def extract(field: str) -> str:
            match = re.search(rf"{field}:\s*(.*)", doc, re.IGNORECASE)
            return match.group(1).strip() if match else ""

        title = extract("Title")
        description = extract("Description")
        feature_text = extract("Features")
        features = self._parse_feature_text(feature_text)
        if "image_url" in features:
            features.pop("image_url", None)

        price = extract("Price")
        price_value = int(re.sub(r"[^\d]", "", price or "")) if price else float("inf")
        area = extract("Area")
        area_value = int(re.sub(r"[^\d]", "", area or "")) if area else 0
        year_built = extract("Year Built")
        year_value = int(re.sub(r"[^\d]", "", year_built or "")) if year_built else 0
        parking_text = extract("Parking")
        parking_spaces = extract("Parking spaces")
        parking_value = int(re.sub(r"[^\d]", "", parking_spaces or "0")) if parking_spaces else 0
        parking_yes = parking_value > 0 or parking_text.lower() in ["yes", "true", "1"]

        return {
            "id": extract("Property ID"),
            "title": title,
            "city": extract("City"),
            "location": extract("Location"),
            "price": price,
            "price_value": price_value,
            "bedrooms": int(re.sub(r"[^\d]", "", extract("Bedrooms") or "0")) if extract("Bedrooms") else 0,
            "bathrooms": int(re.sub(r"[^\d]", "", extract("Bathrooms") or "0")) if extract("Bathrooms") else 0,
            "area": area,
            "area_value": area_value,
            "year_built": year_built,
            "year_value": year_value,
            "parking": parking_text,
            "parking_yes": parking_yes,
            "parking_value": parking_value,
            "description": description,
            "highlight": "",
            "features": features,
            "doc": doc,
        }

    def _passes_strict_filters(self, property_data: dict, filters: dict) -> bool:
        if filters["property_id"] is not None:
            return str(property_data["id"]) == str(filters["property_id"])

        if filters["city"] and filters["city"].lower() not in property_data["city"].lower():
            return False
        if filters["location"] and filters["location"].lower() not in property_data["location"].lower():
            return False
        if filters["bedrooms"] and property_data["bedrooms"] != filters["bedrooms"]:
            return False
        if filters["bathrooms"] and property_data["bathrooms"] != filters["bathrooms"]:
            return False
        if filters["floors"] and property_data.get("floors", 0) != filters["floors"]:
            return False
        if filters["year_built"] and property_data["year_value"] != filters["year_built"]:
            return False
        if filters["min_price"] is not None and property_data["price_value"] < filters["min_price"]:
            return False
        if filters["max_price"] is not None and property_data["price_value"] > filters["max_price"]:
            return False
        if filters["min_area"] is not None and property_data["area_value"] < filters["min_area"]:
            return False
        if filters["max_area"] is not None and property_data["area_value"] > filters["max_area"]:
            return False
        if filters["parking_count"] is not None and property_data["parking_value"] < filters["parking_count"]:
            return False
        if filters["furnished"] and not property_data["features"].get("furnished", "").lower() in ["true", "yes", "1"]:
            return False
        if filters["balcony"] and not property_data["features"].get("balcony", "").lower() in ["true", "yes", "1"]:
            return False
        if filters["featured"] and not property_data["features"].get("featured", "").lower() in ["true", "yes", "1"]:
            return False
        if filters["luxury"]:
            return any(term in property_data["doc"].lower() for term in ["luxury", "premium", "high-end", "exclusive"])
        return True

    def _score_property_match(self, property_data: dict, filters: dict, query: str) -> int:
        q = query.lower()
        score = 0
        if filters["city"] and filters["city"].lower() in property_data["city"].lower():
            score += 6
        if filters["location"] and filters["location"].lower() in property_data["location"].lower():
            score += 4
        if filters["bedrooms"] and property_data["bedrooms"] == filters["bedrooms"]:
            score += 6
        elif filters["bedrooms"] and abs(property_data["bedrooms"] - filters["bedrooms"]) <= 1:
            score += 2
        if filters["bathrooms"] and property_data["bathrooms"] == filters["bathrooms"]:
            score += 3
        if filters["max_price"] is not None and property_data["price_value"] <= filters["max_price"]:
            score += 3
        if filters["min_price"] is not None and property_data["price_value"] >= filters["min_price"]:
            score += 2
        if filters["max_area"] is not None and property_data["area_value"] <= filters["max_area"]:
            score += 2
        if filters["min_area"] is not None and property_data["area_value"] >= filters["min_area"]:
            score += 2
        if filters["parking"] and property_data["parking_yes"]:
            score += 2
        if filters["furnished"] and property_data["features"].get("furnished", "").lower() in ["true", "yes", "1"]:
            score += 2
        if filters["balcony"] and property_data["features"].get("balcony", "").lower() in ["true", "yes", "1"]:
            score += 2
        if filters["featured"] and property_data["features"].get("featured", "").lower() in ["true", "yes", "1"]:
            score += 2
        if self._contains_any(q, ["recommend", "suggest", "find", "show", "need", "looking for", "want", "help"]):
            score += 1
        if self._contains_any(q, ["compare", "comparison", "vs", "versus", "better", "difference", "which one", "which is better"]):
            score += 1

        if self._contains_any(q, ["affordable", "cheap", "budget", "value", "deal", "low", "minimum", "under", "within"]):
            score += 1
            if property_data["price_value"] < 15000000:
                score += 1
        if self._contains_any(q, ["spacious", "large", "big", "size", "area", "space", "maximum", "bigger", "largest"]):
            score += 1
            if property_data["area_value"] > 1500:
                score += 1
        if self._contains_any(q, ["new", "latest", "modern", "recent", "newly built"]):
            score += 1
            if property_data["year_value"] >= 2020:
                score += 1

        for keyword in ["pool", "gym", "garden", "lift", "security", "clubhouse", "wifi", "school", "metro", "hospital", "market", "playground", "pet"]:
            if keyword in q and keyword in property_data["doc"].lower():
                score += 2

        return score

    def _detect_intent(self, query: str) -> str:
        q = query.lower()
        intent_scores = {
            "comparison": 0,
            "recommendation": 0,
            "budget": 0,
            "transaction": 0,
            "pricing": 0,
            "detail": 0,
            "general": 0,
        }

        if self._contains_any(q, ["compare", "comparison", "versus", "vs", "better", "difference", "which is better", "than"]):
            intent_scores["comparison"] += 3
        if self._contains_any(q, ["recommend", "suggest", "find", "show me", "looking for", "need", "want", "help", "best"]):
            intent_scores["recommendation"] += 2
        if self._contains_any(q, ["budget", "affordable", "cheap", "expensive", "cost", "price", "under", "within", "maximum", "minimum", "value", "deal"]):
            intent_scores["budget"] += 2
        if self._contains_any(q, ["rent", "buy", "sell", "purchase", "lease", "investment", "loan", "mortgage", "emi"]):
            intent_scores["transaction"] += 2
        if self._contains_any(q, ["average", "how much", "price range", "cost", "rate", "estimate"]):
            intent_scores["pricing"] += 2

        if self.parse_query(query).get("property_id") is not None:
            intent_scores["detail"] += 3

        best_intent, best_score = max(intent_scores.items(), key=lambda item: item[1])
        return best_intent if best_score > 0 else "general"

    def _build_intro(self, properties: list[dict], query: str, filters: dict, intent: str) -> str:
        q = query.lower()
        if intent == "comparison":
            return "Here’s a comparison of the most relevant properties I found for your request:"
        if intent == "recommendation":
            return "Here are the best matches I found for your search:"
        if intent == "budget":
            return "Here are the best options for your budget and requirements:"
        if intent == "transaction":
            return "Here are the properties that best match your buying or renting goal:"
        if intent == "detail" and properties:
            return "Here’s the property you asked about:"
        if filters.get("city"):
            return f"Here are the properties I found in {filters['city'].title()}:"
        if filters.get("location"):
            return f"Here are the properties I found in {filters['location'].title()}:"
        if filters.get("bedrooms"):
            return f"Here are the best {filters['bedrooms']}BHK options I found:"
        if "price" in q or "budget" in q:
            return "Here are the best-price options I found:"
        return f"Here are the top {len(properties)} properties I found for your request:"

    def properties_to_context(self, properties: list[Property]) -> list[dict]:
        return [
        {
            "document": self._property_document(prop),
            "metadata": {
                "property_id": prop.id,
                "city": prop.city,
                "title": prop.title,
            },
            "distance": 0,
        }
        for prop in properties
    ]

    def _is_real_estate_query(self, query: str) -> bool:
        terms = [
            "property",
            "real estate",
            "home",
            "house",
            "flat",
            "apartment",
            "listing",
            "properties",
            "buy",
            "sell",
            "rent",
            "lease",
            "budget",
            "price",
            "sqft",
            "area",
            "bathroom",
            "bedroom",
            "bhk",
            "parking",
            "loan",
            "mortgage",
            "investment",
            "agent",
            "broker",
            "property tax",
            "emi",
            "amenities",
            "recommend",
            "find",
            "search",
            "compare",
            "comparison",
            "suggest",
            "available",
        ]
        q = query.lower()
        if re.search(r"\d+\s*bhk", q):
            return True
        return any(term in q for term in terms)

    def _real_estate_fallback(self, query: str, retrieved: list[dict]) -> str:
        q = query.lower()
        if "loan" in q or "mortgage" in q or "emi" in q or "interest rate" in q:
            return (
                "For real estate purchases, a loan is usually repaid over 15-30 years. "
                "Your EMI depends on the loan amount, interest rate, and tenure. "
                "I can help you compare property budgets and suggest listings based on price and location."
            )

        if "investment" in q or "best investment" in q or "return" in q:
            return (
                "A strong real estate investment usually balances location, price, and future demand. "
                "Look for properties near good transport, schools, and growing infrastructure. "
                "I can also help you narrow down available listings from our current inventory."
            )

        if "rent" in q and "buy" in q:
            return (
                "Renting is usually better for short-term flexibility, while buying can build equity long-term. "
                "For your needs, I can compare available listings, budgets, and rental-friendly features."
            )

        if retrieved:
            top = retrieved[:3]
            lines = [
                "I didn’t find an exact match to your request, but here are a few relevant properties from our current inventory:"
            ]
            for idx, item in enumerate(top, 1):
                doc = item["document"]
                title = re.search(r"Title:\s*(.*)", doc)
                city = re.search(r"City:\s*(.*)", doc)
                price = re.search(r"Price:\s*(.*)", doc)
                location = re.search(r"Location:\s*(.*)", doc)
                lines.append(f"{idx}. {title.group(1) if title else 'Property'} - {price.group(1) if price else 'N/A'} in {location.group(1) if location else city.group(1) if city else 'N/A'}")
            lines.append(
                "Ask me for a specific budget, city, area, or property feature and I’ll narrow it down further."
            )
            return "\n".join(lines)

        return (
            "I am a real estate assistant. Ask me about property listings, budgets, location filters, amenities, buying or renting advice, "
            "or comparisons between properties and I’ll answer using real estate context."
        )

    def index_property(self, prop: Property):
        if self.collection is None:
            return

        self.collection.upsert(
            ids=[str(prop.id)],
            documents=[self._property_document(prop)],
            metadatas=[
                {
                    "property_id": prop.id,
                    "city": prop.city,
                    "title": prop.title,
                }
            ],
        )

    def remove_property(self, property_id: int):
        if self.collection is None:
            return
        self.collection.delete(ids=[str(property_id)])

    def reindex_all(self, db: Session):
        properties = db.query(Property).all()

        if not properties or self.collection is None:
            return 0

        self.collection.upsert(
            ids=[str(p.id) for p in properties],
            documents=[self._property_document(p) for p in properties],
            metadatas=[
                {
                    "property_id": p.id,
                    "city": p.city,
                    "title": p.title,
                }
                for p in properties
            ],
        )

        return len(properties)

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        if self.collection is None:
            return []

        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.collection.count()),
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved = []

        for doc, meta, distance in zip(documents, metadatas, distances):
            retrieved.append(
                {
                    "document": doc,
                    "metadata": meta,
                    "distance": distance,
                }
            )

        return retrieved

    def _format_property_summary(self, properties: list[dict], query: str) -> str:
        if not properties:
            return "I don't have that information in our listings."

        lines = []
        count = len(properties)
        q = query.lower()

        if "compare" in q or "comparison" in q:
            lines.append("Comparing the best matching properties from our current listings.")
        elif "cheapest" in q or "least expensive" in q or "best value" in q or "low budget" in q or "affordable" in q:
            lines.append("Sorted by price to show the most affordable available options first.")
        sort_preference = self._infer_sort_preference(query)
        if sort_preference == "price_asc":
            lines.append("Sorted by price to show the most affordable options first.")
        elif sort_preference == "price_desc":
            lines.append("Showing the highest-priced premium listings first.")
        elif sort_preference == "area_desc":
            lines.append("Sorted by area so you can see the most spacious listings first.")
        elif sort_preference == "area_asc":
            lines.append("Showing compact listings with smaller area first.")
        elif sort_preference == "year_desc":
            lines.append("Sorted by newest listings so you see the most recently built or added properties.")
        else:
            lines.append(f"Here are the top {count} matching properties:")

        if "budget" in q and "under" in q:
            lines.append("Budget-based results are shown below.")

        for idx, prop in enumerate(properties, 1):
            parking = prop['parking']
            if isinstance(parking, str):
                parking = parking.strip().lower()
                parking = "Yes" if parking in ["true", "1", "yes", "y"] else "No"
            lines.append("")
            lines.append(f"{idx}. 🏠 {prop['title']}")
            lines.append(f"   📍 {prop['location']}, {prop['city']}")
            lines.append(f"   💰 {prop['price']}")
            lines.append(f"   🛏 {prop['bedrooms']} BHK   🚗 Parking: {parking}")
            if prop.get("highlight"):
                highlight = prop['highlight']
                if highlight and highlight.lower() != "n/a":
                    lines.append(f"   ✨ {highlight}")

        top = properties[0]
        lines.append("")
        lines.append(
            f"Top pick: {top['title']} in {top['location']} offers the best combination of value, space, and location."
        )
        return "\n".join(lines)

    def generate_response(
        self,
        query: str,
        retrieved: list[dict],
    ) -> tuple[str, list[dict]]:
        if not retrieved:
            return (
                "I don't have any property listings indexed yet. Please check back after properties are added.",
                [],
            )

        if not self._is_real_estate_query(query):
            return self._real_estate_fallback(query, retrieved), retrieved

        filters = self.parse_query(query)
        intent = self._detect_intent(query)

        parsed_properties = []
        for item in retrieved:
            doc = item["document"]
            property_data = self._extract_property_fields(doc)
            property_data["strict_match"] = self._passes_strict_filters(property_data, filters)
            property_data["score"] = self._score_property_match(property_data, filters, query)
            parsed_properties.append(property_data)

        strict_matches = [p for p in parsed_properties if p["strict_match"]]
        candidates = strict_matches if strict_matches else parsed_properties

        if filters["property_id"] is not None:
            candidates = [p for p in candidates if str(p["id"]) == str(filters["property_id"])]

        if not candidates:
            candidates = parsed_properties

        for property_data in candidates:
            if property_data["strict_match"]:
                property_data["score"] += 10
            if intent == "comparison":
                property_data["score"] += 2
            if intent == "recommendation":
                property_data["score"] += 1
            if intent == "budget":
                property_data["score"] += 1

        if filters["sort_by"] == "price_asc":
            candidates = sorted(
                candidates,
                key=lambda p: (-p["score"], p["price_value"], -p["area_value"], -p["year_value"]),
            )
        elif filters["sort_by"] == "price_desc":
            candidates = sorted(
                candidates,
                key=lambda p: (-p["score"], -p["price_value"], -p["area_value"], -p["year_value"]),
            )
        elif filters["sort_by"] == "area_desc":
            candidates = sorted(
                candidates,
                key=lambda p: (-p["score"], -p["area_value"], p["price_value"], -p["year_value"]),
            )
        elif filters["sort_by"] == "area_asc":
            candidates = sorted(
                candidates,
                key=lambda p: (-p["score"], p["area_value"], p["price_value"], -p["year_value"]),
            )
        elif filters["sort_by"] == "year_desc":
            candidates = sorted(
                candidates,
                key=lambda p: (-p["score"], -p["year_value"], p["price_value"], -p["area_value"]),
            )
        else:
            candidates = sorted(
                candidates,
                key=lambda p: (-p["score"], p["price_value"], -p["area_value"], -p["year_value"]),
            )

        property_list = candidates[: max(3, filters["top_k"])]
        if not property_list:
            property_list = parsed_properties[: max(3, filters["top_k"])]

        summary = self._format_property_summary(property_list, query)
        if filters["compare"] and len(property_list) >= 2:
            first = property_list[0]
            second = property_list[1]
            compare_type = "cheaper" if filters["sort_by"] == "price_asc" else "larger" if filters["sort_by"] == "area_desc" else "newer" if filters["sort_by"] == "year_desc" else "better"
            summary += f"\n\nCompare: {first['title']} is {compare_type} than {second['title']} and is the stronger option for this search."

        return summary, retrieved

rag_service = RAGService()