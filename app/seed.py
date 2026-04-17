from app.database import engine, Base, SessionLocal
from app.models import Product
from sqlalchemy import text
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings
from pinecone import Pinecone
import os

os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview"
)
pc = Pinecone(
    api_key=settings.PINECONE_API_KEY,
)
index = pc.Index("personal-care-products")
def seed_data():
    # First, create all tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    if db.query(Product).count() == 0:
        products = [
            Product(
                name="Lumina Glow Face Wash",
                category="Skincare",
                description="A gentle daily cleanser with vitamin C and aloe vera.",
                benefits="Brightens skin, removes impurities without stripping natural oils.",
                price=15.99
            ),
            Product(
                name="AquaSurge Hydrating Moisturizer",
                category="Skincare",
                description="Lightweight hyaluronic acid moisturizer.",
                benefits="24-hour hydration, plumps skin, reduces fine lines.",
                price=24.50
            ),
            Product(
                name="Velvet Crown Shampoo",
                category="Haircare",
                description="Sulfate-free keratin shampoo for all hair types.",
                benefits="Strengthens hair roots, adds shine, prevents frizz.",
                price=18.00
            ),
            Product(
                name="Aura Shield Sunscreen SPF 50",
                category="Skincare",
                description="Broad-spectrum mineral sunscreen.",
                benefits="Protects against outside UV rays, non-comedogenic, zero white cast.",
                price=22.00
            ),
            Product(
                name="Beard Maestro Nourishing Oil",
                category="Men's Grooming",
                description="Blend of argan and jojoba oils for beard care.",
                benefits="Softens beard hair, soothes skin, promotes healthy growth.",
                price=19.99
            )
        ]
        db.add_all(products)
        db.commit()
    
    db.close()

def upload_products():
    stats = index.describe_index_stats()
    if stats.get("total_vector_count", 0) > 0:
        print("✅ Pinecone already has data. Skipping upload.")
        return
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name, description, category, price, benefits FROM products"))
        rows = result.fetchall()
        vectors = []

        for row in rows:
            text_data = f"{row.name} {row.category} {row.description or ''}"
            vector = embeddings.embed_query(text_data)
            vectors.append({
                "id": str(row.id),
                "values": vector,
                "metadata": {
                    "name": row.name,
                    "description": row.description,
                    "category": row.category,
                    "price": row.price,
                    "benefits": row.benefits
                    
                }
            })

        index.upsert(vectors)
if __name__ == "__main__":
    seed_data()
