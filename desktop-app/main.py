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
        
        # Initialize config manager and API client
        self.config = config_manager.ConfigManager()
        self.api_client = api_client.APIClient()
        self.automation = None
        self.is_running = False
        
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
        
        self.password_entry = tk.Entry(
            main_frame,
            font=("Arial", 11),
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            width=35,
            show="*"
        )
        self.password_entry.pack(pady=(0, 10), ipady=8)
        
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
            command=self.start_automation
        )
        self.start_btn.pack(fill=tk.X, padx=15, pady=(0, 15), ipady=10)
    
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
        
        self.answers_password = tk.Entry(
            fields_frame,
            font=("Arial", 10),
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            show="*"
        )
        self.answers_password.pack(fill=tk.X, pady=(0, 15), ipady=6)
        self.answers_password.insert(0, config.get('answers_password', ''))
        
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
        
        self.target_password = tk.Entry(
            fields_frame,
            font=("Arial", 10),
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            show="*"
        )
        self.target_password.pack(fill=tk.X, pady=(0, 15), ipady=6)
        self.target_password.insert(0, config.get('target_password', ''))
        
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
        
        # Validate inputs
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
        self.status_display.config(text="Running", fg="#f59e0b")
        self.log_text.delete(1.0, tk.END)
        self.log_message("Starting automation...")
        
        # Start automation in thread
        thread = threading.Thread(target=self.run_automation_thread, args=(config,))
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
    
    def show_results(self, result):
        """Show automation results"""
        self.is_running = False
        self.start_btn.config(text="Start Automation", state=tk.NORMAL, bg=self.button_bg)
        self.status_display.config(text="Completed", fg="#10b981")
        
        self.log_message("\nAutomation completed!")
        self.log_message(f"Problems solved: {result['solved']}")
        self.log_message(f"Problems failed: {result['failed']}")
        self.log_message(f"Problems skipped: {result['skipped']}")
        
        # Update credits
        self.refresh_credits()
        
        messagebox.showinfo(
            "Automation Complete",
            f"Solved: {result['solved']}\nFailed: {result['failed']}\nSkipped: {result['skipped']}"
        )
    
    def automation_error(self, error):
        """Handle automation error"""
        self.is_running = False
        self.start_btn.config(text="Start Automation", state=tk.NORMAL, bg=self.button_bg)
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

