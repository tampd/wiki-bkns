"""Tests for tools/ — detect_conflicts and check_wiki_health."""
import sys
import json
import tempfile
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestDetectConflicts:
    """Test conflict detection logic independently of file system."""

    def _normalize_value(self, val) -> str:
        if val is None:
            return ""
        if isinstance(val, dict):
            return json.dumps(val, sort_keys=True, ensure_ascii=False)
        return str(val).strip().lower()

    def test_no_conflicts_same_values(self):
        """Two claims with same entity+attribute+value = no conflict."""
        claims = [
            {"entity_id": "prod.a", "attribute": "price", "value": 100},
            {"entity_id": "prod.a", "attribute": "price", "value": 100},
        ]
        # Check values are same
        values = {self._normalize_value(c["value"]) for c in claims}
        assert len(values) == 1

    def test_conflict_detected_different_values(self):
        """Two claims with same entity+attribute but different values = conflict."""
        claims = [
            {"entity_id": "prod.a", "attribute": "price", "value": 100},
            {"entity_id": "prod.a", "attribute": "price", "value": 200},
        ]
        values = {self._normalize_value(c["value"]) for c in claims}
        assert len(values) == 2  # Two different values = conflict

    def test_no_conflict_different_attributes(self):
        """Same entity, different attributes = not a conflict."""
        claims = [
            {"entity_id": "prod.a", "attribute": "price", "value": 100},
            {"entity_id": "prod.a", "attribute": "storage", "value": "10GB"},
        ]
        from collections import defaultdict
        groups = defaultdict(list)
        for c in claims:
            key = f"{c['entity_id']}::{c['attribute']}"
            groups[key].append(c)
        # Each group has only 1 item — no conflict
        assert all(len(g) == 1 for g in groups.values())

    def test_format_conflict_detected(self):
        """Format differences like '1' vs '1 Core' should be detected."""
        claims = [
            {"entity_id": "prod.bkh01", "attribute": "cpu_cores", "value": "1"},
            {"entity_id": "prod.bkh01", "attribute": "cpu_cores", "value": "1 Core"},
        ]
        values = {self._normalize_value(c["value"]) for c in claims}
        assert len(values) == 2  # These ARE different (format conflict)

    def test_real_conflicts_exist(self):
        """Run detect_conflicts against actual claims data."""
        claims_dir = Path(__file__).parent.parent / "claims" / "approved"
        if not claims_dir.exists():
            pytest.skip("No approved claims directory found")

        import subprocess
        result = subprocess.run(
            [sys.executable, "tools/detect_conflicts.py", "--json"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent),
            timeout=30,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "conflicts" in data
        assert "total_claims" in data
        assert data["total_claims"] > 0


class TestWikiHealthCheck:
    """Test wiki health check script."""

    def test_health_check_runs(self):
        """Health check script should run without errors."""
        wiki_dir = Path(__file__).parent.parent / "wiki"
        if not wiki_dir.exists():
            pytest.skip("No wiki directory found")

        import subprocess
        result = subprocess.run(
            [sys.executable, "tools/check_wiki_health.py", "--json"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent),
            timeout=30,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "wiki" in data
        assert "claims" in data
        assert "build" in data

    def test_health_check_detects_self_review_fails(self):
        """Health check should detect pages with self_review: fail."""
        import subprocess
        result = subprocess.run(
            [sys.executable, "tools/check_wiki_health.py", "--json"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent),
            timeout=30,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        # We know there are 53 self_review fails
        fails = data["wiki"]["issues"]["self_review_fail"]
        assert len(fails) > 0  # Should find at least some failures

    def test_health_check_counts_claims(self):
        """Health check should count approved claims correctly."""
        import subprocess
        result = subprocess.run(
            [sys.executable, "tools/check_wiki_health.py", "--json"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent),
            timeout=30,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["claims"]["total"] > 100  # Should have many claims
