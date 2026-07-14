"""Seed sample properties and reindex ChromaDB."""

from app.database import Base, SessionLocal, engine
from app.models import Property, User, UserRole
from app.services.rag_service import rag_service
from app.utils.security import hash_password

SAMPLE_PROPERTIES = [
    {
        "title": "Luxury 3BHK in Bandra",
        "description": "Spacious sea-facing apartment with modern amenities.",
        "price": 18500000,
        "bedrooms": 3,
        "bathrooms": 3,
        "area_sqft": 1450,
        "floors": 2,
        "year_built": 2018,
        "parking": 2,
        "city": "Mumbai",
        "location": "Bandra",
        "features": {"balcony": True, "gym": True},
    },
    {
        "title": "Modern Villa in Koregaon Park",
        "description": "Independent villa with private garden and terrace.",
        "price": 22000000,
        "bedrooms": 4,
        "bathrooms": 4,
        "area_sqft": 2800,
        "floors": 2,
        "year_built": 2015,
        "parking": 3,
        "city": "Pune",
        "location": "Koregaon Park",
        "features": {"garden": True, "terrace": True},
    },
    {
        "title": "2BHK Apartment in Koramangala",
        "description": "Well-connected apartment near tech parks.",
        "price": 9500000,
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1100,
        "floors": 1,
        "year_built": 2020,
        "parking": 1,
        "city": "Bangalore",
        "location": "Koramangala",
        "features": {"furnished": True},
    },
    {
        "title": "Premium Flat in Saket",
        "description": "High-rise flat with city skyline views.",
        "price": 14000000,
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqft": 1600,
        "floors": 1,
        "year_built": 2017,
        "parking": 2,
        "city": "Delhi",
        "location": "Saket",
        "features": {"pool": True},
    },
    {
        "title": "Gachibowli Tech Hub Home",
        "description": "Ideal for IT professionals, close to offices.",
        "price": 7800000,
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1050,
        "floors": 1,
        "year_built": 2021,
        "parking": 1,
        "city": "Hyderabad",
        "location": "Gachibowli",
        "features": {"security": True},
    },
    {
        "title": "Adyar Family Residence",
        "description": "Quiet neighborhood with schools nearby.",
        "price": 11200000,
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqft": 1350,
        "floors": 1,
        "year_built": 2016,
        "parking": 1,
        "city": "Chennai",
        "location": "Adyar",
        "features": {"near_school": True},
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@realestate.com").first()
        if not admin:
            admin = User(
                email="admin@realestate.com",
                password_hash=hash_password("admin123"),
                full_name="Platform Admin",
                role=UserRole.admin,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

        existing = db.query(Property).count()
        if existing == 0:
            for data in SAMPLE_PROPERTIES:
                prop = Property(**data, created_by=admin.id)
                db.add(prop)
            db.commit()
            print(f"Seeded {len(SAMPLE_PROPERTIES)} properties.")
        else:
            print(f"Skipping property seed — {existing} properties already exist.")

        count = rag_service.reindex_all(db)
        print(f"Indexed {count} properties in ChromaDB.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
