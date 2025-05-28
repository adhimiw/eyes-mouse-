"""
Setup script for Eye-Controlled Computer Interface
Installs dependencies and configures the system
"""

import os
import sys
import subprocess
import platform
import logging
from pathlib import Path

def setup_logging():
    """Setup logging for installation"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('setup.log'),
            logging.StreamHandler()
        ]
    )

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        logging.error("Python 3.6 or higher is required")
        return False
    
    logging.info(f"Python version {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_requirements():
    """Install Python requirements"""
    try:
        logging.info("Installing Python requirements...")
        
        # Core requirements
        requirements = [
            "opencv-python==4.8.1.78",
            "mediapipe==0.10.7",
            "pyautogui==0.9.54",
            "numpy==1.24.3",
            "Pillow==10.0.1",
            "psutil==5.9.6",
            "pynput==1.7.6",
            "screeninfo==0.8.1"
        ]
        
        for requirement in requirements:
            logging.info(f"Installing {requirement}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", requirement], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                logging.error(f"Failed to install {requirement}: {result.stderr}")
                return False
            
        logging.info("All requirements installed successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error installing requirements: {e}")
        return False

def check_camera_access():
    """Check if camera is accessible"""
    try:
        import cv2
        
        logging.info("Testing camera access...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            logging.warning("Camera not accessible. Please check camera permissions.")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            logging.warning("Camera accessible but cannot read frames")
            return False
        
        logging.info("Camera access test successful")
        return True
        
    except Exception as e:
        logging.error(f"Camera test failed: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    try:
        directories = [
            "config",
            "logs",
            "calibration_data",
            "performance_logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logging.info(f"Created directory: {directory}")
        
        return True
        
    except Exception as e:
        logging.error(f"Error creating directories: {e}")
        return False

def create_desktop_shortcut():
    """Create desktop shortcut (Windows only)"""
    if platform.system() != "Windows":
        return True
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Eye Controlled Interface.lnk")
        target = os.path.join(os.getcwd(), "main.py")
        wDir = os.getcwd()
        icon = target
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()
        
        logging.info("Desktop shortcut created")
        return True
        
    except ImportError:
        logging.info("Desktop shortcut creation skipped (winshell not available)")
        return True
    except Exception as e:
        logging.error(f"Error creating desktop shortcut: {e}")
        return True  # Non-critical error

def check_system_requirements():
    """Check system requirements"""
    try:
        import psutil
        
        # Check RAM
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        
        if total_gb < 4:
            logging.warning(f"Low RAM detected: {total_gb:.1f}GB. 4GB+ recommended.")
        else:
            logging.info(f"RAM check passed: {total_gb:.1f}GB available")
        
        # Check CPU cores
        cpu_count = psutil.cpu_count()
        if cpu_count < 2:
            logging.warning(f"Low CPU core count: {cpu_count}. 2+ cores recommended.")
        else:
            logging.info(f"CPU check passed: {cpu_count} cores available")
        
        return True
        
    except Exception as e:
        logging.error(f"System requirements check failed: {e}")
        return False

def configure_permissions():
    """Configure system permissions"""
    system = platform.system()
    
    if system == "Linux":
        logging.info("Linux detected. You may need to add your user to the 'video' group:")
        logging.info("sudo usermod -a -G video $USER")
        logging.info("Then log out and log back in.")
    
    elif system == "macOS":
        logging.info("macOS detected. Camera permissions may be required.")
        logging.info("Go to System Preferences > Security & Privacy > Camera")
        logging.info("and allow access for Terminal or your Python environment.")
    
    elif system == "Windows":
        logging.info("Windows detected. Camera permissions should be automatic.")
    
    return True

def run_initial_test():
    """Run initial system test"""
    try:
        logging.info("Running initial system test...")
        
        # Test MediaPipe
        import mediapipe as mp
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)
        logging.info("MediaPipe test passed")
        
        # Test PyAutoGUI
        import pyautogui
        screen_size = pyautogui.size()
        logging.info(f"PyAutoGUI test passed. Screen size: {screen_size}")
        
        # Test OpenCV
        import cv2
        logging.info(f"OpenCV version: {cv2.__version__}")
        
        logging.info("All component tests passed")
        return True
        
    except Exception as e:
        logging.error(f"Initial test failed: {e}")
        return False

def main():
    """Main setup function"""
    setup_logging()
    
    logging.info("Starting Eye-Controlled Interface setup...")
    logging.info(f"Platform: {platform.system()} {platform.release()}")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        logging.error("Failed to install requirements")
        sys.exit(1)
    
    # Setup directories
    if not setup_directories():
        logging.error("Failed to setup directories")
        sys.exit(1)
    
    # Check system requirements
    if not check_system_requirements():
        logging.warning("System requirements check failed, but continuing...")
    
    # Configure permissions
    configure_permissions()
    
    # Check camera access
    if not check_camera_access():
        logging.warning("Camera access test failed. Please check camera permissions.")
    
    # Create desktop shortcut
    create_desktop_shortcut()
    
    # Run initial test
    if not run_initial_test():
        logging.error("Initial test failed")
        sys.exit(1)
    
    logging.info("Setup completed successfully!")
    logging.info("You can now run the application with: python main.py")
    
    # Offer to run the application
    try:
        response = input("\nWould you like to run the application now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            logging.info("Starting application...")
            subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        logging.info("Setup completed. Run 'python main.py' to start the application.")

if __name__ == "__main__":
    main()
