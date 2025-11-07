"""
test_trace.py - Ultra-simple OpenTelemetry test

This is the absolute simplest script to test if tracing works.
If this doesn't work, we'll know there's a more fundamental issue.
"""

print("=" * 60)
print("STEP 1: Importing libraries...")
print("=" * 60)

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import time

print("✓ All imports successful\n")

print("=" * 60)
print("STEP 2: Setting up tracer...")
print("=" * 60)

# Create resource
resource = Resource.create({
    "service.name": "test-trace",
})

# Create provider
provider = TracerProvider(resource=resource)

# Add console exporter (shows spans in terminal)
console_exporter = ConsoleSpanExporter()
console_processor = BatchSpanProcessor(console_exporter)
provider.add_span_processor(console_processor)

# Add OTLP exporter (sends to Jaeger)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318/v1/traces",
    timeout=10
)
otlp_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(otlp_processor)

# Set as global provider
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("test-trace")

print("✓ Tracer configured\n")

print("=" * 60)
print("STEP 3: Creating a test span...")
print("=" * 60)

with tracer.start_as_current_span("test_span") as span:
    span.set_attribute("test", "hello")
    print("✓ Span created: 'test_span'")
    time.sleep(0.5)

print("✓ Span ended\n")

print("=" * 60)
print("STEP 4: Flushing spans to Jaeger...")
print("=" * 60)

# Force flush
console_processor.force_flush(timeout_millis=10000)
otlp_processor.force_flush(timeout_millis=10000)

print("✓ Flush complete\n")

# Shutdown
console_processor.shutdown()
otlp_processor.shutdown()

print("=" * 60)
print("SUCCESS! If you see span details above, tracing works!")
print("=" * 60)
print("\n📊 Now check Jaeger:")
print("   1. Open: http://localhost:16686")
print("   2. Service: select 'test-trace'")
print("   3. Click 'Find Traces'\n")
print("You should see 1 trace with 1 span named 'test_span'\n")