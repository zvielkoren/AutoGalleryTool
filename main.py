import tkinter as tk
from src.gui.auto_gallery_gui import AutoGalleryGUI

def main():
    root = tk.Tk()
    app = AutoGalleryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
