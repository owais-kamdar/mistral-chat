# Local Mistral Chat with Dashboard

This project entails a terminal based chatbot using `Mistral-7B-Instruct` model with metrics tracking and dashboard visualization. The objective of this system was to create a document based Q and A system that allows users to upload a document in pdf/txt format and asks questions. The system is designed to provide an easy to use and simple chat experience while offering some insights into its operation and effeciency. The application uses llamafile for local inference without the need for any external API dependencies.

## Components

### Main Interface (`main.py`)
The main interface provides a command-line chat experience built with Python's built-in input/output. It uses a chat loop that maintains conversation context using a list-based history. The interface supports file uploads, with validation for PDF and TXT formats. It integrates with the system monitor for metrics display and implements seamless shutdown handling.

### LLM Interface (`llm.py`)
Implements a REST API client that communicates with the local Mistral model server using the `requests` library. It sends HTTP POST requests to the server endpoint with a JSON payload containing the prompt and generation parameters (temperature (0.7) for a good balance, max tokens (1024), stop words). The interface includes error handling for connection issues and invalid responses, with automatic retries for transient failures.

### Document Processor (`document_processor.py`)
Implements document processing using PyPDF2 for PDF extraction and `sentence-transformers` for semantic search. It uses the `all-MiniLM-L6-v2` model for generating 384-dimensional embeddings. This model was chosen due to its balance of speed, size, and performance. The processor implements a sliding window approach for text chunking with configurable size (1000) and overlap (200) for overall coverage and relationships between chunks. The semantic search uses cosine similarity on normalized embeddings for efficient similarity computation.

### Pipeline (`pipeline.py`)
Implements a pipeline that coordinates full flow implementation. It manages the flow of information using a context in the prompt construction system. There is a fallback mechanism for document processing failures and includes error boundary handling.

### System Monitor (`system_monitor.py`)
Implements a metrics collection system using Python's `psutil` for system resource monitoring. The monitor tracks:
- Response times with microsecond precision
- Memory usage in MB
- Character counts for input/output
- Error rates and types
- Session duration and statistics

### Configuration (`config.py`)
Implements a centralized configuration system using Python's pathlib for path handling. It manages:
- LLM parameters (temperature, tokens, stop words)
- Document processing parameters (chunk size, overlap)
- System paths and file locations
- Retry settings

### Logger (`logger.py`)
Implements a file-based logging system using the loguru library. It provides a simple configuration with a centralized logging file and tracks timestamps, errors, performance, and input/outputs.


### Utilities (`utils.py`)
Includes a retry mechanism with exponential backoff (base delay: 1s, max retries: 3).

## Monitoring and Dashboard

The system implements a comprehensive monitoring solution with two components:

### Metrics Collection
- Real-time tracking using decorator-based instrumentation
- Query/response logging with character-level metrics
- Error tracking
- Session management

### Dashboard (`dashboard.py`)
A Streamlit-based visualization tool that provides:
- Session selection with timestamp-based filtering
- Response time analysis
- Memory usage tracking
- Query/response history

The dashboard uses pandas for data manipulation and Plotly for interactive visualizations, providing insights into:
- Response time
- Memory usage patterns
- Error rate trends
- Character count analysis

## Setup

### Prerequisites

Python 3.10+ 

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/owais-kamdar/mistral-chat
   cd local-mistral
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download Mistral model:

- Download mistral-7b-instruct-v0.3.Q4_0.llamafile the llamafile from [This Github](https://github.com/Mozilla-Ocho/llamafile)

- Allow permission to run
    ```bash
    chmod +x Mistral-7B-Instruct-v0.3.Q4_0.llamafile
    ```



## Usage

### Starting the LLM Server

```bash
./Mistral-7b-Instruct-v0.3.Q4_0.llamafile -ngl 9999 --host 0.0.0.0 --port 8080
```

### Running the Chat Interface

Start with:
```bash
python main.py
```

Basic commands:
- Type messages to chat
- `exit` to quit
- `clear` to clear context
- `stats` to view metrics

### Viewing the Dashboard

```bash
streamlit run dashboard.py
```

## File Structure

```
local-mistral/
├── logs/                   # Logs and metrics
│   ├── app.log             
│   ├── metrics_*.jsonl     # Metrics per session
│   └── summary_*.json      # Session summaries
├── uploads/                
│                           # Stores PDF/TXT
├── config.py               # Configuration
├── dashboard.py            # Dashboard
├── document_processor.py   # Processing
├── llm.py                  # LLM interface
├── logger.py               # Logging
├── main.py                 # Main chat interface
├── pipeline.py             # Processing pipeline
├── system_monitor.py       # System monitoring
├── utils.py                # Utility functions
└── requirements.txt        # Python dependencies
```

## MIT License
 