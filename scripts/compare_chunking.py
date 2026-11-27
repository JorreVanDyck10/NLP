"""Vergelijk beide chunkmethodes op dezelfde vragen, zonder receptfilter."""

import argparse
import json
from pathlib import Path

from evaluate_chef import CASES, evidence_rank
from recipe_search import ROOT, STRATEGIES, RecipeSearch


def compare(store, cases, strategy):
    results = []
    for case in cases:
        hits = store.search(case["question"], strategy=strategy, top_k=10)
        results.append({
            "id": case["id"],
            "question": case["question"],
            "evidence_rank": evidence_rank(case, hits),
            "top_3": hits[:3],
        })
    ranks = [row["evidence_rank"] for row in results]
    return {
        "chunks": len(store.chunks[strategy]),
        "questions": len(cases),
        "evidence_at_1": ranks.count(1),
        "evidence_at_3": sum(rank is not None and rank <= 3 for rank in ranks),
        "cases": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optioneel JSON-bestand met de zoekresultaten.")
    args = parser.parse_args()

    cases = [case for case in json.loads(CASES.read_text(encoding="utf-8")) if "evidence" in case]
    case_ids = {case["id"] for case in cases}
    additional = json.loads((ROOT / "data" / "retrieval_checks.json").read_text(encoding="utf-8"))
    cases += [case for case in additional if case["id"] not in case_ids]
    store = RecipeSearch()
    try:
        report = {strategy: compare(store, cases, strategy) for strategy in STRATEGIES}
    finally:
        store.close()

    for strategy, result in report.items():
        print(f"{strategy}: {result['chunks']} chunks, "
              f"plek 1 {result['evidence_at_1']}/{result['questions']}, "
              f"top 3 {result['evidence_at_3']}/{result['questions']}")
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
