"""Seed 300 synthetic properties and reindex ChromaDB."""
import random
from app.database import Base, SessionLocal, engine
from app.models import Property, User, UserRole
from app.services.rag_service import rag_service
from app.utils.security import hash_password

random.seed(42)

CITY_DATA={
 "Mumbai":{"locations":["Bandra","Andheri","Powai","Juhu","Malad","Worli","Thane","Dadar"],"base":140000},
 "Delhi":{"locations":["Dwarka","Lajpat Nagar","Saket","Vasant Kunj","Noida","Gurgaon","Shahdara","Saraswati Colony"],"base":110000},
 "Bangalore":{"locations":["Koramangala","Indiranagar","Whitefield","HSR Layout","Bellandur","Electronic City","Marathahalli","Jayanagar"],"base":100000},
 "Pune":{"locations":["Baner","Hinjewadi","Wakad","Koregaon Park","Aundh","Hadapsar","Viman Nagar","Kothrud"],"base":90000},
 "Hyderabad":{"locations":["Gachibowli","HITEC City","Madhapur","Begumpet","Kondapur","Kukatpally","Banjara Hills","Secunderabad"],"base":85000},
 "Chennai":{"locations":["Adyar","Anna Nagar","Velachery","OMR","Tambaram","Porur","Nungambakkam","T Nagar"],"base":80000},
}
TITLES=["Spacious {b}BHK Apartment","Modern {b}BHK Flat","Elegant {b}BHK Residence","Premium {b}BHK Home","Contemporary {b}BHK Villa","Well-Designed {b}BHK Apartment","Luxury {b}BHK Residence","Comfortable {b}BHK Home"]
DESCS=[
"A well-appointed home with natural light, modern finishes, and excellent connectivity to schools, hospitals, and shopping centers.",
"Designed for comfortable family living, this property offers ample ventilation, smart space utilization, and premium amenities.",
"This residence combines contemporary architecture with practical interiors, making it ideal for both living and investment.",
"Set in a prime neighborhood, the property offers serene surroundings, convenient access to transit, and a refined lifestyle.",
"A thoughtfully planned home with spacious rooms, high-quality fixtures, and a welcoming atmosphere for everyday living."
]
def seed():
 Base.metadata.create_all(bind=engine)
 db=SessionLocal()
 try:
  admin=db.query(User).filter(User.email=="admin@realestate.com").first()
  if not admin:
   admin=User(email="admin@realestate.com",password_hash=hash_password("admin123"),full_name="Platform Admin",role=UserRole.admin)
   db.add(admin);db.commit();db.refresh(admin);print("Created admin user")

  existing_count=db.query(Property).count()
  if existing_count > 0:
   repaired=0
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
   return

  db.query(Property).delete();db.commit()
  cities=list(CITY_DATA.keys())
  props=[]
  for i in range(300):
   city=cities[i%len(cities)]
   loc=random.choice(CITY_DATA[city]["locations"])
   b=random.randint(1,5)
   ba=random.randint(0, b-1)
   area=round(random.uniform(800,2600),1)
   floors=random.randint(1,3);park=random.randint(0,2);year=random.randint(1995,2025)
   price=int(CITY_DATA[city]["base"]*area*(1+b*0.08+ba*0.04)/100)
   p=Property(title=random.choice(TITLES).format(b=b),description=random.choice(DESCS),price=price,bedrooms=b,bathrooms=ba,area_sqft=area,floors=floors,year_built=year,parking=park,city=city,location=loc,created_by=admin.id,features={"featured":True,"parking":park>0,"balcony":random.choice([True,False]),"furnished":random.choice([True,False]),"garden":random.choice([True,False]),"gym":random.choice([True,False]),"security":True,"pool":random.choice([True,False])})
   props.append(p)
  db.add_all(props);db.commit();print("Inserted 300 properties")
  c=rag_service.reindex_all(db);print(f"Indexed {c} properties in ChromaDB.")
 finally:
  db.close()
if __name__=="__main__":
 seed()
