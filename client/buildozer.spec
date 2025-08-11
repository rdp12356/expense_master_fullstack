[app]

# (str) Title of your application
title = SuperApp

# (str) Package name
package.name = superapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (str) The main .py file to use as the main entry point for your app
source.include_exts = py,kv,png,jpg,ttf,atlas

# (list) List of inclusions using pattern matching
source.include_patterns = app.kv, services/*

# (str) Application versioning (method 1)
version = 0.1.0

# (list) Application requirements
# Ensure to keep recipes minimal for faster builds
requirements = python3,kivy==2.3.0,kivymd,requests,kivy_garden.graph

# (str) Supported orientation (one of: landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (int) Target Android API, default is to always use the latest API available.
# android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use. This will automatically be the same as android.api if not set
# android.sdk = 33

# (int) Android NDK version to use
# android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (bool) Android logcat filters to use
# android.logcat_filters = *:S python:D

# (str) Android entrypoint, default is ok for Kivy-based app
# android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is "@android:style/Theme.NoTitleBar"
# android.theme = @android:style/Theme.Material.Light

# (list) Pattern to whitelist for the whole project
# whitelist = *

# (str) Custom source folders for requirements
# (list) Garden requirements
# garden_requirements = graph

# (bool) Indicate whether to force accept all sdk licenses.
android.accept_sdk_license = True

# (str) The file to use as the icon.
# icon.filename = %(source.dir)s/data/icon.png

# (str) Supported architectures
# android.arch = armeabi-v7a, arm64-v8a, x86, x86_64

# (bool) copy library instead of making a libpymodules.so
# android.copy_libs = 1

# (list) Custom Java source folders

# (list) Java .jar files to add to the libs

# (list) Gradle dependencies

# (str) Custom package options

# (bool) Collect library data files
# collect_data = 1


[buildozer]
log_level = 2
warn_on_root = 0