param([string]$EvidenceName)
$settings = Get-Content -Raw -LiteralPath './supplementary/approved/settings.json' | ConvertFrom-Json
$argv = @($settings.preflight_command[1..($settings.preflight_command.Count - 2)])
$argv[[array]::IndexOf($argv, '--evidence')+1] = Join-Path $PWD ('supplementary/' + $EvidenceName + '.json')
$argv[[array]::IndexOf($argv, '--helper-root')+1] = Join-Path $PWD 'supplementary/helpers'
$argv[[array]::IndexOf($argv, '--probe-helper-path')+1] = 'supplementary/helpers/runtime.py'
$argv += @('check', '--', (Join-Path $PWD 'feg_setup.py'), (Join-Path $PWD 'feg_example_lyap.ipynb'))
& $settings.python @argv 2>&1 | Tee-Object -FilePath ('./supplementary/' + $EvidenceName + '-console.txt')
exit $LASTEXITCODE
