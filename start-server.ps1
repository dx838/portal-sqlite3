# 启动服务器的PowerShell脚本

# 设置日志文件
$logFile = "server.log"

# 清除旧日志
if (Test-Path $logFile) {
    Remove-Item $logFile
}

# 启动服务器并将输出重定向到日志文件
Write-Host "正在启动服务器..."
Write-Host "服务器日志将写入: $logFile"
Write-Host "服务器端口: 3001"
Write-Host "访问地址: http://localhost:3001"
Write-Host "按 Ctrl+C 停止服务器"
Write-Host ""

# 启动服务器进程
$process = Start-Process -FilePath "node" -ArgumentList "dist/bin/portal.js" -NoNewWindow -PassThru -RedirectStandardOutput $logFile -RedirectStandardError $logFile

# 显示日志输出
Write-Host "服务器启动中..."
Write-Host ""
Start-Sleep -Seconds 2

# 实时显示日志
Get-Content $logFile -Wait

# 等待用户按任意键停止服务器
Write-Host ""
Write-Host "按任意键停止服务器..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# 停止服务器进程
Write-Host "正在停止服务器..."
Stop-Process -Id $process.Id -Force
Write-Host "服务器已停止"