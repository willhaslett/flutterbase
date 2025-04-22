#!/usr/bin/env python3

import subprocess
import datetime
import os
import sys

def main():
    # Set the test app name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    test_app_name = f"test_flutter_app_{timestamp}"

    print(f"Running template test with app name: {test_app_name}")
    print("----------------------------------------")

    # Run the template script with the test app name
    try:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_script = os.path.join(script_dir, "apply_template.py")
        
        # Run the template script with the test app name
        subprocess.run([sys.executable, template_script, test_app_name], check=True)
        
        print("✅ Template test completed successfully")
        parent_dir = os.path.dirname(os.path.dirname(os.getcwd()))
        print(f"Test app created at: {os.path.join(parent_dir, test_app_name)}")
    except subprocess.CalledProcessError:
        print("❌ Template test failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 