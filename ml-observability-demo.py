"""
ml-observability-demo.py — ML Pipeline with OpenTelemetry tracing

Demonstrates observability best practices for academic AI/ML workflows:
- Each pipeline stage is instrumented with spans
- Performance metrics are captured as span attributes
- Full pipeline visibility for reproducibility and debugging

For use with Jaeger and Positron/Python environments.
"""

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import time

# ---------------------------------------------------------------------
# Configure OpenTelemetry tracer
# ---------------------------------------------------------------------
print("🔧 Setting up OpenTelemetry for ML pipeline...\n")

resource = Resource.create({
    "service.name": "ml-observability-demo",
    "service.namespace": "academic-observability",
    "service.version": "1.0.0",
    "deployment.environment": "research"
})

provider = TracerProvider(resource=resource)

# Console exporter - shows traces in terminal for verification
console_exporter = ConsoleSpanExporter()
console_processor = BatchSpanProcessor(console_exporter)
provider.add_span_processor(console_processor)

# OTLP exporter - sends traces to Jaeger
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318/v1/traces",
    timeout=10
)
otlp_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(otlp_processor)

trace.set_tracer_provider(provider)
tracer = trace.get_tracer("ml-observability-demo")

print("✅ Tracer configured successfully")
print("📊 Starting instrumented ML pipeline...\n")

# ---------------------------------------------------------------------
# Instrumented ML Pipeline
# ---------------------------------------------------------------------
try:
    with tracer.start_as_current_span("ml_pipeline") as pipeline_span:
        # Add pipeline metadata
        pipeline_span.set_attribute("pipeline.type", "supervised_learning")
        pipeline_span.set_attribute("pipeline.model", "linear_regression")
        
        # Stage 1: Data Loading
        with tracer.start_as_current_span("data_loading") as load_span:
            print("1️⃣  Loading synthetic dataset...")
            start_time = time.time()
            
            np.random.seed(42)
            X = np.random.rand(500, 3)
            y = 3*X[:,0] + 2*X[:,1] - 1.5*X[:,2] + np.random.normal(0, 0.2, 500)
            dataset = pd.DataFrame(np.column_stack((X, y)), columns=["x1", "x2", "x3", "target"])
            
            load_time = time.time() - start_time
            load_span.set_attribute("data.rows", len(dataset))
            load_span.set_attribute("data.columns", len(dataset.columns))
            load_span.set_attribute("duration_ms", round(load_time * 1000, 2))
            print(f"   ✓ Loaded {len(dataset)} rows in {load_time:.3f}s\n")

        # Stage 2: Data Preprocessing
        with tracer.start_as_current_span("data_preprocessing") as prep_span:
            print("2️⃣  Preprocessing data...")
            start_time = time.time()
            
            X = dataset[["x1", "x2", "x3"]]
            y = dataset["target"]
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            prep_time = time.time() - start_time
            prep_span.set_attribute("train.size", len(X_train))
            prep_span.set_attribute("test.size", len(X_test))
            prep_span.set_attribute("test.ratio", 0.2)
            prep_span.set_attribute("duration_ms", round(prep_time * 1000, 2))
            print(f"   ✓ Split: {len(X_train)} train, {len(X_test)} test\n")

        # Stage 3: Model Training
        with tracer.start_as_current_span("model_training") as train_span:
            print("3️⃣  Training linear regression model...")
            start_time = time.time()
            
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            train_time = time.time() - start_time
            train_span.set_attribute("model.type", "LinearRegression")
            train_span.set_attribute("model.features", X_train.shape[1])
            train_span.set_attribute("duration_ms", round(train_time * 1000, 2))
            print(f"   ✓ Model trained in {train_time:.3f}s\n")

        # Stage 4: Model Evaluation
        with tracer.start_as_current_span("model_evaluation") as eval_span:
            print("4️⃣  Evaluating model performance...")
            start_time = time.time()
            
            predictions = model.predict(X_test)
            mse = mean_squared_error(y_test, predictions)
            rmse = np.sqrt(mse)
            
            eval_time = time.time() - start_time
            eval_span.set_attribute("metrics.mse", round(mse, 6))
            eval_span.set_attribute("metrics.rmse", round(rmse, 6))
            eval_span.set_attribute("duration_ms", round(eval_time * 1000, 2))
            
            # Also add metrics to parent pipeline span
            pipeline_span.set_attribute("pipeline.mse", round(mse, 6))
            pipeline_span.set_attribute("pipeline.rmse", round(rmse, 6))
            
            print(f"   ✓ Mean Squared Error: {mse:.6f}")
            print(f"   ✓ Root Mean Squared Error: {rmse:.6f}\n")

        # Stage 5: Results Export
        with tracer.start_as_current_span("export_results") as export_span:
            print("5️⃣  Exporting results...")
            start_time = time.time()
            
            results = {
                "model": "LinearRegression",
                "mse": round(mse, 6),
                "rmse": round(rmse, 6),
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            export_time = time.time() - start_time
            export_span.set_attribute("export.format", "dict")
            export_span.set_attribute("duration_ms", round(export_time * 1000, 2))
            print(f"   ✓ Results: {results}\n")

    print("=" * 70)
    print("✅ ML PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ Error during pipeline execution: {e}")
    import traceback
    traceback.print_exc()

finally:
    # CRITICAL: Flush all spans to Jaeger before script ends
    print("\n🔄 Flushing traces to Jaeger...")
    try:
        console_processor.force_flush(timeout_millis=10000)
        otlp_processor.force_flush(timeout_millis=10000)
        print("✅ All traces flushed successfully")
    except Exception as e:
        print(f"⚠️  Warning during flush: {e}")
    
    # Shutdown processors
    try:
        console_processor.shutdown()
        otlp_processor.shutdown()
        print("✅ Processors shut down cleanly\n")
    except Exception as e:
        print(f"⚠️  Warning during shutdown: {e}\n")
    
    # Instructions
    print("=" * 70)
    print("📊 VIEW TRACES IN JAEGER:")
    print("  1. Open: http://localhost:16686")
    print("  2. Service dropdown: select 'ml-observability-demo'")
    print("  3. Click 'Find Traces' button")
    print("  4. Explore the pipeline stages and performance metrics")
    print("=" * 70)
    print("\n💡 TIP: Restart Positron's Python console between runs")
    print("   to avoid TracerProvider conflicts.\n")
