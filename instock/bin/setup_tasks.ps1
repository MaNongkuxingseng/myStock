$ErrorActionPreference='Stop'
$base='G:\openclaw\workspace\projects\active\myStock\instock\bin'

$tasks = @(
  @{ Name='myStock-Main-1620'; Time='16:20'; Cmd="`"$base\run_job_main_local.bat`"" },
  @{ Name='myStock-Patch-2030'; Time='20:30'; Cmd="`"$base\run_job_patch_local.bat`"" },
  @{ Name='myStock-PreOpen-0840'; Time='08:40'; Cmd="`"$base\run_job_patch_local.bat`"" }
)

foreach($t in $tasks){
  schtasks /Delete /TN $t.Name /F | Out-Null
  schtasks /Create /SC DAILY /TN $t.Name /TR $t.Cmd /ST $t.Time /F | Out-Null
  Write-Host "Created task: $($t.Name) @ $($t.Time)"
}
Write-Host 'All tasks created.'
