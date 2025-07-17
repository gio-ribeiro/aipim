from __future__ import annotations
import json
import numbers
from pathlib import Path
import logging

def check_path(path: Path):
    if not isinstance(path, Path):
        raise TypeError("Expected a Path object as base_dir.") 
    
    if not path.is_dir():
        raise FileNotFoundError(f"Path {path} does not exist.")
    
    return
    
def save_numeric_locals(locals_dict: dict, run_dir: Path) -> None:
    """
    Saves all numeric variables from a locals() dictionary to a JSON file.

    Args:
        locals_dict (dict): Dictionary returned by the `locals()` function.
        path (Path): Path to the output JSON file.
    """
    numeric_vars = {
        k: v for k, v in locals_dict.items()
        if isinstance(v, numbers.Number)
    }

    
    run_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = run_dir / 'metadata.json'
    metadata_path.write_text(json.dumps(numeric_vars, indent=2, ensure_ascii=False))

def get_logger(name: str = "aipim", file: str | Path ="aipim.log"):
    if isinstance(file, Path):
        file = str(file.resolve())
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = logging.FileHandler(file)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger

def get_dir_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())

def format_size(bytesize: int) -> str:
    size_with_unit = float(bytesize)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_with_unit < 1024:
            return f"{size_with_unit:.2f} {unit}"
        size_with_unit /= 1024
    return f"{size_with_unit:.2f} TB"

def format_execution_time(seconds: float) -> str:
    if seconds < 1e-3:
        return f"{seconds * 1e6:.2f} µs"
    elif seconds < 1:
        return f"{seconds * 1e3:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        sec = seconds % 60
        return f"{mins} min {sec:.1f} s"
    else:
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        sec = seconds % 60
        return f"{hrs} h {mins} min {sec:.0f} s"