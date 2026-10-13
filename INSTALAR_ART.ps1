param(
    [Parameter(Mandatory=$true)][string]$DestinoArt,
    [Parameter(Mandatory=$true)][string[]]$Codigos,
    [switch]$Simular,
    [switch]$Substituir
)
$artArguments = @((Join-Path $PSScriptRoot 'tools/install_art.py'), '--art-dir', $DestinoArt, '--ids') + $Codigos
if ($Simular) { $artArguments += '--dry-run' }
if ($Substituir) { $artArguments += '--overwrite' }
& python @artArguments
exit $LASTEXITCODE
