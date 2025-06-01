# system_monitor.py
import time
import psutil
import json
import os
from datetime import datetime
from functools import wraps

class SystemMonitor:
    """Class to monitor the system and the LLM."""
    
    def __init__(self):
        self.metrics = []
        self.total_queries = 0
        self.total_chars = 0
        self.errors = 0
        self.total_inference_time = 0
        self.start_time = datetime.now().isoformat()
        self.current_memory_usage_mb = 0
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
    
    def monitor(self, func):
        """Monitor the system and the LLM."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now().isoformat()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            try:
                # Get the current query (last line of the prompt)
                prompt = args[0] if args else ""
                current_query = prompt.split('\n')[-2].replace('Human: ', '') if '\n' in prompt else prompt
                
                result = func(*args, **kwargs)
                

                end_time = datetime.now().isoformat()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                
                # Calculate inference time
                start_dt = datetime.fromisoformat(start_time)
                end_dt = datetime.fromisoformat(end_time)
                inference_time = (end_dt - start_dt).total_seconds()
                memory_usage = end_memory
                
                # Count characters
                input_chars = len(current_query)
                output_chars = len(result)
                total_chars = input_chars + output_chars
                
                # Update metrics
                self.total_queries += 1
                self.total_inference_time += inference_time
                self.total_chars += total_chars
                self.current_memory_usage_mb = memory_usage
                
                # Log metrics
                metric = {
                    "timestamp": datetime.now().isoformat(),
                    "start_time": start_time,
                    "end_time": end_time,
                    "inference_time": inference_time,
                    "memory_usage": memory_usage,
                    "input_chars": input_chars,
                    "output_chars": output_chars,
                    "total_chars": total_chars,
                    "input": f"Human: {current_query}\nAssistant:",
                    "output": result,
                    "session_id": self.session_id
                }
                
                self.metrics.append(metric)
                
                # Save metrics to session-specific file
                metrics_file = f"logs/metrics_{self.session_id}.jsonl"
                with open(metrics_file, 'a') as f:
                    f.write(json.dumps(metric) + '\n')
                
                return result
                
            except Exception as e:
                self.errors += 1
                raise e
        
        return wrapper
    
    def get_summary(self):
        """Get a summary of the current session."""
        # add isoformat to the start_time and end_time for better streamlit compatibility
        current_time = datetime.now().isoformat()
        start_dt = datetime.fromisoformat(self.start_time)
        end_dt = datetime.fromisoformat(current_time)
        session_duration = (end_dt - start_dt).total_seconds()
        
        return {
            "session_id": self.session_id,
            "total_queries": self.total_queries,
            "avg_inference_time": self.total_inference_time / self.total_queries if self.total_queries > 0 else 0,
            "total_chars": self.total_chars,
            "avg_chars_per_query": self.total_chars / self.total_queries if self.total_queries > 0 else 0,
            "errors": self.errors,
            "session_duration": session_duration,
            "current_memory_usage_mb": self.current_memory_usage_mb,
            "start_time": self.start_time,
            "end_time": current_time
        }
    
    def save_summary(self):
        """Save the session summary to a file."""
        summary = self.get_summary()
        summary_file = f"logs/summary_{self.session_id}.json"
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

# Create a global instance
system_monitor = SystemMonitor() 