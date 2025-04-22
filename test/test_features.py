#!/usr/bin/env python3

import subprocess
import datetime
import os
import sys
from pathlib import Path

def main():
    # Set the test app name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    test_app_name = f"test_flutter_app_{timestamp}"

    print(f"Running feature test with app name: {test_app_name}")
    print("----------------------------------------")

    try:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = str(Path(script_dir).parent)
        
        # Add project root to Python path
        sys.path.append(project_root)
        
        # Import our features
        from lib.core.features.feature_manager import FeatureManager
        from lib.core.features.project_setup_feature import ProjectSetupFeature
        from lib.core.features.state_management_feature import StateManagementFeature
        from lib.core.features.theme_feature import ThemeFeature
        from lib.core.features.router_feature import RouterFeature
        from lib.core.features.auth_feature import AuthFeature
        
        # Create feature manager
        parent_dir = os.path.dirname(os.path.dirname(os.getcwd()))
        project_path = os.path.join(parent_dir, test_app_name)
        manager = FeatureManager(project_path)
        
        # Register features
        manager.register_feature(ProjectSetupFeature)
        manager.register_feature(StateManagementFeature)
        manager.register_feature(ThemeFeature)
        manager.register_feature(RouterFeature)
        manager.register_feature(AuthFeature)
        
        # Install project setup first
        print("\nSetting up project...")
        manager.install_feature("Project Setup", config={
            "app_name": test_app_name,
            "org": "com.test",
            "platforms": "ios,android,web,macos"
        })
        
        # Install other features
        print("\nInstalling features...")
        manager.install_feature("State Management")
        manager.install_feature("Theme Support")
        manager.install_feature("Router Support")
        manager.install_feature("Authentication Support")
        
        # Update pubspec.yaml with dependencies
        manager.update_pubspec()
        
        print("✅ Feature test completed successfully")
        print(f"Test app created at: {project_path}")
        
    except Exception as e:
        print(f"❌ Feature test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 