# Academic AI/ML Observability Demo

**Lightning Talk: Observability for Reproducible AI/ML Workflows**

This repository demonstrates how to integrate OpenTelemetry and Jaeger tracing into academic AI/ML research workflows for improved reproducibility, transparency, and debugging.

## Overview

Modern AI/ML research requires: - **Reproducibility**: Track every step of your pipeline - **Performance monitoring**: Identify bottlenecks in data processing and training - **Debugging**: Understand pipeline failures with detailed traces - **Collaboration**: Share observable workflows with colleagues

This demo shows how to instrument Python ML pipelines with OpenTelemetry and visualize traces in Jaeger.

## Demo Scripts

1.  **`main.py`** - Simple "Hello World" tracing demo
2.  **`ml-observability-demo.py`** - Complete ML pipeline with instrumentation

## Prerequisites

-   **Windows 10/11** (Mac/Linux also supported)
-   **Docker Desktop** (for running Jaeger)
-   **Python 3.9+** (tested with Python 3.12)
-   **Positron** or any Python IDE/editor
-   **PowerShell** or terminal access

## Installation & Setup

### Step 1: Install Docker Desktop

1.  Download Docker Desktop: https://www.docker.com/products/docker-desktop/
2.  Install and launch Docker Desktop
3.  Wait for Docker to start (whale icon in system tray should be steady)

### Step 2: Start Jaeger with Docker

Open PowerShell and run:

``` powershell
docker run -d --name jaeger `
  -p 16686:16686 `
  -p 4318:4318 `
  jaegertracing/all-in-one:latest
```

**Verify Jaeger is running:** - Open browser: http://localhost:16686 - You should see the Jaeger UI

**To stop Jaeger later:**

``` powershell
docker stop jaeger
```

**To restart Jaeger:**

``` powershell
docker start jaeger
```

**To remove Jaeger container:**

``` powershell
docker stop jaeger
docker rm jaeger
```

### Step 3: Clone or Download This Repository

``` powershell
cd ~\Documents
git clone https://github.com/YOUR_USERNAME/Academic-AI-Needs-Observability-and-Monitoring.git
cd Academic-AI-Needs-Observability-and-Monitoring
```

Or download the ZIP file and extract it.

### Step 4: Create Python Virtual Environment

**In PowerShell:**

``` powershell
# Navigate to the project directory
cd C:\Users\YOUR_USERNAME\Academic-AI-Needs-Observability-and-Monitoring

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**Note:** If you get a PowerShell execution policy error, run:

``` powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**In Positron/VS Code:** - Open the project folder - Positron should auto-detect the `venv` folder - Select the Python interpreter from `venv\Scripts\python.exe`

### Step 5: Install Required Packages

**With virtual environment activated:**

``` powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**Or install packages individually:**

``` powershell
pip install opentelemetry-api
pip install opentelemetry-sdk
pip install opentelemetry-exporter-otlp-proto-http
pip install pandas
pip install numpy
pip install scikit-learn
```

**Verify installation:**

``` powershell
pip list
```

You should see the OpenTelemetry packages listed.

## 🚀 Running the Demo

### Option 1: Run in Positron (Interactive)

1.  **Open Positron**
2.  **Open the project folder**
3.  **Select Python interpreter** from your `venv`
4.  **Open Console** (bottom panel)
5.  **IMPORTANT: Click the restart button (🔄) in the Console** to start fresh
6.  **Run the script:**
    -   Open `main.py` or `ml-observability-demo.py`
    -   Press `Ctrl+Enter` to run, or use the Run button

**Between runs:** - Always **restart the Python console** (🔄 button) to avoid "TracerProvider already exists" errors

### Option 2: Run from Terminal/PowerShell

``` powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Run simple demo
python main.py

# Run ML pipeline demo
python ml-observability-demo.py
```

## Viewing Traces in Jaeger

1.  **Open Jaeger UI:** http://localhost:16686
2.  **Select Service:**
    -   For `main.py`: select **"positron-demo"**
    -   For `ml-observability-demo.py`: select **"ml-observability-demo"**
3.  **Click "Find Traces"** button
4.  **Click on a trace** to see the detailed timeline
5.  **Explore:**
    -   Span durations
    -   Attributes (metadata)
    -   Parent-child relationships

## Troubleshooting

### Issue: No traces appear in Jaeger

**Solution 1: Verify Jaeger is running**

``` powershell
docker ps
```

You should see `jaegertracing/all-in-one` in the list.

**Solution 2: Test Jaeger connectivity**

``` powershell
curl http://localhost:16686
```

Should return HTML from Jaeger UI.

**Solution 3: Check console output** - The scripts print span details to console - If you see span output but no Jaeger traces, there's a network issue - Try restarting Docker Desktop

### Issue: "TracerProvider already exists" error in Positron

**Solution:** Restart the Python console in Positron: 1. Find the Console panel (bottom of screen) 2. Click the restart icon (🔄) 3. Run your script again

### Issue: PowerShell execution policy error

**Solution:**

``` powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Docker not found

**Solution:** 1. Verify Docker Desktop is installed and running 2. Check system tray for Docker whale icon 3. Try restarting Docker Desktop

### Issue: Port already in use

**Solution:**

``` powershell
# Find what's using the port
netstat -ano | findstr :16686
netstat -ano | findstr :4318

# Kill the process or use different ports in docker run command
```

### Understanding the Code

### Key Components

1.  **Resource** - Identifies your service

    ``` python
    resource = Resource.create({
        "service.name": "ml-observability-demo",
        "service.namespace": "academic-observability",
        "service.version": "1.0.0"
    })
    ```

2.  **TracerProvider** - Manages trace collection

    ``` python
    provider = TracerProvider(resource=resource)
    ```

3.  **Exporters** - Send traces to Jaeger

    ``` python
    exporter = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
    ```

4.  **Spans** - Represent operations

    ``` python
    with tracer.start_as_current_span("operation_name") as span:
        span.set_attribute("key", "value")
        # Your code here
    ```

5.  **Flush** - Ensure traces are sent

    ``` python
    processor.force_flush(timeout_millis=10000)
    ```

### ML Pipeline Instrumentation

The `ml-observability-demo.py` instruments 5 stages: 1. **Data Loading** - Track dataset size and load time 2. **Preprocessing** - Record train/test split ratios 3. **Training** - Capture model type and training duration 4. **Evaluation** - Store performance metrics (MSE, RMSE) 5. **Export** - Log result output timing

Each stage creates a span with relevant attributes for full pipeline observability.

### For the Lightning Talk

### Key Points to Emphasize:

1.  **Reproducibility Crisis**: Traditional print statements aren't enough
2.  **Distributed Tracing**: See your entire pipeline in one view
3.  **Performance Insights**: Identify bottlenecks immediately
4.  **Debugging**: Trace failures across pipeline stages
5.  **Standards-Based**: OpenTelemetry is vendor-neutral
6.  **Easy Integration**: Add 20 lines of code to any Python script

## 📚 Additional Resources

-   **OpenTelemetry Python Docs**: https://opentelemetry.io/docs/languages/python/
-   **Jaeger Documentation**: https://www.jaegertracing.io/docs/
-   **OTLP Specification**: https://opentelemetry.io/docs/specs/otlp/

## Contributing

This is a demo repository for educational purposes.

Feel free to: - Fork and modify for your own talks - Add additional ML pipeline examples - Integrate with your research workflows

## License

MIT License - Free to use for academic and research purposes.

## Contact

For questions about implementing observability in your research: - Open an issue on GitHub - Email: \[jmmcclu3\@ncsu.edu\]

------------------------------------------------------------------------

**Remember:** Good observability practices lead to more reproducible, debuggable, and collaborative AI/ML research!

This material is based upon work supported by the National Science Foundation under Grant #DGE-2222148. Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.