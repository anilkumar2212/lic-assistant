import os
import time
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote

# ================= CONFIG =================
PLAN_CATEGORIES = {
    "endowment-plans": "https://licindia.in/web/guest/endowment-plans",
    "whole-life-plans": "https://licindia.in/web/guest/whole-life-plans",
    "money-back-plans": "https://licindia.in/web/guest/money-back-plans",
    "term-assurance-plans": "https://licindia.in/web/guest/term-assurance-plans",
    "unit-linked-plans": "https://licindia.in/web/guest/unit-linked-plans",
    "pension-plan": "https://licindia.in/web/guest/pension-plan",
}

PLAN_PREFIX = "https://licindia.in/web/guest/"
DOC_PREFIX = "https://licindia.in/documents/"

BASE_DIR = os.path.join("documents", "lic-plans")
os.makedirs(BASE_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# ================= HELPERS =================
def get_with_retry(url):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            return r
        except Exception as e:
            print(f"⚠️ Attempt {attempt}/{MAX_RETRIES} failed: {url}")
            print(f"   Reason: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)

    print(f"❌ Giving up after {MAX_RETRIES} attempts: {url}")
    return None


def sanitize_name(name: str) -> str:
    """Make text safe for folder/file names"""
    name = name.strip()
    name = re.sub(r"[\\/:*?\"<>|]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name


# ================= EXTRACTION =================
def extract_plan_links(category_url):
    """
    Returns:
    {
        plan_url: plan_display_name
    }
    """
    r = get_with_retry(category_url)
    if not r:
        return {}

    soup = BeautifulSoup(r.text, "html.parser")
    plans = {}

    for a in soup.find_all("a", href=True):
        full = urljoin(category_url, a["href"])
        if full.startswith(PLAN_PREFIX) and "lic-s-" in full:  #"lic-sjeevanumang-"
            plan_name = sanitize_name(a.get_text(strip=True))
            plans[full] = plan_name
            print(f"📘 Plan found: {plan_name}")

    return plans


def extract_document_links(plan_url):
    """
    Returns:
    {
        pdf_url: document_display_name
    }
    """
    r = get_with_retry(plan_url)
    if not r:
        return {}

    soup = BeautifulSoup(r.text, "html.parser")
    docs = {}

    for a in soup.find_all("a", href=True):
        full = urljoin(plan_url, a["href"])

        if (
            full.startswith(DOC_PREFIX)
            and ".pdf" in full.lower()
            and not full.lower().endswith("-pop")
        ):
            doc_name = sanitize_name(a.get_text(" ", strip=True))
            if not doc_name.lower().endswith(".pdf"):
                doc_name += ".pdf"

            docs[full] = doc_name
            print(f"📄 Document found: {doc_name}")

    return docs


# ================= MAIN =================
for category, category_url in PLAN_CATEGORIES.items():
    print(f"\n📂 CATEGORY: {category}")

    category_dir = os.path.join(BASE_DIR, category)
    os.makedirs(category_dir, exist_ok=True)

    plan_links = extract_plan_links(category_url)
    print(f"✅ Found {len(plan_links)} plans")

    for plan_url, plan_name in plan_links.items():
        plan_dir = os.path.join(category_dir, plan_name)
        os.makedirs(plan_dir, exist_ok=True)

        print(f"\n➡️ Plan: {plan_name}")

        doc_links = extract_document_links(plan_url)
        print(f"📄 Documents found: {len(doc_links)}")

        for doc_url, doc_name in doc_links.items():
            filepath = os.path.join(plan_dir, doc_name)

            if os.path.exists(filepath):
                print(f"⏭️ Already exists: {doc_name}")
                continue

            print(f"⬇️ Downloading: {doc_name}")
            r = get_with_retry(doc_url)
            if not r:
                continue

            if "application/pdf" not in r.headers.get("Content-Type", ""):
                print(f"⚠️ Skipped non-PDF content")
                continue

            with open(filepath, "wb") as f:
                f.write(r.content)

            print(f"✅ Saved: {filepath}")

        time.sleep(1)

print("\n🎉 ALL LIC PLAN DOCUMENTS DOWNLOADED SUCCESSFULLY")
