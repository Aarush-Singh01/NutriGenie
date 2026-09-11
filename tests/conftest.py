"""
Tests for conftest.py — shared pytest configuration.
"""
import sys
from pathlib import Path

# Ensure backend is on the Python path for all tests
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
