const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');

// Auto-resolve endpoint coordinates
const endpoint = process.env.DYNATRACE_OTLP_ENDPOINT || 
                 (process.env.DYNATRACE_ENV_URL ? `${process.env.DYNATRACE_ENV_URL.replace(/\/$/, '')}/api/v2/otlp/v1/traces` : null);
const token = process.env.DYNATRACE_API_TOKEN;

if (endpoint && token) {
  console.log('[OTel Tracing] Dynatrace configuration detected. Starting tracer SDK...');
  try {
    const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-proto');
    const sdk = new NodeSDK({
      traceExporter: new OTLPTraceExporter({
        url: endpoint,
        headers: { 'Authorization': `Api-Token ${token}` }
      }),
      instrumentations: [getNodeAutoInstrumentations()]
    });
    sdk.start();
  } catch (err) {
    console.error('[OTel Tracing] Failed to initialize OTel SDK:', err);
  }
} else {
  console.log('[OTel Tracing] Credentials not configured. Running microservice without active cloud tracing.');
}
