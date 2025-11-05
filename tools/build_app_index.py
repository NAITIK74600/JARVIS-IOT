# H:/jarvis/build_app_index.py

import os
import json
import winshell

def get_app_paths():
    """Scans Windows Start Menu folders to find application shortcuts and their targets."""
    app_dict = {}
    # List of Start Menu folders to scan
    start_menu_folders = [
        os.path.join(os.environ["ALLUSERSPROFILE"], "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
    ]

    for start_menu_path in start_menu_folders:
        if not os.path.isdir(start_menu_path):
            continue
        for root, _, files in os.walk(start_menu_path):
            for file in files:
                if file.lower().endswith(".lnk"):
                    shortcut_path = os.path.join(root, file)
                    try:
                        # Use winshell to correctly parse the .lnk shortcut file
                        with winshell.shortcut(shortcut_path) as shortcut:
                            target_path = shortcut.path
                            if target_path and os.path.exists(target_path):
                                # Use the shortcut name (without .lnk) as the app's name
                                app_name = os.path.splitext(file)[0].lower()
                                # Do not overwrite if we already found a user-specific shortcut
                                if app_name not in app_dict:
                                    app_dict[app_name] = target_path
                    except Exception as e:
                        print(f"Could not parse shortcut {shortcut_path}: {e}")
    return app_dict

if __name__ == "__main__":
    print("Scanning your computer for applications... This may take a moment.")
    apps = get_app_paths()

    # Save the dictionary of found apps to a JSON file
    with open("app_index.json", "w") as f:
        json.dump(apps, f, indent=4)

    print(f"\nSuccessfully found and indexed {len(apps)} applications.")
    print("Index saved to app_index.json. You can now manually edit this file to add or correct paths.")