import requests
import time
import subprocess
import sys
import os

def test_backend():
    print("Starting backend for testing...")
    # Start the backend in a separate process
    # Assuming we are in water_intake/backend
    # We need to install requirements first usually, but we assume environment is ready or we just test if it runs.
    
    # Using Popen to start server
    try:
        proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"], 
                                cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print(f"Failed to start backend: {e}")
        return

    print("Backend started via subprocess, waiting 5s...")
    time.sleep(5)

    try:
        url = "http://localhost:8000/predict"
        payload = {
            "Age": 25,
            "Gender": "Male",
            "Weight": 70,
            "ActivityLevel": "High",
            "Weather": "Hot"
        }
        
        print(f"Sending request to {url} with payload: {payload}")
        response = requests.post(url, json=payload)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200 and "daily_water_intake_liters" in response.json():
            print("SUCCESS: Backend returned valid prediction.")
        else:
            print("FAILURE: Invalid response.")

    except Exception as e:
        print(f"Error during request: {e}")
    finally:
        print("Killing backend process...")
        proc.terminate()
        try:
            outs, errs = proc.communicate(timeout=2)
            print("Backend output:", outs.decode())
            print("Backend errors:", errs.decode())
        except:
            proc.kill()
            print("Backend killed forcefully.")

if __name__ == "__main__":
    test_backend()
