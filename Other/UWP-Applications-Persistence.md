# UWP / Packaged Desktop Application Startup Persistence

UWP and Packaged desktop applications have the ability to create startup tasks in order to execute at startup. The information about these tasks aren't stored in one of the known registry keys for startup persistence (ex: Run Keys) and is currently not shown by utilities such as autoruns.

Below is a detailed description on how these tasks work.

Note: Thanks to [James](https://twitter.com/James_inthe_box) and [Adam](https://twitter.com/Hexacorn) for initiating the discussion around this on Twitter.

### Use case (Phone Link)

If we take an example UWP application such as the built-in `Phone Link` app. We can see that this application is listed in the 'Startup Apps' section of task manager.

![image](https://github.com/nasbench/Misc-Research/assets/8741929/f491e4bd-58c9-4bdc-ab66-bf5b6c2a5c57)

But taking a look at the Run key where these apps are usually configured to start we don't seem to find references to it.

![image](https://github.com/nasbench/Misc-Research/assets/8741929/bb877c61-cf48-4252-8041-a958879ce68d)

![image](https://github.com/nasbench/Misc-Research/assets/8741929/fe75cbc1-94b3-469e-b0a6-1514801fcac0)

### Tracing W/ Procmon

To know more, let's take a look with Procmon on how task manager is able to Enable/Disbale these apps from startup.

![image](https://github.com/nasbench/Misc-Research/assets/8741929/63056b3a-5cc2-4775-945a-e0f4fb31c129)

We can see requests being made to `HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\SystemAppData\Microsoft.YourPhone_8wekyb3d8bbwe\YourPhone.Start` which contains the following values.

![image](https://github.com/nasbench/Misc-Research/assets/8741929/97e081ac-96d6-462c-a17c-8bb74ff7817d)

From the naming of the values it indeed seems that this is the location where we can enable or disable these startup tasks. Taking other UWP apps as example we can find similar keys.

- Windows Terminal: `HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\SystemAppData\Microsoft.WindowsTerminal_8wekyb3d8bbwe\StartTerminalOnLoginTask`

- Microsoft Teams: `HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\SystemAppData\MicrosoftTeams_8wekyb3d8bbwe\TeamsStartupTask`

- XBOX App: `HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\SystemAppData\Microsoft.GamingApp_8wekyb3d8bbwe\Xbox.App.Tasks.FullTrustComponent`

While this answer our question how are these applications are able to start at the start of Windows. We still don't know what executables they're going to run or what do the values exactly mean. Let's take a closer look.

### Windows Startup Extension

Scrolling a bit on MSDN we find the following [docuemntation](https://learn.microsoft.com/en-us/uwp/api/windows.applicationmodel.startuptask?view=winrt-22621) about a class called `StartupTask`. Which describe exactly the behaviour that we were just investigating.

![image](https://github.com/nasbench/Misc-Research/assets/8741929/4704848d-0c7e-4707-b286-4bfe293d8d7d)

And a couple of lines down we find this interesting information.

![image](https://github.com/nasbench/Misc-Research/assets/8741929/ea71a6d2-28ca-45d8-90c4-2f984af11c0f)


This tells us that the startup definition is stored inside the manifest. Which luckily for us, it can easily be extracted using a simple PowerShell cmdlet called [Get-AppxPackageManifest](https://learn.microsoft.com/en-us/powershell/module/appx/get-appxpackagemanifest?view=windowsserver2022-ps). So let's do that next.

### Finding The Culprit

Taking the same `Phone Link` UWP app example. We can execute the following command to extract the manifest.

```powershell
(Get-AppxPackage -Name "*phone*" | Get-AppxPackageManifest).InnerXml
```

Looking at the content of the XML, specifically the `StartupTask` we find the following definition. Which indicates that this UWP has a startup task to start at windows Startup.

```xml
<uap5:Extension Category="windows.startupTask">
    <uap5:StartupTask TaskId="YourPhone.Start" Enabled="true" DisplayName="ms-resource:AppName" />
</uap5:Extension>
```

From this output we can conclude that the registry path related to the configuration of an app startup task is in the following format.

```
HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\SystemAppData\<PackageFamilyName>\<TaskId>\`
```

Here are a couple of examples from different applications

- Windows Terminal

```xml
<uap5:Extension Category="windows.startupTask">
    <uap5:StartupTask TaskId="StartTerminalOnLoginTask" Enabled="false" DisplayName="ms-resource:AppName" />
</uap5:Extension>
```

- Microsoft Teams

```xml
<desktop:Extension Category="windows.startupTask" Executable="msteams_autostarter.exe" EntryPoint="Windows.FullTrustApplication">
    <desktop:StartupTask TaskId="TeamsStartupTask" Enabled="true" DisplayName="Microsoft Teams" />
</desktop:Extension>
```

- Xbox Gaming App

```xml
<uap5:Extension Category="windows.startupTask" Executable="XboxPcAppFT.exe" EntryPoint="Windows.FullTrustApplication" uap10:Parameters="/startupLaunch">
    <uap5:StartupTask TaskId="Xbox.App.Tasks.FullTrustComponent" Enabled="false" DisplayName="Xbox App Services" />
</uap5:Extension>
```

### Enumerating All UWP / Packaged Destop Applications Startup Tasks

To enumerate all Startup tasks, I wrote this small PowerShell snippet.

```powershell
$packages = Get-AppxPackage
foreach ($package in $packages) {
    $packageName = $package.Name

    # Data
    $ext = ($package | Get-AppxPackageManifest).package.Applications.Application.Extensions.Extension | Where-Object { $_.Category -eq "windows.startupTask" }
    $task = ($package | Get-AppxPackageManifest).package.Applications.Application.Extensions.Extension.StartupTask
    if ($ext -ne $null -and $ext -ne '') {
        
        $Executable = $ext.Executable
        $EntryPoint = $ext.EntryPoint
        $Parameters = $ext.Parameters
        $TaskId = $task.TaskId
        $Enabled = $task.Enabled
        $DisplayName = $task.DisplayName

        Write-Host "Package Name: $packageName"
            
        if ($Executable -ne $null -and $Executable -ne '') {
            Write-Host "Startup Task Executable: $Executable"
        }
        if ($EntryPoint -ne $null -and $EntryPoint -ne '') {
            Write-Host "Startup Task EntryPoint: $EntryPoint"
        }
        if ($Parameters -ne $null -and $Parameters -ne '') {
            Write-Host "Startup Task Parameters: $Parameters"
        }
        if ($TaskId -ne $null -and $TaskId -ne '') {
            Write-Host "Startup Task ID: $TaskId"
        }
        if ($Enabled -ne $null -and $Enabled -ne '') {
            Write-Host "Startup Task Enabled Status: $Enabled"
        }
        if ($DisplayName -ne $null -and $DisplayName -ne '') {
        Write-Host "Startup Task DisplayName: $DisplayName"
        }
        Write-Host "------------------------"

    }
}
```

Below is the results from my lab setup

```yaml
Package Name: Microsoft.WindowsTerminal
Startup Task ID: StartTerminalOnLoginTask
Startup Task Enabled Status: false
Startup Task DisplayName: ms-resource:AppName

------------------------

Package Name: 91750D7E.Slack
Startup Task Executable: app\Slack.exe
Startup Task EntryPoint: Windows.FullTrustApplication
Startup Task ID: SlackStartup
Startup Task Enabled Status: true
Startup Task DisplayName: Slack

------------------------

Package Name: Microsoft.GamingApp
Startup Task Executable: XboxPcAppFT.exe
Startup Task EntryPoint: Windows.FullTrustApplication
Startup Task Parameters: /startupLaunch
Startup Task ID: Xbox.App.Tasks.FullTrustComponent
Startup Task Enabled Status: false
Startup Task DisplayName: Xbox App Services

------------------------

Package Name: MicrosoftTeams
Startup Task Executable: msteams_autostarter.exe
Startup Task EntryPoint: Windows.FullTrustApplication
Startup Task ID: TeamsStartupTask
Startup Task Enabled Status: true
Startup Task DisplayName: Microsoft Teams

------------------------

Package Name: SpotifyAB.SpotifyMusic
Startup Task Executable: SpotifyStartupTask.exe
Startup Task EntryPoint: Windows.FullTrustApplication
Startup Task ID: Spotify
Startup Task Enabled Status: false
Startup Task DisplayName: Spotify

------------------------

Package Name: Microsoft.SkypeApp
Startup Task Executable: Skype\Skype.exe
Startup Task EntryPoint: Windows.FullTrustApplication
Startup Task ID: SkypeStartup
Startup Task Enabled Status: false
Startup Task DisplayName: Skype

------------------------

Package Name: 5319275A.WhatsAppDesktop
Startup Task Executable: WhatsApp.exe
Startup Task EntryPoint: WhatsApp.App
Startup Task ID: WhatsAppStartupTask
Startup Task Enabled Status: false
Startup Task DisplayName: WhatsApp

------------------------

Package Name: Microsoft.PowerAutomateDesktop
Startup Task Executable: PAD.Console.Host.exe
Startup Task EntryPoint: Windows.FullTrustApplication
Startup Task ID: AutoStartTask
Startup Task Enabled Status: true
Startup Task DisplayName: Power Automate Desktop

------------------------

Package Name: Microsoft.Todos
Startup Task ID: ToDoStartupId
Startup Task Enabled Status: false
Startup Task DisplayName: ms-resource:app_name_ms_todo

------------------------

Package Name: AppUp.IntelGraphicsExperience
Startup Task Executable: GCP.ML.BackgroundSysTray\IGCCTray.exe
Startup Task EntryPoint: Windows.FullTrustApplication
Startup Task ID: GCPStartupId
Startup Task Enabled Status: true
Startup Task DisplayName: Intel® Graphics Command Center Startup Task

------------------------

Package Name: Microsoft.YourPhone
Startup Task ID: YourPhone.Start
Startup Task Enabled Status: true
Startup Task DisplayName: ms-resource:AppName
------------------------
```

### Registry Configration

Information about the state of an application is stored in the registry, inside the `<TaskId>` key. It contains the following values

- `LastDisabledTime` (REG_QWORD): Contains a timestamp of when was the last this startup task was disabled
- `State` (REG_DWORD): Indicates the current state of the task and can hold on the following [values](https://learn.microsoft.com/en-us/uwp/api/windows.applicationmodel.startuptaskstate?view=winrt-22621)
    - 0: The task is disabled.
    - 1: The task was disabled by the user. It can only be re-enabled by the user.	
    - 2: The task is enabled.
    - 3: The task is disabled by the administrator or group policy. Platforms that don't support startup tasks also report DisabledByPolicy.
    - 4: The task is enabled by the administrator or group policy.
- `UserEnabledStartupOnce` (REG_DWORD)