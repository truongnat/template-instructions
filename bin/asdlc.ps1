# Agentic SDLC - Command Wrapper
# Usage: .\bin\asdlc.ps1 <command> [args]

$Root = Resolve-Path "$PSScriptRoot\.."
if (Test-Path "$Root\.venv\Scripts\python.exe") {
    $Python = "$Root\.venv\Scripts\python.exe"
} else {
    $Python = "python"
}

& $Python "$Root\tools\core\cli\main.py" @args
