# Windows 安装指南（Git Bash / MINGW64）

## 问题原因

Git Bash 中反斜杠 `\` 是**转义符**，不是路径分隔符。Windows路径需要用**正斜杠 `/`** 或**双反斜杠 `\\`**。

---

## 正确操作步骤

### 第一步：进入下载目录

```bash
# 方法1：使用正斜杠（推荐）
cd /c/Users/COLOR/Downloads

# 方法2：使用双反斜杠
cd C:\\Users\\COLOR\\Downloads

# 方法3：直接拖拽
# 在文件资源管理器中进入 Downloads 文件夹
# 右键空白处 → Git Bash Here
```

### 第二步：解压 ZIP（两种方法）

#### 方法A：用Windows右键解压（最简单）

1. 打开文件资源管理器，进入 `C:\Users\COLOR\Downloads`
2. 右键 `signalis_android_trpg_v2.zip` → **解压全部...**
3. 解压到 `C:\Users\COLOR\Downloads\signalis_trpg\`
4. 进入解压后的文件夹，确认结构：

```
signalis_trpg/
├── main.py                    <-- 直接看到
├── signalis.kv
├── buildozer.spec
├── README.md
├── 安装手册.md
├── .github/                   <-- 直接看到（关键！）
│   └── workflows/
│       └── build_apk.yml
└── bin/
```

**确认 `main.py` 和 `.github` 在同一层！**

#### 方法B：命令行解压（Git Bash内）

```bash
cd /c/Users/COLOR/Downloads

# 解压
unzip signalis_android_trpg_v2.zip -d signalis_trpg

# 如果提示 unzip 未找到，用 jar 解压
jar xf signalis_android_trpg_v2.zip

# 或者用 7z
7z x signalis_android_trpg_v2.zip -osignalis_trpg

# 或者用 Python
python -c "import zipfile; zipfile.ZipFile('signalis_android_trpg_v2.zip').extractall('signalis_trpg')"
```

### 第三步：推送到 GitHub

```bash
# 进入解压后的文件夹（main.py 所在目录）
cd /c/Users/COLOR/Downloads/signalis_trpg

# 确认在正确目录（应看到 main.py 和 .github）
ls
# 输出：buildozer.spec  main.py  README.md  signalis.kv  安装手册.md  .github/  bin/

# 初始化 git
git init

# 添加所有文件
git add .

# 提交
git commit -m "SIGNALIS TRPG v2.0"

# 连接远程仓库（替换 YourName 为你的GitHub用户名）
git remote add origin https://github.com/YourName/signalis-trpg.git

# 推送
git push -u origin main
```

### 第四步：触发 GitHub Actions

1. 浏览器打开 `https://github.com/YourName/signalis-trpg/actions`
2. 如果左侧空白 → 点击 **Settings** → **Actions** → **General** → 选择 **Allow all actions and reusable workflows** → **Save**
3. 刷新页面，左侧出现 **"Build SIGNALIS TRPG APK"**
4. 点击 → 右侧 **Run workflow** → **Run workflow**
5. 等待20-30分钟 → 全部绿色 ✅ → 去 Releases 下载 APK

---

## 常见问题

### Q: `cd C:\Users\COLOR\Downloads` 报错

**A**: 反斜杠在bash中是转义符，改成正斜杠：
```bash
cd /c/Users/COLOR/Downloads
```

### Q: `cd D:\` 后命令不换行

**A**: 反斜杠是转义符，D盘路径这样进：
```bash
cd /d/
# 或
cd D:\\
```

### Q: unzip 命令未找到

**A**: 用Windows右键解压，或用Python：
```bash
python -c "import zipfile; zipfile.ZipFile('signalis_android_trpg_v2.zip').extractall('signalis_trpg')"
```

### Q: 推送到GitHub提示需要登录

**A**: 需要创建Personal Access Token：
1. GitHub → 右上角头像 → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 Generate new token
3. 勾选 `repo` 权限
4. 生成后复制Token
5. 推送时密码栏输入这个Token（代替密码）

### Q: Actions页面看不到"Build SIGNALIS TRPG APK"

**A**: 99%是因为`.github`文件夹不在仓库根目录。检查：
```bash
# 在 signalis_trpg 目录执行
ls .github/workflows/build_apk.yml
# 如果提示 No such file，说明 .github 不在根目录
```

---

## 快速检查清单

- [ ] ZIP解压后 `main.py` 和 `.github` 在同一层
- [ ] 在Git Bash中用 `cd /c/Users/...` 格式（正斜杠）
- [ ] `git init` 在 `main.py` 所在目录执行
- [ ] 推送后GitHub仓库根目录能看到 `main.py` 文件
- [ ] Actions设置中允许了所有工作流
