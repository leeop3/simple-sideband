# setup_github.py - Creates ALL clean files and pushes to GitHub
import os
import subprocess

BASE_DIR = r"F:\simple-sideband"
SRC_DIR = os.path.join(BASE_DIR, "src")

print("=" * 60)
print("  CREATING CLEAN FILES FOR GITHUB")
print("=" * 60)

# Create directories
for subdir in ["src", "src/networking", "src/utils", ".github/workflows"]:
    path = os.path.join(BASE_DIR, subdir)
    os.makedirs(path, exist_ok=True)
    print(f"Created: {path}")

# Create __init__.py files
for subdir in ["", "networking", "utils"]:
    path = os.path.join(SRC_DIR, subdir, "__init__.py") if subdir else os.path.join(SRC_DIR, "__init__.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write("")
    print(f"Created: {path}")

# Create requirements.txt
requirements = """kivy>=2.3.0
kivymd>=1.2.0
rns>=1.8.0
lxmf>=0.9.0
pillow>=10.0.0
msgpack>=1.0.5
requests>=2.31.0
cryptography>=41.0.0
"""
with open(os.path.join(BASE_DIR, "requirements.txt"), "w", encoding="utf-8") as f:
    f.write(requirements)
print("Created: requirements.txt")

# Create buildozer.spec
buildozer_spec = """[app]
title = SimpleSideband
package.name = simplesideband
package.domain = org.yourname
source.dir = src
source.include_exts = py,png,jpg,kv,atlas
source.exclude_exts = spec
version = 0.1.0
requirements = python3,kivy==2.3.0,rns,lxmf,pillow,msgpack,cryptography,requests
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE,CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN
android.api = 33
android.minapi = 27
android.ndk = 25.2.9519653
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
android.recipes = cryptography,pillow
[buildozer]
log_level = 2
warn_on_root = 1
"""
with open(os.path.join(BASE_DIR, "buildozer.spec"), "w", encoding="utf-8") as f:
    f.write(buildozer_spec)
print("Created: buildozer.spec")

print("")
print("=" * 60)
print("  FILES CREATED! NOW PUSH TO GITHUB:")
print("=" * 60)
print("")
print("1. cd F:\\simple-sideband")
print("2. git init")
print("3. git add .")
print("4. git commit -m \"Initial commit\"")
print("5. git remote add origin https://github.com/YOUR_USERNAME/simple-sideband.git")
print("6. git push -u origin main")
print("")
print("Then download from GitHub (no corruption!)")