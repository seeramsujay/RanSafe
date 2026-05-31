#!/usr/bin/env python3
import unittest
import json
import os
import sys
import jsonschema

# Add parent directory to path to import agent modules if necessary
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.validator import run_local_rule_engine, TELEMETRY_SCHEMA_PATH, EXECUTION_SCHEMA_PATH, load_json
from agent.mock_generator import generate_metrics

class TestRanSafeAgent(unittest.TestCase):
    
    def setUp(self):
        self.telemetry_schema = load_json(TELEMETRY_SCHEMA_PATH)
        self.execution_schema = load_json(EXECUTION_SCHEMA_PATH)

    def test_mock_metrics_generation_normal(self):
        """Verify normal mode generates metrics in correct range."""
        for _ in range(50):
            metrics = generate_metrics("normal")
            self.assertTrue(5.0 <= metrics["cpu_utilization_percentage"] <= 45.0)
            self.assertTrue(5 <= metrics["filesystem_write_ops_per_sec"] <= 30)
            self.assertTrue(0.1 <= metrics["entropy_coefficient"] <= 0.4)

    def test_mock_metrics_generation_ransomware(self):
        """Verify ransomware mode generates metrics in high/dangerous range."""
        for _ in range(50):
            metrics = generate_metrics("ransomware")
            self.assertTrue(85.0 <= metrics["cpu_utilization_percentage"] <= 99.9)
            self.assertTrue(200 <= metrics["filesystem_write_ops_per_sec"] <= 800)
            self.assertTrue(0.8 <= metrics["entropy_coefficient"] <= 1.0)

    def test_telemetry_schema_validation(self):
        """Verify that generated mock payloads strictly match telemetry schema."""
        valid_payload = {
            "node_id": "test-node-1",
            "timestamp": "2026-05-31T12:00:00Z",
            "metrics": {
                "cpu_utilization_percentage": 50.0,
                "filesystem_write_ops_per_sec": 12,
                "entropy_coefficient": 0.2
            }
        }
        # Should not raise any exceptions
        jsonschema.validate(instance=valid_payload, schema=self.telemetry_schema)

        # Invalid payload: missing required field
        invalid_payload = {
            "node_id": "test-node-1",
            "timestamp": "2026-05-31T12:00:00Z",
            "metrics": {
                "cpu_utilization_percentage": 50.0
            }
        }
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(instance=invalid_payload, schema=self.telemetry_schema)

    def test_local_rule_engine_airgap(self):
        """Verify local rule engine triggers AIRGAP_NODE under ransomware conditions."""
        payload = {
            "node_id": "node-123",
            "metrics": {
                "cpu_utilization_percentage": 88.5,
                "filesystem_write_ops_per_sec": 250,
                "entropy_coefficient": 0.85
            }
        }
        result = run_local_rule_engine(payload)
        
        # Verify schema
        jsonschema.validate(instance=result, schema=self.execution_schema)
        
        # Verify action
        self.assertEqual(result["action"], "AIRGAP_NODE")
        self.assertEqual(result["target_node_id"], "node-123")
        self.assertIn("AUTH-TOKEN", result["authorization_token"])

    def test_local_rule_engine_reallocate(self):
        """Verify local rule engine triggers REALLOCATE_RESOURCES under high compute load."""
        payload = {
            "node_id": "node-123",
            "metrics": {
                "cpu_utilization_percentage": 78.0,
                "filesystem_write_ops_per_sec": 50,
                "entropy_coefficient": 0.3
            }
        }
        result = run_local_rule_engine(payload)
        
        # Verify schema
        jsonschema.validate(instance=result, schema=self.execution_schema)
        
        # Verify action
        self.assertEqual(result["action"], "REALLOCATE_RESOURCES")

    def test_local_rule_engine_monitor_intense(self):
        """Verify local rule engine triggers MONITOR_INTENSE under mixed conditions."""
        # Condition: high disk write operations, but cpu and entropy normal
        payload = {
            "node_id": "node-123",
            "metrics": {
                "cpu_utilization_percentage": 50.0,
                "filesystem_write_ops_per_sec": 300,
                "entropy_coefficient": 0.4
            }
        }
        result = run_local_rule_engine(payload)
        
        # Verify schema
        jsonschema.validate(instance=result, schema=self.execution_schema)
        self.assertEqual(result["action"], "MONITOR_INTENSE")

if __name__ == "__main__":
    unittest.main()
