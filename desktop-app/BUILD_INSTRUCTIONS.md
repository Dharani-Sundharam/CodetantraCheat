# CodeTantra Automation - Build & Installer Instructions

## 📋 Prerequisites

### Required Software:
1. **Python 3.8+** - [Download here](https://www.python.org/downloads/)
2. **Git** - [Download here](https://git-scm.com/downloads)
3. **Inno Setup** - [Download here](https://jrsoftware.org/isinfo.php)

### Python Packages:
- All required packages are listed in `requirements.txt`
- PyInstaller will be auto-installed if missing

## 🚀 Quick Build Process

### Option 1: Automated Build (Recommended)
```bash
# Navigate to desktop-app folder
cd desktop-app

# Run the automated build script
build_exe.bat
```

### Option 2: Manual Build
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install firefox

# 3. Create executable
pyinstaller CodeTantraAutomation.spec

# 4. Test executable
dist\CodeTantraAutomation.exe
```

## 📦 Creating Installer

### Option 1: Automated Installer Creation
```bash
# After successful build, create installer
create_installer.bat
```

### Option 2: Manual Installer Creation
1. Install **Inno Setup** from [official website](https://jrsoftware.org/isinfo.php)
2. Open `installer.iss` in Inno Setup Compiler
3. Click "Build" → "Compile"
4. Installer will be created in `installer_output/` folder

## 📁 File Structure After Build

```
desktop-app/
├── dist/
│   └── CodeTantraAutomation.exe    # Main executable
├── installer_output/
│   └── CodeTantraAutomation_Setup_v1.0.0.exe  # Installer
├── build_exe.bat                   # Build script
├── create_installer.bat            # Installer creation script
├── CodeTantraAutomation.spec       # PyInstaller spec
├── installer.iss                   # Inno Setup script
└── icon.ico                        # Application icon
```

## 🔧 Troubleshooting

### Common Issues:

#### 1. "Python not found"
- **Solution**: Install Python 3.8+ and add to PATH
- **Check**: Run `python --version` in command prompt

#### 2. "PyInstaller not found"
- **Solution**: Script will auto-install PyInstaller
- **Manual**: `pip install pyinstaller`

#### 3. "Playwright browsers not installed"
- **Solution**: Run `playwright install firefox`
- **Check**: Script handles this automatically

#### 4. "Inno Setup not found"
- **Solution**: Download and install Inno Setup
- **Alternative**: Use manual installer creation

#### 5. "Executable too large"
- **Solution**: This is normal (includes Python runtime + Playwright)
- **Size**: Expect 100-200MB for complete package

#### 6. "Missing modules error"
- **Solution**: Check `CodeTantraAutomation.spec` hiddenimports
- **Add**: Any missing modules to the hiddenimports list

## 📊 Build Output

### Successful Build Output:
```
Building CodeTantra Automation Desktop App
==========================================

Step 1: Installing dependencies...
✓ Dependencies installed

Step 2: Installing Playwright browsers...
✓ Firefox browser installed

Step 3: Creating executable with PyInstaller...
✓ Executable created successfully

Step 4: Testing executable...
✓ Executable created successfully
File size: [Size] bytes

Step 5: Cleaning up build files...
✓ Build complete!
```

### Successful Installer Output:
```
Creating CodeTantra Automation Installer
=========================================

Found Inno Setup at: C:\Program Files (x86)\Inno Setup 6\ISCC.exe

Step 1: Creating installer directory...
Step 2: Compiling installer with Inno Setup...
✓ Installer created successfully!

Installer location: installer_output\CodeTantraAutomation_Setup_v1.0.0.exe
```

## 🎯 Distribution

### For End Users:
1. **Share**: `installer_output\CodeTantraAutomation_Setup_v1.0.0.exe`
2. **Size**: ~150-200MB (includes all dependencies)
3. **Installation**: Standard Windows installer
4. **Requirements**: Windows 10/11, no additional software needed

### For Developers:
1. **Source**: Share the entire project folder
2. **Build**: Users can run `build_exe.bat`
3. **Dependencies**: All listed in `requirements.txt`

## 🔒 Security Notes

- **Antivirus**: May flag as suspicious (false positive)
- **Code Signing**: Consider code signing for production
- **Permissions**: Requires admin rights for installation
- **Network**: Needs internet for API calls

## 📝 Version Management

### Updating Version:
1. Edit `installer.iss` line 5: `#define MyAppVersion "1.0.1"`
2. Rebuild with `create_installer.bat`
3. New installer: `CodeTantraAutomation_Setup_v1.0.1.exe`

### Changelog:
- Keep `CHANGELOG.md` updated
- Document new features and fixes
- Update version numbers consistently

## 🆘 Support

### Build Issues:
1. Check Python version (3.8+ required)
2. Verify all dependencies installed
3. Check Windows version compatibility
4. Review error messages in build output

### Runtime Issues:
1. Test executable before creating installer
2. Check API connectivity
3. Verify browser permissions
4. Review application logs

---

**Happy Building! 🚀**
