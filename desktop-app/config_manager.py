"""
Configuration Manager for CodeTantra Automation Desktop App
Manages user settings, tokens, and credentials using AppData folder
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

class ConfigManager:
    def __init__(self):
        """Initialize config manager and create AppData folders"""
        # Get AppData folder path
        if os.name == 'nt':  # Windows
            appdata = os.getenv('APPDATA')
            self.base_dir = Path(appdata) / 'CodeTantraAutomation'
        else:  # Mac/Linux
            home = Path.home()
            self.base_dir = home / '.codetantra_automation'
        
        # Create directories
        self.config_dir = self.base_dir / 'config'
        self.logs_dir = self.base_dir / 'logs'
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.token_file = self.config_dir / 'token.txt'
        self.user_file = self.config_dir / 'user.json'
        self.automation_config_file = self.config_dir / 'automation.json'
        self.settings_file = self.config_dir / 'settings.json'
    
    def save_token(self, token: str):
        """Save authentication token"""
        try:
            with open(self.token_file, 'w') as f:
                f.write(token)
        except Exception as e:
            print(f"Error saving token: {e}")
    
    def get_token(self) -> Optional[str]:
        """Get saved authentication token"""
        try:
            if self.token_file.exists():
                with open(self.token_file, 'r') as f:
                    token = f.read().strip()
                    return token if token else None
            return None
        except Exception as e:
            print(f"Error reading token: {e}")
            return None
    
    def clear_token(self):
        """Clear saved token"""
        try:
            if self.token_file.exists():
                self.token_file.unlink()
        except Exception as e:
            print(f"Error clearing token: {e}")
    
    def save_user_data(self, user_data: Dict[str, Any]):
        """Save user data"""
        try:
            with open(self.user_file, 'w') as f:
                json.dump(user_data, f, indent=2)
        except Exception as e:
            print(f"Error saving user data: {e}")
    
    def get_user_data(self) -> Dict[str, Any]:
        """Get saved user data"""
        try:
            if self.user_file.exists():
                with open(self.user_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error reading user data: {e}")
            return {}
    
    def clear_user_data(self):
        """Clear saved user data"""
        try:
            if self.user_file.exists():
                self.user_file.unlink()
        except Exception as e:
            print(f"Error clearing user data: {e}")
    
    def save_automation_config(self, config: Dict[str, Any]):
        """Save automation configuration (URLs, credentials, etc.)"""
        try:
            with open(self.automation_config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving automation config: {e}")
    
    def get_automation_config(self) -> Dict[str, Any]:
        """Get saved automation configuration"""
        try:
            if self.automation_config_file.exists():
                with open(self.automation_config_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error reading automation config: {e}")
            return {}
    
    def save_settings(self, settings: Dict[str, Any]):
        """Save application settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get application settings"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            return self.get_default_settings()
        except Exception as e:
            print(f"Error reading settings: {e}")
            return self.get_default_settings()
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default settings"""
        return {
            'api_url': 'http://localhost:8000',
            'check_updates': True,
            'auto_save_logs': True,
            'theme': 'dark'
        }
    
    def get_logs_dir(self) -> Path:
        """Get logs directory path"""
        return self.logs_dir
    
    def get_config_dir(self) -> Path:
        """Get config directory path"""
        return self.config_dir
    
    def save_log_file(self, content: str, filename: Optional[str] = None) -> Path:
        """
        Save log file
        Args:
            content: Log content
            filename: Optional filename (default: timestamp-based)
        Returns: Path to saved log file
        """
        from datetime import datetime
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'automation_log_{timestamp}.txt'
        
        log_file = self.logs_dir / filename
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return log_file
        except Exception as e:
            print(f"Error saving log file: {e}")
            return None
    
    def get_recent_logs(self, limit: int = 10) -> list:
        """
        Get list of recent log files
        Args:
            limit: Maximum number of files to return
        Returns: List of log file paths (most recent first)
        """
        try:
            log_files = list(self.logs_dir.glob('*.txt'))
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return log_files[:limit]
        except Exception as e:
            print(f"Error getting recent logs: {e}")
            return []
    
    def clear_old_logs(self, days: int = 30):
        """
        Clear log files older than specified days
        Args:
            days: Number of days to keep logs
        """
        from datetime import datetime, timedelta
        
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            for log_file in self.logs_dir.glob('*.txt'):
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_time:
                    log_file.unlink()
                    print(f"Deleted old log: {log_file.name}")
        except Exception as e:
            print(f"Error clearing old logs: {e}")
    
    def export_config(self, export_path: str):
        """Export all configuration to a file"""
        try:
            config_data = {
                'user': self.get_user_data(),
                'automation': self.get_automation_config(),
                'settings': self.get_settings()
            }
            
            with open(export_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            print(f"Configuration exported to: {export_path}")
        except Exception as e:
            print(f"Error exporting config: {e}")
    
    def import_config(self, import_path: str):
        """Import configuration from a file"""
        try:
            with open(import_path, 'r') as f:
                config_data = json.load(f)
            
            if 'user' in config_data:
                self.save_user_data(config_data['user'])
            if 'automation' in config_data:
                self.save_automation_config(config_data['automation'])
            if 'settings' in config_data:
                self.save_settings(config_data['settings'])
            
            print(f"Configuration imported from: {import_path}")
        except Exception as e:
            print(f"Error importing config: {e}")
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about storage usage"""
        try:
            def get_dir_size(path: Path) -> int:
                total = 0
                for item in path.rglob('*'):
                    if item.is_file():
                        total += item.stat().st_size
                return total
            
            total_size = get_dir_size(self.base_dir)
            logs_size = get_dir_size(self.logs_dir)
            config_size = get_dir_size(self.config_dir)
            
            log_count = len(list(self.logs_dir.glob('*.txt')))
            
            return {
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'logs_size_mb': round(logs_size / (1024 * 1024), 2),
                'config_size_mb': round(config_size / (1024 * 1024), 2),
                'log_count': log_count,
                'base_dir': str(self.base_dir)
            }
        except Exception as e:
            print(f"Error getting storage info: {e}")
            return {}
    
    def reset_all(self):
        """Reset all configuration (delete all files)"""
        try:
            import shutil
            if self.base_dir.exists():
                shutil.rmtree(self.base_dir)
                print("All configuration reset")
                # Recreate directories
                self.__init__()
        except Exception as e:
            print(f"Error resetting configuration: {e}")

