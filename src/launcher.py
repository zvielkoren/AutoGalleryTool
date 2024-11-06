import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

import argparse
import tkinter as tk
from src.gui.auto_gallery_gui import AutoGalleryGUI
from src.web.app import app

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['web', 'desktop'], default='desktop')
    args = parser.parse_args()

    if args.mode == 'web':
        app.run(debug=True)
    else:
        root = tk.Tk()
        gui = AutoGalleryGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()
