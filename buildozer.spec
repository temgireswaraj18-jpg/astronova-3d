[app]
title = Astronova 3D Solar System Lab
package.name = astronova
package.domain = org.astronova

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0

# Pin python3 and hostpython3 to 3.11.9 so Kivy's Cython C-extensions compile cleanly
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.0,plyer,kivmob,pyjnius,six,android

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

# Required by Google AdMob / KivMob during final Gradle APK/AAB packaging
android.enable_androidx = True

android.release_artifact = aab
android.archs = arm64-v8a, armeabi-v7a

# AdMob Test App ID & KivMob-compatible Play Services Ads dependency
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-3940256099942544~3347511713
android.gradle_dependencies = com.google.android.gms:play-services-ads:20.6.0

[buildozer]
log_level = 2
warn_on_root = 1
