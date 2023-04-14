# Invoke-CommandInDesktopPackage

You can execute commands in the context of an AppX Package to gain access to it's virtualized resources (example virtualized registry keys or files)

### Docs

https://learn.microsoft.com/en-us/powershell/module/appx/invoke-commandindesktoppackage?view=windowsserver2022-ps

### Example

The `Invoke-CommandInDesktopPackage` cmdlet requires 3 mandatory arguments: `-AppId`, `-Command` and `-PackageFamilyName`.

- The `-Command` falg can be any command we want to excute.
- In order to obtain the `PackageFamilyName` we can execute `Get-AppxPackage` with the package name. For example we can for the `Calculator` package:

```powershell
Get-AppxPackage *calc*

Name              : Microsoft.WindowsCalculator
Publisher         : CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US
Architecture      : X64
ResourceId        :
Version           : 11.2210.0.0
PackageFullName   : Microsoft.WindowsCalculator_11.2210.0.0_x64__8wekyb3d8bbwe
InstallLocation   : C:\Program Files\WindowsApps\Microsoft.WindowsCalculator_11.2210.0.0_x64__8wekyb3d8bbwe
IsFramework       : False
PackageFamilyName : Microsoft.WindowsCalculator_8wekyb3d8bbwe
PublisherId       : 8wekyb3d8bbwe
IsResourcePackage : False
IsBundle          : False
IsDevelopmentMode : False
NonRemovable      : False
Dependencies      : {Microsoft.UI.Xaml.2.8_8.2212.15002.0_x64__8wekyb3d8bbwe, Microsoft.NET.Native.Framework.2.2_2.2.29512.0_x64__8wekyb3d8bbwe,
                    Microsoft.NET.Native.Runtime.2.2_2.2.28604.0_x64__8wekyb3d8bbwe, Microsoft.VCLibs.140.00_14.0.30704.0_x64__8wekyb3d8bbwe...}
IsPartiallyStaged : False
SignatureKind     : Store
Status            : Ok
```

- To obtain the `AppId` we need a to query the application manifest. We can do so by using the `Get-AppxPackageManifest` cmdlet and providing it with the `PackageFullName`

```powershell
$(Get-AppxPackageManifest $(Get-AppxPackage *calc*).PackageFullName).Package.Applications.Application.Id
```

Merging all of this and the final query will look like this

```powershell
Get-AppxPackage *calc* | % { Invoke-CommandInDesktopPackage -Command cmd.exe -PreventBreakaway -PackageFamilyName $_.PackageFamilyName -AppId $((Get-AppxPackageManifest $_.PackageFullName).Package.Applications.Application.id) }
```

This new process will have some additional attributes in it's token:

- `WIN://SYSAPPID`
- `WIN://PKG`
- `WIN://PKGHOSTID`

![image](https://user-images.githubusercontent.com/8741929/232060829-b3837033-ae76-42c1-be1e-f71198f582fa.png)
