[app]
title = SimpleSideband
package.name = simplesideband
package.domain = org.yourname
source.dir = src
source.include_exts = py,png,jpg,kv,atlas
source.exclude_exts = spec
android.ndk = 25b
android.api = 33
android.minapi = 21 
version = 0.1.0
requirements = python3,kivy==2.3.0,rns,lxmf,pillow,msgpack,cryptography,requests,openssl
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
