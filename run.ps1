.\.venv\Scripts\Activate.ps1

$test_mode = 0
$show_help = $false
$unknown_arg = $false

foreach ($arg in $args) {
    switch ($arg) {
        "-h" { $show_help = $true }
        "--help" { $show_help = $true }
        "-t" { $test_mode = 1 }
        "-to" { $test_mode = 2 }
        default { 
            $unknown_arg = $true 
            Write-Host "Error: unknown argument '$arg'"
        }
    }
}

if ($show_help -or $unknown_arg) {
    Write-Host "Available modes:"
    Write-Host "-h, --help  - Show this message."
    Write-Host "-t          - Run tests before executing head.py."
    Write-Host "-to         - Run tests ONLY (do not execute head.py)."
    exit
}

if ($test_mode -ge 1) {
    Write-Host "Running tests..."
    python -m unittest discover -s test
}

if ($test_mode -lt 2) {
    Write-Host "Starting main script..."
    python head.py
}

deactivate
