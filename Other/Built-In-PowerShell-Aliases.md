# PowerShell Default Aliases

## Summary

This documents list PowerShell 7/5 default aliases as well as some additions and changes introduced in PowerShell 7 aliases.

You can obtain the alias list by running the command `Get-Alias` from a PowerShell command line or you can check the `System.Management.Automation.dll` and the file `InitialSessionState.cs`

- References:
  - https://github.com/PowerShell/PowerShell/blob/master/src/System.Management.Automation/engine/InitialSessionState.cs#L4565-L4730
  - https://twitter.com/nas_bench/status/1649853976706269188

### PowerShell 5 Built-In Aliases

Last Updated: 22/04/2023

```yml
- ("?", "Where-Object")
- ("%", "ForEach-Object")
- ("ac", "Add-Content")
- ("asnp", "Add-PSSnapIn")
- ("cat", "Get-Content")
- ("cd", "Set-Location")
- ("chdir", "Set-Location")
- ("clc", "Clear-Content")
- ("clear", "Clear-Host")
- ("clhy", "Clear-History")
- ("cli", "Clear-Item")
- ("clp", "Clear-ItemProperty")
- ("cls", "Clear-Host")
- ("clv", "Clear-Variable")
- ("cnsn", "Connect-PSSession")
- ("compare", "Compare-Object")
- ("copy", "Copy-Item")
- ("cp", "Copy-Item")
- ("cpi", "Copy-Item")
- ("cpp", "Copy-ItemProperty")
- ("curl", "Invoke-WebRequest")
- ("cvpa", "Convert-Path")
- ("dbp", "Disable-PSBreakpoint")
- ("del", "Remove-Item")
- ("diff", "Compare-Object")
- ("dir", "Get-ChildItem")
- ("dnsn", "Disconnect-PSSession")
- ("ebp", "Enable-PSBreakpoint")
- ("echo", "Write-Output")
- ("epal", "Export-Alias")
- ("epcsv", "Export-Csv")
- ("epsn", "Export-PSSession")
- ("erase", "Remove-Item")
- ("etsn", "Enter-PSSession")
- ("exsn", "Exit-PSSession")
- ("fc", "Format-Custom")
- ("fl", "Format-List")
- ("foreach", "ForEach-Object")
- ("ft", "Format-Table")
- ("fw", "Format-Wide")
- ("gal", "Get-Alias")
- ("gbp", "Get-PSBreakpoint")
- ("gc", "Get-Content")
- ("gci", "Get-ChildItem")
- ("gcm", "Get-Command")
- ("gcs", "Get-PSCallStack")
- ("gdr", "Get-PSDrive")
- ("ghy", "Get-History")
- ("gi", "Get-Item")
- ("gjb", "Get-Job")
- ("gl", "Get-Location")
- ("gm", "Get-Member")
- ("gmo", "Get-Module")
- ("gp", "Get-ItemProperty")
- ("gps", "Get-Process")
- ("gpv", "Get-ItemPropertyValue")
- ("group", "Group-Object")
- ("gsn", "Get-PSSession")
- ("gsnp", "Get-PSSnapIn")
- ("gsv", "Get-Service")
- ("gu", "Get-Unique")
- ("gv", "Get-Variable")
- ("gwmi", "Get-WmiObject")
- ("h", "Get-History")
- ("history", "Get-History")
- ("icm", "Invoke-Command")
- ("iex", "Invoke-Expression")
- ("ihy", "Invoke-History")
- ("ii", "Invoke-Item")
- ("ipal", "Import-Alias")
- ("ipcsv", "Import-Csv")
- ("ipmo", "Import-Module")
- ("ipsn", "Import-PSSession")
- ("irm", "Invoke-RestMethod")
- ("ise", "powershell_ise.exe")
- ("iwmi", "Invoke-WMIMethod")
- ("iwr", "Invoke-WebRequest")
- ("kill", "Stop-Process")
- ("lp", "Out-Printer")
- ("ls", "Get-ChildItem")
- ("man", "help")
- ("md", "mkdir")
- ("measure", "Measure-Object")
- ("mi", "Move-Item")
- ("mount", "New-PSDrive")
- ("move", "Move-Item")
- ("mp", "Move-ItemProperty")
- ("mv", "Move-Item")
- ("nal", "New-Alias")
- ("ndr", "New-PSDrive")
- ("ni", "New-Item")
- ("nmo", "New-Module")
- ("npssc", "New-PSSessionConfigurationFile")
- ("nsn", "New-PSSession")
- ("nv", "New-Variable")
- ("ogv", "Out-GridView")
- ("oh", "Out-Host")
- ("popd", "Pop-Location")
- ("ps", "Get-Process")
- ("pushd", "Push-Location")
- ("pwd", "Get-Location")
- ("r", "Invoke-History")
- ("rbp", "Remove-PSBreakpoint")
- ("rcjb", "Receive-Job")
- ("rcsn", "Receive-PSSession")
- ("rd", "Remove-Item")
- ("rdr", "Remove-PSDrive")
- ("ren", "Rename-Item")
- ("ri", "Remove-Item")
- ("rjb", "Remove-Job")
- ("rm", "Remove-Item")
- ("rmdir", "Remove-Item")
- ("rmo", "Remove-Module")
- ("rni", "Rename-Item")
- ("rnp", "Rename-ItemProperty")
- ("rp", "Remove-ItemProperty")
- ("rsn", "Remove-PSSession")
- ("rsnp", "Remove-PSSnapin")
- ("rujb", "Resume-Job")
- ("rv", "Remove-Variable")
- ("rvpa", "Resolve-Path")
- ("rwmi", "Remove-WMIObject")
- ("sajb", "Start-Job")
- ("sal", "Set-Alias")
- ("saps", "Start-Process")
- ("sasv", "Start-Service")
- ("sbp", "Set-PSBreakpoint")
- ("sc", "Set-Content")
- ("select", "Select-Object")
- ("set", "Set-Variable")
- ("shcm", "Show-Command")
- ("si", "Set-Item")
- ("sl", "Set-Location")
- ("sleep", "Start-Sleep")
- ("sls", "Select-String")
- ("sort", "Sort-Object")
- ("sp", "Set-ItemProperty")
- ("spjb", "Stop-Job")
- ("spps", "Stop-Process")
- ("spsv", "Stop-Service")
- ("start", "Start-Process")
- ("sujb", "Suspend-Job")
- ("sv", "Set-Variable")
- ("swmi", "Set-WMIInstance")
- ("tee", "Tee-Object")
- ("trcm", "Trace-Command")
- ("type", "Get-Content")
- ("wget", "Invoke-WebRequest")
- ("where", "Where-Object")
- ("wjb", "Wait-Job")
- ("write", "Write-Output")
```

### PowerShell 7 Built-In Aliases

Last Updated: 22/04/2023


```yml
- ("?", "Where-Object")
- ("%", "ForEach-Object")
- ("ac", "Add-Content")
- ("cat", "Get-Content")
- ("cd", "Set-Location")
- ("chdir", "Set-Location")
- ("clc", "Clear-Content")
- ("clear", "Clear-Host")
- ("clhy", "Clear-History")
- ("cli", "Clear-Item")
- ("clp", "Clear-ItemProperty")
- ("cls", "Clear-Host")
- ("clv", "Clear-Variable")
- ("cnsn", "Connect-PSSession")
- ("compare", "Compare-Object")
- ("copy", "Copy-Item")
- ("cp", "Copy-Item")
- ("cpi", "Copy-Item")
- ("cpp", "Copy-ItemProperty")
- ("cvpa", "Convert-Path")
- ("dbp", "Disable-PSBreakpoint")
- ("del", "Remove-Item")
- ("diff", "Compare-Object")
- ("dir", "Get-ChildItem")
- ("dnsn", "Disconnect-PSSession")
- ("ebp", "Enable-PSBreakpoint")
- ("echo", "Write-Output")
- ("epal", "Export-Alias")
- ("epcsv", "Export-Csv")
- ("epsn", "Export-PSSession")
- ("erase", "Remove-Item")
- ("etsn", "Enter-PSSession")
- ("exsn", "Exit-PSSession")
- ("fc", "Format-Custom")
- ("fl", "Format-List")
- ("foreach", "ForEach-Object")
- ("ft", "Format-Table")
- ("fw", "Format-Wide")
- ("gal", "Get-Alias")
- ("gbp", "Get-PSBreakpoint")
- ("gc", "Get-Content")
- ("gci", "Get-ChildItem")
- ("gcm", "Get-Command")
- ("gcs", "Get-PSCallStack")
- ("gdr", "Get-PSDrive")
- ("gerr", "Get-Error")
- ("ghy", "Get-History")
- ("gi", "Get-Item")
- ("gjb", "Get-Job")
- ("gl", "Get-Location")
- ("gm", "Get-Member")
- ("gmo", "Get-Module")
- ("gp", "Get-ItemProperty")
- ("gps", "Get-Process")
- ("gpv", "Get-ItemPropertyValue")
- ("group", "Group-Object")
- ("gsn", "Get-PSSession")
- ("gsv", "Get-Service")
- ("gu", "Get-Unique")
- ("gv", "Get-Variable")
- ("gwmi", "Get-WmiObject")
- ("h", "Get-History")
- ("history", "Get-History")
- ("icm", "Invoke-Command")
- ("iex", "Invoke-Expression")
- ("ihy", "Invoke-History")
- ("ii", "Invoke-Item")
- ("ipal", "Import-Alias")
- ("ipcsv", "Import-Csv")
- ("ipmo", "Import-Module")
- ("ipsn", "Import-PSSession")
- ("irm", "Invoke-RestMethod")
- ("ise", "powershell_ise.exe")
- ("iwmi", "Invoke-WMIMethod")
- ("iwr", "Invoke-WebRequest")
- ("kill", "Stop-Process")
- ("ls", "Get-ChildItem")
- ("man", "help")
- ("md", "mkdir")
- ("measure", "Measure-Object")
- ("mi", "Move-Item")
- ("mount", "New-PSDrive")
- ("move", "Move-Item")
- ("mp", "Move-ItemProperty")
- ("mv", "Move-Item")
- ("nal", "New-Alias")
- ("ndr", "New-PSDrive")
- ("ni", "New-Item")
- ("nmo", "New-Module")
- ("npssc", "New-PSSessionConfigurationFile")
- ("nsn", "New-PSSession")
- ("nv", "New-Variable")
- ("ogv", "Out-GridView")
- ("oh", "Out-Host")
- ("popd", "Pop-Location")
- ("ps", "Get-Process")
- ("pushd", "Push-Location")
- ("pwd", "Get-Location")
- ("r", "Invoke-History")
- ("rbp", "Remove-PSBreakpoint")
- ("rcjb", "Receive-Job")
- ("rcsn", "Receive-PSSession")
- ("rd", "Remove-Item")
- ("rdr", "Remove-PSDrive")
- ("ren", "Rename-Item")
- ("ri", "Remove-Item")
- ("rjb", "Remove-Job")
- ("rm", "Remove-Item")
- ("rmdir", "Remove-Item")
- ("rmo", "Remove-Module")
- ("rni", "Rename-Item")
- ("rnp", "Rename-ItemProperty")
- ("rp", "Remove-ItemProperty")
- ("rsn", "Remove-PSSession")
- ("rujb", "Resume-Job")
- ("rv", "Remove-Variable")
- ("rvpa", "Resolve-Path")
- ("rwmi", "Remove-WMIObject")
- ("sajb", "Start-Job")
- ("sal", "Set-Alias")
- ("saps", "Start-Process")
- ("sasv", "Start-Service")
- ("sbp", "Set-PSBreakpoint")
- ("sc", "Set-Content")
- ("select", "Select-Object")
- ("set", "Set-Variable")
- ("shcm", "Show-Command")
- ("si", "Set-Item")
- ("sl", "Set-Location")
- ("sleep", "Start-Sleep")
- ("sls", "Select-String")
- ("sort", "Sort-Object")
- ("sp", "Set-ItemProperty")
- ("spjb", "Stop-Job")
- ("spps", "Stop-Process")
- ("spsv", "Stop-Service")
- ("start", "Start-Process")
- ("sujb", "Suspend-Job")
- ("sv", "Set-Variable")
- ("swmi", "Set-WMIInstance")
- ("tee", "Tee-Object")
- ("trcm", "Trace-Command")
- ("type", "Get-Content")
- ("where", "Where-Object")
- ("wjb", "Wait-Job")
- ("write", "Write-Output")
```

## Interesting Changes

- The Aliases `wget` and `curl` that were mapping to `Invoke-WebRequest` have been [removed](https://github.com/PowerShell/PowerShell/pull/5268/files#diff-ad3fd038bf04bb095940b4786d074a68d6c310f623bdd7cfe8f60fc7775a495aL4787-L4792) from PowerShell 7. The only one left is the `iwr`
- New alias added to PowerShell 7 `gerr` mapping to the new `Get-Error` function
- The following aliases from PowerShell 5 were removed in PowerShell 7:
  - `asnp` -> `Add-PSSnapIn`
  - `gsnp` -> `Get-PSSnapIn`
  - `rsnp` -> `Remove-PSSnapin`
  - `lp` -> `Out-Printer`
