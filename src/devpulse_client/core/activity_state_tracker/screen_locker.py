import platform
import ctypes
import subprocess

def lock_screen() -> None:
   
    system = platform.system()

    if system == "Windows":
        # Primary, zero-dependency approach
        if ctypes.windll.user32.LockWorkStation():
            return
        # Fallback: run the shell command
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True, shell=False)
        return

    if system == "Linux":  # Covers Ubuntu and most derivatives
        # Try common desktop-agnostic helpers in order of availability
        for cmd in (
            ["loginctl", "lock-session"],              # systemd-logind (modern approach)
            ["gnome-screensaver-command", "-l"],       # Legacy GNOME/Unity
            ["dm-tool", "lock"],                       # LightDM display manager
            ["xdg-screensaver", "lock"],               # XDG spec; usually present
        ):
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"Locked screen using {cmd[0]}")
                return
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        raise RuntimeError("No working screen lock method found")
