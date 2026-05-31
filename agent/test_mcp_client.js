#!/usr/bin/env node

const assert = require('assert');
const { validateTelemetry, getMockDynatraceMcpMetrics } = require('./mcp_client');

console.log('Running Node.js MCP Client unit tests...');

// Test 1: Mock Metrics Generation structure
const mockPayload = getMockDynatraceMcpMetrics('node-test-xyz');
assert.strictEqual(mockPayload.node_id, 'node-test-xyz');
assert.strictEqual(typeof mockPayload.timestamp, 'string');
assert.strictEqual(typeof mockPayload.metrics.cpu_utilization_percentage, 'number');
assert.strictEqual(Number.isInteger(mockPayload.metrics.filesystem_write_ops_per_sec), true);
assert.strictEqual(typeof mockPayload.metrics.entropy_coefficient, 'number');
console.log('✓ Mock metrics generation schema structure matches expectations.');

// Test 2: Valid payload verification
const validPayload = {
  node_id: 'node-abc-123',
  timestamp: new Date().toISOString(),
  metrics: {
    cpu_utilization_percentage: 45.2,
    filesystem_write_ops_per_sec: 12,
    entropy_coefficient: 0.223
  }
};
assert.strictEqual(validateTelemetry(validPayload), true);
console.log('✓ Valid telemetry payload successfully passes validation.');

// Test 3: Invalid payload - missing node_id
const invalidPayload1 = {
  timestamp: new Date().toISOString(),
  metrics: {
    cpu_utilization_percentage: 45.2,
    filesystem_write_ops_per_sec: 12,
    entropy_coefficient: 0.223
  }
};
assert.throws(() => validateTelemetry(invalidPayload1), /Invalid or missing node_id/);
console.log('✓ Handled invalid node_id correctly.');

// Test 4: Invalid payload - incorrect metrics types (CPU utilization as string)
const invalidPayload2 = {
  node_id: 'node-abc-123',
  timestamp: new Date().toISOString(),
  metrics: {
    cpu_utilization_percentage: '45.2%',
    filesystem_write_ops_per_sec: 12,
    entropy_coefficient: 0.223
  }
};
assert.throws(() => validateTelemetry(invalidPayload2), /metrics.cpu_utilization_percentage must be a number/);
console.log('✓ Handled non-numeric CPU utilization correctly.');

// Test 5: Invalid payload - filesystem_write_ops_per_sec as float
const invalidPayload3 = {
  node_id: 'node-abc-123',
  timestamp: new Date().toISOString(),
  metrics: {
    cpu_utilization_percentage: 45.2,
    filesystem_write_ops_per_sec: 12.5,
    entropy_coefficient: 0.223
  }
};
assert.throws(() => validateTelemetry(invalidPayload3), /metrics.filesystem_write_ops_per_sec must be an integer/);
console.log('✓ Handled float filesystem_write_ops_per_sec correctly.');

console.log('\nAll Node.js MCP Client unit tests PASSED successfully.');
process.exit(0);
