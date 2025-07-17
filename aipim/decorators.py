from __future__ import annotations
from logging import Logger
from pathlib import Path
from datetime import datetime
from functools import wraps
import json
import numbers
import inspect

from .aux_functions import check_path, format_size, get_dir_size, get_logger, format_execution_time, save_numeric_metadata


def manage_logging(study_dir: Path, log: Logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            initial_time = datetime.timestamp(datetime.now())        
            
            log.info(f"[aipim] Running '{func.__name__}'...")
            
            result = func(*args, **kwargs)
        
            final_time = datetime.timestamp(datetime.now())
            execution_time = format_execution_time(final_time - initial_time)
            
            dir_dize = format_size(get_dir_size(study_dir))
            
            log.info(f"[aipim] '{func.__name__}' completed in {execution_time}.")
            log.info(f"[aipim] Total size of generated files: {dir_dize}.")
            
            return result
        return wrapper
    return decorator


def study(base_dir: Path = Path()):
    check_path(base_dir)
    
    def decorator(func):
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            sig = inspect.signature(func)
            bound_args = sig.bind_partial(*args, **kwargs)

            study_dir = base_dir / func.__name__
            run_dir = study_dir / timestamp
                        
            selected_data_dir = study_dir / 'selected_data'
            selected_data_dir.mkdir(parents=True, exist_ok=True)
            
            selected_results_dir = study_dir / 'selected_results'
            selected_results_dir.mkdir(parents=True, exist_ok=True)
            
            if 'data_dir' not in bound_args.arguments:
                data_dir = run_dir / 'data'
                data_dir.mkdir(parents=True, exist_ok=True)
                bound_args.arguments['data_dir'] = data_dir
                
            if 'results_dir' not in bound_args.arguments:
                
                results_dir =  run_dir / 'results'
                results_dir.mkdir(parents=True, exist_ok=True)
                bound_args.arguments['results_dir'] = results_dir

            log = get_logger(name=func.__name__, file=study_dir / "aipim.log")
            
            bound_args.arguments['log'] = log
           
            func_with_logging = manage_logging(study_dir, log)(func)
            
            func_locals = func_with_logging(*bound_args.args, **bound_args.kwargs)
            
            save_numeric_metadata(func_locals, run_dir / "metadata.json")
            
            return func_locals
        return wrapper
    return decorator


if __name__ == "__main__":
    path = Path(r'C:\Users\giovanni.ribeiro\_home\01_projects\aipim\tests')
    
    @study(path)
    def test01(data_dir, results_dir):
        a = 2
        print(a)
        return locals()
        
    test01()
    