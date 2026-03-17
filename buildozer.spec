[app]
title = SimpleSideband
package.name = simplesideband
package.domain = org.simplesideband
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,db
source.exclude_exts = spec
version = 0.2.0

# Requirements: sqlite3 removed (built into Python, not a valid p4a recipe)
requirements = python3,kivy==2.3.0,rns,lxmf,pillow,msgpack,cryptography,requests,plyer,libbz2

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,RECEIVE_BOOT_COMPLETED,VIBRATE,WAKE_LOCK,FOREGROUND_SERVICE

android.api = 33
android.minapi = 27
android.ndk = r25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True

# Recipes: sqlite3 removed (not a p4a recipe); bz2 kept for libbz2 support
android.recipes = cryptography,pillow,bz2

android.add_aars =
android.extra_gradle_repositories =
android.gradle_dependencies = androidx.core:core-ktx:1.9.0

[buildozer]
log_level = 2
warn_on_root = 1
