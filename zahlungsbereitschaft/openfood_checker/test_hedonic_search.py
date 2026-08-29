import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import hedonic_product_checker as hpc


def test_search_candidates_returns_products():
    results = hpc.normalize_search_results([
        {"product_name": "Emmi Caffe Latte 330ml", "brands": "Emmi", "categories": "Coffee drinks", "quantity": "330 ml", "generic_name": "Caffe latte", "packaging": "Plastic bottle", "labels": "Bio", "countries": "Switzerland", "stores": "Coop", "code": "p1", "price": 2.95},
        {"product_name": "Aldi Latte 330ml", "brands": "Aldi", "categories": "Coffee drinks", "quantity": "330 ml", "generic_name": "Caffe latte", "packaging": "Plastic bottle", "labels": "", "countries": "Switzerland", "stores": "Aldi", "code": "p2", "price": 2.40},
    ], "Emmi Caffe Latte")
    assert isinstance(results, list)
    assert len(results) >= 1
    first = results[0]
    assert "product_name" in first
    assert "brand" in first


def test_no_valid_prices_raises_value_error():
    try:
        hpc.normalize_search_results([
            {"product_name": "Random product", "brands": "X", "categories": "Coffee", "quantity": "330 ml", "generic_name": "", "packaging": "", "labels": "", "countries": "", "stores": "", "code": "p1", "price": None},
        ], "Nutella")
        assert False, "Expected ValueError for missing prices"
    except ValueError as exc:
        assert "No valid product prices" in str(exc)


def test_build_regression_data_uses_prices_and_attributes():
    data = [
        {"product_name": "A", "brand": "Emmi", "quantity": "330 ml", "category": "coffee", "price": 2.80, "is_coffee": 1, "is_latte": 1, "is_organic": 0},
        {"product_name": "B", "brand": "Migros", "quantity": "330 ml", "category": "coffee", "price": 2.20, "is_coffee": 1, "is_latte": 0, "is_organic": 0},
        {"product_name": "C", "brand": "Coop", "quantity": "500 ml", "category": "coffee", "price": 3.10, "is_coffee": 1, "is_latte": 1, "is_organic": 1},
    ]
    df = hpc.build_regression_frame(data)
    assert set(["brand_Emmi", "brand_Migros", "brand_Coop"]).issubset(df.columns)
    assert "price" in df.columns
    assert len(df) == 3


def test_run_analysis_requires_valid_prices():
    try:
        hpc.run_analysis("Nutella", product_limit=3)
        assert False, "Expected run_analysis to abort when no valid prices are available"
    except ValueError as exc:
        assert "No valid product prices" in str(exc)


def test_generate_search_variants_for_common_products():
    variants = hpc.generate_search_variants("CocaCola")
    assert any("coca cola" in variant for variant in variants)
    assert "cola" in variants
    variants_nutella = hpc.generate_search_variants("Nutella")
    assert any("nutella spread" in variant for variant in variants_nutella)


def test_fetch_open_prices_for_barcode_returns_records():
    records = hpc.fetch_open_prices_by_barcode("5449000131836")
    assert isinstance(records, list)
    assert len(records) >= 1
    first = records[0]
    assert "price" in first or "price_numeric" in first
    assert "date" in first or "date_created" in first
