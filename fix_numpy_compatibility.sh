#!/bin/bash

# NumPy Compatibility Fix Script for Fedora Linux
# Resolves NumPy 2.x compatibility issues with OpenCV, MediaPipe, and PyAutoGUI

echo "============================================================"
echo "    NumPy Compatibility Fix for Eye-Controlled Interface"
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

# Check current NumPy version
print_status "Checking current NumPy version..."
NUMPY_VERSION=$(python3 -c "import numpy; print(numpy.__version__)" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "Current NumPy version: $NUMPY_VERSION"
    if [[ $NUMPY_VERSION == 2.* ]]; then
        print_warning "NumPy 2.x detected - this causes compatibility issues"
        NEEDS_DOWNGRADE=true
    else
        print_success "NumPy 1.x detected - compatible version"
        NEEDS_DOWNGRADE=false
    fi
else
    print_error "NumPy not found or import failed"
    NEEDS_DOWNGRADE=true
fi

# Function to uninstall conflicting packages
uninstall_packages() {
    print_status "Uninstalling conflicting packages..."
    
    # Remove system packages that might conflict
    sudo dnf remove -y python3-opencv python3-numpy python3-scipy 2>/dev/null || true
    
    # Remove pip packages
    python3 -m pip uninstall -y opencv-python opencv-contrib-python mediapipe pyautogui numpy scipy 2>/dev/null || true
    
    print_success "Conflicting packages removed"
}

# Function to install compatible NumPy version
install_compatible_numpy() {
    print_status "Installing compatible NumPy version..."
    
    # Install NumPy 1.24.3 (last stable 1.x version)
    python3 -m pip install --user "numpy>=1.21.0,<2.0.0"
    
    if [ $? -eq 0 ]; then
        print_success "Compatible NumPy installed"
    else
        print_error "Failed to install compatible NumPy"
        return 1
    fi
}

# Function to install packages with compatible versions
install_compatible_packages() {
    print_status "Installing packages with compatible versions..."
    
    # Install packages in specific order to avoid conflicts
    packages=(
        "numpy>=1.21.0,<2.0.0"
        "opencv-python==4.8.1.78"
        "mediapipe==0.10.7"
        "pyautogui==0.9.54"
        "Pillow>=9.0.0,<11.0.0"
        "psutil>=5.8.0"
        "pynput>=1.7.0"
        "screeninfo>=0.8.0"
    )
    
    for package in "${packages[@]}"; do
        print_status "Installing $package..."
        python3 -m pip install --user --force-reinstall "$package"
        
        if [ $? -eq 0 ]; then
            print_success "Successfully installed $package"
        else
            print_error "Failed to install $package"
            
            # Try alternative installation
            package_name=$(echo "$package" | cut -d'>' -f1 | cut -d'=' -f1 | cut -d'<' -f1)
            print_status "Trying alternative installation for $package_name..."
            python3 -m pip install --user --force-reinstall "$package_name"
        fi
    done
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    python3 -c "
import sys
import warnings
warnings.filterwarnings('ignore')

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
        
        # Special check for NumPy version
        if module == 'numpy':
            if version.startswith('2.'):
                print(f'⚠️  Warning: NumPy 2.x detected ({version}) - may cause issues')
            else:
                print(f'✅ NumPy version compatible: {version}')
                
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
    
    # Test basic functionality
    try:
        import cv2
        import numpy as np
        
        # Test OpenCV with NumPy
        test_array = np.zeros((100, 100, 3), dtype=np.uint8)
        result = cv2.cvtColor(test_array, cv2.COLOR_BGR2RGB)
        print('✅ OpenCV-NumPy integration test passed')
        
    except Exception as e:
        print(f'❌ OpenCV-NumPy integration test failed: {e}')
        sys.exit(1)
"
    
    return $?
}

# Main execution
print_status "Starting NumPy compatibility fix..."

# Step 1: Backup current environment info
print_status "Backing up current environment info..."
python3 -m pip list --user > pip_packages_backup.txt 2>/dev/null || true

# Step 2: Check if fix is needed
if [ "$NEEDS_DOWNGRADE" = true ]; then
    print_warning "NumPy compatibility fix required"
    
    # Step 3: Uninstall conflicting packages
    uninstall_packages
    
    # Step 4: Install compatible NumPy
    install_compatible_numpy
    if [ $? -ne 0 ]; then
        print_error "Failed to install compatible NumPy"
        exit 1
    fi
    
    # Step 5: Install other packages
    install_compatible_packages
    
else
    print_status "NumPy version appears compatible, but reinstalling packages to ensure compatibility..."
    install_compatible_packages
fi

# Step 6: Verify installation
print_status "Verifying installation..."
if verify_installation; then
    print_success "NumPy compatibility fix completed successfully!"
else
    print_error "Verification failed - some issues remain"
    exit 1
fi

# Step 7: Additional recommendations
echo ""
echo "============================================================"
echo "                    FIX COMPLETED"
echo "============================================================"
print_success "NumPy compatibility issues resolved!"
echo ""
echo "Next steps:"
echo "1. Test the eye tracking application:"
echo "   python3 simple_eye_mouse.py"
echo ""
echo "2. Run system tests:"
echo "   python3 test_system.py"
echo ""
echo "3. Launch the full application:"
echo "   python3 main.py"
echo ""
print_warning "Important notes:"
echo "- Keep NumPy < 2.0 to maintain compatibility"
echo "- If you need NumPy 2.x for other projects, consider using virtual environments"
echo "- Package versions are pinned to ensure compatibility"
echo ""
echo "============================================================"
