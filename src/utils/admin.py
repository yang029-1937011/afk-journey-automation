"""Administrator privilege utilities."""

import ctypes
import sys
import os


def is_admin() -> bool:
    """Check if the current process has administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def request_admin() -> None:
    """Request administrator privileges if not already elevated."""
    if not is_admin():
        try:
            # Re-run the program with admin rights
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([script] + sys.argv[1:])
            
            # ShellExecute with 'runas' verb to request elevation
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable, 
                params, 
                None, 
                1  # SW_SHOWNORMAL
            )
            sys.exit(0)
        except Exception as e:
            print(f"Failed to elevate privileges: {e}")
            # Continue running without admin
    else:
        print("Running with administrator privileges")
