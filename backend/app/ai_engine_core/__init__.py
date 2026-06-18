"""AI Engine Core - Lazy imports to avoid crash on missing dependencies"""

def run_full_intelligence(*args, **kwargs):
    """Lazy import to avoid crash on missing optional deps"""
    from .orchestrator import run_full_intelligence as _run
    return _run(*args, **kwargs)


__all__ = ['run_full_intelligence']
