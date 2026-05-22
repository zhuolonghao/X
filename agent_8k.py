import sys
sys.path.insert(0, "_src")
from financial_tools import FMPClient

import pandas as pd
from datetime import date
from pathlib import Path

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)

# --- Configuration ---
output_dir = Path("sec_filings_8k") / date.today().strftime("%Y-%m-%d")
output_dir.mkdir(exist_ok=True) 

# --- Instantiate the Classes ---
client1 = FMPClient()
filings_8k = client1.get_data('sec-filings-8k', "ALL")
pd.DataFrame(filings_8k).to_csv(output_dir / "filings_8k.csv", index=False)



from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import requests
from pathlib import Path
import time


SEC_BASE = "https://www.sec.gov"

session = requests.Session()
session.headers.update({
    "User-Agent": "Dave Zhuo zhuo.longhao@gmail.com",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})


def download_sec_html(url, timeout=(5, 20)):
    r = session.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text


def html_to_clean_text(html):
    soup = BeautifulSoup(html, "html.parser")

    # remove junk
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text


def extract_sec_documents(filing_detail_url, filing_detail_html):
    """
    Parse the SEC filing detail page and return document links.
    """
    soup = BeautifulSoup(filing_detail_html, "html.parser")

    docs = []

    table = soup.find("table", class_="tableFile", summary="Document Format Files")
    if not table:
        return docs

    rows = table.find_all("tr")[1:]

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 5:
            continue

        seq = cells[0].get_text(" ", strip=True)
        description = cells[1].get_text(" ", strip=True)
        document_cell = cells[2]
        doc_type = cells[3].get_text(" ", strip=True)
        size = cells[4].get_text(" ", strip=True)

        a = document_cell.find("a")
        if not a:
            continue

        href = a.get("href")
        document_name = a.get_text(" ", strip=True)

        # Important:
        # /ix?doc=/Archives/... is the inline XBRL viewer.
        # We want the real document path after doc=
        if href.startswith("/ix?doc="):
            href = href.replace("/ix?doc=", "")

        full_url = urljoin(SEC_BASE, href)

        docs.append({
            "seq": seq,
            "description": description,
            "document": document_name,
            "type": doc_type,
            "size": size,
            "url": full_url,
        })

    return docs

def has_keywords_in_text(text):
    text = text.lower()

    keywords = [
        "credit agreement",
        "amended and restated credit agreement",
        "loan agreement",
        "revolving credit facility",
        "term loan",
        "entry into a material definitive agreement",
        "item 1.01",
    ]

    return any(keyword in text for keyword in keywords)

def search_actual_sec_documents(filing_detail_url):
    index_html = download_sec_html(filing_detail_url)
    docs = extract_sec_documents(filing_detail_url, index_html)

    results = []

    for doc in docs:
        doc_type = doc["type"].upper()

        # Usually useful documents only
        if doc_type not in ["8-K", "EX-10.1", "EX-10.2", "EX-99.1"]:
            continue

        try:
            html = download_sec_html(doc["url"])
            text = html_to_clean_text(html)
            matched = has_keywords_in_text(text)

            results.append({
                "type": doc["type"],
                "description": doc["description"],
                "document": doc["document"],
                "url": doc["url"],
                "matched": matched,
                "text": text,
            })

            time.sleep(0.2)

        except Exception as e:
            results.append({
                "type": doc["type"],
                "description": doc["description"],
                "document": doc["document"],
                "url": doc["url"],
                "matched": False,
                "text": "",
                "error": str(e),
            })

    return results

all_results = []

for i, filing in enumerate(filings_8k[:4], start=1):
    symbol = filing.get("symbol")
    filing_date = filing.get("filingDate")
    filing_detail_url = filing.get("link")

    print(f"[{i}/{len(filings_8k)}] Assessing: {symbol} | {filing_date}")

    try:
        doc_results = search_actual_sec_documents(filing_detail_url)

        matched_docs = [r for r in doc_results if r["matched"]]

        for r in doc_results:
            all_results.append({
                "symbol": symbol,
                "filingDate": filing_date,
                "filing_detail_url": filing_detail_url,
                "document_type": r.get("type"),
                "document_description": r.get("description"),
                "document_url": r.get("url"),
                "matched": r.get("matched"),
                "error": r.get("error"),
            })

        if matched_docs:
            print(f"  MATCH: {len(matched_docs)} document(s)")
        else:
            print("  No match")

    except Exception as e:
        print(f"  ERROR: {e}")

        all_results.append({
            "symbol": symbol,
            "filingDate": filing_date,
            "filing_detail_url": filing_detail_url,
            "document_type": None,
            "document_description": None,
            "document_url": None,
            "matched": False,
            "error": str(e),
        })

    time.sleep(0.2)

pd.DataFrame(all_results).to_csv(output_dir / "filings_8k_assessment.csv", index=False)

results_df = pd.DataFrame(all_results)
results_df = results_df[results_df["matched"] == True]
results_df = results_df[results_df["document_type"] == "8-K"]
results_df = results_df[["symbol", "filingDate", "filing_detail_url", "document_type"]]
results_df.to_csv(output_dir / "filings_8k_assessment_matched.csv", index=False)

import subprocess
def git_push(message, folder_path):
    try:
        # Add files in the specific output directory
        subprocess.run(["git", "add", folder_path], check=True)
        # Also add any other modified files in the repo
        subprocess.run(["git", "add", "-A"], check=True)
        
        # Check if there are staged changes
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if result.returncode == 0:
            print("No changes to commit")
            return
        
        # Commit with a custom message
        subprocess.run(["git", "commit", "-m", message], check=True)
        # Push to the remote repository
        subprocess.run(["git", "push"], check=True)
        print("Successfully pushed to Git!")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")
git_push("8-K Filings Assessment", output_dir)
