"""
CodeTantra Automation - Desktop Application
Dark themed Tkinter interface with API integration
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
import sys
import os
from pathlib import Path
import threading
import requests
from datetime import datetime

# Import our modules
import api_client
import automation_runner
import config_manager

class CodeTantraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CodeTantra Automation Pro")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Set minimum window size
        self.root.minsize(800, 600)
        
        # Configure dark theme colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#667eea"
        self.button_bg = "#667eea"
        self.button_hover = "#5568d3"
        self.entry_bg = "#2d2d30"
        self.frame_bg = "#252526"
        
        # Configure root background
        self.root.configure(bg=self.bg_color)
        
        # Show disclaimer first
        if not self.show_disclaimer():
            self.root.quit()
            return
        
        # Initialize config manager and API client
        self.config = config_manager.ConfigManager()
        self.api_client = api_client.APIClient()
        self.automation = None
        self.is_running = False
        
        # Check API health at startup
        self.api_available = self.check_api_health_at_startup()
        
        # Check if logged in
        token = self.config.get_token()
        if token:
            user_data = self.api_client.validate_token(token)
            if user_data:
                self.show_main_screen()
            else:
                self.show_login_screen()
        else:
            self.show_login_screen()
    
    def check_api_health_at_startup(self):
        """Check API health at startup and show UI warning if needed"""
        try:
            # Test API connectivity
            if self.api_client.ping():
                print("[OK] API server is healthy")
                return True
            else:
                print("[WARNING] API server is not responding")
                # Schedule the warning dialog to show after the main window is ready
                self.root.after(1000, self.show_api_warning_dialog)
                # Also show a simple messagebox as fallback
                self.root.after(2000, self.show_fallback_warning)
                return False
        except Exception as e:
            print(f"[WARNING] API health check failed: {e}")
            # Schedule the warning dialog to show after the main window is ready
            self.root.after(1000, self.show_api_warning_dialog)
            # Also show a simple messagebox as fallback
            self.root.after(2000, self.show_fallback_warning)
            return False
    
    def show_disclaimer(self):
        """Show disclaimer dialog before application starts"""
        disclaimer_window = tk.Toplevel(self.root)
        disclaimer_window.title("Disclaimer - Educational Use Only")
        disclaimer_window.geometry("600x400")
        disclaimer_window.resizable(False, False)
        disclaimer_window.configure(bg=self.bg_color)
        
        # Center the window
        disclaimer_window.transient(self.root)
        disclaimer_window.grab_set()
        
        # Make window appear in center of screen
        disclaimer_window.update_idletasks()
        x = (disclaimer_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (disclaimer_window.winfo_screenheight() // 2) - (400 // 2)
        disclaimer_window.geometry(f"600x400+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(disclaimer_window, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="IMPORTANT DISCLAIMER",
            font=("Arial", 16, "bold"),
            fg="#ff6b6b",
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 20))
        
        # Disclaimer text
        disclaimer_text = """
This software is provided for EDUCATIONAL PURPOSES ONLY.

By using this application, you acknowledge and agree that:

• This tool is intended solely for educational and learning purposes
• You are using this software at your own risk
• The developers are NOT responsible for any consequences of using this software
• You are responsible for complying with all applicable terms of service
• Any misuse of this software is strictly prohibited
• Academic integrity policies must be followed at all times

The developers disclaim all liability for any damages, losses, or consequences
resulting from the use of this software.

If you do not agree with these terms, please close this application immediately.
        """
        
        text_widget = tk.Text(
            main_frame,
            height=15,
            width=70,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg=self.entry_bg,
            fg=self.fg_color,
            relief=tk.FLAT,
            borderwidth=0,
            padx=10,
            pady=10
        )
        text_widget.pack(pady=(0, 20))
        text_widget.insert(tk.END, disclaimer_text.strip())
        text_widget.config(state=tk.DISABLED)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Agree button
        agree_btn = tk.Button(
            button_frame,
            text="I AGREE - Continue",
            command=lambda: self.accept_disclaimer(disclaimer_window),
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        agree_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Disagree button
        disagree_btn = tk.Button(
            button_frame,
            text="I DISAGREE - Exit",
            command=lambda: self.reject_disclaimer(disclaimer_window),
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        disagree_btn.pack(side=tk.LEFT)
        
        # Store the result
        self.disclaimer_accepted = False
        
        # Wait for user response
        disclaimer_window.wait_window()
        
        return self.disclaimer_accepted
    
    def accept_disclaimer(self, window):
        """User accepted the disclaimer"""
        self.disclaimer_accepted = True
        window.destroy()
    
    def reject_disclaimer(self, window):
        """User rejected the disclaimer"""
        self.disclaimer_accepted = False
        window.destroy()

    def show_api_warning_dialog(self):
        """Show warning dialog when API is not available - BLOCKS usage in offline mode"""
        print("[DEBUG] Showing API warning dialog...")
        
        # Create a custom warning dialog
        warning_window = tk.Toplevel(self.root)
        warning_window.title("API Connection Required")
        warning_window.geometry("500x500")
        warning_window.resizable(False, False)
        warning_window.configure(bg=self.bg_color)
        
        # Center the window and make it modal
        warning_window.transient(self.root)
        warning_window.grab_set()
        warning_window.protocol("WM_DELETE_WINDOW", lambda: None)  # Prevent closing
        
        # Make it appear on top and focus
        warning_window.lift()
        warning_window.focus_force()
        warning_window.attributes('-topmost', True)
        warning_window.after_idle(lambda: warning_window.attributes('-topmost', False))
        
        print("[DEBUG] Warning dialog created and configured")
        
        # Main frame
        main_frame = tk.Frame(warning_window, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Warning icon and title
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill="x", pady=(0, 20))
        
        # Warning icon (using text symbol)
        warning_icon = tk.Label(
            title_frame,
            text="🚫",
            font=("Arial", 48, "bold"),
            bg=self.bg_color,
            fg="#ef4444"
        )
        warning_icon.pack(side="left", padx=(0, 15))
        
        # Title text
        title_text = tk.Label(
            title_frame,
            text="API Server Required",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg="#ef4444"
        )
        title_text.pack(side="left")
        
        # Warning message
        warning_text = tk.Text(
            main_frame,
            height=16,
            width=50,
            wrap="word",
            font=("Arial", 11),
            bg=self.entry_bg,
            fg=self.fg_color,
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=15
        )
        warning_text.pack(fill="both", expand=True, pady=(0, 20))
        
        # Insert warning message
        warning_message = """OFFLINE MODE NOT ALLOWED

The API server is currently unavailable. This application requires an active API connection to function properly.

WHY API IS REQUIRED:
• Credit system management
• User authentication and validation
• Problem tracking and statistics
• Security and rate limiting
• Real-time status updates

POSSIBLE CAUSES:
• Server is starting up (30-60 seconds)
• Server is sleeping (inactive 15+ minutes)
• Network connectivity issues
• Server maintenance

WHAT TO DO:
1. Check your internet connection
2. Wait 1-2 minutes for server startup
3. Click "Retry Connection" to test again
4. Contact support if problem persists

You cannot use the automation features without API connectivity."""
        
        warning_text.insert("1.0", warning_message)
        warning_text.config(state="disabled")
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Retry button
        retry_button = tk.Button(
            button_frame,
            text="Retry Connection",
            font=("Arial", 12, "bold"),
            bg="#3b82f6",
            fg="white",
            relief="flat",
            padx=20,
            pady=10,
            command=lambda: self.retry_api_connection(warning_window)
        )
        retry_button.pack(side="right", padx=(10, 0))
        
        # Exit button
        exit_button = tk.Button(
            button_frame,
            text="Exit Application",
            font=("Arial", 12),
            bg="#6b7280",
            fg="white",
            relief="flat",
            padx=20,
            pady=10,
            command=self.root.quit
        )
        exit_button.pack(side="right")
        
        # Center the window on screen
        warning_window.update_idletasks()
        x = (warning_window.winfo_screenwidth() // 2) - (warning_window.winfo_width() // 2)
        y = (warning_window.winfo_screenheight() // 2) - (warning_window.winfo_height() // 2)
        warning_window.geometry(f"+{x}+{y}")
        
        print("[DEBUG] Warning dialog positioned and ready")
        
        # Force update and show
        warning_window.update()
        warning_window.deiconify()
    
    def show_fallback_warning(self):
        """Show a simple messagebox warning as fallback - BLOCKS usage"""
        try:
            print("[DEBUG] Showing fallback warning messagebox...")
            messagebox.showerror(
                "API Server Required",
                "OFFLINE MODE NOT ALLOWED\n\n"
                "The API server is not responding.\n\n"
                "This application requires an active API connection to function.\n\n"
                "Possible causes:\n"
                "• Server is starting up (30-60 seconds)\n"
                "• Server is sleeping (inactive 15+ minutes)\n"
                "• Network connectivity issues\n\n"
                "Please check your connection and restart the application."
            )
        except Exception as e:
            print(f"[ERROR] Failed to show fallback warning: {e}")
    
    def retry_api_connection(self, warning_window):
        """Retry API connection and update dialog"""
        # Show loading state
        for widget in warning_window.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        child.config(state="disabled", text="Testing...")
        
        # Test connection
        if self.api_client.ping():
            # Success - update API status and close dialog
            self.api_available = True
            self.api_status_label.config(text="[ONLINE] API Available", fg="#10b981")
            self.log_message("[SUCCESS] API connection restored!")
            
            # Show success message briefly then close
            self.show_api_success_message(warning_window)
            
            # Close dialog after 2 seconds
            warning_window.after(2000, lambda: self.close_api_warning(warning_window, continue_anyway=True))
        else:
            # Still failed - re-enable buttons
            for widget in warning_window.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Button):
                            child.config(state="normal")
                            if "Testing" in child.cget("text"):
                                child.config(text="Retry Connection")
    
    def show_api_success_message(self, warning_window):
        """Show success message when API connection is restored"""
        # Update the warning text to show success
        for widget in warning_window.winfo_children():
            if isinstance(widget, tk.Text):
                widget.config(state="normal")
                widget.delete("1.0", "end")
                widget.insert("1.0", "✅ API CONNECTION RESTORED!\n\nYou can now use all features normally.\n\nThis dialog will close automatically...")
                widget.config(state="disabled")
                break
        
        # Update buttons to show success
        for widget in warning_window.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        if "Retry" in child.cget("text"):
                            child.config(text="✅ Connected", state="disabled", bg="#10b981")
                        elif "Exit" in child.cget("text"):
                            child.pack_forget()
    
    def close_api_warning(self, warning_window, continue_anyway=False):
        """Close the API warning dialog"""
        warning_window.destroy()
        if continue_anyway:
            # API is restored, enable automation buttons
            self.start_btn.config(state=tk.NORMAL)
            self.endless_btn.config(state=tk.NORMAL)
            self.log_message("[INFO] All features are now available!")
        else:
            self.root.quit()
    
    def refresh_api_status(self):
        """Refresh API status and update UI"""
        try:
            # Show loading state
            self.refresh_api_btn.config(text="Testing...", state="disabled")
            self.api_status_label.config(text="[TESTING] Checking API...", fg="#6b7280")
            
            # Test API connection
            if self.api_client.ping():
                self.api_available = True
                self.api_status_label.config(text="[ONLINE] API Available", fg="#10b981")
                self.log_message("[SUCCESS] API connection restored!")
                # Enable automation buttons
                self.start_btn.config(state=tk.NORMAL)
                self.endless_btn.config(state=tk.NORMAL)
            else:
                self.api_available = False
                self.api_status_label.config(text="[OFFLINE] API Unavailable", fg="#ef4444")
                self.log_message("[ERROR] API connection failed")
                # Disable automation buttons
                self.start_btn.config(state=tk.DISABLED)
                self.endless_btn.config(state=tk.DISABLED)
            
            # Re-enable button
            self.refresh_api_btn.config(text="Refresh API Status", state="normal")
            
        except Exception as e:
            self.api_available = False
            self.api_status_label.config(text="[ERROR] API Error", fg="#ef4444")
            self.refresh_api_btn.config(text="Refresh API Status", state="normal")
            # Disable automation buttons on error
            self.start_btn.config(state=tk.DISABLED)
            self.endless_btn.config(state=tk.DISABLED)
            self.log_message(f"[ERROR] API test error: {e}")
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Display login screen"""
        self.clear_window()
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo
        logo_label = tk.Label(
            main_frame,
            text="CT",
            font=("Arial", 36, "bold"),
            bg=self.accent_color,
            fg="white",
            width=3,
            height=1
        )
        logo_label.pack(pady=(0, 20))
        
        # Title
        title = tk.Label(
            main_frame,
            text="CodeTantra Automation Pro",
            font=("Arial", 20, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        title.pack(pady=(0, 10))
        
        subtitle = tk.Label(
            main_frame,
            text="Login to continue",
            font=("Arial", 12),
            bg=self.bg_color,
            fg="#999999"
        )
        subtitle.pack(pady=(0, 30))
        
        # Email
        tk.Label(
            main_frame,
            text="Email:",
            font=("Arial", 11),
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(anchor="w", pady=(0, 5))
        
        self.email_entry = tk.Entry(
            main_frame,
            font=("Arial", 11),
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            width=35
        )
        self.email_entry.pack(pady=(0, 15), ipady=8)
        
        # Password
        tk.Label(
            main_frame,
            text="Password:",
            font=("Arial", 11),
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(anchor="w", pady=(0, 5))
        
        # Password frame for entry and view button
        password_frame = tk.Frame(main_frame, bg=self.bg_color)
        password_frame.pack(pady=(0, 10))
        
        self.password_entry = tk.Entry(
            password_frame,
            font=("Arial", 11),
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            width=30,
            show="*"
        )
        self.password_entry.pack(side=tk.LEFT, ipady=8)
        
        # View password button
        self.show_password = tk.BooleanVar()
        self.view_password_btn = tk.Button(
            password_frame,
            text="Show",
            font=("Arial", 8),
            bg=self.entry_bg,
            fg=self.fg_color,
            relief=tk.FLAT,
            width=4,
            command=self.toggle_password_visibility
        )
        self.view_password_btn.pack(side=tk.LEFT, padx=(5, 0), ipady=8)
        
        # Remember me
        self.remember_var = tk.BooleanVar()
        remember_check = tk.Checkbutton(
            main_frame,
            text="Remember me",
            variable=self.remember_var,
            font=("Arial", 10),
            bg=self.bg_color,
            fg="#999999",
            selectcolor=self.entry_bg,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        remember_check.pack(pady=(0, 20))
        
        # Login button
        login_btn = tk.Button(
            main_frame,
            text="Login",
            font=("Arial", 12, "bold"),
            bg=self.button_bg,
            fg="white",
            relief=tk.FLAT,
            width=35,
            cursor="hand2",
            command=self.handle_login
        )
        login_btn.pack(ipady=8)
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 10),
            bg=self.bg_color,
            fg="red"
        )
        self.status_label.pack(pady=(15, 0))
        
        # Bind enter key
        self.password_entry.bind('<Return>', lambda e: self.handle_login())
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password.get():
            self.password_entry.config(show="")
            self.view_password_btn.config(text="Hide")
        else:
            self.password_entry.config(show="*")
            self.view_password_btn.config(text="Show")
        self.show_password.set(not self.show_password.get())
    
    def toggle_target_password_visibility(self):
        """Toggle target password visibility"""
        if self.show_target_password.get():
            self.target_password.config(show="")
            self.view_target_password_btn.config(text="Hide")
        else:
            self.target_password.config(show="*")
            self.view_target_password_btn.config(text="Show")
        self.show_target_password.set(not self.show_target_password.get())
    
    def toggle_answers_password_visibility(self):
        """Toggle answers password visibility"""
        if self.answers_show_password.get():
            self.answers_password.config(show="")
            self.view_answers_password_btn.config(text="Hide")
        else:
            self.answers_password.config(show="*")
            self.view_answers_password_btn.config(text="Show")
        self.answers_show_password.set(not self.answers_show_password.get())
    
    def handle_login(self):
        """Handle login button click"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not email or not password:
            self.status_label.config(text="Please enter both email and password")
            return
        
        self.status_label.config(text="Logging in...", fg=self.accent_color)
        self.root.update()
        
        result = self.api_client.login(email, password, self.remember_var.get())
        
        if result['success']:
            self.config.save_token(result['token'])
            self.config.save_user_data(result['user'])
            self.show_main_screen()
        else:
            self.status_label.config(text=result['error'], fg="red")
    
    def show_main_screen(self):
        """Display main application screen"""
        self.clear_window()
        
        # Get user data
        user_data = self.config.get_user_data()
        credits = user_data.get('credits', 0)
        
        # Header Frame
        header_frame = tk.Frame(self.root, bg=self.frame_bg, height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Logo and title in header
        logo_frame = tk.Frame(header_frame, bg=self.frame_bg)
        logo_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(
            logo_frame,
            text="CT",
            font=("Arial", 18, "bold"),
            bg=self.accent_color,
            fg="white",
            width=2
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            logo_frame,
            text="CodeTantra Automation Pro",
            font=("Arial", 16, "bold"),
            bg=self.frame_bg,
            fg=self.fg_color
        ).pack(side=tk.LEFT)
        
        # Credits and logout in header
        right_frame = tk.Frame(header_frame, bg=self.frame_bg)
        right_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        self.credits_label = tk.Label(
            right_frame,
            text=f"Credits: {credits}",
            font=("Arial", 12, "bold"),
            bg=self.frame_bg,
            fg="#10b981"
        )
        self.credits_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # API Status indicator
        self.api_status_label = tk.Label(
            right_frame,
            text="[ONLINE] API Available" if self.api_available else "[OFFLINE] API Unavailable",
            font=("Arial", 10),
            bg=self.frame_bg,
            fg="#10b981" if self.api_available else "#ef4444"
        )
        self.api_status_label.pack(side=tk.LEFT, padx=(0, 15))
        
        logout_btn = tk.Button(
            right_frame,
            text="Logout",
            font=("Arial", 10),
            bg="#ef4444",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.handle_logout
        )
        logout_btn.pack(side=tk.LEFT)
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Configuration
        left_panel = tk.Frame(content_frame, bg=self.frame_bg, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        tk.Label(
            left_panel,
            text="Configuration",
            font=("Arial", 14, "bold"),
            bg=self.frame_bg,
            fg=self.fg_color
        ).pack(pady=(15, 10), padx=15, anchor="w")
        
        # Create input fields
        self.create_config_fields(left_panel)
        
        # Right panel - Logs and Control
        right_panel = tk.Frame(content_frame, bg=self.frame_bg)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            right_panel,
            text="Automation Status",
            font=("Arial", 14, "bold"),
            bg=self.frame_bg,
            fg=self.fg_color
        ).pack(pady=(15, 10), padx=15, anchor="w")
        
        # Status display
        self.status_display = tk.Label(
            right_panel,
            text="Ready",
            font=("Arial", 12),
            bg=self.frame_bg,
            fg="#10b981"
        )
        self.status_display.pack(pady=(0, 10), padx=15, anchor="w")
        
        # Logs
        tk.Label(
            right_panel,
            text="Activity Log:",
            font=("Arial", 11),
            bg=self.frame_bg,
            fg=self.fg_color
        ).pack(pady=(10, 5), padx=15, anchor="w")
        
        self.log_text = scrolledtext.ScrolledText(
            right_panel,
            height=20,
            bg="#0d1117",
            fg="#c9d1d9",
            font=("Consolas", 9),
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Start button
        self.start_btn = tk.Button(
            right_panel,
            text="Start Automation",
            font=("Arial", 12, "bold"),
            bg=self.button_bg,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.start_automation,
            state=tk.NORMAL if self.api_available else tk.DISABLED
        )
        self.start_btn.pack(fill=tk.X, padx=15, pady=(0, 10), ipady=10)
        
        # Endless mode button
        self.endless_btn = tk.Button(
            right_panel,
            text="Endless Mode",
            font=("Arial", 12, "bold"),
            bg="#10b981",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.start_endless_mode,
            state=tk.NORMAL if self.api_available else tk.DISABLED
        )
        self.endless_btn.pack(fill=tk.X, padx=15, pady=(0, 10), ipady=10)
        
        # API Status refresh button
        self.refresh_api_btn = tk.Button(
            right_panel,
            text="Refresh API Status",
            font=("Arial", 10),
            bg="#6b7280",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.refresh_api_status
        )
        self.refresh_api_btn.pack(fill=tk.X, padx=15, pady=(0, 10), ipady=8)
        
    
    def create_config_fields(self, parent):
        """Create configuration input fields"""
        fields_frame = tk.Frame(parent, bg=self.frame_bg)
        fields_frame.pack(fill=tk.BOTH, padx=15, pady=10)
        
        # Load saved config
        config = self.config.get_automation_config()
        
        # URL
        tk.Label(
            fields_frame,
            text="CodeTantra URL:",
            font=("Arial", 10),
            bg=self.frame_bg,
            fg=self.fg_color
        ).pack(anchor="w", pady=(0, 5))
        
        self.url_entry = tk.Entry(
            fields_frame,
            font=("Arial", 10),
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT
        )
        self.url_entry.pack(fill=tk.X, pady=(0, 15), ipady=6)
        self.url_entry.insert(0, config.get('url', ''))
        
        # Answers Email
        tk.Label(
            fields_frame,
            text="Answers Account Email:",
            font=("Arial", 10),
            bg=self.frame_bg,
            fg=self.fg_color
        ).pack(anchor="w", pady=(0, 5))
        
        self.answers_email = tk.Entry(
            fields_frame,
            font=("Arial", 10),
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT
        )
        self.answers_email.pack(fill=tk.X, pady=(0, 10), ipady=6)
        self.answers_email.insert(0, config.get('answers_email', ''))
        
        # Answers Password
        tk.Label(
            fields_frame,
            text="Answers Account Password:",
            font=("Arial", 10),
            bg=self.frame_bg,
            fg=self.fg_color
        ).pack(anchor="w", pady=(0, 5))
        
        # Answers password frame for entry and view button
        answers_password_frame = tk.Frame(fields_frame, bg=self.frame_bg)
        answers_password_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.answers_password = tk.Entry(
            answers_password_frame,
            font=("Arial", 10),
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            show="*"
        )
        self.answers_password.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        self.answers_password.insert(0, config.get('answers_password', ''))
        
        # View answers password button
        self.answers_show_password = tk.BooleanVar()
        self.view_answers_password_btn = tk.Button(
            answers_password_frame,
            text="Show",
            font=("Arial", 8),
            bg=self.entry_bg,
            fg=self.fg_color,
            relief=tk.FLAT,
            width=5,
            command=self.toggle_answers_password_visibility
        )
        self.view_answers_password_btn.pack(side=tk.LEFT, padx=(5, 0), ipady=6)
        
        # Target Email
        tk.Label(
            fields_frame,
            text="Target Account Email:",
            font=("Arial", 10),
            bg=self.frame_bg,
            fg=self.fg_color
        ).pack(anchor="w", pady=(0, 5))
        
        self.target_email = tk.Entry(
            fields_frame,
            font=("Arial", 10),
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT
        )
        self.target_email.pack(fill=tk.X, pady=(0, 10), ipady=6)
        self.target_email.insert(0, config.get('target_email', ''))
        
        # Target Password
        tk.Label(
            fields_frame,
            text="Target Account Password:",
            font=("Arial", 10),
            bg=self.frame_bg,
            fg=self.fg_color
        ).pack(anchor="w", pady=(0, 5))
        
        # Target password frame
        target_password_frame = tk.Frame(fields_frame, bg=self.frame_bg)
        target_password_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.target_password = tk.Entry(
            target_password_frame,
            font=("Arial", 10),
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            show="*"
        )
        self.target_password.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        self.target_password.insert(0, config.get('target_password', ''))
        
        # View target password button
        self.show_target_password = tk.BooleanVar()
        self.view_target_password_btn = tk.Button(
            target_password_frame,
            text="Show",
            font=("Arial", 8),
            bg=self.entry_bg,
            fg=self.fg_color,
            relief=tk.FLAT,
            width=4,
            command=self.toggle_target_password_visibility
        )
        self.view_target_password_btn.pack(side=tk.LEFT, padx=(5, 0), ipady=6)
        
        # Number of problems
        tk.Label(
            fields_frame,
            text="Number of Problems:",
            font=("Arial", 10),
            bg=self.frame_bg,
            fg=self.fg_color
        ).pack(anchor="w", pady=(0, 5))
        
        self.num_problems = tk.Entry(
            fields_frame,
            font=("Arial", 10),
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT
        )
        self.num_problems.pack(fill=tk.X, pady=(0, 15), ipady=6)
        self.num_problems.insert(0, config.get('num_problems', '10'))
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def start_automation(self):
        """Start the automation process"""
        if self.is_running:
            messagebox.showwarning("Already Running", "Automation is already in progress")
            return
        
        # Check API availability
        if not self.api_available:
            messagebox.showerror(
                "API Required", 
                "API server is unavailable!\n\n"
                "This application requires an active API connection to function.\n\n"
                "Please check your connection and try again."
            )
            return
        
        # Validate inputs first
        if not all([
            self.url_entry.get(),
            self.answers_email.get(),
            self.answers_password.get(),
            self.target_email.get(),
            self.target_password.get(),
            self.num_problems.get()
        ]):
            messagebox.showerror("Missing Information", "Please fill in all fields")
            return
        
        # Save configuration
        config = {
            'url': self.url_entry.get(),
            'answers_email': self.answers_email.get(),
            'answers_password': self.answers_password.get(),
            'target_email': self.target_email.get(),
            'target_password': self.target_password.get(),
            'num_problems': self.num_problems.get()
        }
        self.config.save_automation_config(config)
        
        # Update UI
        self.is_running = True
        self.start_btn.config(text="Running...", state=tk.DISABLED, bg="#999999")
        self.endless_btn.config(text="Endless Mode", state=tk.DISABLED, bg="#999999")
        self.status_display.config(text="Running", fg="#f59e0b")
        self.log_text.delete(1.0, tk.END)
        self.log_message("Starting automation...")
        
        # Start automation in thread
        thread = threading.Thread(target=self.run_automation_thread, args=(config,))
        thread.daemon = True
        thread.start()
    
    def start_endless_mode(self):
        """Start endless mode - solve all available problems"""
        if self.is_running:
            messagebox.showwarning("Already Running", "Automation is already in progress")
            return
        
        # Check API availability
        if not self.api_available:
            messagebox.showerror(
                "API Required", 
                "API server is unavailable!\n\n"
                "This application requires an active API connection to function.\n\n"
                "Please check your connection and try again."
            )
            return
        
        # Validate inputs
        if not all([
            self.url_entry.get(),
            self.answers_email.get(),
            self.answers_password.get(),
            self.target_email.get(),
            self.target_password.get()
        ]):
            messagebox.showerror("Missing Information", "Please fill in all fields")
            return
        
        # Confirm endless mode
        if not messagebox.askyesno("Endless Mode", 
            "Endless mode will attempt to solve ALL available problems.\n"
            "This may take a very long time and use many credits.\n"
            "Are you sure you want to continue?"):
            return
        
        # Save configuration
        config = {
            'url': self.url_entry.get(),
            'answers_email': self.answers_email.get(),
            'answers_password': self.answers_password.get(),
            'target_email': self.target_email.get(),
            'target_password': self.target_password.get(),
            'num_problems': '999999',  # Very large number for endless mode
            'endless_mode': True
        }
        self.config.save_automation_config(config)
        
        # Update UI
        self.is_running = True
        self.start_btn.config(text="Running...", state=tk.DISABLED, bg="#6b7280")
        self.endless_btn.config(text="Endless Running...", state=tk.DISABLED, bg="#6b7280")
        self.status_display.config(text="Endless Mode Running", fg="#10b981")
        self.log_text.delete(1.0, tk.END)
        self.log_message("Starting endless mode...")
        self.log_message("This will attempt to solve ALL available problems!")
        
        # Start endless automation in thread
        thread = threading.Thread(target=self.run_endless_automation_thread, args=(config,))
        thread.daemon = True
        thread.start()
    
    def run_automation_thread(self, config):
        """Run automation in separate thread"""
        try:
            # Create automation runner
            runner = automation_runner.AutomationRunner(
                config,
                self.api_client,
                self.log_message
            )
            
            # Run automation
            result = runner.run()
            
            # Update UI with results
            self.root.after(0, self.show_results, result)
            
        except Exception as e:
            self.root.after(0, self.automation_error, str(e))
    
    def run_endless_automation_thread(self, config):
        """Run endless automation in separate thread"""
        try:
            # Create automation runner for endless mode
            runner = automation_runner.AutomationRunner(
                config,
                self.api_client,
                self.log_message
            )
            
            # Run endless automation
            result = runner.run_endless()
            
            # Update UI with results
            self.root.after(0, self.show_endless_results, result)
            
        except Exception as e:
            self.root.after(0, self.automation_error, str(e))
    
    def show_results(self, result):
        """Show automation results with detailed breakdown"""
        self.is_running = False
        self.start_btn.config(text="Start Automation", state=tk.NORMAL, bg=self.button_bg)
        self.endless_btn.config(text="Endless Mode", state=tk.NORMAL, bg="#10b981")
        self.status_display.config(text="Completed", fg="#10b981")
        
        self.log_message("\nAutomation completed!")
        self.log_message(f"Problems solved: {result['solved']}")
        self.log_message(f"Problems failed: {result['failed']}")
        self.log_message(f"Problems skipped: {result['skipped']}")
        
        # Show detailed breakdown if available
        if 'problem_details' in result:
            self.log_message("\n📊 DETAILED BREAKDOWN BY QUESTION TYPE:")
            for question_type, counts in result['problem_details'].items():
                if sum(counts.values()) > 0:
                    type_name = question_type.replace('_', ' ').title()
                    self.log_message(f"  {type_name}:")
                    self.log_message(f"    ✓ Solved: {counts['solved']}")
                    self.log_message(f"    ⊘ Skipped: {counts['skipped']}")
                    self.log_message(f"    ✗ Failed: {counts['failed']}")
        
        # Show credits information if available
        if 'credits' in result:
            credit_info = result['credits']
            self.log_message(f"\n💰 CREDITS CALCULATION:")
            self.log_message(f"  Total credits to deduct: {credit_info['total_credits']}")
            for question_type, breakdown in credit_info['breakdown'].items():
                if breakdown['total_credits'] > 0:
                    type_name = question_type.replace('_', ' ').title()
                    self.log_message(f"  {type_name}: {breakdown['total_credits']} credits")
        
        # Update credits
        self.refresh_credits()
        
        # Create detailed message for dialog
        message = f"Solved: {result['solved']}\nFailed: {result['failed']}\nSkipped: {result['skipped']}"
        if 'credits' in result:
            message += f"\n\nCredits to deduct: {result['credits']['total_credits']}"
        
        # Show detailed results dialog
        self.show_detailed_results_dialog(result)
    
    def show_detailed_results_dialog(self, result):
        """Show detailed results in a custom dialog"""
        # Create detailed results window
        results_window = tk.Toplevel(self.root)
        results_window.title("Automation Results - Detailed Report")
        results_window.geometry("600x500")
        results_window.resizable(True, True)
        results_window.configure(bg=self.bg_color)
        
        # Make it modal
        results_window.transient(self.root)
        results_window.grab_set()
        
        # Center the window
        results_window.update_idletasks()
        x = (results_window.winfo_screenwidth() // 2) - (results_window.winfo_width() // 2)
        y = (results_window.winfo_screenheight() // 2) - (results_window.winfo_height() // 2)
        results_window.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(results_window, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Automation Complete!",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg="#10b981"
        )
        title_label.pack(pady=(0, 20))
        
        # Summary frame
        summary_frame = tk.LabelFrame(
            main_frame,
            text="Summary",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            relief=tk.RAISED,
            bd=1
        )
        summary_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Summary content
        summary_content = tk.Frame(summary_frame, bg=self.bg_color)
        summary_content.pack(fill=tk.X, padx=10, pady=10)
        
        # Summary stats
        stats_frame = tk.Frame(summary_content, bg=self.bg_color)
        stats_frame.pack(fill=tk.X)
        
        tk.Label(stats_frame, text=f"Solved: {result['solved']}", font=("Arial", 11), bg=self.bg_color, fg="#10b981").pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(stats_frame, text=f"Failed: {result['failed']}", font=("Arial", 11), bg=self.bg_color, fg="#ef4444").pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(stats_frame, text=f"Skipped: {result['skipped']}", font=("Arial", 11), bg=self.bg_color, fg="#f59e0b").pack(side=tk.LEFT)
        
        # Credits info
        if 'credits' in result:
            credits_frame = tk.Frame(summary_content, bg=self.bg_color)
            credits_frame.pack(fill=tk.X, pady=(10, 0))
            tk.Label(credits_frame, text=f"Credits Deducted: {result['credits']['total_credits']}", font=("Arial", 11, "bold"), bg=self.bg_color, fg="#3b82f6").pack()
        
        # Detailed breakdown
        if 'problem_details' in result:
            details_frame = tk.LabelFrame(
                main_frame,
                text="Breakdown by Question Type",
                font=("Arial", 12, "bold"),
                bg=self.bg_color,
                fg=self.fg_color,
                relief=tk.RAISED,
                bd=1
            )
            details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            
            # Create scrollable text widget
            text_frame = tk.Frame(details_frame, bg=self.bg_color)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            details_text = tk.Text(
                text_frame,
                height=12,
                wrap=tk.WORD,
                font=("Consolas", 10),
                bg=self.entry_bg,
                fg=self.fg_color,
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=10
            )
            details_text.pack(fill=tk.BOTH, expand=True)
            
            # Add scrollbar
            scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=details_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            details_text.config(yscrollcommand=scrollbar.set)
            
            # Populate details
            details_content = ""
            for question_type, counts in result['problem_details'].items():
                if sum(counts.values()) > 0:
                    type_name = question_type.replace('_', ' ').title()
                    details_content += f"{type_name}:\n"
                    details_content += f"  Solved: {counts['solved']}\n"
                    details_content += f"  Failed: {counts['failed']}\n"
                    details_content += f"  Skipped: {counts['skipped']}\n\n"
            
            if 'credits' in result:
                details_content += "\nCredits Breakdown:\n"
                for question_type, breakdown in result['credits']['breakdown'].items():
                    if breakdown['total_credits'] > 0:
                        type_name = question_type.replace('_', ' ').title()
                        details_content += f"{type_name}: {breakdown['total_credits']} credits\n"
            
            details_text.insert(tk.END, details_content)
            details_text.config(state=tk.DISABLED)
        
        # Close button
        close_btn = tk.Button(
            main_frame,
            text="Close",
            font=("Arial", 12, "bold"),
            bg="#6b7280",
            fg="white",
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor="hand2",
            command=results_window.destroy
        )
        close_btn.pack(pady=(10, 0))
    
    
    
    def show_endless_results(self, result):
        """Show endless mode results with detailed breakdown"""
        self.is_running = False
        self.start_btn.config(text="Start Automation", state=tk.NORMAL, bg=self.button_bg)
        self.endless_btn.config(text="Endless Mode", state=tk.NORMAL, bg="#10b981")
        self.status_display.config(text="Endless Mode Completed", fg="#10b981")
        
        self.log_message("\nEndless mode completed!")
        self.log_message(f"Total problems solved: {result['solved']}")
        self.log_message(f"Total problems failed: {result['failed']}")
        self.log_message(f"Total problems skipped: {result['skipped']}")
        self.log_message(f"Total time: {result.get('duration', 'Unknown')}")
        
        # Show detailed breakdown if available
        if 'problem_details' in result:
            self.log_message("\n📊 DETAILED BREAKDOWN BY QUESTION TYPE:")
            for question_type, counts in result['problem_details'].items():
                if sum(counts.values()) > 0:
                    type_name = question_type.replace('_', ' ').title()
                    self.log_message(f"  {type_name}:")
                    self.log_message(f"    ✓ Solved: {counts['solved']}")
                    self.log_message(f"    ⊘ Skipped: {counts['skipped']}")
                    self.log_message(f"    ✗ Failed: {counts['failed']}")
        
        # Show credits information if available
        if 'credits' in result:
            credit_info = result['credits']
            self.log_message(f"\n💰 CREDITS CALCULATION:")
            self.log_message(f"  Total credits to deduct: {credit_info['total_credits']}")
            for question_type, breakdown in credit_info['breakdown'].items():
                if breakdown['total_credits'] > 0:
                    type_name = question_type.replace('_', ' ').title()
                    self.log_message(f"  {type_name}: {breakdown['total_credits']} credits")
        
        # Update credits
        self.refresh_credits()
        
        # Create detailed message for dialog
        message = f"Endless mode finished!\n\n"
        message += f"Solved: {result['solved']}\n"
        message += f"Failed: {result['failed']}\n"
        message += f"Skipped: {result['skipped']}\n"
        message += f"Duration: {result.get('duration', 'Unknown')}"
        if 'credits' in result:
            message += f"\n\nCredits to deduct: {result['credits']['total_credits']}"
        
        # Show detailed results dialog
        self.show_detailed_results_dialog(result)
    
    def automation_error(self, error):
        """Handle automation error"""
        self.is_running = False
        self.start_btn.config(text="Start Automation", state=tk.NORMAL, bg=self.button_bg)
        self.endless_btn.config(text="Endless Mode", state=tk.NORMAL, bg="#10b981")
        self.status_display.config(text="Error", fg="red")
        self.log_message(f"Error: {error}")
        messagebox.showerror("Automation Error", f"An error occurred:\n{error}")
    
    
    def refresh_credits(self):
        """Refresh credits display"""
        user_data = self.api_client.get_profile()
        if user_data:
            credits = user_data.get('credits', 0)
            self.credits_label.config(text=f"Credits: {credits}")
            self.config.save_user_data(user_data)
    
    def handle_logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.config.clear_token()
            self.show_login_screen()

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = CodeTantraApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

