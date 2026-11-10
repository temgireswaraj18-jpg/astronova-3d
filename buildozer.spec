[app]
title = Astronova 3D Solar System Lab
package.name = astronova
package.domain = org.astronova

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0

# Removed 'kivmob' (tar.gz only) so p4a's --only-binary wheel installer succeeds cleanly
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.0,plyer,pyjnius,six,android

icon.filename = %(source.dir)s/assets/icon_512x512.png
presplash.filename = %(source.dir)s/assets/presplash.png
android.presplash_color = #070B1A

orientation = portrait,landscape
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE

android.api = 35
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.enable_androidx = True

android.release_artifact = aab
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
