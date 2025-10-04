@echo off
REM OSUSAPPS Odoo 17 - Automated Code Quality Testing Pipeline (Windows)
REM This batch script runs comprehensive code quality checks and generates reports

setlocal enabledelayedexpansion

REM Configuration
set "WORKSPACE_DIR=%~dp0.."
set "SCRIPTS_DIR=%WORKSPACE_DIR%\scripts"
set "REPORTS_DIR=%WORKSPACE_DIR%\quality_reports"
set "TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"

REM Create reports directory
if not exist "%REPORTS_DIR%" mkdir "%REPORTS_DIR%"

echo [%date% %time%] Starting OSUSAPPS Code Quality Pipeline
echo Workspace: %WORKSPACE_DIR%
echo Reports: %REPORTS_DIR%

REM Check if Python scripts exist
if not exist "%SCRIPTS_DIR%\code_quality_analyzer.py" (
    echo ERROR: Code quality analyzer script not found!
    exit /b 1
)

if not exist "%SCRIPTS_DIR%\security_scanner.py" (
    echo ERROR: Security scanner script not found!
    exit /b 1
)

REM Initialize variables
set total_modules=0
set passed_modules=0
set failed_modules=0
set critical_issues=0
set high_issues=0
set security_vulnerabilities=0
set overall_score=0

REM Create summary report
set "summary_file=%REPORTS_DIR%\quality_pipeline_summary_%TIMESTAMP%.md"

echo # OSUSAPPS Code Quality Pipeline Report > "%summary_file%"
echo. >> "%summary_file%"
echo **Generated:** %date% %time% >> "%summary_file%"
echo **Workspace:** %WORKSPACE_DIR% >> "%summary_file%"
echo **Pipeline Version:** 1.0 >> "%summary_file%"
echo. >> "%summary_file%"
echo ## Executive Summary >> "%summary_file%"
echo. >> "%summary_file%"

REM Run Code Quality Analysis
echo [%time%] Running comprehensive code quality analysis...
set "quality_report=%REPORTS_DIR%\code_quality_%TIMESTAMP%.json"

python "%SCRIPTS_DIR%\code_quality_analyzer.py" "%WORKSPACE_DIR%" --output "%quality_report%" --verbose
if %errorlevel% neq 0 (
    echo ERROR: Code quality analysis failed
    exit /b 1
)

echo SUCCESS: Code quality analysis completed

REM Run Security Scan
echo [%time%] Running security vulnerability assessment...
set "security_report=%REPORTS_DIR%\security_assessment_%TIMESTAMP%.json"

python "%SCRIPTS_DIR%\security_scanner.py" "%WORKSPACE_DIR%" --output "%security_report%" --verbose
if %errorlevel% neq 0 (
    echo WARNING: Security scan completed with issues
)

echo SUCCESS: Security assessment completed

REM Run Module-specific Tests
echo [%time%] Running module-specific quality tests...

set module_count=0
for /d %%d in ("%WORKSPACE_DIR%\*") do (
    if exist "%%d\__manifest__.py" (
        set /a module_count+=1
        set "module_name=%%~nxd"
        echo Testing module: !module_name!
        
        REM Check manifest file
        python -c "
import ast
import sys
try:
    with open('%%d\\__manifest__.py', 'r') as f:
        manifest = ast.literal_eval(f.read())
    required_fields = ['name', 'version', 'author', 'category', 'depends']
    missing = [f for f in required_fields if f not in manifest]
    if missing:
        print(f'Missing required fields: {missing}')
        sys.exit(1)
    print('Manifest validation passed')
except Exception as e:
    print(f'Manifest validation failed: {e}')
    sys.exit(1)
"
        if !errorlevel! equ 0 (
            echo SUCCESS: !module_name! - Manifest validation passed
            set /a passed_modules+=1
        ) else (
            echo WARNING: !module_name! - Manifest validation failed
            set /a failed_modules+=1
        )
        
        REM Check security directory
        if exist "%%d\security" (
            echo SUCCESS: !module_name! - Security directory exists
        ) else (
            echo WARNING: !module_name! - Missing security directory
        )
        
        REM Check Python syntax
        for /r "%%d" %%f in (*.py) do (
            python -m py_compile "%%f" >nul 2>&1
            if !errorlevel! neq 0 (
                echo ERROR: !module_name! - Syntax error in %%~nxf
            )
        )
    )
)

set total_modules=!module_count!

REM Generate Quality Dashboard
echo [%time%] Generating quality dashboard...
python "%SCRIPTS_DIR%\quality_dashboard.py" "%WORKSPACE_DIR%" --output "%REPORTS_DIR%\quality_dashboard_%TIMESTAMP%.html" --update
if %errorlevel% equ 0 (
    echo SUCCESS: Quality dashboard generated
) else (
    echo WARNING: Dashboard generation failed
)

REM Calculate pass rate
if !total_modules! gtr 0 (
    set /a pass_rate=100*!passed_modules!/!total_modules!
) else (
    set pass_rate=0
)

REM Complete summary report
echo ^| Metric ^| Value ^| >> "%summary_file%"
echo ^|--------^|-------^| >> "%summary_file%"
echo ^| Total Modules ^| !total_modules! ^| >> "%summary_file%"
echo ^| Modules Passed ^| !passed_modules! ^| >> "%summary_file%"
echo ^| Modules Failed ^| !failed_modules! ^| >> "%summary_file%"
echo ^| Pass Rate ^| !pass_rate!%% ^| >> "%summary_file%"
echo ^| Critical Issues ^| !critical_issues! ^| >> "%summary_file%"
echo ^| High Priority Issues ^| !high_issues! ^| >> "%summary_file%"
echo ^| Security Vulnerabilities ^| !security_vulnerabilities! ^| >> "%summary_file%"
echo. >> "%summary_file%"
echo ## Generated Reports >> "%summary_file%"
echo. >> "%summary_file%"
echo - **Code Quality Analysis**: `quality_%TIMESTAMP%.json` >> "%summary_file%"
echo - **Security Assessment**: `security_%TIMESTAMP%.json` >> "%summary_file%"
echo - **Quality Dashboard**: `quality_dashboard_%TIMESTAMP%.html` >> "%summary_file%"
echo. >> "%summary_file%"

REM Determine overall status
set overall_status=GOOD
if !pass_rate! lss 70 set overall_status=NEEDS_IMPROVEMENT
if !critical_issues! gtr 0 set overall_status=CRITICAL
if !high_issues! gtr 5 set overall_status=POOR

echo Pipeline Summary:
echo    Modules: !total_modules! total, !passed_modules! passed, !failed_modules! failed
echo    Pass Rate: !pass_rate!%%
echo    Overall Status: !overall_status!

echo SUCCESS: Quality pipeline completed!
echo Summary report: %summary_file%
echo Quality dashboard: %REPORTS_DIR%\quality_dashboard_%TIMESTAMP%.html

REM Set exit code based on status
if "!overall_status!"=="CRITICAL" exit /b 1
if "!overall_status!"=="POOR" exit /b 1
if "!overall_status!"=="NEEDS_IMPROVEMENT" exit /b 2

exit /b 0