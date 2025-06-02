#!/usr/bin/env python3
"""
Azure OpenAI → Google Gemini Migration Installation Script

This script helps you install dependencies and set up the environment 
for the Google Gemini migration.

Usage:
    python install_migration.py [--vertex-ai]
    
Arguments:
    --vertex-ai: Set up for Vertex AI instead of Gemini Developer API
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

class MigrationInstaller:
    def __init__(self, use_vertex_ai: bool = False):
        self.use_vertex_ai = use_vertex_ai
        self.backend_dir = Path("backend")
        self.root_dir = Path(".")
        
    def print_step(self, step: str):
        """Print a formatted step message."""
        print(f"\n🔧 {step}")
        print("-" * 50)
    
    def run_command(self, command: list, description: str):
        """Run a command with error handling."""
        try:
            print(f"Running: {' '.join(command)}")
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running {description}: {e}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            return False
        except FileNotFoundError:
            print(f"❌ Command not found: {command[0]}")
            print(f"Please install {command[0]} and try again.")
            return False
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        self.print_step("Checking Python Version")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Python {version.major}.{version.minor} detected.")
            print("Google GenAI SDK requires Python 3.8 or higher.")
            print("Please upgrade Python and try again.")
            return False
        
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible.")
        return True
    
    def install_backend_dependencies(self):
        """Install backend Python dependencies."""
        self.print_step("Installing Backend Dependencies")
        
        if not self.backend_dir.exists():
            print(f"❌ Backend directory not found: {self.backend_dir}")
            return False
        
        requirements_file = self.backend_dir / "requirements.txt"
        if not requirements_file.exists():
            print(f"❌ Requirements file not found: {requirements_file}")
            return False
        
        # Change to backend directory
        original_dir = os.getcwd()
        try:
            os.chdir(self.backend_dir)
            
            # Upgrade pip first
            print("Upgrading pip...")
            self.run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                           "pip upgrade")
            
            # Install requirements
            success = self.run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                                     "requirements installation")
            
            if success:
                print("✅ Backend dependencies installed successfully!")
            
            return success
            
        finally:
            os.chdir(original_dir)
    
    def setup_environment_file(self):
        """Set up the environment file."""
        self.print_step("Setting Up Environment File")
        
        env_example = self.backend_dir / "env.example"
        env_file = self.backend_dir / ".env"
        
        if not env_example.exists():
            print(f"❌ Environment example file not found: {env_example}")
            return False
        
        if env_file.exists():
            print(f"⚠️  Environment file already exists: {env_file}")
            response = input("Do you want to overwrite it? (y/N): ").strip().lower()
            if response != 'y':
                print("Skipping environment file setup.")
                return True
        
        # Copy example to .env
        try:
            with open(env_example, 'r') as src:
                content = src.read()
            
            with open(env_file, 'w') as dst:
                dst.write(content)
            
            print(f"✅ Environment file created: {env_file}")
            print("\n📝 Next steps:")
            print(f"1. Edit {env_file}")
            
            if self.use_vertex_ai:
                print("2. Set up Vertex AI:")
                print("   - Set USE_VERTEX_AI=true")
                print("   - Set GOOGLE_CLOUD_PROJECT=your-project-id")
                print("   - Set GOOGLE_CLOUD_LOCATION=us-central1")
                print("   - Authenticate with: gcloud auth application-default login")
            else:
                print("2. Add your Google API key:")
                print("   - Get API key from: https://aistudio.google.com/")
                print("   - Set GOOGLE_API_KEY=your_actual_api_key")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating environment file: {e}")
            return False
    
    def setup_vertex_ai(self):
        """Set up Vertex AI if requested."""
        if not self.use_vertex_ai:
            return True
            
        self.print_step("Setting Up Vertex AI")
        
        # Check if gcloud is installed
        if not self.run_command(["gcloud", "version"], "gcloud version check"):
            print("\n📥 Please install Google Cloud SDK:")
            print("Windows: https://cloud.google.com/sdk/docs/install")
            print("macOS: brew install google-cloud-sdk")
            print("Linux: curl https://sdk.cloud.google.com | bash")
            return False
        
        print("\n📋 Vertex AI Setup Instructions:")
        print("1. Create a Google Cloud Project (if you don't have one)")
        print("2. Enable the Vertex AI API")
        print("3. Set up authentication:")
        print("   gcloud auth application-default login")
        print("4. Update your .env file with project details")
        
        return True
    
    def run_migration_test(self):
        """Run the migration test."""
        self.print_step("Running Migration Test")
        
        test_file = self.backend_dir / "test_migration.py"
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return False
        
        print("🧪 Running migration tests...")
        print("Note: This will fail if you haven't set up your API key yet.")
        
        original_dir = os.getcwd()
        try:
            os.chdir(self.backend_dir)
            success = self.run_command([sys.executable, "test_migration.py"], 
                                     "migration test")
            return success
        finally:
            os.chdir(original_dir)
    
    def print_final_instructions(self):
        """Print final setup instructions."""
        self.print_step("Migration Complete! 🎉")
        
        print("✅ Dependencies installed")
        print("✅ Environment file created")
        print("✅ Google Gemini client configured")
        
        print("\n📋 Final Steps:")
        print("1. Complete your .env file configuration")
        
        if self.use_vertex_ai:
            print("2. Set up Vertex AI authentication")
            print("3. Test with: cd backend && python test_migration.py")
        else:
            print("2. Get your Google API key from https://aistudio.google.com/")
            print("3. Add GOOGLE_API_KEY to your .env file")
            print("4. Test with: cd backend && python test_migration.py")
        
        print("\n📚 Documentation:")
        print("- Migration Guide: ./MIGRATION_GUIDE.md")
        print("- Google AI Studio: https://aistudio.google.com/")
        print("- Vertex AI: https://cloud.google.com/vertex-ai")
        
        print("\n🚀 Happy coding with Google Gemini!")
    
    def run_installation(self):
        """Run the complete installation process."""
        print("🚀 Azure OpenAI → Google Gemini Migration Installer")
        print("=" * 60)
        
        if self.use_vertex_ai:
            print("🔧 Setting up for Vertex AI (Enterprise)")
        else:
            print("🔧 Setting up for Gemini Developer API")
        
        steps = [
            ("Python Version Check", self.check_python_version),
            ("Backend Dependencies", self.install_backend_dependencies),
            ("Environment Setup", self.setup_environment_file),
        ]
        
        if self.use_vertex_ai:
            steps.append(("Vertex AI Setup", self.setup_vertex_ai))
        
        # Run all steps
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n❌ Installation failed at: {step_name}")
                return False
        
        # Print final instructions
        self.print_final_instructions()
        
        # Optionally run test (might fail if API key not set)
        print("\n🧪 Would you like to run the migration test now?")
        print("(This will fail if you haven't configured your API key yet)")
        response = input("Run test? (y/N): ").strip().lower()
        
        if response == 'y':
            self.run_migration_test()
        
        return True

def main():
    parser = argparse.ArgumentParser(description="Install Google Gemini migration")
    parser.add_argument("--vertex-ai", action="store_true", 
                       help="Set up for Vertex AI instead of Developer API")
    
    args = parser.parse_args()
    
    installer = MigrationInstaller(use_vertex_ai=args.vertex_ai)
    success = installer.run_installation()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 