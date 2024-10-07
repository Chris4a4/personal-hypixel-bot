# Define the name of the virtual environment directory
$venvDir = "venv"
$backendRequirementsFile = "backend/requirements.txt"
$botRequirementsFile = "bot/requirements.txt"

# Function to check if a virtual environment exists
function Test-Venv {
    if (Test-Path -Path "$venvDir/Scripts/Activate.ps1") {
        return $true
    }
    return $false
}

# Function to create a new virtual environment
function New-Venv {
    python -m venv $venvDir
    if (-not $?){
        Write-Host "Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "Virtual environment created successfully."
}

# Function to install requirements
function Install-Requirements {
    & "$venvDir\Scripts\Activate"
    if (Test-Path -Path $backendRequirementsFile) {
        pip install -r $backendRequirementsFile
        if (-not $?){
            Write-Host "Failed to install backend requirements" -ForegroundColor Red
            exit 1
        }
        Write-Host "Backend requirements installed successfully."
    } else {
        Write-Host "No backend requirements.txt file found." -ForegroundColor Yellow
    }
    if (Test-Path -Path $botRequirementsFile) {
        pip install -r $botRequirementsFile
        if (-not $?){
            Write-Host "Failed to install bot requirements" -ForegroundColor Red
            exit 1
        }
        Write-Host "Bot requirements installed successfully."
    } else {
        Write-Host "No bot requirements.txt file found." -ForegroundColor Yellow
    }
    deactivate
}

# Main script
if (-not (Test-Venv)) {
    Write-Host "Virtual environment not found. Creating a new one..."
    New-Venv
} else {
    Write-Host "Virtual environment already exists."
}

Install-Requirements
