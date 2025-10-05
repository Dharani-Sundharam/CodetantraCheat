import os
import sys
import base64
import secrets
import tempfile
import importlib.util
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import requests
import json

class _L:
    def __init__(self):
        self._a = "https://ctautomationpro.onrender.com"
        self._s = requests.Session()
        self._s.timeout = 30
        self._t = None
        self._m = {}
        self._d = None
    
    def _g(self, t: str) -> str:
        try:
            h = {
                'Authorization': f'Bearer {t}',
                'User-Agent': 'SecureLoader/1.0',
                'X-Request-ID': secrets.token_hex(16)
            }
            r = self._s.get(f"{self._a}/api/encryption/key", headers=h)
            if r.status_code == 200:
                d = r.json()
                if 'key' in d and len(d['key']) >= 32:
                    return d['key']
            return None
        except Exception:
            return None
    
    def _v(self, t: str) -> bool:
        try:
            h = {'Authorization': f'Bearer {t}'}
            r = self._s.get(f"{self._a}/api/user/profile", headers=h)
            return r.status_code == 200
        except Exception:
            return False
    
    def _l(self) -> bool:
        try:
            p = os.path.join(os.path.dirname(__file__), 'encrypted_manifest.json')
            if not os.path.exists(p):
                return False
            with open(p, 'r') as f:
                self._d = json.load(f)
            return True
        except Exception:
            return False
    
    def _d(self, n: str, k: str) -> str:
        if not self._d:
            return None
        mf = None
        for fp, d in self._d.items():
            if fp.endswith(f"{n}.py"):
                mf = fp
                break
        if not mf:
            return None
        try:
            ed = base64.b64decode(self._d[mf]['data'])
            s = base64.b64decode(self._d[mf]['salt'])
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=s,
                iterations=100000,
            )
            dk = base64.urlsafe_b64encode(kdf.derive(k.encode()))
            f = Fernet(dk)
            dd = f.decrypt(ed)
            return dd.decode('utf-8')
        except Exception:
            return None
    
    def _c(self, n: str, c: str):
        if not self._t:
            self._t = tempfile.mkdtemp(prefix='secure_loader_')
        mp = os.path.join(self._t, f"{n}.py")
        with open(mp, 'w', encoding='utf-8') as f:
            f.write(c)
        return mp
    
    def load_module(self, n: str, t: str):
        if not self._v(t):
            raise Exception("Invalid authentication token")
        k = self._g(t)
        if not k:
            raise Exception("Failed to get decryption key from server")
        if not self._l():
            raise Exception("Failed to load encrypted manifest")
        if n in self._m:
            return self._m[n]
        c = self._d(n, k)
        if not c:
            raise Exception(f"Failed to decrypt module: {n}")
        mp = self._c(n, c)
        spec = importlib.util.spec_from_file_location(n, mp)
        module = importlib.util.module_from_spec(spec)
        sys.modules[n] = module
        spec.loader.exec_module(module)
        self._m[n] = module
        return module
    
    def cleanup(self):
        if self._t and os.path.exists(self._t):
            import shutil
            try:
                shutil.rmtree(self._t)
            except Exception:
                pass

_l = _L()

def load_encrypted_module(n: str, t: str):
    return _l.load_module(n, t)

def cleanup_loader():
    _l.cleanup()

import atexit
atexit.register(cleanup_loader)
