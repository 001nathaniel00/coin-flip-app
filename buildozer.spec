[app]

# (str) Title of your application
title = Coin Flip Ultimate

# (str) Package name (no spaces or special characters)
package.name = coinflipultimate

# (str) Package domain (reverse-DNS style, used for Android package id).
# Change this to something you actually control if you plan to publish.
package.domain = org.kevwe

# (str) Source code where main.py lives
source.dir = .

# (list) File extensions to include in the build
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf

# (list) Directories to exclude from the build
source.exclude_dirs = tests, bin, venv, .buildozer, .git, __pycache__

# (str) Application version
version = 0.1

# (list) Application requirements, comma separated
requirements = python3,kivy

# (str) Presplash image (shown while the app loads) — uncomment and add a file if you want one
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) App icon — uncomment and add a file if you want one
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation: landscape, sensorLandscape, portrait, or all
orientation = portrait

#
# Android specific
#

# (bool) Fullscreen (hides the status bar)
fullscreen = 0

# (list) Android permissions — this app doesn't touch network/storage/camera, so none needed
android.permissions =

# (int) Target Android API — should be as high as possible for Play Store compliance
android.api = 34

# (int) Minimum Android API this APK will run on
android.minapi = 21

# (bool) Automatically accept the Android SDK license.
# Required for CI/headless builds — there's no terminal to type "y" at,
# so without this the build-tools install gets silently skipped and
# buildozer fails later with "Aidl not found, please install it."
android.accept_sdk_license = True

# (list) Architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Allow Android's automatic backup of app data
android.allow_backup = True

# (str) Package format: apk (sideloadable) or aab (Play Store)
android.release_artifact = apk

#
# python-for-android specific
#

# (str) p4a branch to use — leave default unless you hit a build issue that a newer branch fixes
#p4a.branch = master

[buildozer]

# (int) Log verbosity: 0 = error only, 1 = info, 2 = debug (full command output)
log_level = 2

# (int) Warn if buildozer is being run as root
warn_on_root = 1
