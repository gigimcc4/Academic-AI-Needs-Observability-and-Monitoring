"""
main.py — Simple observability demo for Positron/Python with Jaeger

This script demonstrates how to send traces from Python to Jaeger using
OpenTelemetry, ensuring proper service identification in the Jaeger UI.

Intended use:
- Demonstrations of reproducible workflows in AI/ML and data science
- Educational examples of observability instrumentation
- Validation of trace propagation between local code and Jaeger

Environment requirements:
- Docker container running Jaeger (port 16686 for UI, 4318 for OTLP)
- Python 3.12+ with OpenTelemetry packages installed
"""

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import time

# ---------------------------------------------------------------------
# 1. Configure the tracer with explicit service identification
# ---------------------------------------------------------------------
# The Resource object ensures the Jaeger UI correctly attributes spans
# to the defined service. These attributes are displayed under
# "Process" metadata in the Jaeger trace viewer.
print("Setting up OpenTelemetry tracer...")

resource = Resource.create({
    "service.name": "positron-demo",           # Logical service name in Jaeger
    "service.namespace": "academic-observability",  # Grouping identifier for related services
    "service.version": "1.0.0"                 # Version label for reproducibility tracking
})

# The TracerProvider manages span processors and exporters.
provider = TracerProvider(resource=resource)

# ---------------------------------------------------------------------
# 2. Add exporters: console (for verification) and OTLP (for Jaeger)
# ---------------------------------------------------------------------
# ConsoleSpanExporter prints traces to the local terminal to confirm
# instrumentation is working even if Jaeger is not connected.
console_exporter = ConsoleSpanExporter()
console_processor = BatchSpanProcessor(console_exporter)
provider.add_span_processor(console_processor)

# The OTLP exporter transmits spans to Jaeger through the HTTP endpoint.
# Port 4318 must be accessible on the local Docker instance.
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318/v1/traces",
    timeout=10
)
otlp_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(otlp_processor)

# Register the configured provider globally so subsequent tracer calls use it.
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("positron-demo")

print("Tracer configured successfully.\n")

# ---------------------------------------------------------------------
# 3. Create and send test trace
# ---------------------------------------------------------------------
# Each call to start_as_current_span() begins a new trace span that can
# include descriptive attributes. These will appear in Jaeger under the
# selected service.
print("Creating test trace...")

with tracer.start_as_current_span("hello_trace") as span:
    span.set_attribute("test.attribute", "demo_value")
    span.set_attribute("demo.purpose", "academic_reproducibility")
    time.sleep(0.3)  # Simulated operation latency
    print("  → Span 'hello_trace' created.")

print("\nTrace created successfully.")

# ---------------------------------------------------------------------
# 4. Flush and shutdown exporters to ensure trace delivery
# ---------------------------------------------------------------------
# For short-running scripts, it is essential to flush and shut down
# processors manually. Otherwise, spans may remain buffered and never
# reach Jaeger.
print("\nFlushing spans to Jaeger...")
console_processor.force_flush(timeout_millis=10000)
otlp_processor.force_flush(timeout_millis=10000)
print("Spans flushed successfully.\n")

# Shut down processors in the correct order to release resources.
console_processor.shutdown()
otlp_processor.shutdown()

# ---------------------------------------------------------------------
# 5. User instructions for viewing results in Jaeger
# ---------------------------------------------------------------------
print("=" * 70)
print("VIEW TRACES IN JAEGER:")
print("  1. Open a web browser to: http://localhost:16686")
print("  2. In the 'Service' dropdown, select: positron-demo")
print("  3. Click the 'Find Traces' button to view spans")
print("=" * 70)
print("\nNote: When running repeatedly in Positron, restart the Python console")
print("      between executions to avoid 'TracerProvider already exists' warnings.\n")
