# Risk register

| Risk | Mitigation |
|---|---|
| Synthetic data overstates accuracy | Repeat on independently audited real-return holdout |
| Wrong high-priority root cause | Confidence >=0.78 + 2 evidence streams + manual review |
| Missing inspection evidence | Confidence penalty and conservative fallback |
| Contradictory damage vs size text | Confirmed inspection damage takes precedence |
| Worker overload | Hard 25-task cap and overflow queue |
| Taxonomy drift | Product-team review of errors and monthly taxonomy update |
