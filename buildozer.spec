[app]

# (str) Title of your application
title = SIGNALIS TRPG

# (str) Package name
package.name = signalis_trpg

# (str) Package domain (needed for android/ios packaging)
package.domain = org.signalis

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,kv,json,png,jpg,otf,ttf,xml

# (str) Application versioning
version = 2.0.3

# (list) Application requirements
# Kivy 2.3.0 for Android 15 compatibility
# MUST lock both hostpython3 and python3 to same version
requirements = hostpython3==3.11.9,python3==3.11.9,kivy==2.3.0,pygments,sdl2,sdl2_image,sdl2_mixer,sdl2_ttf,requests,urllib3,certifi,charset_normalizer,idna

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
# 0 = windowed mode, better compatibility with Android 15
fullscreen = 0

# Presplash background color during loading
android.presplash_color = #FF1a1a2e

#
# Android specific - Optimized for Android 15
#

# (list) Permissions - minimal set for Android 15
android.permissions = INTERNET

# (int) Target Android API - API 35 for Android 15 full compatibility
android.api = 35

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 35

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (bool) Enable AndroidX support for modern Android compatibility
android.enable_androidx = True

# (str) launchMode to set for the main activity
android.manifest.launch_mode = singleTask

# (str) Extra xml to write directly inside the <manifest> element
# Add explicit SDK target for Android 15 compatibility
android.extra_manifest_xml = ./extra_manifest.xml

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (bool) enables Android auto backup feature
android.allow_backup = True

# (str) Android logcat filters to use - capture Python errors
android.logcat_filters = *:S python:D SDL:D

# (bool) Android logcat only display log for activity's pid
android.logcat_pid_only = False

# (list) packaging options to avoid conflicts
android.add_packaging_options = "exclude 'META-INF/DUMMY.SF'", "exclude 'META-INF/DUMMY.RSA'"

#
# Python for android (p4a) specific
#

# Use stable p4a master branch
p4a.branch = master

# (str) extra command line arguments to pass when invoking gradle
p4a.gradle_options = -Xmx4096m

#
# Buildozer specific
#

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0
