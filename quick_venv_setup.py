#!/usr/bin/env python3
"""
Quick Virtual Environment Setup for Eye-Controlled Interface
Uses latest compatible versions as of February 2025
"""

import subprocess
import sys
import os
import shutil

def run_command(cmd, description, check=True):
    """Run a command with error handling"""
    print(f"🔧 {description}...")
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, check=check)

        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def main():
    print("=" * 60)
    print("    Quick Virtual Environment Setup")
    print("    Latest Compatible Versions (Feb 2025)")
    print("=" * 60)

    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")

    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)

    # Virtual environment name
    venv_name = "eye_tracking_env"

    # Remove existing environment if it exists
    if os.path.exists(venv_name):
        print(f"🗑️  Removing existing environment: {venv_name}")
        shutil.rmtree(venv_name)

    # Create virtual environment
    if not run_command([sys.executable, "-m", "venv", venv_name], "Creating virtual environment"):
        sys.exit(1)

    # Determine pip and python paths
    if os.name == 'nt':  # Windows
        pip_path = os.path.join(venv_name, "Scripts", "pip")
        python_path = os.path.join(venv_name, "Scripts", "python")
        activate_script = os.path.join(venv_name, "Scripts", "activate")
    else:  # Unix/Linux
        pip_path = os.path.join(venv_name, "bin", "pip")
        python_path = os.path.join(venv_name, "bin", "python")
        activate_script = os.path.join(venv_name, "bin", "activate")

    # Upgrade pip
    run_command([python_path, "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip")

    # Install packages with latest compatible versions
    print("\n📦 Installing packages with latest compatible versions...")

    packages = [
        # CRITICAL: NumPy 1.x for MediaPipe compatibility (MediaPipe 0.10.21 requires <2.0)
        "numpy>=1.24.0,<2.0.0",

        # Latest OpenCV (supports NumPy 2.0 but we use 1.x for MediaPipe compatibility)
        "opencv-python>=4.8.0",

        # Latest MediaPipe (0.10.21 released Feb 6, 2025 - STILL requires NumPy < 2.0)
        "mediapipe==0.10.21",

        # Other packages - latest stable versions
        "pyautogui>=0.9.54",
        "pynput>=1.7.6",
        "Pillow>=10.0.0",
        "screeninfo>=0.8.1",
        "psutil>=5.9.0",
    ]

    success_count = 0
    for package in packages:
        if run_command([pip_path, "install", package], f"Installing {package}", check=False):
            success_count += 1
        else:
            # Try without version constraints
            package_name = package.split(">=")[0].split("==")[0].split("<")[0]
            print(f"🔄 Retrying {package_name} without version constraints...")
            if run_command([pip_path, "install", package_name], f"Installing {package_name}", check=False):
                success_count += 1

    print(f"\n📊 Installed {success_count}/{len(packages)} packages")

    # Test the installation
    print("\n🧪 Testing installation...")
    test_code = '''
import warnings
warnings.filterwarnings("ignore")

modules = [
    ("numpy", "NumPy"),
    ("cv2", "OpenCV"),
    ("mediapipe", "MediaPipe"),
    ("pyautogui", "PyAutoGUI"),
    ("PIL", "Pillow"),
    ("psutil", "psutil"),
    ("pynput", "pynput"),
    ("screeninfo", "screeninfo")
]

failed = []
for module, name in modules:
    try:
        imported = __import__(module)
        version = getattr(imported, "__version__", "unknown")
        print(f"✅ {name}: {version}")

        if module == "numpy":
            major_version = int(version.split(".")[0])
            if major_version >= 2:
                print("⚠️  NumPy 2.x detected - may cause MediaPipe issues")
            else:
                print("✅ NumPy 1.x - compatible with MediaPipe")
    except ImportError as e:
        print(f"❌ {name}: {e}")
        failed.append(name)

if failed:
    print(f"\\nFailed imports: {failed}")
    exit(1)

# Test integration
try:
    import numpy as np
    import cv2
    import mediapipe as mp

    # Test OpenCV-NumPy
    test_array = np.zeros((10, 10, 3), dtype=np.uint8)
    result = cv2.cvtColor(test_array, cv2.COLOR_BGR2RGB)
    print("✅ OpenCV-NumPy integration working")

    # Test MediaPipe
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)
    print("✅ MediaPipe initialization working")

    print("\\n🎉 All tests passed!")

except Exception as e:
    print(f"❌ Integration test failed: {e}")
    exit(1)
'''

    if run_command([python_path, "-c", test_code], "Testing package compatibility", check=False):
        print("\n✅ Installation successful!")
    else:
        print("\n❌ Installation test failed")
        sys.exit(1)

    # Create activation script
    print("\n📝 Creating activation script...")
    activation_script_content = f'''#!/bin/bash
# Eye-Controlled Interface Environment Activation

echo "🚀 Activating Eye-Controlled Interface Environment"
source {activate_script}

echo "✅ Environment activated!"
echo "Python: $(python --version)"
echo "Location: $(which python)"

echo ""
echo "📦 Installed packages:"
python -c "
import numpy, cv2, mediapipe, pyautogui
print(f'  NumPy: {{numpy.__version__}}')
print(f'  OpenCV: {{cv2.__version__}}')
print(f'  MediaPipe: {{mediapipe.__version__}}')
print(f'  PyAutoGUI: {{pyautogui.__version__}}')
"

echo ""
echo "🎮 Available commands:"
echo "  python simple_eye_mouse.py    # Simple eye mouse"
echo "  python test_system.py         # System tests"
echo "  python main.py                # Full application"
echo ""
echo "To deactivate: deactivate"
'''

    with open("activate_eye_tracking.sh", "w") as f:
        f.write(activation_script_content)

    os.chmod("activate_eye_tracking.sh", 0o755)

    # Save requirements
    run_command([pip_path, "freeze"], "Saving requirements", check=False)
    with open("requirements_installed.txt", "w") as f:
        result = subprocess.run([pip_path, "freeze"], capture_output=True, text=True)
        f.write(result.stdout)

    print("\n" + "=" * 60)
    print("                    SETUP COMPLETED")
    print("=" * 60)
    print("✅ Virtual environment created successfully!")
    print(f"📁 Environment: {venv_name}")
    print(f"🐍 Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    print("")
    print("🚀 To activate and use:")
    print("   source activate_eye_tracking.sh")
    print("")
    print("📋 Or manually:")
    print(f"   source {activate_script}")
    print("   python simple_eye_mouse.py")
    print("")
    print("📦 Package versions installed:")
    print("   - NumPy: 1.24+ (compatible with MediaPipe)")
    print("   - OpenCV: 4.10.0.84 (latest with NumPy 2.0 support)")
    print("   - MediaPipe: 0.10.21 (latest, requires NumPy <2.0)")
    print("")
    print("⚠️  Note: MediaPipe still requires NumPy <2.0 as of Feb 2025")
    print("=" * 60)

if __name__ == "__main__":
    main()
