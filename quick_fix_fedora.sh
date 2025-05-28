#!/bin/bash

# Quick Fix for Fedora - Install Essential Dependencies
echo "🔧 Quick Fix for Fedora Linux"
echo "Installing essential dependencies..."

# Install pip and tkinter first
echo "📦 Installing pip and tkinter..."
sudo dnf install -y python3-pip python3-tkinter

# Install system packages that are available via dnf
echo "📦 Installing system packages..."
sudo dnf install -y \
    python3-numpy \
    python3-opencv \
    python3-pillow \
    python3-psutil \
    v4l-utils

# Install remaining packages via pip
echo "📦 Installing Python packages via pip..."
python3 -m pip install --user --upgrade pip
python3 -m pip install --user mediapipe pyautogui pynput screeninfo

# Add user to video group
echo "👤 Adding user to video group..."
sudo usermod -a -G video $USER

echo "✅ Quick fix completed!"
echo ""
echo "Next steps:"
echo "1. Log out and log back in (for video group permissions)"
echo "2. Test: python3 -c 'import cv2, mediapipe, pyautogui, tkinter; print(\"Success!\")'"
echo "3. Run: python3 simple_eye_mouse.py"
