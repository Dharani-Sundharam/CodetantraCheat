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
        
        # Detailed problem tracking
        self.problem_details = {
            'code_completion': {'solved': 0, 'failed': 0, 'skipped': 0},
            'multiple_choice': {'solved': 0, 'failed': 0, 'skipped': 0},
            'fill_blank': {'solved': 0, 'failed': 0, 'skipped': 0},
            'other': {'solved': 0, 'failed': 0, 'skipped': 0}
        }
        
        self.start_time = None
        self.end_time = None
    
    def track_problem(self, problem_type: str, result: str):
        """Track a problem by type and result"""
        if problem_type not in self.problem_details:
            problem_type = 'other'
        
        if result == 'solved':
            self.problems_solved += 1
            self.problem_details[problem_type]['solved'] += 1
        elif result == 'failed':
            self.problems_failed += 1
            self.problem_details[problem_type]['failed'] += 1
        elif result == 'skipped':
            self.problems_skipped += 1
            self.problem_details[problem_type]['skipped'] += 1
    
    def calculate_credits(self) -> Dict[str, Any]:
        """Calculate credits based on problem types and results"""
        total_credits = 0
        credit_breakdown = {}
        
        for problem_type, counts in self.problem_details.items():
            # Credits: code_completion=5, others=3, unsolved=1
            if problem_type == 'code_completion':
                solved_credits = counts['solved'] * 5
                failed_credits = counts['failed'] * 1
                skipped_credits = counts['skipped'] * 1
            else:
                solved_credits = counts['solved'] * 3
                failed_credits = counts['failed'] * 1
                skipped_credits = counts['skipped'] * 1
            
            type_total = solved_credits + failed_credits + skipped_credits
            total_credits += type_total
            
            credit_breakdown[problem_type] = {
                'solved_credits': solved_credits,
                'failed_credits': failed_credits,
                'skipped_credits': skipped_credits,
                'total_credits': type_total,
                'counts': counts
            }
        
        return {
            'total_credits': total_credits,
            'breakdown': credit_breakdown
        }
    
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
            
            # Check minimum credit requirement
            num_problems = int(self.config.get('num_problems', 10))
            estimated_credits = num_problems * 5  # Assume all are code problems
            
            if credits < estimated_credits:
                self.log(f"WARNING: You have {credits} credits but may need ~{estimated_credits} credits")
                self.log("Automation will continue but may stop if credits run out")
            
            if credits < 1:
                self.log("Error: Insufficient credits (0 credits remaining)")
                return self.get_error_result("Insufficient credits. Please add more credits to continue.")
            
            # Create credentials.py file
            self.create_credentials_file()
            
            # Import and run automation
            self.log("Starting CodeTantra automation...")
            
            try:
                from codetantra_playwright import CodeTantraPlaywrightAutomation
                
                # Create automation instance
                automation = CodeTantraPlaywrightAutomation(auto_login=False)
                
                # Set automation runner reference for credit deduction
                automation.automation_runner = self
                
                # Run automation with asyncio
                async def run_automation():
                    from playwright.async_api import async_playwright
                    
                    async with async_playwright() as playwright:
                        automation.playwright = playwright
                        
                        try:
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
                            
                            # Question matching is now handled inside the automation itself
                            
                            # Run automation normally
                            num_problems = int(self.config.get('num_problems', 10))
                            result = await automation.run_automation(num_problems=num_problems)
                            
                            # Check if automation returned an error
                            if isinstance(result, dict) and result.get('error') == 'accounts_not_synced':
                                return self.get_error_result("questions_not_synced")
                            
                            # Cleanup browsers only when automation completes successfully
                            await automation.cleanup()
                            
                            # Get detailed problem summary from automation
                            if hasattr(automation, 'get_problem_summary'):
                                problem_summary = automation.get_problem_summary()
                                # Update our tracking with the detailed results
                                for question_type, counts in problem_summary['by_type'].items():
                                    if question_type in self.problem_details:
                                        self.problem_details[question_type] = counts
                                
                                # Update total counters
                                self.problems_solved = problem_summary['total']['solved']
                                self.problems_failed = problem_summary['total']['failed']
                                self.problems_skipped = problem_summary['total']['skipped']
                            else:
                                # Fallback to basic tracking
                                self.problems_solved = getattr(automation, 'problems_solved', 0)
                                self.problems_failed = getattr(automation, 'problems_failed', 0)
                                self.problems_skipped = getattr(automation, 'problems_skipped', 0)
                            # Using detailed problem tracking instead of individual attributes
                            
                            # Calculate and deduct credits after completion
                            # Credits are now deducted per problem, not at the end
                            
                        finally:
                            # Only cleanup if automation actually completed or failed due to credits
                            # Don't cleanup if problems don't match - keep browsers open
                            pass
                
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
        """Check if API is running with multiple attempts and detailed diagnostics"""
        try:
            self.log("Checking API server health...")
            
            # Try multiple times with different endpoints
            endpoints_to_try = [
                ("ping", self.api_client.ping),
                ("health", lambda: self.api_client.get_credits() is not None),
                ("profile", lambda: self.api_client.get_profile() is not None)
            ]
            
            for endpoint_name, check_func in endpoints_to_try:
                try:
                    self.log(f"  Testing {endpoint_name} endpoint...")
                    if check_func():
                        self.log(f"  [OK] {endpoint_name} endpoint is healthy")
                        return True
                    else:
                        self.log(f"  [FAIL] {endpoint_name} endpoint failed")
                except Exception as e:
                    self.log(f"  [ERROR] {endpoint_name} endpoint error: {e}")
            
            # If all endpoints failed
            self.log("[WARNING] All API endpoints are unreachable!")
            self.log("This could be due to:")
            self.log("  - Server is starting up (Render takes 30-60 seconds)")
            self.log("  - Server is sleeping (inactive for 15+ minutes)")
            self.log("  - Network connectivity issues")
            self.log("  - Server maintenance")
            self.log("")
            self.log("Please try:")
            self.log("  1. Wait 1-2 minutes and try again")
            self.log("  2. Open https://ctautomationpro.onrender.com in your browser")
            self.log("  3. Check your internet connection")
            return False
            
        except Exception as e:
            self.log(f"[CRITICAL] API connectivity check failed: {e}")
            self.log("Please check your internet connection and try again.")
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
    
    def deduct_credits_for_problem(self, question_type: str, success: bool) -> bool:
        """Deduct credits for a single problem immediately after solving"""
        try:
            # Check API connectivity
            if not self.check_api_connectivity():
                return False
            
            # Get current credits
            current_credits = self.api_client.get_credits()
            if current_credits is None:
                return False
            
            # Calculate credit amount based on question type and success
            if success:
                # Solved problems: code=5, non-code=3
                if question_type == "code_completion":
                    credit_amount = 5
                else:
                    credit_amount = 3
            else:
                # Failed/skipped problems: 1 credit each
                credit_amount = 1
            
            # Check if we have enough credits
            if current_credits < credit_amount:
                self.log(f"Insufficient credits: need {credit_amount}, have {current_credits}")
                return False
            
            # Deduct credits
            result = self.api_client.deduct_credits(
                problem_type=question_type,
                success=success,
                problem_number=None
            )
            
            if result.get('success'):
                self.log(f"Credits deducted: {credit_amount} for {question_type} ({'solved' if success else 'failed/skipped'})")
                return True
            else:
                self.log(f"Credit deduction failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.log(f"Error deducting credits: {e}")
            return False
    
    def get_final_result(self) -> Dict[str, Any]:
        """Get final automation result with detailed tracking and credits"""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        
        # Calculate credits
        credit_info = self.calculate_credits()
        
        return {
            'success': True,
            'solved': self.problems_solved,
            'failed': self.problems_failed,
            'skipped': self.problems_skipped,
            'duration': duration,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'problem_details': self.problem_details,
            'credits': credit_info
        }
    
    def run_endless(self) -> Dict[str, Any]:
        """
        Run endless automation - solve all available problems
        Requires minimum 50 credits to start
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
            
            # Endless mode requires minimum 50 credits
            if credits < 50:
                self.log(f"Error: Endless mode requires at least 50 credits")
                self.log(f"You currently have {credits} credits")
                return self.get_error_result(f"Insufficient credits for endless mode. Required: 50, Available: {credits}")
            
            # Create credentials.py file
            self.create_credentials_file()
            
            # Import and run the automation
            try:
                from codetantra_playwright import CodeTantraPlaywrightAutomation
                
                # Create automation instance
                automation = CodeTantraPlaywrightAutomation(auto_login=False)
                
                # Set automation runner reference for credit deduction
                automation.automation_runner = self
                
                # Run endless automation with asyncio
                async def run_endless_automation():
                    from playwright.async_api import async_playwright
                    
                    async with async_playwright() as playwright:
                        automation.playwright = playwright
                        
                        try:
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
                            
                            # Question matching is now handled inside the automation itself
                            
                            # Run endless mode
                            result = await automation.run_automation(num_problems=999999, endless_mode=True)
                            
                            # Check if automation returned an error
                            if isinstance(result, dict) and result.get('error') == 'accounts_not_synced':
                                return self.get_error_result("questions_not_synced")
                            
                            # Cleanup browsers only when automation completes successfully
                            await automation.cleanup()
                            
                            # Get detailed problem summary from automation
                            if hasattr(automation, 'get_problem_summary'):
                                problem_summary = automation.get_problem_summary()
                                # Update our tracking with the detailed results
                                for question_type, counts in problem_summary['by_type'].items():
                                    if question_type in self.problem_details:
                                        self.problem_details[question_type] = counts
                                
                                # Update total counters
                                self.problems_solved = problem_summary['total']['solved']
                                self.problems_failed = problem_summary['total']['failed']
                                self.problems_skipped = problem_summary['total']['skipped']
                            else:
                                # Fallback to basic tracking
                                self.problems_solved = getattr(automation, 'problems_solved', 0)
                                self.problems_failed = getattr(automation, 'problems_failed', 0)
                                self.problems_skipped = getattr(automation, 'problems_skipped', 0)
                            # Using detailed problem tracking instead of individual attributes
                            
                            # Calculate and deduct credits after completion
                            # Credits are now deducted per problem, not at the end
                            
                        finally:
                            # Only cleanup if automation actually completed or failed due to credits
                            # Don't cleanup if problems don't match - keep browsers open
                            pass
                
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

