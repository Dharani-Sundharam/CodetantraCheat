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
                
                # Create automation instance
                automation = CodeTantraPlaywrightAutomation(auto_login=False)
                
                # Run automation with asyncio
                async def run_automation():
                    from playwright.async_api import async_playwright
                    
                    async with async_playwright() as playwright:
                        automation.playwright = playwright
                        
                        # Setup browsers
                        await automation.setup_browsers()
                        
                        # Navigate to CodeTantra
                        await automation.navigate_to_codetantra(self.config['url'])
                        
                        # Login to both accounts
                        await automation.login_to_account(
                            automation.page_answers,
                            self.config['answers_email'],
                            self.config['answers_password'],
                            "Answers Account"
                        )
                        
                        await automation.login_to_account(
                            automation.page_target,
                            self.config['target_email'],
                            self.config['target_password'],
                            "Target Account"
                        )
                        
                        # Run automation with credit tracking
                        num_problems = int(self.config.get('num_problems', 10))
                        await self.run_automation_with_credits(automation, num_problems)
                        
                        # Update counters from automation
                        self.problems_solved = automation.problems_solved
                        self.problems_failed = automation.problems_failed
                        self.problems_skipped = automation.problems_skipped
                
                # Execute the automation
                asyncio.run(run_automation())
                
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
    
    def check_api_connectivity(self):
        """Check if API is running and show warning if not"""
        try:
            if not self.api_client.ping():
                self.log("⚠️ WARNING: API server is not running!")
                self.log("Please open the website in your browser and try again later.")
                self.log("Website URL: https://ctautomationpro.onrender.com")
                return False
            return True
        except Exception as e:
            self.log(f"⚠️ WARNING: Cannot connect to API server: {e}")
            self.log("Please open the website in your browser and try again later.")
            self.log("Website URL: https://ctautomationpro.onrender.com")
            return False
    
    def deduct_credits(self, problem_type: str, success: bool, problem_number: int):
        """Deduct credits via API with proper error handling"""
        try:
            # Check API connectivity first
            if not self.check_api_connectivity():
                self.log("Skipping credit deduction - API not available")
                return False
            
            result = self.api_client.deduct_credits(problem_type, success, problem_number)
            
            if result['success']:
                credits_used = result['credits_deducted']
                remaining = result['remaining_credits']
                self.log(f"Credits used: {credits_used}, Remaining: {remaining}")
                return True
            else:
                self.log(f"Warning: {result['error']}")
                return False
        except Exception as e:
            self.log(f"Error deducting credits: {e}")
            return False
    
    async def run_automation_with_credits(self, automation, num_problems, endless_mode=False):
        """Run automation with credit tracking for each problem"""
        try:
            # Reset counters
            automation.problems_solved = 0
            automation.problems_failed = 0
            automation.problems_skipped = 0
            
            # Check initial API connectivity
            if not self.check_api_connectivity():
                self.log("Starting automation without credit tracking...")
            
            # Run the main automation loop
            while True:
                if not endless_mode and num_problems and automation.problems_solved >= num_problems:
                    self.log(f"Completed {num_problems} problems as requested")
                    break
                    
                if endless_mode:
                    self.log(f"Endless mode - Problem {automation.problems_solved + 1}...")
                
                # Process current problem
                result = await automation.process_single_problem()
                
                # Determine problem type and credit amount
                question_type = await automation.detect_question_type(automation.page_answers)
                problem_type = 'code_completion' if question_type == 'code_completion' else 'other'
                current_problem = await automation.get_current_problem_number(automation.page_target)
                
                if result == True:
                    # Success - deduct credits based on problem type
                    automation.problems_solved += 1
                    credits_to_deduct = 5 if problem_type == 'code_completion' else 3
                    self.log(f"Problem {current_problem} solved successfully! (+{credits_to_deduct} credits)")
                    
                    # Deduct credits via API
                    self.deduct_credits(problem_type, True, current_problem)
                    
                elif result == "skipped":
                    # Skipped - deduct 1 credit
                    automation.problems_skipped += 1
                    self.log(f"Problem {current_problem} skipped (+1 credit)")
                    self.deduct_credits(problem_type, False, current_problem)
                    
                else:
                    # Failed - deduct 1 credit
                    automation.problems_failed += 1
                    self.log(f"Problem {current_problem} failed (+1 credit)")
                    self.deduct_credits(problem_type, False, current_problem)
                
                # Move to next problem
                if not await automation.move_to_next_problem():
                    self.log("Reached end of problems")
                    break
                    
                # Small pause between problems
                await asyncio.sleep(2)
                
        except Exception as e:
            self.log(f"Error in automation with credits: {e}")
            raise
    
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
    
    def run_endless(self) -> Dict[str, Any]:
        """
        Run endless automation - solve all available problems
        Returns: Dictionary with results
        """
        try:
            self.log("Initializing endless mode...")
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
            
            # Import and run the automation
            try:
                from codetantra_playwright import CodeTantraPlaywrightAutomation
                
                # Create automation instance
                automation = CodeTantraPlaywrightAutomation(auto_login=False)
                
                # Run endless automation with asyncio
                async def run_endless_automation():
                    from playwright.async_api import async_playwright
                    
                    async with async_playwright() as playwright:
                        automation.playwright = playwright
                        
                        # Setup browsers
                        await automation.setup_browsers()
                        
                        # Navigate to CodeTantra
                        await automation.navigate_to_codetantra(self.config['url'])
                        
                        # Login to both accounts
                        await automation.login_to_account(
                            automation.page_answers,
                            self.config['answers_email'],
                            self.config['answers_password'],
                            "Answers Account"
                        )
                        
                        await automation.login_to_account(
                            automation.page_target,
                            self.config['target_email'],
                            self.config['target_password'],
                            "Target Account"
                        )
                        
                        # Run endless mode with credit tracking
                        await self.run_automation_with_credits(automation, 999999, endless_mode=True)
                        
                        # Update counters from automation
                        self.problems_solved = automation.problems_solved
                        self.problems_failed = automation.problems_failed
                        self.problems_skipped = automation.problems_skipped
                
                # Execute the endless automation
                asyncio.run(run_endless_automation())
                
                self.end_time = datetime.now()
                duration = str(self.end_time - self.start_time).split('.')[0]
                
                self.log(f"Endless mode completed!")
                self.log(f"Total problems solved: {self.problems_solved}")
                self.log(f"Total problems failed: {self.problems_failed}")
                self.log(f"Total problems skipped: {self.problems_skipped}")
                self.log(f"Total duration: {duration}")
                
                return {
                    'success': True,
                    'solved': self.problems_solved,
                    'failed': self.problems_failed,
                    'skipped': self.problems_skipped,
                    'duration': duration,
                    'start_time': self.start_time.isoformat() if self.start_time else None,
                    'end_time': self.end_time.isoformat() if self.end_time else None
                }
                
            except ImportError as e:
                self.log(f"Error importing automation module: {e}")
                return self.get_error_result(f"Import error: {e}")
            except Exception as e:
                self.log(f"Error during automation: {e}")
                return self.get_error_result(f"Automation error: {e}")
                
        except Exception as e:
            self.log(f"Unexpected error: {e}")
            return self.get_error_result(f"Unexpected error: {e}")
    
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

