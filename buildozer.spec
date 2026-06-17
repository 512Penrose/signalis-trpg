[app]
# =============================================================================
# SIGNALIS TRPG Adjudicator - Buildozer Configuration
# =============================================================================

# 应用标题 (App title)
title = SIGNALIS TRPG Adjudicator

# 包名 (Package name)
package.name = signalis_trpg

# 包域名 (Package domain)
package.domain = org.signalis

# 源代码目录 (Source directory)
source.dir = .

# 包含的文件扩展名 (Included file extensions)
source.include_exts = py,kv,json,ttf

# 排除的文件模式 (Exclude patterns)
source.exclude_patterns = __pycache__,*.pyc,.git

# 应用版本 (Version)
version = 2.0.0

# 依赖项 - 仅使用轻量Kivy (Requirements - only lightweight Kivy)
requirements = python3,kivy

# 横屏模式 (Landscape orientation)
orientation = landscape

# 全屏模式 (Fullscreen)
fullscreen = 1

# Android API 版本
android.api = 33

# Android 最低 API 版本
android.minapi = 21

# Android SDK 版本
android.sdk = 33

# Android NDK 版本
android.ndk = 25b

# Android 目标架构 (arm64-v8a for modern devices)
android.archs = arm64-v8a

# 应用权限 (Permissions)
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# 禁用某些Android特性以减少包大小
android.wakelock = False

# 是否复制libs
android.copy_libs = 1

# =============================================================================
# iOS 配置 (保留默认值)
# =============================================================================
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false

# =============================================================================
# 构建设置 (Build settings)
# =============================================================================

# 是否使用预编译的python分发版
android.allow_backup = True

# 禁用Android NDK的某些检查
android.skip_update = False

# 自动接受Android SDK许可证
android.accept_sdk_license = True

# 日志级别
log_level = 2

# 警告为错误 (Warning as error)
warn_on_root = 1
