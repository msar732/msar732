#!/usr/bin/env python3

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import sys


# Single-file implementation: MotorPricePredictor, RecommendationEngine, CLI


@dataclass
class MotorListing:
    id: int
    title: str
    make: str
    year: int
    mileage: float
    engine_size: float
    fuel_type: str  # petrol, diesel, electric, hybrid
    transmission: str  # manual, automatic
    doors: int
    condition: str  # poor, fair, good, excellent
    price: float
    state: str = ""
    district: str = ""


class MotorPricePredictor:
    """Heuristic motor price predictor (no external dependencies).
    This is a simple rule-based model intended to run offline.
    """

    def __init__(self):
        self.make_baseline: Dict[str, float] = {
            'Toyota': 700000,
            'Honda': 650000,
            'Hyundai': 600000,
            'Maruti': 550000,
            'Tata': 600000,
            'Mahindra': 650000,
            'BMW': 2500000,
            'Mercedes': 3000000,
            'Audi': 2800000,
            'Kia': 650000,
            'Skoda': 900000,
            'Volkswagen': 950000,
        }
        self.fuel_adjust: Dict[str, float] = {
            'petrol': 1.0,
            'diesel': 1.05,
            'electric': 1.25,
            'hybrid': 1.15,
        }
        self.transmission_adjust: Dict[str, float] = {
            'manual': 1.0,
            'automatic': 1.08,
        }
        self.condition_adjust: Dict[str, float] = {
            'poor': 0.7,
            'fair': 0.85,
            'good': 1.0,
            'excellent': 1.15,
        }

    def _depreciation_factor(self, year: int) -> float:
        # Assume current year 2025 for offline logic
        current_year = 2025
        age = max(0, current_year - year)
        # 15% first year, 10% afterwards, floor at 0.35
        if age == 0:
            return 1.0
        value = 1.0 * 0.85 * (0.90 ** (age - 1))
        return max(0.35, value)

    def _mileage_penalty(self, mileage_km: float) -> float:
        # 40,000 km free, then mild penalty
        threshold = 40000.0
        if mileage_km <= threshold:
            return 1.0
        # Extra 0.5% per 5000 km beyond threshold, capped at 25%
        extra = mileage_km - threshold
        steps = extra / 5000.0
        penalty = min(0.25, steps * 0.005)
        return 1.0 - penalty

    def _engine_size_adjust(self, engine_l: float) -> float:
        # Slight premium for larger engines up to 3.0L
        if engine_l <= 1.0:
            return 0.95
        if engine_l >= 3.0:
            return 1.10
        # linear scale between 1.0 and 3.0
        return 0.95 + (engine_l - 1.0) * (1.10 - 0.95) / 2.0

    def predict(self, listing: MotorListing) -> float:
        base = self.make_baseline.get(listing.make, 600000.0)
        base *= self.fuel_adjust.get(str(listing.fuel_type).lower(), 1.0)
        base *= self.transmission_adjust.get(str(listing.transmission).lower(), 1.0)
        base *= self.condition_adjust.get(str(listing.condition).lower(), 1.0)
        base *= self._depreciation_factor(int(listing.year))
        base *= self._mileage_penalty(float(listing.mileage))
        base *= self._engine_size_adjust(float(listing.engine_size or 1.2))
        # Doors small premium for >= 5
        if int(listing.doors) >= 5:
            base *= 1.02
        # Round to nearest hundred
        return float(int(round(base / 100.0)) * 100)

    def analyze(self, listing: MotorListing) -> Dict[str, Any]:
        predicted = self.predict(listing)
        actual = float(listing.price)
        if predicted == 0:
            market_position = 'unknown'
            delta_percent = None
        else:
            ratio = actual / predicted
            market_position = (
                'above_market' if ratio > 1.15 else (
                    'below_market' if ratio < 0.85 else 'market_average'
                )
            )
            delta_percent = round(((actual - predicted) / predicted) * 100.0, 2)
        return {
            'predicted_price': predicted,
            'market_position': market_position,
            'price_delta': round(actual - predicted, 2),
            'delta_percent': delta_percent,
        }


class RecommendationEngine:
    """Simple content-based recommendations using token similarity of titles."""

    def _tokens(self, text: str) -> set:
        cleaned = ''.join(ch if ch.isalnum() else ' ' for ch in (text or ''))
        return {t.lower() for t in cleaned.split() if t}

    def recommend(self, seed: MotorListing, others: List[MotorListing], limit: int = 5) -> List[MotorListing]:
        seed_tokens = self._tokens(
            f"{seed.title} {seed.make} {seed.fuel_type} {seed.transmission}"
        )
        scored: List[tuple] = []
        for item in others:
            if item.id == seed.id:
                continue
            tokens = self._tokens(
                f"{item.title} {item.make} {item.fuel_type} {item.transmission}"
            )
            inter = seed_tokens & tokens
            union = seed_tokens | tokens
            jaccard = (len(inter) / len(union)) if union else 0.0
            # Proximity bonus for similar year and price
            year_bonus = 1.0 - min(0.5, abs(seed.year - item.year) * 0.05)
            denom = max(1.0, (seed.price + item.price) / 2.0)
            price_bonus = 1.0 - min(0.5, abs(seed.price - item.price) / denom)
            score = jaccard * 0.6 + year_bonus * 0.2 + price_bonus * 0.2
            scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [it for _, it in scored[:limit]]


def _parse_listing(obj: Dict[str, Any]) -> MotorListing:
    return MotorListing(
        id=int(obj.get('id', 0)),
        title=str(obj.get('title', '')),
        make=str(obj.get('make', 'Unknown')),
        year=int(obj.get('year', 2018)),
        mileage=float(obj.get('mileage', 30000)),
        engine_size=float(obj.get('engine_size', 1.2)),
        fuel_type=str(obj.get('fuel_type', 'petrol')),
        transmission=str(obj.get('transmission', 'manual')),
        doors=int(obj.get('doors', 4)),
        condition=str(obj.get('condition', 'good')),
        price=float(obj.get('price', 600000)),
        state=str(obj.get('state', '')),
        district=str(obj.get('district', '')),
    )


def _demo_data() -> List[MotorListing]:
    raw = [
        {'id': 1, 'title': 'Toyota Corolla Altis', 'make': 'Toyota', 'year': 2019, 'mileage': 42000, 'engine_size': 1.8, 'fuel_type': 'petrol', 'transmission': 'automatic', 'doors': 4, 'condition': 'good', 'price': 980000},
        {'id': 2, 'title': 'Honda City ZX', 'make': 'Honda', 'year': 2020, 'mileage': 35000, 'engine_size': 1.5, 'fuel_type': 'petrol', 'transmission': 'manual', 'doors': 4, 'condition': 'excellent', 'price': 1100000},
        {'id': 3, 'title': 'Hyundai Creta SX', 'make': 'Hyundai', 'year': 2018, 'mileage': 60000, 'engine_size': 1.6, 'fuel_type': 'diesel', 'transmission': 'manual', 'doors': 5, 'condition': 'good', 'price': 950000},
        {'id': 4, 'title': 'Maruti Swift VXi', 'make': 'Maruti', 'year': 2017, 'mileage': 70000, 'engine_size': 1.2, 'fuel_type': 'petrol', 'transmission': 'manual', 'doors': 5, 'condition': 'fair', 'price': 520000},
        {'id': 5, 'title': 'BMW 3 Series 320d', 'make': 'BMW', 'year': 2021, 'mileage': 20000, 'engine_size': 2.0, 'fuel_type': 'diesel', 'transmission': 'automatic', 'doors': 4, 'condition': 'excellent', 'price': 3200000},
    ]
    return [_parse_listing(x) for x in raw]


def main(argv: List[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description='Motor price analysis and recommendations (single-file).'
    )
    parser.add_argument('--input-json', type=str, help='Path to JSON file with a listing to analyze')
    parser.add_argument('--recommend', action='store_true', help='Show recommendations against demo dataset')
    parser.add_argument('--seed-id', type=int, default=1, help='Seed listing id from demo data when using --recommend')
    args = parser.parse_args(argv)

    predictor = MotorPricePredictor()
    rec_engine = RecommendationEngine()

    if args.input_json:
        with open(args.input_json, 'r') as f:
            obj = json.load(f)
        listing = _parse_listing(obj)
    else:
        listing = _demo_data()[0]

    analysis = predictor.analyze(listing)
    print(json.dumps({'listing': asdict(listing), 'analysis': analysis}, indent=2))

    if args.recommend:
        dataset = _demo_data()
        seed = next((x for x in dataset if x.id == args.seed_id), dataset[0])
        others = [x for x in dataset if x.id != seed.id]
        recs = rec_engine.recommend(seed, others, limit=3)
        print('\nRecommendations:')
        for i, rec in enumerate(recs, 1):
            print(f"{i}. {rec.title} ({rec.make}, {rec.year}) - ₹{int(rec.price):,}")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

