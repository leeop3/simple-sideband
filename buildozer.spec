[app]
title = SimpleSideband
package.name = simplesideband
package.domain = org.simplesideband
source.dir = src
source.include_exts = py,png,jpg,kv,atlas,json,db
source.exclude_exts = spec
source.exclude_dirs = venv,.venv,tests,__pycache__,.git,.buildozer,bin
source.exclude_patterns = license,images/originals/*
version = 0.2.0

# --- FIXED REQUIREMENTS ---
# Added 'pyjnius' for Java bridge and ensured 'libbz2' is present for RNS
requirements = python3, kivy==2.3.0, rns, lxmf, pillow, msgpack, cryptography, requests, plyer, sqlite3, hostpython3, openssl, libbz2, pyjnius

orientation = portrait
fullscreen = 0

# --- PERMISSIONS ---
# Verified all Bluetooth permissions for Android 13 (API 33)
android.permissions = INTERNET,ACCESS_NETWORK_STATE,CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,BLUETOOTH_ADVERTISE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,RECEIVE_BOOT_COMPLETED,VIBRATE,WAKE_LOCK,FOREGROUND_SERVICE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True

# --- CUSTOM JAVA CONFIGURATION ---
# 1. Path to your custom Java files (src/java/org/simplesideband/simplesideband/...)
android.add_src = src/java

 2. Add Kotlin support to Gradle dependencies
# We add the Kotlin stdlib and the Core-KTX library
android.gradle_dependencies = 
    androidx.core:core-ktx:1.9.0,
    org.jetbrains.kotlin:kotlin-stdlib:1.8.22

# 2. Tell Android to use YOUR PythonActivity instead of the default one
android.activity_class = org.simplesideband.simplesideband.PythonActivity

# --- RECIPES ---
android.recipes = cryptography, pillow, sqlite3, openssl, libbz2

android.gradle_dependencies = androidx.core:core-ktx:1.9.0