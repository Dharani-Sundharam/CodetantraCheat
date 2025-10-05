import os
import sys
import asyncio
from secure_loader import load_encrypted_module, cleanup_loader

def _v():
    rf = ['encrypted_manifest.json']
    for f in rf:
        if not os.path.exists(os.path.join(os.path.dirname(__file__), f)):
            return False
    return True

def _g():
    try:
        import config_manager
        config = config_manager.ConfigManager()
        token = config.get_token()
        if token:
            return token
    except Exception:
        pass
    token = input("Token: ").strip()
    return token if token else None

async def _r():
    try:
        if not _v():
            return False
        token = _g()
        if not token:
            return False
        m = load_encrypted_module('codetantra_playwright', token)
        c = m.CodeTantraPlaywrightAutomation
        a = c(auto_login=False)
        await a.run_automation()
        return True
    except Exception:
        return False
    finally:
        cleanup_loader()

def main():
    try:
        success = asyncio.run(_r())
    except Exception:
        pass
    finally:
        cleanup_loader()

if __name__ == "__main__":
    main()
