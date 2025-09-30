import os, sys

# needed to add pngs to exe
def resource_path(relative_path):
    try:
        # for exe
        base_path = sys._MEIPASS
    except Exception:
        # for dev
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_images_folder():
    # always use the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # running as exe
        exe_dir = os.path.dirname(sys.executable)  # ← This uses where the EXE is located
    else:
        # running as script (for dev)
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    
    images_dir = os.path.join(exe_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    return images_dir