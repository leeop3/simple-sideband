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

# Requirements: sqlite3 removed (built into Python, not a valid p4a recipe)
requirements = python3, kivy==2.3.0, rns, lxmf, pillow, msgpack, cryptography, requests, plyer, sqlite3, hostpython3, openssl, libbz2

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,BLUETOOTH_ADVERTISE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,RECEIVE_BOOT_COMPLETED,VIBRATE,WAKE_LOCK,FOREGROUND_SERVICE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True

# Recipes: sqlite3 removed (not a p4a recipe); bz2 kept for libbz2 support
android.recipes = cryptography, pillow, sqlite3, openssl, libbz2, bz2, pyjnius

android.add_aars =
android.extra_gradle_repositories =
android.gradle_dependencies = androidx.core:core-ktx:1.9.0


[buildozer]
log_level = 2
warn_on_root = 1
