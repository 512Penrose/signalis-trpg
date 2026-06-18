# SIGNALIS TRPG 判定程序 - 安卓APK

基于独立游戏 SIGNALIS 的生化朋克/太空克苏鲁 TRPG 数值判定程序。

## 功能特点

- 完整的共振骰池系统(RDPS)判定
- 角色/敌人管理（JSON导入导出）
- 8大功能Tab：基础检定、对抗检定、战斗判定、恐怖检定、生物共振、PCD操作、贴贴机制、恢复治疗
- 中文显示完整补全（属性/技能/装备全部中文）
- 暗色主题（SIGNALIS铜橙色风格）
- 横屏模式，适配2772x1280等高分辨率折叠屏

## 快速安装（推荐）

### 方式一：GitHub Actions 自动打包（推荐）

> **重要**：ZIP解压后，`.github` 文件夹必须在项目**根目录**，不能嵌套在子文件夹内。

1. 解压ZIP文件，确保文件结构如下（`main.py` 和 `.github` 同级）：
   ```
   main.py
   signalis.kv
   buildozer.spec
   .github/workflows/build_apk.yml   <-- 关键！
   ```
2. 将全部文件推送到 GitHub 仓库（确保 `.github` 在根目录）
3. 进入仓库的 Actions 页面，如未显示工作流：
   - 点击 **Settings** → **Actions** → **General**
   - 选择 **Allow all actions and reusable workflows**
   - 保存后刷新页面
4. 左侧应出现 **"Build SIGNALIS TRPG APK"**，点击它
5. 点击右侧 **"Run workflow"** → **Run workflow** 触发打包
6. 等待约20-30分钟，在 Releases 页面下载 APK

### 方式二：本地 Buildozer 打包

```bash
# 安装依赖
sudo apt-get install -y autoconf automake libtool pkg-config \
  zlib1g-dev libncurses5-dev libncursesw5-dev libffi-dev \
  libssl-dev libltdl-dev git wget unzip default-jdk
pip install buildozer cython

# 解压ZIP并进入项目目录（解压后直接进入，不要cd到子文件夹）
# 确保 main.py 和 buildozer.spec 在当前目录
ls main.py buildozer.spec   # 验证

# 打包APK
buildozer android debug

# 输出文件在 bin/ 目录
ls bin/*.apk
```

### 方式三：直接运行（无需打包）

```bash
# 安装 Kivy
pip install kivy

# 运行程序
python main.py
```

## 项目结构（ZIP根目录）

```
main.py              # Kivy主程序（核心逻辑+UI）
signalis.kv          # KV样式文件（暗色主题）
buildozer.spec       # Buildozer打包配置
README.md            # 本文件
安装手册.md           # 详细操作手册
.github/
└── workflows/
    └── build_apk.yml  # GitHub Actions自动打包（必须在根目录！）
```

## 使用说明

### 界面布局（横屏）

```
+-----------+------------------+------------+
|  左栏25%   |     中栏50%      |  右栏25%   |
| 角色管理   |   8 Tab判定面板   |  判定日志  |
+-----------+------------------+------------+
```

### 8个功能Tab

| Tab | 功能 |
|-----|------|
| 基础检定 | 属性+技能+情境调整，执行检定 |
| 对抗检定 | 攻击方vs防御方，双方属性技能 |
| 战斗判定 | 武器选择+瞄准部位+攻击 |
| 恐怖检定 | 4级恐怖（不安/恐惧/绝望/疯狂）|
| 生物共振 | 8种能力+共振爆发 |
| PCD操作 | 人格模型校正数据的重掷/加骰/过载 |
| 贴贴机制 | 情感连接(-2)/深度亲密(-3)降低压力 |
| 恢复治疗 | 仿形体快速/人类自然/纳米针剂恢复 |

### 中文显示

- **属性**：PHY(体格)、AGI(敏捷)、PER(感知)、INT(智力)、WIL(意志)、RES(共振)
- **技能**：firearms(枪械)、melee(近战武器)、dodge(闪避) 等22项
- **护甲/武器/恐怖/共振**：全部中文显示

## 系统要求

- Android 8.0+ (API 26+)
- 横屏模式
- 建议分辨率：2772x1280 或更高

## 版本

v2.0 - 共振骰池系统(RDPS)完整版
