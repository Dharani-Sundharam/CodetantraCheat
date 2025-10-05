
import os
import sys

def _s():
    print("=" * 60)
    print("ENCRYPTED MODULE - SECURITY PROTECTED")
    print("=" * 60)

def _c():
    if not os.path.exists('encrypted_manifest.json'):
        _s()
        return False
    return True

_s()

class CodeTantraPlaywrightAutomation:
    def __init__(self, *args, **kwargs):
        _s()
        raise Exception("This module is encrypted.")
    
    async def run_automation(self, *args, **kwargs):
        raise Exception("This module is encrypted.")

if __name__ == "__main__":
    _s()
    sys.exit(1)
