import importlib.util
from pathlib import Path
from app.layout import layout
from terminal import Scheduler

def run_automatic_bootstrapper():
    bootstrapper_path = Path(__file__).parent / "bootstrapper.py"
    if bootstrapper_path.exists():
        spec = importlib.util.spec_from_file_location("app.bootstrapper", bootstrapper_path)
        if spec and spec.loader:
            bootstrapper_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(bootstrapper_module)
            if hasattr(bootstrapper_module, "init"):
                bootstrapper_module.init()

def start_application():
    run_automatic_bootstrapper()

    content = layout()
    Scheduler.populate(content)
    Scheduler.run()

__all__ = ["start_application"]