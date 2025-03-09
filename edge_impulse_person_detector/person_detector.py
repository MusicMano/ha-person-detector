import os

# Get and print raw environment variables for debugging
print("Environment variables as received:")
print(f"CAMERA_ENTITY = {os.environ.get('CAMERA_ENTITY', 'not set')}")
print(f"CONFIDENCE_THRESHOLD = {os.environ.get('CONFIDENCE_THRESHOLD', 'not set')}")
print(f"SCAN_INTERVAL = {os.environ.get('SCAN_INTERVAL', 'not set')}")
print(f"EDGE_IMPULSE_API_KEY = {'[present]' if os.environ.get('EDGE_IMPULSE_API_KEY') else 'not set'}")

# Handle environment variables more safely
def get_float_env(name, default):
    value = os.environ.get(name, default)
    try:
        return float(value)
    except (ValueError, TypeError):
        print(f"Warning: Could not convert {name}='{value}' to float. Using default {default}")
        return float(default)

def get_int_env(name, default):
    value = os.environ.get(name, default)
    try:
        return int(value)
    except (ValueError, TypeError):
        print(f"Warning: Could not convert {name}='{value}' to int. Using default {default}")
        return int(default)

# Set variables with safe conversion
CAMERA_ENTITY = os.environ.get('CAMERA_ENTITY', 'camera.front_door')
CONFIDENCE_THRESHOLD = get_float_env('CONFIDENCE_THRESHOLD', '0.7')
SCAN_INTERVAL = get_int_env('SCAN_INTERVAL', '1')
EDGE_IMPULSE_API_KEY = os.environ.get('EDGE_IMPULSE_API_KEY', '')

# Add a simple main function that just loops and stays alive
def main():
    print("Person detector starting...")
    print(f"Using camera: {CAMERA_ENTITY}")
    print(f"Confidence threshold: {CONFIDENCE_THRESHOLD}")
    print(f"Scan interval: {SCAN_INTERVAL}")
    print(f"API key present: {'Yes' if EDGE_IMPULSE_API_KEY else 'No'}")
    
    # Just stay alive
    import time
    while True:
        print("Still running...")
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error in main: {e}")
        # Stay alive even after error
        import time
        while True:
            print("Error occurred, but keeping container alive for troubleshooting")
            time.sleep(300)