import sys
import os

def get_app_root():
    """
    Returns the absolute path to the directory containing the application.
    Works for both source code (dev) and PyInstaller/Nuitka frozen binaries.
    """
    if getattr(sys, 'frozen', False):
        # Running as a bundled executable
        # sys.executable is the path to the executable (e.g. dist/main/main.exe)
        return os.path.dirname(os.path.abspath(sys.executable))
    
    # Running from source
    # __file__ is video_inference_tool/utils/paths.py, so we go up 2 levels
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def resolve_path(relative_path):
    """
    Resolves a relative path to an absolute path based on the application root.
    """
    if os.path.isabs(relative_path):
        return relative_path
    return os.path.join(get_app_root(), relative_path)
