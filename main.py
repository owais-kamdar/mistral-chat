# main.py
import os
import shutil
from pipeline import run_pipeline
from config import UPLOAD_DIR
from system_monitor import system_monitor

def read_file():
    """Handle file upload and return the file path."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # user input
    print("\nChoose input method:")
    print("1. Upload a .pdf or .txt file")
    print("2. Start chat without document")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        file_name = input("Enter the full path to your file: ").strip()
        # Remove quotes if present
        file_name = file_name.strip("'\"")
        
        if os.path.exists(file_name):
            # Get the filename from the path
            base_name = os.path.basename(file_name)
            # Create destination path in uploads directory
            dest_path = os.path.join(UPLOAD_DIR, base_name)
            
            # Copy file to uploads directory
            try:
                shutil.copy2(file_name, dest_path)
                print(f"\nFile copied to uploads directory: {dest_path}")
                return dest_path
            except Exception as e:
                print(f"\nError copying file: {str(e)}")
                print("Starting chat without document.")
        else:
            print(f"\nFile not found: {file_name}")
            print("Starting chat without document.")
    return None

def chat_loop(file_path=None):
    """Run a continuous chat loop with the LLM."""
    print("\nStarting chat (type 'exit' to quit, 'clear' to clear context, 'stats' for metrics)")
    print("=" * 50)
    
    context = []
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        # Handle special commands
        if user_input.lower() == 'exit':
            print("\nSaving metrics and exiting...")
            system_monitor.save_summary()
            print("\nGoodbye!")
            break
        elif user_input.lower() == 'clear':
            context = []
            print("\nContext cleared!")
            continue
        elif user_input.lower() == 'stats':
            # summary log file
            summary = system_monitor.get_summary()
            print("\nCurrent Metrics:")
            print(f"Total Queries: {summary['total_queries']}")
            print(f"Average Response Time: {summary['avg_inference_time']:.2f}s")
            print(f"Total Characters: {summary['total_chars']}")
            print(f"Average Characters per Query: {summary['avg_chars_per_query']:.1f}")
            print(f"Errors: {summary['errors']}")
            print(f"Memory Usage: {summary['current_memory_usage_mb']:.1f} MB")
            print(f"Session Duration: {summary['session_duration']:.1f}s")
            continue
        
        # Add user message to context
        context.append(f"Human: {user_input}")
        
        # Prepare prompt with context
        prompt = "\n".join(context) + "\nAssistant:"
        
        # Get response
        response = run_pipeline(prompt, file_path)
        
        # Add response to context
        context.append(f"Assistant: {response}")
        
        # Print response
        print("\nAssistant:", response)
        print("-" * 50)

if __name__ == "__main__":
    try:
        # Handle file upload if any
        file_path = read_file()
        
        # Start chat loop
        chat_loop(file_path)
    except KeyboardInterrupt:
        print("\n\nSaving metrics and ending chat...")
        system_monitor.save_summary()
        print("Chat ended by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        system_monitor.save_summary()