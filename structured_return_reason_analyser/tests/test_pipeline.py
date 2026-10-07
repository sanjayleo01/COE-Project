from src.generate_data import main
from src.evaluate import run
from pathlib import Path
def test_pipeline():
    main(); run(); assert Path("data/returns.csv").exists(); assert Path("reports/evaluation.json").exists()
