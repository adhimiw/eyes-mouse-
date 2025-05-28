#!/bin/bash

# Fedora Linux Installation Script for Eye-Controlled Interface
# This script installs all required system packages and Python dependencies

echo "============================================================"
echo "    Eye-Controlled Interface - Fedora Installation"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo dnf update -y

# Install system dependencies
print_status "Installing system dependencies..."

# Python and pip
print_status "Installing Python and pip..."
sudo dnf install -y python3 python3-pip python3-devel

# Tkinter (usually comes with python3-tkinter on Fedora)
print_status "Installing Tkinter..."
sudo dnf install -y python3-tkinter

# OpenCV dependencies
print_status "Installing OpenCV system dependencies..."
sudo dnf install -y \
    opencv-devel \
    opencv-python3 \
    libgtk-3-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    gfortran \
    openexr-dev \
    libatlas-base-dev \
    python3-numpy \
    libtbb2 \
    libtbb-dev \
    libjasper-dev \
    libdc1394-22-dev

# Camera and video dependencies
print_status "Installing camera and video dependencies..."
sudo dnf install -y \
    v4l-utils \
    cheese \
    guvcview

# Audio dependencies (for streaming controls)
print_status "Installing audio dependencies..."
sudo dnf install -y \
    pulseaudio \
    pulseaudio-utils \
    alsa-utils

# Development tools
print_status "Installing development tools..."
sudo dnf install -y \
    gcc \
    gcc-c++ \
    cmake \
    make \
    pkg-config

# Add user to video group for camera access
print_status "Adding user to video group..."
sudo usermod -a -G video $USER

# Install Python packages
print_status "Installing Python packages..."

# Upgrade pip first
python3 -m pip install --user --upgrade pip

# Install packages one by one with error handling
packages=(
    "numpy==1.24.3"
    "opencv-python==4.8.1.78"
    "mediapipe==0.10.7"
    "pyautogui==0.9.54"
    "Pillow==10.0.1"
    "psutil==5.9.6"
    "pynput==1.7.6"
    "screeninfo==0.8.1"
)

for package in "${packages[@]}"; do
    print_status "Installing $package..."
    if python3 -m pip install --user "$package"; then
        print_success "Successfully installed $package"
    else
        print_error "Failed to install $package"
        print_status "Trying alternative installation..."
        # Try without version constraint
        package_name=$(echo "$package" | cut -d'=' -f1)
        python3 -m pip install --user "$package_name"
    fi
done

# Test camera access
print_status "Testing camera access..."
if ls /dev/video* >/dev/null 2>&1; then
    print_success "Camera devices found: $(ls /dev/video*)"
else
    print_warning "No camera devices found. Please connect a camera."
fi

# Test Python imports
print_status "Testing Python imports..."
python3 -c "
import sys
modules = ['cv2', 'mediapipe', 'pyautogui', 'numpy', 'PIL', 'psutil', 'pynput', 'screeninfo', 'tkinter']
failed = []
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError as e:
        print(f'❌ {module}: {e}')
        failed.append(module)

if failed:
    print(f'\\nFailed imports: {failed}')
    sys.exit(1)
else:
    print('\\n🎉 All modules imported successfully!')
"

if [ $? -eq 0 ]; then
    print_success "All Python modules are working!"
else
    print_error "Some Python modules failed to import"
    print_status "Trying alternative installation methods..."
    
    # Try installing with dnf for some packages
    print_status "Installing packages via dnf..."
    sudo dnf install -y \
        python3-opencv \
        python3-numpy \
        python3-pillow \
        python3-psutil
fi

# Set up permissions
print_status "Setting up permissions..."

# Create udev rule for camera access
echo 'SUBSYSTEM=="video4linux", GROUP="video", MODE="0664"' | sudo tee /etc/udev/rules.d/99-camera-permissions.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Test the installation
print_status "Running system test..."
if python3 test_system.py; then
    print_success "System test completed!"
else
    print_warning "System test had some issues, but installation may still work"
fi

echo ""
echo "============================================================"
echo "                    INSTALLATION COMPLETE"
echo "============================================================"
print_success "Installation completed!"
echo ""
echo "Next steps:"
echo "1. Log out and log back in (for video group permissions)"
echo "2. Run: python3 test_system.py"
echo "3. Run: python3 main.py"
echo ""
print_warning "If you encounter issues:"
echo "- Restart your computer to ensure all permissions take effect"
echo "- Check camera permissions: ls -la /dev/video*"
echo "- Test camera: cheese or guvcview"
echo ""
echo "============================================================"
