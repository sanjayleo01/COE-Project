"""Compatibility entry point for the upgraded C28 MVP."""
from structured_return_reason_analyser.src.analyser import ReturnReasonAnalyser

if __name__ == "__main__":
    print("Use: python -m structured_return_reason_analyser.src.generate_data")
    print("Then: python -m structured_return_reason_analyser.src.evaluate")
