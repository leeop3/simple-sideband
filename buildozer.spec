[app]
title = SimpleSideband
package.name = simplesideband
package.domain = org.yourname
source.dir = src
source.include_exts = py,png,jpg,kv,atlas,json,db
source.exclude_exts = spec
version = 0.2.0

# FIXED: Added libbz2 for _bz2 module
requirements = python3,kivy==2.3.0,rns,lxmf,pillow,msgpack,cryptography,requests,plyer,sqlite3,libbz2

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,RECEIVE_BOOT_COMPLETED,VIBRATE,WAKE_LOCK,FOREGROUND_SERVICE

android.api = 33
android.minapi = 27
android.ndk = 25.2.9519653
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True

# FIXED: Added bz2 recipe
android.recipes = cryptography,pillow,sqlite3,bz2

android.add_aars = 
android.extra_gradle_repositories = 
android.gradle_dependencies = androidx.core:core-ktx:1.9.0

[buildozer]
log_level = 2
warn_on_root = 1
