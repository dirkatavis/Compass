# Quick Setup for Users Without Admin Rights

If you don't have administrator rights on your machine, you can still set up Compass automation completely!

## Option 1: One-Click Setup (Handles Everything)
```powershell
iwr -useb https://raw.githubusercontent.com/dirkatavis/Compass/main/install-compass.ps1 | iex
```
**When prompted about admin rights:** Choose option **1** (user-level installation)

## Option 2: Bootstrap with User Installation
```powershell
# Download bootstrap script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/dirkatavis/Compass/main/bootstrap.ps1" -OutFile "bootstrap.ps1"

# Run bootstrap - it will detect no admin rights and offer options
.\bootstrap.ps1

# When prompted, choose option 1 for user-level installation
```

## Option 3: Manual Installation (No Admin Required)

### Step 1: Install Python (User-Only)
1. Download Python from: https://www.python.org/downloads/
2. During installation:
   - ✅ Check "Add Python to PATH"  
   - ✅ Check "Install for all users" = **NO** (user installation only)
3. Restart PowerShell

### Step 2: Install Git (User-Only) 
1. Download from: https://git-scm.com/download/win
2. During installation:
   - Choose "Install for current user only"
3. Restart PowerShell

### Step 3: Set Up Compass
```powershell
# Create your project folder
mkdir C:\Users\$env:USERNAME\Dev\Compass
cd C:\Users\$env:USERNAME\Dev\Compass

# Clone repository
git clone https://github.com/dirkatavis/Compass.git .

# Run setup
.\setup.ps1
```

## What Works Without Admin Rights:

✅ **Python installation** (user-level)  
✅ **Git installation** (user-level)  
✅ **Virtual environment creation**  
✅ **Dependency installation** (via pip)  
✅ **All Compass functionality**  
✅ **WebDriver download** (to project folder)

## What You Can't Do Without Admin Rights:

❌ System-wide software installation  
❌ Installing to Program Files  
❌ Modifying system PATH globally

**But none of these limitations affect Compass automation functionality!**

## Troubleshooting No-Admin Setup

### Python/Git Not Recognized After Install
```powershell
# Refresh your PowerShell session
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User")
```

### Installation Fails
If user-level installation fails:
1. Use portable versions:
   - **Python**: Download "embeddable zip file" from python.org
   - **Git**: Download "Portable Git" from git-scm.com  
2. Extract to a folder you control (like Documents)
3. Add to PATH manually in PowerShell session

### Alternative Locations
Install to locations you control:
```powershell
# Good locations for no-admin users:
C:\Users\$env:USERNAME\Tools\Compass
C:\Users\$env:USERNAME\Documents\Dev\Compass  
D:\MyProjects\Compass  # If you have access to other drives
```

The key is that **Compass automation works perfectly without admin rights** - all the functionality runs in user space!