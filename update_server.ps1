# PowerShell скрипт для обновления сервера
Write-Host "Подключение к серверу и обновление бота..." -ForegroundColor Green

# Параметры подключения
$serverIP = "95.215.8.138"
$username = "root"
$password = "sq8Iff0x3eXYL5"

# Создаем SSH сессию
Write-Host "Подключаемся к серверу $serverIP..." -ForegroundColor Yellow
$securePassword = ConvertTo-SecureString $password -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential ($username, $securePassword)

# Выполняем команды на сервере
$commands = @"
echo "=== Обновление проекта на сервере ==="
cd /root/som_lit_bot

echo "Получение последних изменений из GitHub..."
git pull origin main

echo "Перезапуск контейнеров Docker..."
docker-compose down
docker-compose up -d --build

echo "Проверка статуса контейнеров..."
docker ps -a | grep literary

echo "=== Обновление завершено ==="
"@

# Выполняем команды через SSH
$commands | Out-File -FilePath "temp_commands.sh" -Encoding UTF8
try {
    # Используем expect-like подход для передачи пароля
    $sshCommands = @"
#!/usr/bin/expect -f
set timeout 30
spawn ssh root@$serverIP "bash -s"
expect "password:"
send "sq8Iff0x3eXYL5\r"
expect eof
"@

    $sshCommands | Out-File -FilePath "ssh_script.exp" -Encoding UTF8

    # Выполняем команды через SSH с использованием expect
    $result = & "C:\Windows\System32\OpenSSH\ssh.exe" root@$serverIP "bash -s" < temp_commands.sh 2>&1
    Write-Host $result -ForegroundColor Cyan
} catch {
    Write-Host "Ошибка при выполнении команд на сервере: $_" -ForegroundColor Red
} finally {
    Remove-Item -Path "temp_commands.sh" -ErrorAction SilentlyContinue
    Remove-Item -Path "ssh_script.exp" -ErrorAction SilentlyContinue
}

Write-Host "Обновление сервера завершено!" -ForegroundColor Green
