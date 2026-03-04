import subprocess
import sys
import os

def handler(event, context):
    try:
        # Run streamlit app
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "../streamlit_app.py", 
            "--server.headless", "true",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], capture_output=True, text=True, timeout=30)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': result.stdout if result.stdout else "Streamlit app running"
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }
