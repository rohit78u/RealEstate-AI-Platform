import random

from app.database import Base, SessionLocal, engine
from app.models import Property

random.seed(42)

CITY_DATA = {
    "Mumbai": {
        "locations": [
            "Bandra",
            "Andheri",
            "Powai",
            "Worli",
            "Malad",
            "Juhu",
            "Thane",
            "Dadar",
        ],
        "base_price": 140000,
    },
    "Delhi": {
        "locations": [
            "Saraswati Colony",
            "Gurgaon",
            "Noida",
            "Dwarka",
            "Saket",
            "Vasant Kunj",
            "Shahdara",
            "Lajpat Nagar",
        ],
        "base_price": 110000,
    },
    "Bangalore": {
        "locations": [
            "Koramangala",
            "Indiranagar",
            "Whitefield",
            "Jayanagar",
            "HSR Layout",
            "Marathahalli",
            "Electronic City",
            "Bellandur",
        ],
        "base_price": 100000,
    },
    "Pune": {
        "locations": [
            "Koregaon Park",
            "Baner",
            "Hinjewadi",
            "Wakad",
            "Kothrud",
            "Viman Nagar",
            "Hadapsar",
            "Aundh",
        ],
        "base_price": 90000,
    },
    "Hyderabad": {
        "locations": [
            "Gachibowli",
            "Madhapur",
            "HITEC City",
            "Kondapur",
            "Banjara Hills",
            "Begumpet",
            "Kukatpally",
            "Secunderabad",
        ],
        "base_price": 85000,
    },
    "Chennai": {
        "locations": [
            "Adyar",
            "Anna Nagar",
            "Velachery",
            "OMR",
            "Tambaram",
            "Porur",
            "Nungambakkam",
            "T Nagar",
        ],
        "base_price": 80000,
    },
}

PROPERTY_TITLES = [
    "Spacious {bedrooms}BHK Apartment",
    "Modern {bedrooms}BHK Flat",
    "Elegant {bedrooms}BHK Residence",
    "Premium {bedrooms}BHK Home",
    "Contemporary {bedrooms}BHK Villa",
    "Well-Designed {bedrooms}BHK Apartment",
    "Luxury {bedrooms}BHK Residence",
    "Comfortable {bedrooms}BHK Home",
]

PROPERTY_DESCRIPTIONS = [
    "A well-appointed home with natural light, modern finishes, and excellent connectivity to schools, hospitals, and shopping centers.",
    "Designed for comfortable family living, this property offers ample ventilation, smart space utilization, and premium amenities.",
    "This residence combines contemporary architecture with practical interiors, making it ideal for both living and investment.",
    "Set in a prime neighborhood, the property offers serene surroundings, convenient access to transit, and a refined lifestyle.",
    "A thoughtfully planned home with spacious rooms, high-quality fixtures, and a welcoming atmosphere for everyday living.",
]


def build_property_payload(index: int, city: str, location: str) -> dict:
    city_data = CITY_DATA[city]
    bedrooms = random.randint(1, 5)
    bathrooms = random.randint(0, bedrooms - 1)
    floors = random.randint(1, 3)
    parking = random.randint(0, 2)
    area_sqft = round(random.uniform(800, 2600), 1)
    year_built = random.randint(1995, 2025)

    price_multiplier = 1.0 + (bedrooms * 0.08) + (bathrooms * 0.04) + (floors * 0.03)
    price = round(city_data["base_price"] * area_sqft * price_multiplier / 100, 2)
    price = int(price)

    title = random.choice(PROPERTY_TITLES).format(bedrooms=bedrooms)
    description = random.choice(PROPERTY_DESCRIPTIONS)
    image_url = f"https://example.com/images/{city.lower().replace(' ', '-')}/{index + 1}.jpg"

    return {
        "title": title,
        "description": description,
        "price": price,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "area_sqft": area_sqft,
        "floors": floors,
        "year_built": year_built,
        "parking": parking,
        "city": city,
        "location": location,
        "features": {
            "featured": True,
            "parking": parking > 0,
            "furnished": random.choice([True, False]),
            "balcony": random.choice([True, False]),
            "image_url": image_url,
        },
    }


def seed_properties(count: int = 300) -> int:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing_count = db.query(Property).count()
        if existing_count > 0:
            repaired = 0
            for prop in db.query(Property).filter(Property.bathrooms >= Property.bedrooms).all():
                prop.bathrooms = 0 if prop.bedrooms <= 1 else prop.bedrooms - 1
                repaired += 1
            for prop in db.query(Property).filter(Property.bathrooms < 0).all():
                prop.bathrooms = 0
                repaired += 1
            if repaired > 0:
                db.commit()
                print(f"Repaired {repaired} existing property bathroom values.")
            print(f"Skipping property seed — {existing_count} properties already exist.")
            return 0

        cities = list(CITY_DATA.keys())
        properties = []

        for index in range(count):
            city = cities[index % len(cities)]
            location = random.choice(CITY_DATA[city]["locations"])
            payload = build_property_payload(index, city, location)
            property_obj = Property(**payload)
            properties.append(property_obj)

        db.add_all(properties)
        db.commit()
        print(f"Inserted {len(properties)} properties.")
        return len(properties)
    finally:
        db.close()


if __name__ == "__main__":
    seed_properties()
