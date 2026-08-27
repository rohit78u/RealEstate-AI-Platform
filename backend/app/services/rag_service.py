import re
from pathlib import Path
from typing import Any

try:
    import chromadb
except ImportError:  # pragma: no cover
    chromadb = None

try:
    from groq import Groq
except ImportError:  # pragma: no cover
    Groq = None

from app.config import settings
from app.models import Property


class RAGService:
    """Retrieval, deterministic property filtering, and grounded LLM responses."""

    COLLECTION_NAME = "properties"
    DEFAULT_RETRIEVAL_K = 8
    MAX_RETRIEVAL_K = 8
    MAX_CONTEXT_PROPERTIES = 8

    def __init__(self):
        self.client = None
        self.collection = None
        self.client_ai = None

        if chromadb is not None:
            try:
                Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
                self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
                self.collection = self.client.get_or_create_collection(
                    name=self.COLLECTION_NAME
                )
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
                str(key): value
                for key, value in features.items()
                if value is not None
                and str(key).lower() not in {"image_url", "imageurl", "images"}
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
            f"Area: {float(prop.area_sqft):,.0f} sqft\n"
            f"Bedrooms: {prop.bedrooms}\n"
            f"Bathrooms: {prop.bathrooms}\n"
            f"Floors: {prop.floors}\n"
            f"Year Built: {prop.year_built}\n"
            f"Parking: {'Yes' if int(prop.parking or 0) > 0 else 'No'}\n"
            f"Parking spaces: {int(prop.parking or 0)}\n"
            f"Description: {prop.description or 'N/A'}\n"
            f"Features: {features_text or 'N/A'}"
        )

    def properties_to_context(self, properties: list[Property]) -> list[dict[str, Any]]:
        return [
            {
                "document": self._property_document(prop),
                "metadata": {
                    "property_id": prop.id,
                    "city": prop.city,
                    "title": prop.title,
                },
                "distance": 0.0,
            }
            for prop in properties
        ]

    @staticmethod
    def _contains_any(text: str, terms: list[str]) -> bool:
        return any(term in text for term in terms)

    @staticmethod
    def _money_to_rupees(amount: float, unit: str | None) -> int:
        if not unit:
            return int(amount if amount >= 1000 else amount * 100000)

        unit = unit.lower()
        if unit in {"cr", "crore", "crores", "c"}:
            return int(amount * 10_000_000)
        if unit in {"l", "lac", "lacs", "lakh", "lakhs"}:
            return int(amount * 100_000)
        return int(amount)

    def _infer_sort_preference(self, query: str) -> str | None:
        q = query.lower()

        if self._contains_any(q, [
            "cheapest", "least expensive", "lowest price", "lowest cost",
            "affordable", "cheap", "budget", "best value", "good deal",
            "low cost", "under", "within budget", "cheaper", "lower price",
            "minimum price", "minimum", "lowest",
        ]):
            return "price_asc"

        if self._contains_any(q, [
            "most expensive", "highest price", "premium", "expensive",
            "luxury", "high-end", "maximum price", "costly",
        ]):
            return "price_desc"

        if self._contains_any(q, [
            "largest", "most spacious", "biggest", "larger", "maximum area",
            "maximum size", "spacious", "largest area",
        ]):
            return "area_desc"

        if self._contains_any(q, [
            "smallest", "compact", "smaller", "tiny", "minimum area", "minimum size",
        ]):
            return "area_asc"

        if self._contains_any(q, [
            "newest", "latest", "newly built", "recently built", "recent", "new build",
        ]):
            return "year_desc"

        if self._contains_any(q, [
            "most parking", "maximum parking", "highest parking",
            "most parking spaces", "maximum parking spaces",
        ]):
            return "parking_desc"

        return None

    def parse_query(self, query: str) -> dict[str, Any]:
        q = query.lower().strip()

        filters: dict[str, Any] = {
            "city": None,
            "cities": [],
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
            "sort_by": self._infer_sort_preference(q),
            "compare": (
                "compare" in q
                or "comparison" in q
                or "versus" in q
                or re.search(r"\bvs\.?\b", q) is not None
                or "more affordable" in q
                or "which is better" in q
            ),
            "compare_ids": [],
            "property_id": None,
            "top_k": 5,
        }

        cities = [
            "mumbai", "bangalore", "bengaluru", "delhi", "hyderabad",
            "pune", "chennai", "kolkata", "ahmedabad",
        ]
        found_cities: list[str] = []
        for city in cities:
            if re.search(rf"\b{re.escape(city)}\b", q):
                canonical = "bangalore" if city == "bengaluru" else city
                if canonical not in found_cities:
                    found_cities.append(canonical)
        filters["cities"] = found_cities
        filters["city"] = found_cities[0] if found_cities else None
        if len(found_cities) > 1 and " or " in q:
            filters["compare"] = True

        match = re.search(r"\b(\d+)\s*(?:bhk|bed(?:room)?s?)\b", q)
        if match:
            filters["bedrooms"] = int(match.group(1))

        match = re.search(r"\b(\d+)\s*(?:bath|baths|bathroom|bathrooms)\b", q)
        if match:
            filters["bathrooms"] = int(match.group(1))

        match = re.search(r"\b(\d+)\s*(?:floor|storey|story|storeys|stories)\b", q)
        if match:
            filters["floors"] = int(match.group(1))

        match = re.search(r"(?:built in|year built|since)\s*(\d{4})", q)
        if match:
            filters["year_built"] = int(match.group(1))

        ids = re.findall(r"(?:property|listing)\s*#?\s*(\d+)\b", q)
        if filters["compare"] and len(ids) >= 2:
            filters["compare_ids"] = [int(value) for value in ids[:2]]
        elif ids:
            filters["property_id"] = int(ids[0])

        price_pattern = re.compile(
            r"(?:under|below|up to|maximum|max|budget|within)\s*₹?\s*"
            r"([\d,.]+)\s*(crore|cr|crores|lakh|lac|lacs|lakhs|[cl])?\b"
        )
        match = price_pattern.search(q)
        if not match:
            # Also accept a direct expression such as "₹1.5 crore".
            match = re.search(
                r"₹?\s*([\d,.]+)\s*(crore|cr|crores|lakh|lac|lacs|lakhs|[cl])\b",
                q,
            )
        if match:
            filters["max_price"] = self._money_to_rupees(
                float(match.group(1).replace(",", "")), match.group(2)
            )

        match = re.search(
            r"(?:from|above|over|at least|minimum|min)\s*₹?\s*"
            r"([\d,.]+)\s*(crore|cr|crores|lakh|lac|lacs|lakhs|[cl])?\b",
            q,
        )
        if match:
            filters["min_price"] = self._money_to_rupees(
                float(match.group(1).replace(",", "")), match.group(2)
            )

        match = re.search(
            r"(?:under|below|up to|max|maximum)\s*([\d,.]+)\s*(?:sq\.?\s*ft|sqft|square feet)",
            q,
        )
        if match:
            filters["max_area"] = int(float(match.group(1).replace(",", "")))

        match = re.search(
            r"(?:at least|minimum|min|above|over|from)\s*([\d,.]+)\s*(?:sq\.?\s*ft|sqft|square feet)",
            q,
        )
        if match:
            filters["min_area"] = int(float(match.group(1).replace(",", "")))

        parking_match = re.search(r"\b(\d+)\s*parking(?:\s*spaces?)?\b", q)
        if parking_match:
            filters["parking"] = True
            filters["parking_count"] = int(parking_match.group(1))
        elif "parking" in q and not re.search(r"\bno\s+parking\b", q):
            filters["parking"] = True

        filters["furnished"] = "furnished" in q and "unfurnished" not in q
        filters["balcony"] = "balcony" in q
        filters["featured"] = "featured" in q
        filters["luxury"] = self._contains_any(q, ["luxury", "premium", "high-end", "exclusive"])

        top_match = re.search(r"\btop\s*(\d+)\b", q)
        if top_match:
            filters["top_k"] = max(1, min(int(top_match.group(1)), 10))

        locations = [
            "bandra", "thane", "malad", "jayanagar", "hsr layout", "electronic city",
            "whitefield", "aundh", "baner", "kukatpally", "hitec city",
            "koramangala", "bellandur", "juhu",
        ]
        for location in locations:
            if location in q:
                filters["location"] = location
                break

        # Preserve an unknown but explicit location (for example,
        # "properties in Antarctica") so it cannot silently fall back to
        # unrelated listings. Known city names remain city filters.
        if filters["location"] is None:
            location_match = re.search(
                r"\bin\s+([a-z][a-z0-9 -]*?)(?=\s+(?:under|below|up to|within|with|and|for)\b|$)",
                q,
            )
            if location_match:
                candidate = location_match.group(1).strip()
                known_cities = {"mumbai", "bangalore", "bengaluru", "delhi", "hyderabad", "pune", "chennai", "kolkata", "ahmedabad"}
                if candidate and candidate not in known_cities:
                    filters["location"] = candidate

        return filters

    def index_property(self, prop: Property) -> None:
        if self.collection is None:
            return

        self.collection.upsert(
            ids=[str(prop.id)],
            documents=[self._property_document(prop)],
            metadatas=[
                {
                    "property_id": int(prop.id),
                    "city": prop.city,
                    "title": prop.title,
                }
            ],
        )

    def remove_property(self, property_id: int) -> None:
        if self.collection is None:
            return
        self.collection.delete(ids=[str(property_id)])

    def reindex_all(self, db) -> int:
        if self.collection is None:
            return 0

        properties = db.query(Property).all()
        if not properties:
            return 0

        self.collection.upsert(
            ids=[str(prop.id) for prop in properties],
            documents=[self._property_document(prop) for prop in properties],
            metadatas=[
                {
                    "property_id": int(prop.id),
                    "city": prop.city,
                    "title": prop.title,
                }
                for prop in properties
            ],
        )
        return len(properties)

    def retrieve(self, query: str, top_k: int = DEFAULT_RETRIEVAL_K) -> list[dict[str, Any]]:
        if self.collection is None or self.collection.count() == 0:
            return []

        requested_k = min(max(top_k, 1), self.MAX_RETRIEVAL_K)
        n_results = min(requested_k, self.collection.count())
        results = self.collection.query(query_texts=[query], n_results=n_results)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        return [
            {
                "document": document,
                "metadata": metadata or {},
                "distance": float(distance) if distance is not None else 0.0,
            }
            for document, metadata, distance in zip(documents, metadatas, distances)
        ]

    @staticmethod
    def _parse_feature_text(feature_text: str) -> dict[str, str]:
        parsed: dict[str, str] = {}
        for part in feature_text.split(","):
            if ":" in part:
                key, value = part.split(":", 1)
                parsed[key.strip().lower()] = value.strip()
        return parsed

    @staticmethod
    def _extract(doc: str, field: str) -> str:
        match = re.search(
            rf"^{re.escape(field)}:\s*(.*)$",
            doc,
            re.IGNORECASE | re.MULTILINE,
        )
        return match.group(1).strip() if match else ""

    def _extract_property(self, doc: str) -> dict[str, Any]:
        features = self._parse_feature_text(self._extract(doc, "Features"))
        price_text = self._extract(doc, "Price")
        area_text = self._extract(doc, "Area")
        year_text = self._extract(doc, "Year Built")
        parking_text = self._extract(doc, "Parking")
        parking_spaces_text = self._extract(doc, "Parking spaces")

        def number(text: str, default: int = 0) -> int:
            digits = re.sub(r"[^\d]", "", text or "")
            return int(digits) if digits else default

        parking_spaces = number(parking_spaces_text)
        parking_yes = parking_spaces > 0 or parking_text.lower() in {"yes", "true", "1"}

        return {
            "id": number(self._extract(doc, "Property ID")),
            "title": self._extract(doc, "Title"),
            "city": self._extract(doc, "City"),
            "location": self._extract(doc, "Location"),
            "price": price_text,
            "price_value": number(price_text),
            "bedrooms": number(self._extract(doc, "Bedrooms")),
            "bathrooms": number(self._extract(doc, "Bathrooms")),
            "floors": number(self._extract(doc, "Floors")),
            "area": area_text,
            "area_value": number(area_text),
            "year_built": year_text,
            "year_value": number(year_text),
            "parking": parking_text,
            "parking_yes": parking_yes,
            "parking_value": parking_spaces,
            "description": self._extract(doc, "Description"),
            "features": features,
            "doc": doc,
        }

    @staticmethod
    def _feature_enabled(features: dict[str, str], key: str) -> bool:
        return features.get(key, "").strip().lower() in {"true", "yes", "1"}

    def _passes_filters(self, prop: dict[str, Any], filters: dict[str, Any]) -> bool:
        compare_ids = filters["compare_ids"]
        if compare_ids:
            if prop["id"] not in compare_ids:
                return False
        elif filters["property_id"] is not None and prop["id"] != filters["property_id"]:
            return False

        requested_cities = filters.get("cities") or ([filters["city"]] if filters["city"] else [])
        if requested_cities:
            actual = prop["city"].lower()
            if not any(
                requested in actual
                or (requested == "bangalore" and "bengaluru" in actual)
                for requested in requested_cities
            ):
                return False

        if filters["location"] and filters["location"] not in prop["location"].lower():
            return False
        if filters["bedrooms"] is not None and prop["bedrooms"] != filters["bedrooms"]:
            return False
        if filters["bathrooms"] is not None and prop["bathrooms"] != filters["bathrooms"]:
            return False
        if filters["floors"] is not None and prop["floors"] != filters["floors"]:
            return False
        if filters["year_built"] is not None and prop["year_value"] != filters["year_built"]:
            return False
        if filters["min_price"] is not None and prop["price_value"] < filters["min_price"]:
            return False
        if filters["max_price"] is not None and prop["price_value"] > filters["max_price"]:
            return False
        if filters["min_area"] is not None and prop["area_value"] < filters["min_area"]:
            return False
        if filters["max_area"] is not None and prop["area_value"] > filters["max_area"]:
            return False
        if filters["parking"] and filters["sort_by"] != "parking_desc" and not prop["parking_yes"]:
            return False
        if filters["parking_count"] is not None and prop["parking_value"] < filters["parking_count"]:
            return False
        if filters["furnished"] and not self._feature_enabled(prop["features"], "furnished"):
            return False
        if filters["balcony"] and not self._feature_enabled(prop["features"], "balcony"):
            return False
        if filters["featured"] and not self._feature_enabled(prop["features"], "featured"):
            return False
        if filters["luxury"] and not self._contains_any(
            prop["doc"].lower(), ["luxury", "premium", "high-end", "exclusive"]
        ):
            return False

        return True

    def _rank_properties(
        self,
        properties: list[dict[str, Any]],
        filters: dict[str, Any],
    ) -> list[dict[str, Any]]:
        sort_by = filters["sort_by"]

        if sort_by == "price_asc":
            properties.sort(key=lambda item: item["price_value"])
        elif sort_by == "price_desc":
            properties.sort(key=lambda item: item["price_value"], reverse=True)
        elif sort_by == "area_asc":
            properties.sort(key=lambda item: item["area_value"])
        elif sort_by == "area_desc":
            properties.sort(key=lambda item: item["area_value"], reverse=True)
        elif sort_by == "year_desc":
            properties.sort(key=lambda item: item["year_value"], reverse=True)
        elif sort_by == "parking_desc":
            properties.sort(key=lambda item: item["parking_value"], reverse=True)
            if properties:
                highest = properties[0]["parking_value"]
                # Keep every tied maximum (within the global context bound).
                return [
                    item for item in properties if item["parking_value"] == highest
                ][: self.MAX_CONTEXT_PROPERTIES]

        return properties[: filters["top_k"]]

    @staticmethod
    def _is_real_estate_query(query: str) -> bool:
        terms = [
            "property", "real estate", "home", "house", "flat", "apartment",
            "listing", "buy", "sell", "rent", "lease", "budget", "price",
            "sqft", "area", "bathroom", "bedroom", "bhk", "parking", "loan",
            "mortgage", "investment", "emi", "amenities", "recommend", "find",
            "search", "compare", "comparison", "suggest", "available",
            "furnished", "balcony", "location", "city", "under", "below",
            "within", "lakh", "lakhs", "lac", "crore", "crores", "cr",
            "cheapest", "most", "maximum", "highest", "parking spaces",
        ]
        q = query.lower()
        locations = [
            "whitefield", "jayanagar", "hsr layout", "electronic city", "aundh",
            "baner", "kukatpally", "hitec city", "koramangala", "bellandur",
            "bandra", "thane", "malad", "juhu",
        ]
        return (
            bool(re.search(r"\d+\s*(?:bhk|bed(?:room)?s?)", q))
            or any(term in q for term in terms)
            or any(location in q for location in locations)
        )

    def _format_property_summary(
        self,
        properties: list[dict[str, Any]],
        query: str,
    ) -> str:
        if not properties:
            return "I couldn't find a property matching those requirements in the current listings."

        q = query.lower()
        lines: list[str] = []
        comparison_query = self.parse_query(query)["compare"]

        if comparison_query:
            lines.append("Here are the matching properties for comparison:")
        elif "cheapest" in q or "affordable" in q or "budget" in q:
            lines.append("Here are the most affordable matching properties:")
        elif "largest" in q or "spacious" in q or "biggest" in q:
            lines.append("Here are the most spacious matching properties:")
        elif "newest" in q or "latest" in q:
            lines.append("Here are the newest matching properties:")
        else:
            lines.append(f"I found {len(properties)} matching properties:")

        # For multi-city comparisons, keep each city's listings together so a
        # user can compare like-for-like results without guessing which city a
        # numbered item belongs to.
        parsed_query = self.parse_query(query)
        grouped = bool(comparison_query and len(parsed_query.get("cities", [])) > 1)
        entries = properties
        if grouped:
            entries = []
            for city in parsed_query["cities"]:
                entries.extend([prop for prop in properties if city in prop["city"].lower() or (city == "bangalore" and "bengaluru" in prop["city"].lower())])

        current_city = None
        for index, prop in enumerate(entries, 1):
            if grouped:
                city_key = prop["city"].lower()
                if city_key != current_city:
                    lines.extend(["", f"{prop['city']}:"])
                    current_city = city_key
            lines.extend(
                [
                    "",
                    f"{index}. {prop['title']}",
                    f"   📍 Location: {prop['location']}, {prop['city']}",
                    f"   💰 {prop['price']}",
                    f"   🛏 {prop['bedrooms']} BHK | 🛁 {prop['bathrooms']} bath | 📐 {prop['area']}",
                    f"   🚗 Parking: {'Yes' if prop['parking_yes'] else 'No'} ({prop['parking_value']} spaces)",
                ]
            )
            if "furnished" in q:
                lines.append("   🛋 Furnished: Yes")
            if "balcony" in q:
                lines.append("   🌇 Balcony: Yes")

            if prop["description"] and prop["description"].lower() != "n/a":
                lines.append(f"   ✨ {prop['description']}")

        if comparison_query:
            lowest = min(properties, key=lambda item: item["price_value"])
            highest = max(properties, key=lambda item: item["price_value"])
            if lowest["id"] != highest["id"]:
                lines.extend([
                    "",
                    f"Grounded comparison: {lowest['title']} is listed at {lowest['price']}; "
                    f"{highest['title']} is listed at {highest['price']}."
                ])

        return "\n".join(lines)

    def _generate_with_groq(
        self,
        query: str,
        properties: list[dict[str, Any]],
    ) -> str | None:
        if self.client_ai is None or not properties:
            return None

        context = "\n\n".join(
            prop["doc"] for prop in properties[: self.MAX_CONTEXT_PROPERTIES]
        )

        system_prompt = (
            "You are the AI Real Estate Assistant for a property listing platform. "
            "Use ONLY the supplied property context for listing facts. "
            "Never invent a property, price, location, feature, availability, or statistic. "
            "Do not infer a feature that is not explicitly present in the context. "
            "If the context does not contain the requested fact, say that it is not available in the listings. "
            "When comparing properties, compare only the properties supplied in the context. "
            "Keep the answer concise and practical. "
            "Do not mention RAG, ChromaDB, prompts, or implementation details."
        )

        user_prompt = f"User request:\n{query}\n\nVerified property context:\n{context}"

        try:
            completion = self.client_ai.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_completion_tokens=700,
                include_reasoning=False,
            )
            answer = completion.choices[0].message.content
            return answer.strip() if answer else None
        except Exception:
            return None

    def generate_response(
        self,
        query: str,
        retrieved: list[dict[str, Any]],
    ) -> tuple[str, list[dict[str, Any]]]:
        if not self._is_real_estate_query(query):
            return (
                "I’m your AI Real Estate Assistant. Ask me about properties, budgets, cities, BHK, "
                "amenities, comparisons, buying, renting, or investment considerations.",
                [],
            )

        filters = self.parse_query(query)

        parsed: list[dict[str, Any]] = []
        seen_ids: set[int] = set()
        for item in retrieved:
            prop = self._extract_property(item["document"])
            if prop["id"] in seen_ids:
                continue
            if self._passes_filters(prop, filters):
                prop["distance"] = item.get("distance", 0.0)
                parsed.append(prop)
                seen_ids.add(prop["id"])

        ranked = self._rank_properties(parsed, filters)

        if not ranked:
            return (
                "I couldn't find a property matching those requirements in the current listings.",
                [],
            )

        # Comparisons and numeric rankings are rendered deterministically so
        # city grouping, ties, and factual claims cannot be changed by model
        # wording. Groq remains available for ordinary grounded searches.
        answer = None
        if not filters["compare"] and filters["sort_by"] != "parking_desc":
            answer = self._generate_with_groq(query, ranked)
        if not answer:
            answer = self._format_property_summary(ranked, query)

        context = [
            {
                "document": prop["doc"],
                "metadata": {
                    "property_id": prop["id"],
                    "city": prop["city"],
                    "title": prop["title"],
                },
                "distance": prop.get("distance", 0.0),
            }
            for prop in ranked
        ]

        return answer, context


rag_service = RAGService()
