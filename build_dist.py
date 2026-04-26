import os
import subprocess
import shutil
import sys

def run_build():
    """
    Builds the ITMS Video Inference Tool into a standalone executable directory.
    Uses PyInstaller --onedir mode.
    """
    print("🚀 Starting ITMS Inference Tool Build Process...")
    
    # 1. Define command
    # --onedir: Create a directory containing the executable and dependencies
    # --noconsole: Hide the terminal window (GUI only)
    # --name: Name of the output executable
    cmd = [
        "pyinstaller",
        "--onedir",
        "--noconsole",
        "--name", "ITMS_Inference_Tool",
        "--clean",
        # Hidden imports often needed for CV2/Torch/PyQt6
        "--hidden-import", "PyQt6",
        "--hidden-import", "ultralytics",
        "--hidden-import", "cv2",
        "--hidden-import", "torch",
        "--exclude-module", "PyQt5",
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ PyInstaller build successful.")
    except subprocess.CalledProcessError:
        print("\n❌ PyInstaller build failed.")
        return

    # 2. Add Dynamic Folders to the Dist directory
    # We copy them so the user has a working baseline distribution
    dist_path = os.path.join("dist", "ITMS_Inference_Tool")
    folders_to_copy = ["models", "config.json"]
    
    print("\n📦 Packaging dynamic assets (models/config)...")
    for item in folders_to_copy:
        src = item
        dst = os.path.join(dist_path, item)
        
        if os.path.exists(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
                
        if os.path.isdir(src):
            shutil.copytree(src, dst)
            print(f"  + Copied directory: {src}")
        else:
            shutil.copy2(src, dst)
            print(f"  + Copied file: {src}")

    print(f"\n✨ Build Complete! Your application is in: {os.path.abspath(dist_path)}")
    print("💡 You can now safely share the 'ITMS_Inference_Tool' folder.")
    print("💡 Users can modify config.json or swap models in the 'models' folder dynamically.")

if __name__ == "__main__":
    run_build()
