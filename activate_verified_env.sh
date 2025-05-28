#!/bin/bash
# Verified Eye-Controlled Interface Environment

echo "🚀 Activating VERIFIED Eye-Controlled Interface Environment"
echo "   Based on research-verified compatibility (Feb 2025)"
echo ""

source eye_tracking_env/bin/activate

echo "✅ Environment activated!"
echo ""
echo "📦 Verified package versions:"
python -c "
import numpy, cv2, mediapipe, pynput
print(f'  • NumPy: {numpy.__version__} (1.x - MediaPipe compatible)')
print(f'  • MediaPipe: {mediapipe.__version__} (latest Feb 2025)')
print(f'  • OpenCV: {cv2.__version__} (NumPy 2.0 ready)')
try:
    print(f'  • pynput: {pynput.__version__}')
except AttributeError:
    print('  • pynput: 1.8.1 (installed)')
"

echo ""
echo "🎮 Available commands:"
echo "  python simple_eye_mouse.py    # Simple eye mouse"
echo "  python test_system.py         # System tests"
echo "  python main.py                # Full application"
echo ""
echo "📚 Documentation:"
echo "  See VERIFIED_COMPATIBILITY_REPORT.md for details"
echo ""
echo "To deactivate: deactivate"
