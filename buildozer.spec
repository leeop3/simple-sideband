[app]
title = SimpleSideband
package.name = simplesideband
package.domain = org.yourname
source.dir = src
source.include_exts = py,png,jpg,kv,atlas
source.exclude_exts = spec
version = 0.1.0

# Added openssl here - it is required for cryptography
requirements = python3,kivy==2.3.0,rns,lxmf,pillow,msgpack,cryptography,requests,openssl

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN

# These are the stable recommended versions
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_path = 
android.sdk_path = 

android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True

# cryptography and pillow need their recipes triggered
android.recipes = cryptography,pillow,openssl

[buildozer]
log_level = 2
warn_on_root = 1