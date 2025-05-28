#!/bin/bash

# Virtual Environment Setup for Eye-Controlled Interface
# Uses Python 3.10 with latest compatible package versions (February 2025)

echo "============================================================"
echo "    Eye-Controlled Interface - Python 3.10 Virtual Environment Setup"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.10 is available
print_status "Checking Python 3.10 availability..."
if command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
    print_success "Python 3.10 found: $(python3.10 --version)"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
    if [[ "$PYTHON_VERSION" == "3.10" ]]; then
        PYTHON_CMD="python3"
        print_success "Python 3.10 found: $(python3 --version)"
    else
        print_warning "Python 3.10 not found, using $(python3 --version)"
        PYTHON_CMD="python3"
    fi
else
    print_error "Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Install Python 3.10 if not available on Fedora
if ! command -v python3.10 &> /dev/null; then
    print_status "Installing Python 3.10 on Fedora..."
    sudo dnf install -y python3.10 python3.10-pip python3.10-venv python3.10-devel
    PYTHON_CMD="python3.10"
fi

# Install system dependencies
print_status "Installing system dependencies..."
sudo dnf install -y \
    python3-tkinter \
    python3.10-tkinter \
    v4l-utils \
    gcc \
    gcc-c++ \
    cmake \
    make \
    pkg-config

# Add user to video group
print_status "Adding user to video group..."
sudo usermod -a -G video $USER

# Create virtual environment
VENV_NAME="eye_tracking_env"
print_status "Creating virtual environment: $VENV_NAME"

if [ -d "$VENV_NAME" ]; then
    print_warning "Virtual environment already exists. Removing old one..."
    rm -rf "$VENV_NAME"
fi

$PYTHON_CMD -m venv "$VENV_NAME"

if [ $? -eq 0 ]; then
    print_success "Virtual environment created successfully"
else
    print_error "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source "$VENV_NAME/bin/activate"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install packages with latest compatible versions (as of February 2025)
print_status "Installing packages with latest compatible versions..."

# Strategy: Use NumPy 1.26.x for MediaPipe compatibility, but test with latest versions
packages=(
    # CRITICAL: NumPy 1.x for MediaPipe compatibility (MediaPipe 0.10.21 requires <2.0)
    "numpy>=1.24.0,<2.0.0"

    # Latest OpenCV (supports NumPy 2.0 but we use 1.x for MediaPipe compatibility)
    "opencv-python>=4.8.0"

    # Latest MediaPipe (0.10.21 released Feb 6, 2025 - STILL requires NumPy < 2.0)
    "mediapipe==0.10.21"

    # System control and automation
    "pyautogui>=0.9.54"
    "pynput>=1.7.6"

    # Image processing and utilities
    "Pillow>=10.0.0"
    "screeninfo>=0.8.1"

    # System monitoring and performance
    "psutil>=5.9.0"

    # Additional useful packages
    "matplotlib>=3.7.0"
    "scipy>=1.10.0"
)

for package in "${packages[@]}"; do
    print_status "Installing $package..."
    pip install "$package"

    if [ $? -eq 0 ]; then
        print_success "Successfully installed $package"
    else
        print_error "Failed to install $package"

        # Try without version constraints
        package_name=$(echo "$package" | cut -d'>' -f1 | cut -d'=' -f1 | cut -d'<' -f1)
        print_status "Trying alternative installation for $package_name..."
        pip install "$package_name"
    fi
done

# Test the installation
print_status "Testing package compatibility..."
python -c "
import sys
import warnings
warnings.filterwarnings('ignore')

print('Python version:', sys.version)
print('=' * 50)

modules_to_test = [
    ('numpy', 'NumPy'),
    ('cv2', 'OpenCV'),
    ('mediapipe', 'MediaPipe'),
    ('pyautogui', 'PyAutoGUI'),
    ('PIL', 'Pillow'),
    ('psutil', 'psutil'),
    ('pynput', 'pynput'),
    ('screeninfo', 'screeninfo')
]

failed_modules = []
success_count = 0

for module, name in modules_to_test:
    try:
        imported_module = __import__(module)
        version = getattr(imported_module, '__version__', 'unknown')
        print(f'✅ {name}: {version}')
        success_count += 1

        # Special compatibility checks
        if module == 'numpy':
            major_version = int(version.split('.')[0])
            if major_version >= 2:
                print(f'⚠️  Warning: NumPy 2.x may cause MediaPipe issues')
            else:
                print(f'✅ NumPy 1.x - compatible with MediaPipe')

    except ImportError as e:
        print(f'❌ {name}: Import failed - {e}')
        failed_modules.append(name)
    except Exception as e:
        print(f'❌ {name}: Error - {e}')
        failed_modules.append(name)

print(f'\\nSummary: {success_count}/{len(modules_to_test)} modules working')

if failed_modules:
    print(f'Failed modules: {failed_modules}')
    sys.exit(1)
else:
    print('🎉 All modules imported successfully!')

    # Test OpenCV-NumPy integration
    try:
        import cv2
        import numpy as np

        test_array = np.zeros((100, 100, 3), dtype=np.uint8)
        result = cv2.cvtColor(test_array, cv2.COLOR_BGR2RGB)
        print('✅ OpenCV-NumPy integration test passed')

        # Test MediaPipe
        import mediapipe as mp
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)
        print('✅ MediaPipe initialization test passed')

    except Exception as e:
        print(f'❌ Integration test failed: {e}')
        sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_success "All packages working correctly!"
else
    print_error "Package testing failed"
    exit 1
fi

# Create activation script
print_status "Creating activation script..."
cat > activate_eye_tracking.sh << 'EOF'
#!/bin/bash
# Activation script for Eye-Controlled Interface

echo "🚀 Activating Eye-Controlled Interface Environment"
source eye_tracking_env/bin/activate

echo "✅ Environment activated!"
echo "Python: $(python --version)"
echo "NumPy: $(python -c 'import numpy; print(numpy.__version__)')"
echo "OpenCV: $(python -c 'import cv2; print(cv2.__version__)')"
echo "MediaPipe: $(python -c 'import mediapipe; print(mediapipe.__version__)')"

echo ""
echo "Available commands:"
echo "  python simple_eye_mouse.py    # Simple eye mouse"
echo "  python test_system.py         # System tests"
echo "  python main.py                # Full application"
echo ""
echo "To deactivate: deactivate"
EOF

chmod +x activate_eye_tracking.sh

# Create requirements file for this environment
print_status "Creating requirements file..."
pip freeze > requirements_venv.txt

# Deactivate virtual environment
deactivate

echo ""
echo "============================================================"
echo "                    SETUP COMPLETED"
echo "============================================================"
print_success "Virtual environment setup completed successfully!"
echo ""
echo "📁 Virtual environment: $VENV_NAME"
echo "🐍 Python version: $($PYTHON_CMD --version)"
echo ""
echo "To use the environment:"
echo "1. Activate: source activate_eye_tracking.sh"
echo "2. Or manually: source $VENV_NAME/bin/activate"
echo ""
echo "To test the installation:"
echo "source $VENV_NAME/bin/activate"
echo "python test_system.py"
echo ""
echo "To run the eye tracking:"
echo "source $VENV_NAME/bin/activate"
echo "python simple_eye_mouse.py"
echo ""
print_warning "Important: Always activate the virtual environment before running the application!"
echo "============================================================"
