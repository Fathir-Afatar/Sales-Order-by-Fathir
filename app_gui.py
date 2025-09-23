"""Main GUI application for POS Pintar by Fathir.

This module provides the main application window with navigation
to various POS system modules.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add current directory to Python path for module imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import GUI modules
from app.gui.member_gui import buat_frame_member
from app.gui.supplier_gui import buat_frame_supplier
from app.gui.produk_gui import buat_frame_produk
from app.gui.pengeluaran_gui import buat_frame_pengeluaran
from app.gui.pembelian_gui import buat_frame_pembelian
from app.gui.penjualan_gui import buat_frame_penjualan
from app.gui.stok_gui import buat_frame_stok
from app.gui.laporan_gui import buat_frame_laporan

class POSApplication:
    """Main POS application class."""
    
    def __init__(self):
        """Initialize the POS application."""
        self.root = None
        self.nav_frame = None
        self.content_frame = None
        self.navigation_buttons = []
        
    def setup_main_window(self):
        """Set up the main application window."""
        self.root = tk.Tk()
        self.root.title("POS Pintar by Fathir")
        self.root.geometry("1200x700")
        self.root.configure(bg="white")
        
    def setup_frames(self):
        """Set up the navigation and content frames."""
        # Navigation frame (left sidebar)
        self.nav_frame = tk.Frame(self.root, bg="#f0f0f0", width=200)
        self.nav_frame.pack(side="left", fill="y")
        self.nav_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Content frame (main area)
        self.content_frame = tk.Frame(self.root, bg="white")
        self.content_frame.pack(side="right", fill="both", expand=True)
        
    def create_navigation_buttons(self):
        """Create navigation buttons for different modules."""
        navigation_config = [
            ("Member", buat_frame_member),
            ("Supplier", buat_frame_supplier),
            ("Produk", buat_frame_produk),
            ("Pengeluaran", buat_frame_pengeluaran),
            ("Pembelian", buat_frame_pembelian),
            ("Penjualan", buat_frame_penjualan),
            ("Stok", buat_frame_stok),
            ("Laporan", buat_frame_laporan),
        ]
        
        for label, frame_function in navigation_config:
            button = tk.Button(
                self.nav_frame,
                text=label,
                font=("Arial", 11),
                width=20,
                pady=5,
                bg="#4CAF50",
                fg="white",
                relief="flat",
                command=lambda f=frame_function: self.show_frame(f)
            )
            button.pack(pady=2, padx=5, fill="x")
            self.navigation_buttons.append(button)
            
    def show_frame(self, frame_function):
        """Display the selected frame in the content area."""
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        try:
            # Create and display the new frame
            frame_function(self.content_frame)
            logger.info(f"Successfully loaded frame: {frame_function.__name__}")
        except Exception as e:
            error_msg = f"Error loading frame {frame_function.__name__}: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def run(self):
        """Start the application."""
        try:
            self.setup_main_window()
            self.setup_frames()
            self.create_navigation_buttons()
            
            # Show default frame
            self.show_frame(buat_frame_penjualan)
            
            logger.info("POS Pintar application started successfully")
            self.root.mainloop()
            
        except Exception as e:
            error_msg = f"Application startup error: {str(e)}"
            logger.critical(error_msg, exc_info=True)
            messagebox.showerror("Fatal Error",
                               "Application failed to start. Check app.log for details.")
            sys.exit(1)


def main():
    """Main entry point for the POS application."""
    app = POSApplication()
    app.run()


if __name__ == "__main__":
    main()