[app]
title = SONGO
package.name = songo
package.domain = org.jeusongo
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

# Pour compiler l'APK Android avec Buildozer (Linux recommandé)
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
