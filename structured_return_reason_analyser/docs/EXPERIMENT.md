# Experiment

Baseline: keyword classifier.
Hybrid: source-aware rules + TF-IDF semantic similarity.

Targets:
- normal-day macro F1 >= 0.75
- disruption-day macro F1 >= 0.55
- high-priority requires >=2 independent evidence streams
- worker cap = 25 tasks/shift

Run `python -m src.generate_data` then `python -m src.evaluate`.

The dataset is synthetic and reproducible; production rollout requires an independent audited real-return holdout. `reports/error_analysis.csv` is the false-positive/false-negative inspection artifact.
