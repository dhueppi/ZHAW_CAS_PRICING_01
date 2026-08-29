from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd
import requests
import statsmodels.api as sm


API_BASE = "https://world.openfoodfacts.org"
API_SEARCH_URL = "https://world.openfoodfacts.org/api/v2/search"
OPEN_PRICES_PRODUCT_URL = "https://prices.openfoodfacts.org/api/v1/products"
OPEN_PRICES_PRICE_URL = "https://prices.openfoodfacts.org/api/v1/prices"

def request_json(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; openfood_checker/1.0; +https://example.com)"}
    response = requests.get(url, params=params, headers=headers, timeout=30)
    if response.status_code == 403:
        raise PermissionError("Open Food Facts blocked the request; retry later or use a different endpoint.")
    response.raise_for_status()
    return response.json()


@dataclass
class ProductMatch:
    code: str
    product_name: str
    brand: str
    category: str
    quantity: str
    generic_name: str
    packaging: str
    labels: str
    countries: str
    stores: str
    price: Optional[float]
    score: float
    source: str = "openfoodfacts"

    def as_row(self) -> Dict[str, Any]:
        return asdict(self)


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def clean_product_name(name: str) -> str:
    value = normalize_text(name)
    value = value.replace("\n", " ")
    value = re.sub(r"\s+", " ", value)
    return value


def extract_quantity(raw: Any) -> str:
    text = normalize_text(raw)
    if not text:
        return ""
    return text


def get_product_search_url(query: str, page_size: int = 10) -> str:
    return API_SEARCH_URL


def fetch_search_results(query: str, page_size: int = 10) -> List[Dict[str, Any]]:
    params = {
        "search_terms": query,
        "page_size": page_size,
        "sort_by": "unique_scans_n",
        "fields": "product_name,brands,quantity,categories,generic_name,packaging,labels,countries,stores,code",
    }
    payload = request_json(API_SEARCH_URL, params)
    products = payload.get("products", [])
    return products


def fetch_barcode_product(barcode: str) -> Dict[str, Any]:
    value = clean_product_name(barcode)
    if not re.fullmatch(r"\d{8,20}", value):
        raise ValueError(f"'{barcode}' is not a valid barcode.")
    url = f"{API_BASE}/api/v2/product/{value}.json"
    payload = request_json(url, {})
    product = payload.get("product")
    if not product:
        raise ValueError(f"No product found for barcode {value}.")
    return product


def _coerce_price(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    cleaned = text.replace("€", "").replace("£", "").replace("$", "")
    cleaned = cleaned.replace(" ", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _extract_country(location: Dict[str, Any]) -> str:
    if not isinstance(location, dict):
        return ""
    osm_display = location.get("osm_display_name") or location.get("display_name") or ""
    if osm_display:
        parts = [part.strip() for part in osm_display.split(",") if part.strip()]
        if parts:
            return parts[-1]
    return normalize_text(location.get("country"))


def normalize_open_prices_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    product = raw.get("product") if isinstance(raw.get("product"), dict) else {}
    location = raw.get("location") if isinstance(raw.get("location"), dict) else {}
    product_name = normalize_text(raw.get("product_name") or product.get("product_name") or raw.get("name"))
    brand = normalize_text(raw.get("brand") or product.get("brands") or product.get("brand"))
    category = ", ".join(str(tag).replace("en:", "") for tag in product.get("categories_tags", []) if tag)
    if not category:
        category = normalize_text(raw.get("category_tag") or product.get("categories") or "")
    quantity = normalize_text(raw.get("receipt_quantity") or raw.get("product_quantity") or product.get("quantity") or raw.get("quantity"))
    date_value = raw.get("date") or raw.get("created") or raw.get("updated")
    if isinstance(date_value, str):
        date_value = date_value.split("T")[0]
    price_value = _coerce_price(raw.get("price"))
    country = _extract_country(location)
    row = {
        "product_code": normalize_text(raw.get("product_code") or product.get("code") or raw.get("code")),
        "product_name": product_name,
        "brand": brand,
        "category": category,
        "quantity": quantity,
        "price": price_value,
        "price_numeric": price_value,
        "currency": normalize_text(raw.get("currency") or product.get("currency") or ""),
        "date": normalize_text(date_value),
        "date_created": normalize_text(raw.get("created")),
        "country": country,
        "location_name": normalize_text(location.get("osm_name") or location.get("name") or raw.get("location_name") or ""),
        "source": "openprices",
    }
    if not row["product_name"]:
        row["product_name"] = normalize_text(product.get("product_name"))
    if not row["brand"]:
        row["brand"] = normalize_text(product.get("brands"))
    return row


def fetch_open_prices_by_barcode(barcode: str, limit: int = 100) -> List[Dict[str, Any]]:
    value = clean_product_name(barcode)
    if not re.fullmatch(r"\d{8,20}", value):
        raise ValueError(f"'{barcode}' is not a valid barcode.")

    rows: List[Dict[str, Any]] = []
    page = 1
    while True:
        payload = request_json(OPEN_PRICES_PRICE_URL, {"product_code": value, "page": page})
        items = payload.get("items", [])
        if not items:
            break
        for item in items:
            rows.append(normalize_open_prices_record(item))
            if limit and len(rows) >= limit:
                return rows[:limit]
        total_pages = int(payload.get("pages") or 1)
        if page >= total_pages:
            break
        page += 1

    return rows


def fetch_open_prices_product_summary(barcode: str) -> Dict[str, Any]:
    value = clean_product_name(barcode)
    if not re.fullmatch(r"\d{8,20}", value):
        raise ValueError(f"'{barcode}' is not a valid barcode.")
    payload = request_json(OPEN_PRICES_PRODUCT_URL, {"code": value})
    items = payload.get("items", [])
    if not items:
        raise ValueError(f"No Open Prices product summary found for barcode {value}.")
    product = items[0]
    return product


def score_candidate(reference: str, candidate_name: str, candidate_brand: str, category: str) -> float:
    ref = clean_product_name(reference).lower()
    cand = clean_product_name(candidate_name).lower()
    cand_brand = clean_product_name(candidate_brand).lower()
    category = clean_product_name(category).lower()

    score = 0.0
    ref_tokens = set(re.findall(r"[a-z0-9]+", ref))
    cand_tokens = set(re.findall(r"[a-z0-9]+", cand))
    overlap = len(ref_tokens & cand_tokens)
    score += overlap * 2.5

    if cand_brand and cand_brand in ref:
        score += 2.0
    if category and category in ref:
        score += 1.0

    if "latte" in cand and "latte" in ref:
        score += 2.0
    if "caffe" in cand and "caffe" in ref:
        score += 2.0
    if "330" in cand and "330" in ref:
        score += 1.5

    return score


def _build_search_result(product: Dict[str, Any], query: str) -> Dict[str, Any]:
    name = clean_product_name(product.get("product_name", product.get("product_name_en", "")))
    if not name:
        return {}
    brand = clean_product_name(product.get("brands", ""))
    category = clean_product_name(product.get("categories", ""))
    quantity = extract_quantity(product.get("quantity", ""))
    score = score_candidate(query, name, brand, category)
    return {
        "code": str(product.get("code", "")),
        "product_name": name,
        "brand": brand,
        "category": category,
        "quantity": quantity,
        "generic_name": clean_product_name(product.get("generic_name", "")),
        "packaging": clean_product_name(product.get("packaging", "")),
        "labels": clean_product_name(product.get("labels", "")),
        "countries": clean_product_name(product.get("countries", "")),
        "stores": clean_product_name(product.get("stores", "")),
        "price": product.get("price"),
        "score": score,
        "source": "openfoodfacts",
    }


def generate_search_variants(query: str) -> List[str]:
    q = clean_product_name(query).lower()
    variants = []
    if not q:
        return variants

    variants.append(q)
    if "cocacola" in q or "coca" in q or "cola" in q:
        variants.extend(["coca cola", "coca-cola", "cola", "soft drink cola"])
    if "nutella" in q:
        variants.extend(["nutella", "nutella spread", "hazelnut spread", "nutella cream"])
    if "emmi" in q or "latte" in q:
        variants.extend(["emmi caffe latte", "caffe latte", "latte", "coffee latte"])

    seen = set()
    ordered = []
    for variant in variants:
        normalized = clean_product_name(variant).lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            ordered.append(normalized)
    return ordered


def normalize_search_results(raw: Iterable[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    results = []
    for product in raw:
        row = _build_search_result(product, query)
        if row:
            results.append(row)

    if not results:
        raise ValueError(f"No valid product matches returned for '{query}'. Aborting hedonic analysis.")

    if all((item.get("price") in (None, "") for item in results)):
        raise ValueError(f"No valid product prices found for '{query}'. Aborting hedonic analysis.")

    results.sort(key=lambda item: item["score"], reverse=True)
    return results


def search_products_by_barcode(barcode: str, page_size: int = 10) -> List[Dict[str, Any]]:
    product = fetch_barcode_product(barcode)
    row = _build_search_result(product, barcode)
    if not row:
        raise ValueError(f"Barcode {barcode} returned no usable product record.")
    return [row]


def search_products(query: str, page_size: int = 10) -> List[Dict[str, Any]]:
    value = clean_product_name(query)
    if re.fullmatch(r"\d{8,20}", value):
        return search_products_by_barcode(value, page_size=page_size)

    variants = generate_search_variants(query)
    last_error = None
    for variant in variants:
        try:
            raw = fetch_search_results(variant, page_size=page_size)
            results = normalize_search_results(raw, variant)
            if results:
                return results[:page_size]
        except Exception as exc:
            last_error = exc
    if last_error is not None:
        raise ValueError(f"No valid product prices found for '{query}'. Suggested search terms: {', '.join(variants)}. Aborting hedonic analysis.") from last_error
    raise ValueError(f"No valid product prices found for '{query}'. Aborting hedonic analysis.")


def choose_match(reference_product: str, candidates: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    return candidates[:limit]


def build_regression_frame(rows: Iterable[Dict[str, Any]]) -> pd.DataFrame:
    data = list(rows)
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df["price"] = pd.to_numeric(df.get("price", pd.Series([None] * len(df))), errors="coerce")
    df = df.dropna(subset=["price"]).copy()
    if df.empty:
        return df

    df["brand"] = df["brand"].fillna("Unknown")
    df["quantity"] = df["quantity"].fillna("")
    df["category"] = df["category"].fillna("Unknown")
    df["is_latte"] = df.get("is_latte", 0).fillna(0).astype(int)
    df["is_organic"] = df.get("is_organic", 0).fillna(0).astype(int)
    df["is_coffee"] = df.get("is_coffee", 0).fillna(0).astype(int)

    df = pd.get_dummies(df, columns=["brand"], prefix="brand", drop_first=False)
    df = pd.get_dummies(df, columns=["category"], prefix="category", drop_first=False)
    return df


def fit_hedonic_model(df: pd.DataFrame) -> sm.regression.linear_model.RegressionResultsWrapper:
    if df.empty:
        raise ValueError("No rows available for the hedge model.")

    required_columns = ["price"]
    for col in ["is_latte", "is_organic", "is_coffee"]:
        if col not in df.columns:
            df[col] = 0
        required_columns.append(col)

    drop_cols = ["product_name", "code", "generic_name", "packaging", "labels", "countries", "stores", "source", "score", "quantity"]
    feature_cols = [col for col in df.columns if col not in drop_cols + ["price"]]
    if "brand_Unknown" in feature_cols:
        feature_cols.remove("brand_Unknown")
    if "category_Unknown" in feature_cols:
        feature_cols.remove("category_Unknown")

    X = df[feature_cols].copy()
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0).astype(float)
    X = sm.add_constant(X)
    y = pd.to_numeric(df["price"], errors="coerce").fillna(0)
    model = sm.OLS(y, X).fit()
    return model


def export_rows_to_csv(rows: Iterable[Dict[str, Any]], path: str | Path) -> Path:
    out = Path(path)
    rows = list(rows)
    if not rows:
        raise ValueError("No rows to export.")
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return out


def run_analysis(reference_product: str, product_limit: int = 10) -> Dict[str, Any]:
    if re.fullmatch(r"\d{8,20}", clean_product_name(reference_product)):
        raw_prices = fetch_open_prices_by_barcode(reference_product, limit=product_limit)
        if not raw_prices:
            raise ValueError(f"No valid product prices found for '{reference_product}'. Aborting hedonic analysis.")

        rows = []
        for item in raw_prices:
            product_name = item.get("product_name") or reference_product
            row = {
                "product_name": product_name,
                "brand": item.get("brand"),
                "category": item.get("category"),
                "quantity": item.get("quantity"),
                "price": item.get("price"),
                "is_latte": 1 if "latte" in (product_name + " " + (item.get("category") or "")).lower() else 0,
                "is_organic": 1 if "bio" in (product_name + " " + (item.get("country") or "")).lower() else 0,
                "is_coffee": 1 if any(token in (product_name + " " + (item.get("category") or "")).lower() for token in ["coffee", "caffe", "latte"]) else 0,
                "source": item.get("source", "openprices"),
                "date": item.get("date"),
                "country": item.get("country"),
                "location_name": item.get("location_name"),
                "currency": item.get("currency"),
            }
            rows.append(row)

        df = build_regression_frame(rows)
        if df.empty:
            return {
                "reference_product": reference_product,
                "candidates": raw_prices,
                "model_summary": "No usable data captured for regression.",
                "regression_data": [],
            }

        model = fit_hedonic_model(df)
        summary = model.summary()
        return {
            "reference_product": reference_product,
            "candidates": raw_prices,
            "model_summary": summary.as_text(),
            "regression_data": df.to_dict(orient="records"),
        }

    candidates = search_products(reference_product, page_size=product_limit)
    chosen = choose_match(reference_product, candidates, limit=product_limit)

    rows = []
    for item in chosen:
        row = {
            "product_name": item["product_name"],
            "brand": item["brand"],
            "category": item["category"],
            "quantity": item["quantity"],
            "price": item.get("price"),
            "is_latte": 1 if "latte" in (item["product_name"] + " " + item["category"]).lower() else 0,
            "is_organic": 1 if "bio" in (item["product_name"] + " " + item["labels"]).lower() else 0,
            "is_coffee": 1 if any(token in (item["product_name"] + " " + item["category"]).lower() for token in ["coffee", "caffe", "latte"]) else 0,
            "source": item["source"],
            "score": item["score"],
        }
        rows.append(row)

    df = build_regression_frame(rows)
    if df.empty:
        return {
            "reference_product": reference_product,
            "candidates": chosen,
            "model_summary": "No usable data captured for regression.",
            "regression_data": [],
        }

    model = fit_hedonic_model(df)
    summary = model.summary()
    return {
        "reference_product": reference_product,
        "candidates": chosen,
        "model_summary": summary.as_text(),
        "regression_data": df.to_dict(orient="records"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Search a product by barcode or by text and run a simple hedonic price analysis.")
    parser.add_argument("query", nargs="?", default="5449000000996", help="Barcode or text search term for the product to analyze")
    parser.add_argument("--limit", type=int, default=10, help="Number of close matches to consider")
    parser.add_argument("--csv", type=str, default=None, help="Optional output CSV file. If omitted, nothing is written to disk.")
    args = parser.parse_args()

    try:
        results = search_products(args.query, page_size=args.limit)
    except ValueError as exc:
        print(f"Error: {exc}")
        suggested = generate_search_variants(args.query)
        if len(suggested) > 1:
            print("Suggested alternatives:")
            for i, suggestion in enumerate(suggested[1:6], start=1):
                print(f"  {i}. {suggestion}")
        raise SystemExit(1) from exc

    print(f"Gefundene Kandidaten für: {args.query}")
    for i, item in enumerate(results[: args.limit], 1):
        print(f"{i}. {item['product_name']} | brand={item['brand']} | qty={item['quantity']} | score={item['score']:.2f}")

    if args.csv:
        out_path = export_rows_to_csv(results, args.csv)
        print(f"CSV exportiert: {out_path}")

    if re.fullmatch(r"\d{8,20}", clean_product_name(args.query)):
        print("\nOpen Prices records:")
        price_records = fetch_open_prices_by_barcode(args.query, limit=args.limit)
        if not price_records:
            print("Keine Open-Prices-Datensätze gefunden.")
        else:
            for i, item in enumerate(price_records[: args.limit], 1):
                print(
                    f"{i}. date={item.get('date') or item.get('date_created') or '-'} | "
                    f"price={item.get('price') if item.get('price') is not None else item.get('price_numeric')} | "
                    f"currency={item.get('currency') or '-'} | "
                    f"country={item.get('country') or '-'} | "
                    f"store={item.get('location_name') or '-'} | "
                    f"source={item.get('source') or '-'}"
                )

    analysis = run_analysis(args.query, product_limit=args.limit)
    print("\nHedonic model summary:")
    print(analysis["model_summary"])


if __name__ == "__main__":
    main()
