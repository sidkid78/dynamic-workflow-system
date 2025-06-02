# start-servers.ps1
# Enhanced startup script with automatic dependency installation

param(
    [switch]$SkipInstall,
    [switch]$Force
)

function Write-ColorHost($Text, $Color = "White") {
    Write-Host $Text -ForegroundColor $Color
}

function Test-Prerequisites {
    Write-ColorHost "🔍 Checking prerequisites..." "Cyan"
    
    # Check Python
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion -match "Python (\d+\.\d+)") {
            $version = [version]$matches[1]
            if ($version -ge [version]"3.8") {
                Write-ColorHost "✅ Python $($matches[1]) found" "Green"
            } else {
                Write-ColorHost "❌ Python 3.8+ required. Found $($matches[1])" "Red"
                return $false
            }
        }
    } catch {
        Write-ColorHost "❌ Python not found. Please install Python 3.8+" "Red"
        return $false
    }
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            Write-ColorHost "✅ Node.js $nodeVersion found" "Green"
        }
    } catch {
        Write-ColorHost "❌ Node.js not found. Please install Node.js" "Red"
        return $false
    }
    
    return $true
}

if (-not $SkipInstall) {
    Write-ColorHost "🚀 Effective Dynamic Workflow System - Auto Setup & Start" "Magenta"
    Write-ColorHost "=" * 60 "DarkGray"
    
    if (-not (Test-Prerequisites)) {
        Write-ColorHost "Prerequisites check failed. Please install missing dependencies." "Red"
        exit 1
    }
}

Write-ColorHost "🔧 Setting up Backend Server..." "Green"

# Enhanced Backend Setup and Start
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`
    `$ErrorActionPreference = 'Continue'; `
    Write-Host '🐍 Setting up Python backend...' -ForegroundColor Cyan; `
    cd backend; `
    `
    # Create virtual environment if it doesn't exist `
    if (-not (Test-Path .\venv)) { `
        Write-Host '📦 Creating Python virtual environment...' -ForegroundColor Yellow; `
        python -m venv venv; `
        if (`$LASTEXITCODE -ne 0) { `
            Write-Host '❌ Failed to create virtual environment' -ForegroundColor Red; `
            Read-Host 'Press Enter to close...'; `
            exit 1; `
        } `
    } `
    `
    # Activate virtual environment `
    if (Test-Path .\venv\Scripts\activate.ps1) { `
        Write-Host '🔄 Activating virtual environment...' -ForegroundColor Cyan; `
        .\venv\Scripts\activate.ps1; `
        `
        # Install/Update dependencies `
        if ($($args[0]) -eq '--force' -or -not (Test-Path .\venv\pyvenv.cfg) -or (Get-ChildItem requirements.txt).LastWriteTime -gt (Get-ChildItem .\venv\pyvenv.cfg).LastWriteTime) { `
            Write-Host '📥 Installing/updating Python dependencies...' -ForegroundColor Yellow; `
            Write-Host 'This may take a few minutes on first run...' -ForegroundColor Gray; `
            python -m pip install --upgrade pip; `
            pip install -r requirements.txt; `
            if (`$LASTEXITCODE -ne 0) { `
                Write-Host '❌ Failed to install dependencies' -ForegroundColor Red; `
                Read-Host 'Press Enter to close...'; `
                exit 1; `
            } `
        } else { `
            Write-Host '✅ Dependencies already installed' -ForegroundColor Green; `
        } `
        `
        # Check environment file `
        if (-not (Test-Path .env)) { `
            Write-Host '⚠️  No .env file found. Copying from example...' -ForegroundColor Yellow; `
            if (Test-Path env.example) { `
                Copy-Item env.example .env; `
                Write-Host '📝 Created .env file from example. Please configure your API keys!' -ForegroundColor Cyan; `
            } else { `
                Write-Host '❌ No env.example found. Please create .env file manually.' -ForegroundColor Red; `
            } `
        } `
        `
        Write-Host '🚀 Starting backend server...' -ForegroundColor Green; `
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; `
    } else { `
        Write-Host '❌ Failed to setup virtual environment' -ForegroundColor Red; `
    } `
    Read-Host 'Backend server window. Press Enter to close...' `
" -ArgumentList $(if ($Force) { "--force" } else { "" })

Start-Sleep -Seconds 2

Write-ColorHost "🌐 Setting up Frontend Server..." "Green"

# Enhanced Frontend Setup and Start  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`
    `$ErrorActionPreference = 'Continue'; `
    Write-Host '⚛️  Setting up React frontend...' -ForegroundColor Cyan; `
    cd frontend; `
    `
    # Install dependencies if needed `
    if (-not (Test-Path node_modules) -or -not (Test-Path package-lock.json)) { `
        Write-Host '📥 Installing Node.js dependencies...' -ForegroundColor Yellow; `
        Write-Host 'This may take a few minutes on first run...' -ForegroundColor Gray; `
        npm install; `
        if (`$LASTEXITCODE -ne 0) { `
            Write-Host '❌ Failed to install npm dependencies' -ForegroundColor Red; `
            Read-Host 'Press Enter to close...'; `
            exit 1; `
        } `
    } else { `
        # Check if package.json is newer than node_modules `
        if ((Get-ChildItem package.json).LastWriteTime -gt (Get-ChildItem node_modules).LastWriteTime) { `
            Write-Host '🔄 Package.json updated, reinstalling dependencies...' -ForegroundColor Yellow; `
            npm install; `
        } else { `
            Write-Host '✅ Dependencies already installed' -ForegroundColor Green; `
        } `
    } `
    `
    Write-Host '🚀 Starting frontend development server...' -ForegroundColor Green; `
    npm run dev; `
    Read-Host 'Frontend server window. Press Enter to close...' `
"

Write-ColorHost "✨ Both servers are starting up!" "Green"
Write-ColorHost "" "White"
Write-ColorHost "📋 Server Information:" "Cyan"
Write-ColorHost "  🔗 Frontend: http://localhost:3000" "White"
Write-ColorHost "  🔗 Backend:  http://localhost:8000" "White"
Write-ColorHost "  📚 API Docs: http://localhost:8000/docs" "White"
Write-ColorHost "" "White"
Write-ColorHost "💡 First time setup tips:" "Yellow"
Write-ColorHost "  1. Configure your .env file in the backend directory" "Gray"
Write-ColorHost "  2. Add your Google API key for Gemini" "Gray"
Write-ColorHost "  3. Both servers will auto-reload on file changes" "Gray"
Write-ColorHost "" "White"
Write-ColorHost "🎯 Use Ctrl+C in each server window to stop them" "Cyan"

# Optional: Create desktop shortcuts
if (-not $SkipInstall) {
    $createShortcuts = Read-Host "Create desktop shortcuts for easy access? (y/N)"
    if ($createShortcuts -eq 'y' -or $createShortcuts -eq 'Y') {
        $desktop = [Environment]::GetFolderPath("Desktop")
        $currentDir = Get-Location
        
        # Backend shortcut
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut("$desktop\Effective Backend.lnk")
        $shortcut.TargetPath = "powershell.exe"
        $shortcut.Arguments = "-Command `"cd '$currentDir\backend'; .\venv\Scripts\activate.ps1; uvicorn app.main:app --reload`""
        $shortcut.WorkingDirectory = "$currentDir\backend"
        $shortcut.Description = "Start Effective Backend Server"
        $shortcut.Save()
        
        # Frontend shortcut
        $shortcut2 = $shell.CreateShortcut("$desktop\Effective Frontend.lnk")
        $shortcut2.TargetPath = "powershell.exe" 
        $shortcut2.Arguments = "-Command `"cd '$currentDir\frontend'; npm run dev`""
        $shortcut2.WorkingDirectory = "$currentDir\frontend"
        $shortcut2.Description = "Start Effective Frontend Server"
        $shortcut2.Save()
        
        Write-ColorHost "✅ Desktop shortcuts created!" "Green"
    }
} 