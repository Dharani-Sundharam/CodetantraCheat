"""
API Client for CodeTantra Automation Desktop App
Handles all communication with backend API
"""

import requests
from typing import Optional, Dict, Any

class APIClient:
    def __init__(self, base_url: str = "https://ctautomationpro.onrender.com"):
        """Initialize API client"""
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
        # Configure session for better HTTPS handling
        self.session.verify = True  # Enable SSL verification
        self.session.timeout = 30   # Set timeout to 30 seconds
    
    def set_token(self, token: str):
        """Set authentication token"""
        self.token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })
    
    def login(self, email: str, password: str, remember_me: bool = False) -> Dict[str, Any]:
        """
        Login to the service
        Returns: {'success': bool, 'token': str, 'user': dict, 'error': str}
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={
                    'email': email,
                    'password': password,
                    'remember_me': remember_me
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.set_token(data['access_token'])
                return {
                    'success': True,
                    'token': data['access_token'],
                    'user': data['user'],
                    'error': None
                }
            else:
                error_data = response.json()
                return {
                    'success': False,
                    'token': None,
                    'user': None,
                    'error': error_data.get('detail', 'Login failed')
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'token': None,
                'user': None,
                'error': f'Network error: {str(e)}'
            }
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate token and get user data
        Returns: user_data dict or None if invalid
        """
        try:
            self.set_token(token)
            response = self.session.get(f"{self.base_url}/api/user/profile")
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def get_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get current user profile
        Returns: user profile dict or None
        """
        try:
            response = self.session.get(f"{self.base_url}/api/user/profile")
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def get_credits(self) -> Optional[int]:
        """
        Get current credits balance
        Returns: credits as int or None
        """
        try:
            response = self.session.get(f"{self.base_url}/api/user/credits")
            
            if response.status_code == 200:
                data = response.json()
                return data.get('credits', 0)
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def deduct_credits(self, problem_type: str, success: bool, problem_number: Optional[int] = None) -> Dict[str, Any]:
        """
        Deduct credits for problem completion
        Args:
            problem_type: 'code_completion' or 'other'
            success: True if problem solved successfully
            problem_number: Problem number (optional)
        Returns: {'success': bool, 'credits_deducted': int, 'remaining_credits': int, 'error': str}
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/credits/deduct",
                json={
                    'problem_type': problem_type,
                    'success': success,
                    'problem_number': problem_number
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'credits_deducted': data.get('credits_deducted', 0),
                    'remaining_credits': data.get('remaining_credits', 0),
                    'error': None
                }
            elif response.status_code == 402:
                return {
                    'success': False,
                    'credits_deducted': 0,
                    'remaining_credits': 0,
                    'error': 'Insufficient credits'
                }
            else:
                error_data = response.json()
                return {
                    'success': False,
                    'credits_deducted': 0,
                    'remaining_credits': 0,
                    'error': error_data.get('detail', 'Failed to deduct credits')
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'credits_deducted': 0,
                'remaining_credits': 0,
                'error': f'Network error: {str(e)}'
            }
    
    def get_usage_history(self, limit: int = 100) -> Optional[list]:
        """
        Get usage history
        Returns: list of usage log entries or None
        """
        try:
            response = self.session.get(f"{self.base_url}/api/user/usage-history")
            
            if response.status_code == 200:
                data = response.json()
                return data.get('logs', [])
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def get_transactions(self) -> Optional[list]:
        """
        Get transaction history
        Returns: list of transactions or None
        """
        try:
            response = self.session.get(f"{self.base_url}/api/user/transactions")
            
            if response.status_code == 200:
                data = response.json()
                return data.get('transactions', [])
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def check_sufficient_credits(self, problem_type: str, success: bool) -> bool:
        """
        Check if user has sufficient credits for operation
        Args:
            problem_type: 'code_completion' or 'other'
            success: True if problem solved successfully
        Returns: True if sufficient credits, False otherwise
        """
        credits = self.get_credits()
        if credits is None:
            return False
        
        # Calculate required credits
        if success:
            required = 5 if problem_type == 'code_completion' else 3
        else:
            required = 1
        
        return credits >= required
    
    def get_license_status(self) -> Optional[Dict[str, Any]]:
        """
        Get license status for the current user
        Returns: license status dict or None if not available
        """
        try:
            response = self.session.get(f"{self.base_url}/api/user/license")
            
            if response.status_code == 200:
                return response.json()
            else:
                # If license endpoint doesn't exist, assume valid
                return {'valid': True, 'message': 'License check not implemented'}
        except requests.exceptions.RequestException:
            # If license check fails, assume valid for backward compatibility
            return {'valid': True, 'message': 'License check unavailable'}
    
    def get_encryption_key(self) -> Optional[str]:
        """
        Get encryption key from server for decrypting modules
        Returns: encryption key string or None if not available
        """
        try:
            response = self.session.get(f"{self.base_url}/api/encryption/key")
            
            if response.status_code == 200:
                data = response.json()
                return data.get('key')
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def ping(self) -> bool:
        """
        Check if API is reachable
        Returns: True if API is up, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

