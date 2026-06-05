# remove_system_paths.py

def remove_system_paths():
    """
    Remove system Python and user-local paths from sys.path to ensure
    only environment packages (e.g., conda) are used.
    """
    import sys
    sys.path[:] = [p for p in sys.path 
                   if not p.startswith('/usr/lib/python3') 
                   and not p.startswith('/home/a33shen/.local')]