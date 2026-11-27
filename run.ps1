# Sobe o Flowise localmente com as variáveis do .env
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

# Node.js 24 é exigido pelo Flowise 3.1.4
try { $nodeVer = (node -v) } catch { $nodeVer = $null }
if (-not $nodeVer) { Write-Host 'Node.js não encontrado. Instale o Node.js 24 LTS: https://nodejs.org' -ForegroundColor Red; exit 1 }
if ([int]($nodeVer.TrimStart('v').Split('.')[0]) -lt 24) { Write-Host "Node.js $nodeVer encontrado, mas o Flowise exige a versão 24." -ForegroundColor Red; exit 1 }

if ($PSScriptRoot -like '*OneDrive*') {
    Write-Host 'Atenção: o projeto está dentro do OneDrive. Mova para fora (ex.: C:\GitHub) para evitar erros EBUSY/EPERM.' -ForegroundColor Yellow
}

if (-not (Test-Path .env)) { Write-Host 'Crie o arquivo .env antes. Veja o README.' -ForegroundColor Red; exit 1 }

# Carrega o .env (aceita valores com ou sem aspas)
Get-Content .env | ForEach-Object {
    $linha = $_.Trim()
    if ($linha -and -not $linha.StartsWith('#') -and $linha.Contains('=')) {
        $nome, $valor = $linha.Split('=', 2)
        $valor = $valor.Trim()
        if ($valor.Length -ge 2 -and (($valor[0] -eq "'" -and $valor[-1] -eq "'") -or ($valor[0] -eq '"' -and $valor[-1] -eq '"'))) {
            $valor = $valor.Substring(1, $valor.Length - 2)
        }
        [Environment]::SetEnvironmentVariable($nome.Trim(), $valor, 'Process')
    }
}

# Instala o Flowise na pasta do projeto (só na primeira vez)
if (-not (Test-Path node_modules\.bin\flowise.cmd)) {
    Write-Host 'Instalando Flowise 3.1.4, a primeira vez demora alguns minutos...'
    # --ignore-scripts: não compila pacotes nativos que o Flowise não usa (ex.: better-sqlite3)
    npm install --no-fund --no-audit --ignore-scripts --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 flowise@3.1.4
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path node_modules\.bin\flowise.cmd)) {
        Write-Host ''
        Write-Host 'A instalação do Flowise falhou (veja o erro acima).' -ForegroundColor Red
        Write-Host 'Apague a pasta node_modules e rode o run.bat de novo.' -ForegroundColor Yellow
        exit 1
    }
    # O banco local do Flowise (SQLite) precisa do binário do sqlite3, que vem pronto para Windows
    Write-Host 'Preparando o SQLite (banco local do Flowise)...'
    # Em versões novas do npm, scripts de instalação precisam ser aprovados por pacote
    try { npm install-scripts approve sqlite3 *> $null } catch { }
    npm rebuild sqlite3 --foreground-scripts
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'Falha ao preparar o sqlite3 (veja o erro acima).' -ForegroundColor Red
        exit 1
    }
}

if (-not $env:PORT) { $env:PORT = '3000' }
Write-Host "Flowise em http://localhost:$($env:PORT)" -ForegroundColor Green
& .\node_modules\.bin\flowise.cmd start
