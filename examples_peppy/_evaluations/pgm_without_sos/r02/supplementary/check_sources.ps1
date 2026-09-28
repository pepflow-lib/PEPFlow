param([string]$Evidence, [string[]]$Targets=@('pgm_setup.py','pgm_example_lyap.ipynb','supplementary/helpers/runtime.py','supplementary/helpers/certificate.py'))
$s = Get-Content -LiteralPath './supplementary/approved/settings.json' -Raw | ConvertFrom-Json
$a = @($s.preflight_command | Select-Object -Skip 1)
$a = $a[0..($a.Count-2)]
$a[[array]::IndexOf($a,'--helper-root')+1] = Join-Path $s.output_root 'supplementary/helpers'
$a[[array]::IndexOf($a,'--probe-helper-path')+1] = 'supplementary/helpers/runtime.py'
$a[[array]::IndexOf($a,'--evidence')+1] = Join-Path $s.output_root $Evidence
$a += @('check','--') + $Targets
& $s.python @a
