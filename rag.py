import os
import json
import re
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv()

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

session = {
    "stage": None,
    "product": None,
    "category": None
}

with open("products.json", "r") as f:
    products_dataset = json.load(f)

ALL_CATEGORIES = sorted(list(set([p["category"] for p in products_dataset])))

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="products")

if collection.count() == 0:
    ids, docs, metas, embeddings = [], [], [], []

    for p in products_dataset:
        pid = str(p["id"])

        text = f"""
Name: {p['name']}
Category: {p['category']}
Price: {p['price']}
Features: {' '.join(map(str, p.get('features', [])))}
Integrations: {' '.join(map(str, p.get('integrations', [])))}
Support: {p.get('support', 'N/A')}
"""

        ids.append(pid)
        docs.append(text)

        metas.append({
            "id": pid,
            "name": p["name"],
            "category": p["category"],
            "price": p["price"]
        })

        embeddings.append(embed_model.encode(text).tolist())

    collection.add(
        ids=ids,
        documents=docs,
        metadatas=metas,
        embeddings=embeddings
    )

def search_products(query, k=5):
    q_emb = embed_model.encode(query).tolist()
    return collection.query(
        query_embeddings=[q_emb],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

def extract_email(text):
    match = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match[0] if match else None

def extract_name(text):
    match = re.search(r"(?:my name is|i am|i'm)\s+([a-zA-Z]+)", text.lower())
    return match.group(1).capitalize() if match else None

def is_greeting(q):
    return any(w in q for w in ["hi", "hello", "hey", "heyy", "hola"])

def is_purchase(q):
    patterns = [
        "buy",
        "purchase",
        "order",
        "make order",
        "i want to buy",
        "i want to purchase",
        "i want to order"
    ]
    return any(p in q for p in patterns)

def is_category_query(q):
    patterns = [
        "type", "types",
        "category", "categories",
        "what do you offer",
        "what do you have",
        "products do you have",
        "show products"
    ]
    return any(p in q for p in patterns)

def is_detail_request(q):
    patterns = [
        "full details",
        "all details",
        "show full",
        "complete info",
        "tell me more",
        "more details",
        "details of",
        "about "
    ]
    return any(p in q for p in patterns)

def get_product_by_name(name):
    for p in products_dataset:
        if p["name"].lower() == name.lower():
            return p
    return None

def save_lead(email, product=None):
    data = []

    if os.path.exists("leads.json"):
        with open("leads.json", "r") as f:
            data = json.load(f)

    data.append({
        "email": email,
        "product": product if product else "unknown"
    })

    with open("leads.json", "w") as f:
        json.dump(data, f, indent=2)

def format_summary(p):
    return f"""
Name: {p.get('name')}
Category: {p.get('category')}
Users: {p.get('users', 'N/A')}

Features:
- {chr(10).join(p.get('features', [])[:4])}

Support: {p.get('support')}
"""

def agent(query):

    global session
    q = query.lower().strip()

    email = extract_email(q)

    if email and session["stage"] == "awaiting_email":
        product = session.get("product")
        category = session.get("category")

        save_lead(email=email, product=product)

        session["stage"] = None
        session["product"] = None
        session["category"] = None

        return {
            "intent": "lead",
            "response": f"Our team will contact you soon on product: {product} 🚀",
            "tool": "lead_saved"
        }

    if is_purchase(q):
        results = search_products(q)
        metas = results.get("metadatas", [[]])[0]

        best_product = metas[0]["name"] if metas else "unknown"
        best_category = metas[0]["category"] if metas else "unknown"

        session["stage"] = "awaiting_email"
        session["product"] = best_product
        session["category"] = best_category

        return {
            "intent": "purchase",
            "response": f"Great 👍 You want to buy: {best_product}. Please provide your email.",
            "tool": "purchase_flow"
        }

    if is_greeting(q):
        return {
            "intent": "greeting",
            "response": "Hey! I’m your SaaS assistant. Ask me about products, pricing, or categories.",
            "tool": "chat"
        }

    if is_category_query(q):
        return {
            "intent": "categories",
            "response": "We offer these product categories:\n\n" + "\n".join(ALL_CATEGORIES),
            "tool": "db_only"
        }

    results = search_products(q)
    metas = results.get("metadatas", [[]])[0]

    if not metas:
        return {
            "intent": "fallback",
            "response": "I couldn’t find that in our catalog.",
            "tool": "safe_fallback"
        }

    best_product_name = metas[0]["name"]
    full_product = get_product_by_name(best_product_name)

    if is_detail_request(q):
        return {
            "intent": "product_detail",
            "response": full_product,
            "tool": "full_json"
        }

    return {
        "intent": "product_search",
        "response": format_summary(full_product),
        "product": full_product.get("name"),
        "category": full_product.get("category"),
        "tool": "summary_view"
    }