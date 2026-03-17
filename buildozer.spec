[app]

# (str) Title of your application
title = SimpleSideband

# (str) Package name
package.name = simplesideband

# (str) Package domain (needed for android/ios packaging)
package.domain = org.simplesideband

# (str) Custom Android Manifest to use
android.manifest = src/AndroidManifest.xml

# (str) Source code where the main.py live
source.dir = src

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,db

# (list) List of inclusions using pattern matching
source.exclude_patterns = license,images/originals/*

# (list) List of exclusions using pattern matching
source.exclude_dirs = venv,.venv,tests,__pycache__,.git,.buildozer,bin

# (str) Application versioning
version = 0.2.0

# (list) Application requirements
# hostpython3 and pyjnius are required for your custom Java/Kotlin code
# sqlite3, openssl, and libbz2 are required for Reticulum/RNS
requirements = python3, kivy==2.3.0, rns, lxmf, pillow, msgpack, cryptography, requests, plyer, sqlite3, hostpython3, openssl, libbz2, pyjnius

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE, CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, BLUETOOTH_ADVERTISE, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, RECEIVE_BOOT_COMPLETED, VIBRATE, WAKE_LOCK, FOREGROUND_SERVICE

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) The Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Accept SDK license
android.accept_sdk_license = True

# --- CUSTOM JAVA/KOTLIN CONFIGURATION ---

# (list) The directory where your Java/Kotlin files are (src/java/org/simplesideband/simplesideband/...)
android.add_src = src/java

# (str) Full name of the Java class that starts the app (MUST match your PythonActivity.java package)
android.activity_class = org.simplesideband.simplesideband.PythonActivity

# (list) Gradle dependencies (Merged Core-KTX and Kotlin support into ONE line)
android.gradle_dependencies = androidx.core:core-ktx:1.9.0, org.jetbrains.kotlin:kotlin-stdlib:1.8.22

# --- COMPILATION RECIPES ---

# (list) Recipes to use during build (Ensure C-extensions are compiled correctly)
android.recipes = cryptography, pillow, sqlite3, openssl, libbz2, bz2

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1