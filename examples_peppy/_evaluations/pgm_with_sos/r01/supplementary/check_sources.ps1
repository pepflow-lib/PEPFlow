param([string]$Evidence)
$settings=Get-Content -Raw -LiteralPath './supplementary/approved/settings.json' | ConvertFrom-Json
$a=@($settings.preflight_command)
$a=$a[1..($a.Count-2)]
for($i=0;$i -lt $a.Count;$i++) {
 if($a[$i] -eq '--evidence'){$a[$i+1]=Join-Path $settings.output_root $Evidence}
 if($a[$i] -eq '--helper-root'){$a[$i+1]=Join-Path $settings.output_root 'supplementary/helpers'}
 if($a[$i] -eq '--probe-helper-path'){$a[$i+1]='supplementary/helpers/runtime.py'}
}
$a+=@('check','--','pgm_setup.py','pgm_example_lyap.ipynb','supplementary/helpers/runtime.py','supplementary/helpers/candidates.py')
& $settings.python $a
exit $LASTEXITCODE
