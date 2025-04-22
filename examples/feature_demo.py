#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from lib.core.features.feature_manager import FeatureManager
from lib.core.features.theme_feature import ThemeFeature
from lib.core.features.router_feature import RouterFeature
from lib.core.features.auth_feature import AuthFeature

def main():
    # Create a FeatureManager instance
    project_path = "example_project"
    manager = FeatureManager(project_path)
    
    # Register features
    manager.register_feature(ThemeFeature)
    manager.register_feature(RouterFeature)
    manager.register_feature(AuthFeature)
    
    # Print available features
    print("Available features:")
    for feature in manager.get_available_features():
        print(f"- {feature}")
    
    # Install features
    print("\nInstalling features...")
    manager.install_feature("Theme Support")
    manager.install_feature("Router Support")
    manager.install_feature("Authentication Support")
    
    # Update pubspec.yaml with dependencies
    manager.update_pubspec()
    
    # Print installed features
    print("\nInstalled features:")
    for feature in manager.get_installed_features():
        print(f"- {feature}")
    
    # Example of uninstalling a feature
    # manager.uninstall_feature("Theme Support")

if __name__ == "__main__":
    main() 