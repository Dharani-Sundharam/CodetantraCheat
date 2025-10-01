"""
Automation Runner - Integration with CodeTantra Playwright Automation
Manages the automation process and API communication
"""

import sys
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, Callable
from datetime import datetime

# Add parent directory to path to import codetantra_playwright
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

class AutomationRunner:
    def __init__(self, config: Dict[str, Any], api_client, log_callback: Callable[[str], None]):
        """
        Initialize automation runner
        Args:
            config: Configuration dictionary with URLs and credentials
            api_client: API client instance
            log_callback: Callback function for logging messages
        """
        self.config = config
        self.api_client = api_client
        self.log = log_callback
        
        self.problems_solved = 0
        self.problems_failed = 0
        self.problems_skipped = 0
        
        self.start_time = None
        self.end_time = None
    
    def run(self) -> Dict[str, Any]:
        """
        Run the automation process
        Returns: Dictionary with results
        """
        try:
            self.log("Initializing automation...")
            self.start_time = datetime.now()
            
            # Check API connection
            if not self.api_client.ping():
                self.log("Error: Cannot connect to API server")
                return self.get_error_result("API connection failed")
            
            # Check credits
            credits = self.api_client.get_credits()
            if credits is None:
                self.log("Error: Cannot retrieve credits")
                return self.get_error_result("Credits check failed")
            
            self.log(f"Current credits: {credits}")
            
            if credits < 1:
                self.log("Error: Insufficient credits")
                return self.get_error_result("Insufficient credits")
            
            # Create credentials.py file
            self.create_credentials_file()
            
            # Import and run automation
            self.log("Starting CodeTantra automation...")
            
            try:
                from codetantra_playwright import CodeTantraPlaywrightAutomation
                
                # Run automation with asyncio
                automation = CodeTantraPlaywrightAutomation(auto_login=True)
                
                # Monkey patch the automation to intercept results
                original_process = automation.process_single_problem
                
                async def patched_process():
                    """Patched process that reports to API"""
                    try:
                        result = await original_process()
                        
                        # Get current problem number
                        current_problem = await automation.get_current_problem_number(automation.page_target)
                        
                        # Determine problem type and success
                        question_type = await automation.detect_question_type(automation.page_answers)
                        problem_type = 'code_completion' if question_type == 'code_completion' else 'other'
                        
                        if result == True:
                            # Success
                            self.problems_solved += 1
                            self.log(f"Problem {current_problem} solved successfully")
                            self.deduct_credits(problem_type, True, current_problem)
                        elif result == "skipped":
                            # Skipped
                            self.problems_skipped += 1
                            self.log(f"Problem {current_problem} skipped")
                            self.deduct_credits(problem_type, False, current_problem)
                        else:
                            # Failed
                            self.problems_failed += 1
                            self.log(f"Problem {current_problem} failed")
                            self.deduct_credits(problem_type, False, current_problem)
                        
                        return result
                    except Exception as e:
                        self.log(f"Error processing problem: {e}")
                        self.problems_failed += 1
                        return False
                
                automation.process_single_problem = patched_process
                
                # Run automation
                num_problems = int(self.config.get('num_problems', 10))
                asyncio.run(automation.run_automation(num_problems))
                
            except ImportError as e:
                self.log(f"Error importing automation module: {e}")
                return self.get_error_result("Automation import failed")
            except Exception as e:
                self.log(f"Automation error: {e}")
                return self.get_error_result(str(e))
            
            self.end_time = datetime.now()
            return self.get_final_result()
            
        except Exception as e:
            self.log(f"Fatal error: {e}")
            return self.get_error_result(str(e))
    
    def create_credentials_file(self):
        """Create credentials.py file from config"""
        try:
            credentials_content = f'''"""
Auto-generated credentials file
Do not edit manually
"""

LOGIN_URL = "{self.config['url']}"

ANSWERS_ACCOUNT = {{
    "username": "{self.config['answers_email']}",
    "password": "{self.config['answers_password']}"
}}

TARGET_ACCOUNT = {{
    "username": "{self.config['target_email']}",
    "password": "{self.config['target_password']}"
}}
'''
            
            credentials_path = Path(__file__).parent.parent / 'credentials.py'
            with open(credentials_path, 'w') as f:
                f.write(credentials_content)
            
            self.log("Credentials configured")
        except Exception as e:
            self.log(f"Error creating credentials file: {e}")
            raise
    
    def deduct_credits(self, problem_type: str, success: bool, problem_number: int):
        """Deduct credits via API"""
        try:
            result = self.api_client.deduct_credits(problem_type, success, problem_number)
            
            if result['success']:
                credits_used = result['credits_deducted']
                remaining = result['remaining_credits']
                self.log(f"Credits used: {credits_used}, Remaining: {remaining}")
            else:
                self.log(f"Warning: {result['error']}")
        except Exception as e:
            self.log(f"Error deducting credits: {e}")
    
    def get_final_result(self) -> Dict[str, Any]:
        """Get final automation result"""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        
        return {
            'success': True,
            'solved': self.problems_solved,
            'failed': self.problems_failed,
            'skipped': self.problems_skipped,
            'duration': duration,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }
    
    def get_error_result(self, error: str) -> Dict[str, Any]:
        """Get error result"""
        return {
            'success': False,
            'solved': self.problems_solved,
            'failed': self.problems_failed,
            'skipped': self.problems_skipped,
            'error': error
        }
    
    def generate_report(self) -> str:
        """Generate text report of automation run"""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        report = f"""
CodeTantra Automation Report
============================

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Duration: {minutes}m {seconds}s

Results:
--------
Problems Solved: {self.problems_solved}
Problems Failed: {self.problems_failed}
Problems Skipped: {self.problems_skipped}
Total Problems: {self.problems_solved + self.problems_failed + self.problems_skipped}

Configuration:
--------------
URL: {self.config['url']}
Number of Problems: {self.config.get('num_problems', 'N/A')}

Credits Usage:
--------------
Solved (5 credits each): {self.problems_solved * 5}
Other (3 credits each): 0
Failed (1 credit each): {self.problems_failed + self.problems_skipped}
Total Credits Used: {(self.problems_solved * 5) + (self.problems_failed + self.problems_skipped)}
"""
        return report

