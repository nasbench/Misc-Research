# Windows Compatibility QUIRKS

> **Note**
>
> The following research is still a work in progress and some of the information might be slightly or perhaps completely inaccurate in some areas.
> Please provide feedback if you find such cases :)

### Introduction

A compatibility QUIRK is feature that allows an application to change its behavior during the execution. In practice its implemented as a boolean value that can affect the code path in a program depending on its state.

Binaries that make use of Application compatibility QUIRKs from the Shim database usually imports one or more of the `QuirkIsEnabled*` style of functions. Here is a list:

```yaml
- QuirkIsEnabled
- QuirkIsEnabled2
- QuirkIsEnabled2Worker
- QuirkIsEnabled3
- QuirkIsEnabled3Worker
- QuirkIsEnabledForPackage
- QuirkIsEnabledForPackage2
- QuirkIsEnabledForPackage2Worker
- QuirkIsEnabledForPackage3
- QuirkIsEnabledForPackage3Worker
- QuirkIsEnabledForPackage4
- QuirkIsEnabledForPackage4Worker
- QuirkIsEnabledForPackageWorker
- QuirkIsEnabledForProcess
- QuirkIsEnabledForProcessWorker
- QuirkIsEnabledWorker
```

Let's take an example from the built-in SHIM database `sysmain.sdb`. Using [Sdb Explorer](https://ericzimmerman.github.io/#!index.md) we can parse the database and see the defined QUIRKS. 

```yaml

QUIRK: XAML.ForcePostParseNameRegistration
    NAME: XAML.ForcePostParseNameRegistration
    FIX_ID: 16c1bc37-c9a9-465f-9a09-7f23ac6ad9cf
    QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
    EDITION: 262143
    QUIRK_COMPONENT_CODE_ID: 2
    QUIRK_CODE_ID: 110
    TELEMETRY_OFF: True
```

> **Note**
>
> To learn more about the structure of a QUIRK and the meaning and possible values of the fields, please give the [Shim-Database-XML-Format](./Shim-Database-XML-Format.md) writeup a read.

The example above define a compatibility quirk named `XAML.ForcePostParseNameRegistration`. I'll explain the fields

- The `QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT` field indicate the status of the QUIRK (enabled, disabled or enabled for specific versions). A value of "0" in this case indicate that this QUIRK is disabled.
- The `EDITION` field indicates on what edition of "OS" is this applied. Currently i've been able to document 18 possible values. These values can be combined with each other. In this case the value `262143` is a combination of the following editions
    - 'UAP'
    - 'DESKTOP'
    - 'MOBILE'
    - 'XBOX'
    - 'TEAM'
    - 'IOT'
    - 'IOTHEADLESS'
    - 'SERVER'
    - 'HOLOGRAPHIC'
    - 'XBOXSRA'
    - 'XBOXERA'
    - '7067329'
    - 'WINDOWSCOREHEADLESS'
- `QUIRK_COMPONENT_CODE_ID` and `QUIRK_CODE_ID` are both and unique identifier for the QUIRK and the QUIRK_COMPONENT and they are used to select a QUIRK via the `QuirkIsEnabled`
- `TELEMETRY` - Currently I don't know the true "purpose" of this value apart from the obvious inference that its related to sending telemetry.

Currently i don't have a good way of finding where a quirk is actually used because contrary to a SHIM definition, a QUIRK doesn't define a specific DLL where its implemented but its actually enumerated when an application invokes the function `QuirkIsEnabled*` (as we can see by events emitted to the respective ETW channel). Fortunately with some QUIRKS there seems to be some kind of a convention on what DLL/Binary is potentially hosting this quirk.

In our example the quirk `XAML.ForcePostParseNameRegistration` starts with the `XAML` prefix. Which is an indication of what this QUIRK might be related to. Looking at XAML related DLLs we can find a couple importing `QuirkIsEnabled` related functions.

```yaml
- Windows.UI.Xaml.dll
- Windows.UI.Xaml.InkControls.dll
- Windows.UI.Xaml.Maps.dll
- Windows.UI.Xaml.Phone.dll
```

Inspecting their functions using IDA and loading Symbols we can see a function with a similar name to the QUIRK defined in `Windows.UI.Xaml.dll` called `CQuirksMode2::QuirkForcePostParseNameRegistration`

![image](https://github.com/nasbench/Misc-Research/assets/8741929/8d80b2d2-596e-4af3-85fb-1688fb64a9c2)

> **Note**
>
> This isn't usually the case as most other QUIRKS implementation i've looked at are implemented directly in other unrelated functions. The name of the QUIRK is only a human readable reference, internally quirks are called via an ID

This function is called from `CCoreServices::ParseXamlWithExistingFrameworkRoot` and its used as part of a condition

![image](https://github.com/nasbench/Misc-Research/assets/8741929/4b38145b-af9c-491a-bbd6-084cc6e9fbf6)

This function basically calls `QuirkIsEnabled` to determine the state of the QUIRK which will return a boolean value that can be used to determine the state of the condition and choose a different path.

The value of the argument passed to `QuirkIsEnabled` is determined based on the QUIRK and its COMPONENT `CODE_ID`. Where the value is a 32 bit DWORD that's the combination of QUIRK_COMPONENT_CODE_ID (higher 16bits) and QUIRK_CODE_ID (lower 16bits).

From our example here are the values

- QUIRK_COMPONENT_CODE_ID = 2
- QUIRK_CODE_ID = 6E

Which in turns gives 0x0002006E that we see being passed on to the function `XamlQuirkIsEnabled` which will in turn call `QuirkIsEnabled`

```c
bool __stdcall CQuirksMode2::QuirkForcePostParseNameRegistration()
{
  if ( CQuirksMode2::m_quirkCacheSuppressions )
    return CQuirksMode2::XamlQuirkIsEnabled((void *)0x2006E);
  InitOnceExecuteOnce(&InitOnce, (PINIT_ONCE_FN)CQuirksMode2::InitOnceCallback, &dword_10D54158, 0);
  return *(_BYTE *)dword_10D54158 >> 7;
}
```

```c
bool __thiscall CQuirksMode2::XamlQuirkIsEnabled(void *quirk)
{
  return !CQuirksMode2::m_quirksDisabledForProcess
      && (CQuirksMode2::m_tlsXamlPresenter == -1 || !TlsGetValue(CQuirksMode2::m_tlsXamlPresenter))
      && QuirkIsEnabled(quirk);
}
```

### Another Example (DXGI.DLL)

Just to illustrate the concept a bit further and show that its not consistent. Let's take a look at another QUIRK and how its defined.

From `sysmain.sdb` we have the following QUIRKS

```yaml

QUIRK: DXGI.Quirk5601080x1920As720x1280
    NAME: DXGI.Quirk1080x1920As720x1280
    FIX_ID: b5939a12-8764-4576-8ec0-8e038666d313
    QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
    EDITION: 81940
    QUIRK_COMPONENT_CODE_ID: 16
    QUIRK_CODE_ID: 0
    TELEMETRY_OFF: True


QUIRK: DXGI.Quirk540x960As480x800
    NAME: DXGI.Quirk540x960As480x800
    FIX_ID: f1d2af20-8df4-4478-9033-57ed1d90f3ff
    QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
    EDITION: 81940
    QUIRK_COMPONENT_CODE_ID: 16
    QUIRK_CODE_ID: 1
    TELEMETRY_OFF: True


QUIRK: DXGI.Quirk1440x2560As720x1280
    NAME: DXGI.Quirk1440x2560As720x1280
    FIX_ID: 688bc727-a361-4647-ba69-c2bc6e3caafa
    QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
    EDITION: 81940
    QUIRK_COMPONENT_CODE_ID: 16
    QUIRK_CODE_ID: 6
    TELEMETRY_OFF: True
```

Following the same logic as before we can see the prefix `DXGI` which "implies" that these are somewhat define in DXGI dll. Looking for DLL with that name that import the `QuirkIsEnabled` function. We find `dxgi.dll`

Importing the binary into IDA and loading symbols to look for function names that are similar to the QUIRK names will not yield positive results. (Which implies that its not the same as I said)

Doing an xref on the `QuirkIsEnabled` function we can find a function called `ApplyCompatResolutionQuirking` that does the following

```c
  if ( *a2 == 1080 && *a3 == 1920 && QuirkIsEnabled(0x100000) )
    goto LABEL_31;
  if ( *a2 == 540 && *a3 == 960 && QuirkIsEnabled(0x100001) )
  {
    *a2 = 480;
    *a3 = 800;
    return;
  }
  if ( *a2 == 1440 && *a3 == 2560 && QuirkIsEnabled(0x100006) )
  {
LABEL_31:
    *a2 = 720;
    *a3 = 1280;
  }
```

The first thing we notice is that the variable are being compared to similar values in the name of the quirk indicating some resolution settings (as the quirk suggests). Converting the values being passed to `QuirkIsEnabled` we find that indeed these are the quirk being passed.

Example `DXGI.Quirk1440x2560As720x1280` defines `QUIRK_COMPONENT_CODE_ID: 10` and `QUIRK_CODE_ID: 6` which give a value of `0x100006`.

### QUIRK ETW Debug Event

Calls to `QuirkIsEnabled` and related QUIRK functions will end up in `Kernel32.dll` (after being redirect from `api-ms-win-core-quirks-l1-1-0.dll`, `api-ms-win-core-quirks-l1-1-1.dll`, `KernelBase.dll` and `ext-ms-win-kernel32-quirks-l1-1-0.dll`).

Before being able to check for the status of a QUIRK the ``QuirksTable`` structure needs to be initialized. If its not the case `Kernel32.dll` will call `CptpQuirksInitOnce` which will perform the heavy lifting and eventually wil end up calling `NtApphelpCacheControl`.

The `CptpQuirksInitOnce` function also execute a couple more things that are interesting from a debug perspective

- Register an instance of an ETW provider (Microsoft-Windows-Application-Experience - {EEF54E71-0661-422D-9A98-82FD4940B820}) and enables the EventID 2005

```c
if ( (int)EtwEventRegister(&AE_LOG, 0i64, 0i64, &QuirksEtwProvider) < 0 )
    {
        QuirksEtwProvider = 0i64;
        v5 = 0;
    }
else
    {
        v5 = (unsigned __int8)EtwEventEnabled(QuirksEtwProvider, &QUIRKS_DEBUG_EVENT);
    }
QuirksEtwEventEnabledCache = v5;
```

If you subscribe to the ETW in question and monitor for this event you'll see something like this. Indicating which the package that made the request and the state of the QUIRK

```json
{
    "EventHeader": {
        "Size": 330, 
        "HeaderType": 0, 
        "Flags": 576, 
        "EventProperty": 0, 
        "ThreadId": 61384, 
        "ProcessId": 52316, 
        "TimeStamp": 100504502030762786, 
        "ProviderId": "{EEF54E71-0661-422D-9A98-82FD4940B820}", 
        "EventDescriptor": {
            "Id": 2005, 
            "Version": 0, 
            "Channel": 0, 
            "Level": 4, 
            "Opcode": 0, 
            "Task": 0, 
            "Keyword": 512}, 
            "KernelTime": 0, 
            "UserTime": 0, 
            "ActivityId": "{00000000-0000-0000-0000-000000000000}"
        }, 
        "Task Name": "MICROSOFT-WINDOWS-APPLICATION-EXPERIENCE", 
        "ProcessId": "52316", 
        "QuirkId": "131177", 
        "QuirkName": "XAML.ResourceSetRootInstanceWithTargetResourceDictionary", 
        "CommandLine": "", 
        "Enabled": "1", 
        "Forced": "0", 
        "PackageFullName": "Microsoft.XboxGamingOverlay_6.123.11012.0_x64__8wekyb3d8bbwe", 
        "ApplicationUserModelId": "", 
        "Description": "%3 "
}
```

- Initialize debug mode by checking if the current application is being debugged and reading the value `Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Quirks\<packageFullName>` (Still a work in progress on what it actually does)

- Initialize an internal variable called `QuirksGlobalOverride` by reading the value of the environement variable `QUIRKS_FORCE_RESULT`. If this is not 0 this will evaluate `QuirksGlobalOverride` to true internally. Which will change certain behaviors (Still a work in progress on what it actually does)


### Appendix

The following is a list of DLLs and binaries that import quirk related functions

<details>
    <summary>Expand Details</summary>

```yaml
- C:\Windows\System32\ACPBackgroundManagerPolicy.dll
- C:\Windows\System32\ActivationManager.dll
- C:\Windows\System32\AcWinRT.dll
- C:\Windows\System32\AppXDeploymentExtensions.onecore.dll
- C:\Windows\System32\AppXDeploymentServer.dll
- C:\Windows\System32\BackgroundMediaPolicy.dll
- C:\Windows\System32\bisrv.dll
- C:\Windows\System32\biwinrt.dll
- C:\Windows\System32\CapabilityAccessManager.dll
- C:\Windows\System32\combase.dll
- C:\Windows\System32\CompPkgSup.dll
- C:\Windows\System32\CoreUIComponents.dll
- C:\Windows\System32\d3d11.dll
- C:\Windows\System32\D3D12Core.dll
- C:\Windows\System32\dafBth.dll
- C:\Windows\System32\dxgi.dll
- C:\Windows\System32\ExecModelClient.dll
- C:\Windows\System32\Geolocation.dll
- C:\Windows\System32\iertutil.dll
- C:\Windows\System32\InputHost.dll
- C:\Windows\System32\LockHostingFramework.dll
- C:\Windows\System32\MFCaptureEngine.dll
- C:\Windows\System32\modernexecserver.dll
- C:\Windows\System32\msftedit.dll
- C:\Windows\System32\mshtml.dll
- C:\Windows\System32\ole32.dll
- C:\Windows\System32\PsmServiceExtHost.dll
- C:\Windows\System32\rmclient.dll
- C:\Windows\System32\SebBackgroundManagerPolicy.dll
- C:\Windows\System32\SHCore.dll
- C:\Windows\System32\SmartCardBackgroundPolicy.dll
- C:\Windows\System32\StartTileData.dll
- C:\Windows\System32\threadpoolwinrt.dll
- C:\Windows\System32\twinapi.appcore.dll
- C:\Windows\System32\twinui.dll
- C:\Windows\System32\twinui.pcshell.dll
- C:\Windows\System32\uDWM.dll
- C:\Windows\System32\UserDataPlatformHelperUtil.dll
- C:\Windows\System32\WindowManagement.dll
- C:\Windows\System32\Windows.ApplicationModel.dll
- C:\Windows\System32\Windows.Devices.Bluetooth.dll
- C:\Windows\System32\Windows.Devices.Sensors.dll
- C:\Windows\System32\Windows.Gaming.Input.dll
- C:\Windows\System32\Windows.Globalization.Fontgroups.dll
- C:\Windows\System32\Windows.Internal.Devices.Bluetooth.dll
- C:\Windows\System32\Windows.Media.MediaControl.dll
- C:\Windows\System32\Windows.Networking.Connectivity.dll
- C:\Windows\System32\Windows.Networking.dll
- C:\Windows\System32\Windows.Networking.HostName.dll
- C:\Windows\System32\Windows.Perception.Stub.dll
- C:\Windows\System32\windows.storage.dll
- C:\Windows\System32\Windows.System.Launcher.dll
- C:\Windows\System32\Windows.System.Profile.SystemId.dll
- C:\Windows\System32\Windows.UI.Core.TextInput.dll
- C:\Windows\System32\Windows.UI.dll
- C:\Windows\System32\Windows.UI.Xaml.dll
- C:\Windows\System32\Windows.UI.Xaml.InkControls.dll
- C:\Windows\System32\Windows.UI.Xaml.Maps.dll
- C:\Windows\System32\Windows.UI.Xaml.Phone.dll
- C:\Windows\System32\Windows.Web.dll
- C:\Windows\System32\wpnapps.dll
- C:\Windows\System32\wpnclient.dll
- C:\Windows\System32\WWAHost.exe
- C:\Windows\System32\XInput1_4.dll
- C:\Windows\SysWOW64\ActivationManager.dll
- C:\Windows\SysWOW64\AcWinRT.dll
- C:\Windows\SysWOW64\BackgroundMediaPolicy.dll
- C:\Windows\SysWOW64\biwinrt.dll
- C:\Windows\SysWOW64\combase.dll
- C:\Windows\SysWOW64\CompPkgSup.dll
- C:\Windows\SysWOW64\CoreUIComponents.dll
- C:\Windows\SysWOW64\d3d11.dll
- C:\Windows\SysWOW64\D3D12Core.dll
- C:\Windows\SysWOW64\dxgi.dll
- C:\Windows\SysWOW64\ExecModelClient.dll
- C:\Windows\SysWOW64\Geolocation.dll
- C:\Windows\SysWOW64\iertutil.dll
- C:\Windows\SysWOW64\InputHost.dll
- C:\Windows\SysWOW64\MFCaptureEngine.dll
- C:\Windows\SysWOW64\msftedit.dll
- C:\Windows\SysWOW64\mshtml.dll
- C:\Windows\SysWOW64\ole32.dll
- C:\Windows\SysWOW64\rmclient.dll
- C:\Windows\SysWOW64\SHCore.dll
- C:\Windows\SysWOW64\threadpoolwinrt.dll
- C:\Windows\SysWOW64\twinapi.appcore.dll
- C:\Windows\SysWOW64\twinui.dll
- C:\Windows\SysWOW64\UserDataPlatformHelperUtil.dll
- C:\Windows\SysWOW64\Windows.ApplicationModel.dll
- C:\Windows\SysWOW64\Windows.Devices.Bluetooth.dll
- C:\Windows\SysWOW64\Windows.Devices.Sensors.dll
- C:\Windows\SysWOW64\Windows.Gaming.Input.dll
- C:\Windows\SysWOW64\Windows.Globalization.Fontgroups.dll
- C:\Windows\SysWOW64\Windows.Internal.Devices.Bluetooth.dll
- C:\Windows\SysWOW64\Windows.Media.MediaControl.dll
- C:\Windows\SysWOW64\Windows.Networking.Connectivity.dll
- C:\Windows\SysWOW64\Windows.Networking.dll
- C:\Windows\SysWOW64\Windows.Networking.HostName.dll
- C:\Windows\SysWOW64\Windows.Perception.Stub.dll
- C:\Windows\SysWOW64\windows.storage.dll
- C:\Windows\SysWOW64\Windows.System.Launcher.dll
- C:\Windows\SysWOW64\Windows.System.Profile.SystemId.dll
- C:\Windows\SysWOW64\Windows.UI.Core.TextInput.dll
- C:\Windows\SysWOW64\Windows.UI.dll
- C:\Windows\SysWOW64\Windows.UI.Xaml.dll
- C:\Windows\SysWOW64\Windows.UI.Xaml.InkControls.dll
- C:\Windows\SysWOW64\Windows.UI.Xaml.Maps.dll
- C:\Windows\SysWOW64\Windows.UI.Xaml.Phone.dll
- C:\Windows\SysWOW64\Windows.Web.dll
- C:\Windows\SysWOW64\wpnapps.dll
- C:\Windows\SysWOW64\wpnclient.dll
- C:\Windows\SysWOW64\WWAHost.exe
- C:\Windows\SysWOW64\XInput1_4.dll
```

</details>

- The following is a list of built-in QUIRKS as of Windows version 22621.3007

<details>
    <summary>Expand Details</summary>

```yaml
QUIRK: COMPAT.OlderThanWin7
   NAME: COMPAT.OlderThanWin7
   FIX_ID: ac4e2db8-649e-42d6-9a04-4d909397a64b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688854155231232
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 0
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: COMPAT.OlderThanWin8
   NAME: COMPAT.OlderThanWin8
   FIX_ID: f549022d-0e51-45c3-a63e-6ea065731d32
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688858450198528
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 0
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: COMPAT.OlderThanBlue
   NAME: COMPAT.OlderThanBlue
   FIX_ID: b582a5aa-176b-47cb-9f8a-82e6922613bf
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 0
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: COMPAT.OlderThanThresholdAllEditions
   NAME: COMPAT.OlderThanThresholdAllEditions
   FIX_ID: 7caafdf1-1178-4d4f-9204-e95cf9ff0735
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 0
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: COMPAT.OlderThanThresholdDesktopOnly
   NAME: COMPAT.OlderThanThresholdDesktopOnly
   FIX_ID: d9c28d15-426b-454c-95b5-dcc0ca8a2331
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 0
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: COMPAT.OlderThanThresholdMobileOnly
   NAME: COMPAT.OlderThanThresholdMobileOnly
   FIX_ID: d3e5b989-027d-47fc-8101-095386dd048f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 0
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: COMPAT.OlderThanThresholdMobileAndIot
   NAME: COMPAT.OlderThanThresholdMobileAndIot
   FIX_ID: f0f2b4db-4141-46cf-b024-f0dc073f9ca6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 82068
   QUIRK_COMPONENT_CODE_ID: 0
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: COMPAT.ForceEnabledDesktopOnly
   NAME: COMPAT.ForceEnabledDesktopOnly
   FIX_ID: 17a840fd-d3ae-4ee9-8189-dc5b490c8811
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: -1
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 0
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: COMPAT.OlderThanThresholdXboxOnly
   NAME: COMPAT.OlderThanThresholdXboxOnly
   FIX_ID: f58d7c3c-ae23-40cd-a206-aac48bfe9fa5
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 32
   QUIRK_COMPONENT_CODE_ID: 0
   QUIRK_CODE_ID: 8
   TELEMETRY_OFF: True

QUIRK: COMPAT.ForceEnabledXboxOnly
   NAME: COMPAT.ForceEnabledXboxOnly
   FIX_ID: 762bacf2-1453-4d85-82c5-60243be04c57
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: -1
   EDITION: 32
   QUIRK_COMPONENT_CODE_ID: 0
   QUIRK_CODE_ID: 9
   TELEMETRY_OFF: True

QUIRK: COMPAT.ForceEnabledXboxSRAOnly
   NAME: COMPAT.ForceEnabledXboxSRAOnly
   FIX_ID: 2fcf6f68-b3e5-4752-b6ee-b11ce8431dc2
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: -1
   EDITION: 2048
   QUIRK_COMPONENT_CODE_ID: 0
   QUIRK_CODE_ID: 10
   TELEMETRY_OFF: True

QUIRK: COMPAT.ForceEnabledXboxERAOnly
   NAME: COMPAT.ForceEnabledXboxERAOnly
   FIX_ID: 8e595f86-4238-4432-984f-f9d1689c93fb
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: -1
   EDITION: 4096
   QUIRK_COMPONENT_CODE_ID: 0
   QUIRK_CODE_ID: 11
   TELEMETRY_OFF: True

QUIRK: NETFX.Quirk1
   NAME: NETFX.Quirk1
   FIX_ID: 6c4e39ed-f3c1-4a41-a4e1-cced8c3409a4
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 1
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: NETFX.Quirk2
   NAME: NETFX.Quirk2
   FIX_ID: d5d3133f-5eb9-49e2-8cf7-96c84b3bd044
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: -1
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 1
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: NETFX.Quirk3
   NAME: NETFX.Quirk3
   FIX_ID: ee021f04-d467-488b-86f3-74b6bb1490f7
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 1
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: NETFX.Quirk4
   NAME: NETFX.Quirk4
   FIX_ID: f96f7c34-2c6a-475b-b3aa-88b23e42654a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 1
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: NETFX.HostNameIPInformation
   NAME: NETFX.HostNameIPInformation
   FIX_ID: 4a1b7ca5-3b50-4b0d-acee-847678fc5d2a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 1
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: NETFX.AcquireConnectionAsyncDefaultAllow
   NAME: NETFX.AcquireConnectionAsyncDefaultAllow
   FIX_ID: 24f3118b-b2da-43a1-9b34-60d4164636dd
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 1
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: NETFX.Quirk7
   NAME: NETFX.Quirk7
   FIX_ID: 060b6cf4-6126-468d-9681-cd5962731ed2
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 1
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: NETFX.Quirk8
   NAME: NETFX.Quirk8
   FIX_ID: 406cf89d-9cdb-475b-943c-a6346313736d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 1
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: XAML.ThemeResource
   NAME: XAML.ThemeResource
   FIX_ID: 8061933d-07d9-4a19-a7b2-3a8fd2265028
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: XAML.ScrollViewerStaticZoomFactor
   NAME: XAML.ScrollViewerStaticZoomFactor
   FIX_ID: 4f91c89e-2398-4db2-b047-46a420451ed8
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: XAML.TrackerPtrCreateManagedReferenceForDependencyObject
   NAME: XAML.TrackerPtrCreateManagedReferenceForDependencyObject
   FIX_ID: a42c6a68-bf6d-4e4f-bf43-a4aa6155fb12
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: XAML.SendManipulationStartingEventAfterGesture
   NAME: XAML.SendManipulationStartingEventAfterGesture
   FIX_ID: ba2c95ec-bc20-4340-a6d9-78ab141c6a34
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: XAML.MultipleLayoutUpdatedEventSubscribers
   NAME: XAML.MultipleLayoutUpdatedEventSubscribers
   FIX_ID: 1c563b60-cae4-4aaa-ac21-449d5438abe0
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: XAML.UIAAccessibilityViewForTemplatedPrimitiveControls
   NAME: XAML.UIAAccessibilityViewForTemplatedPrimitiveControls
   FIX_ID: a3ba680d-1990-4111-afed-96bd68d22167
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: XAML.CanDisableStateAnimationAndVisualTransitions
   NAME: XAML.CanDisableStateAnimationAndVisualTransitions
   FIX_ID: 7214a128-6eb3-4a57-83bb-0e852ebe529d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: XAML.CanDisableThemeTransitions
   NAME: XAML.CanDisableThemeTransitions
   FIX_ID: 2472dca1-dc84-45c8-9eb7-317267941950
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: XAML.UIAGivePrecedenceToDataPeer
   NAME: XAML.UIAGivePrecedenceToDataPeer
   FIX_ID: 78e15567-9b7b-447d-898f-41634011dd95
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 8
   TELEMETRY_OFF: True

QUIRK: XAML.AllowContinuousAnimationHandoff
   NAME: XAML.AllowContinuousAnimationHandoff
   FIX_ID: 7dd6c175-1613-4a3f-9615-2516a0095197
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 9
   TELEMETRY_OFF: True

QUIRK: XAML.AllowImplicitStyleOnRootScrollViewer
   NAME: XAML.AllowImplicitStyleOnRootScrollViewer
   FIX_ID: 76ab9cd9-e50c-47a5-833a-be4a41c783bc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 10
   TELEMETRY_OFF: True

QUIRK: XAML.IncrementalDataVisualizationInListViews
   NAME: XAML.IncrementalDataVisualizationInListViews
   FIX_ID: 073e84d4-e9c2-4f60-b683-2444e0fafcee
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 11
   TELEMETRY_OFF: True

QUIRK: XAML.TreatNotStartedAsStoppedClockState
   NAME: XAML.TreatNotStartedAsStoppedClockState
   FIX_ID: 4f43fda4-1f57-4f4b-84c9-6b70db7d49fd
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 12
   TELEMETRY_OFF: True

QUIRK: XAML.SkipDmPointerHitTestProcessing
   NAME: XAML.SkipDmPointerHitTestProcessing
   FIX_ID: 8f492c03-9bb2-44ca-9106-abd4059f7796
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 13
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotProcessPointerExitedEventByPointerEnteredElementStateChange
   NAME: XAML.DoNotProcessPointerExitedEventByPointerEnteredElementStateChange
   FIX_ID: b7c5297a-2bf8-4b0b-a0ba-a72018c5ea04
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 14
   TELEMETRY_OFF: True

QUIRK: XAML.ItemsPresenterHeaderAlwaysLeftOrTopAligned
   NAME: XAML.ItemsPresenterHeaderAlwaysLeftOrTopAligned
   FIX_ID: 4bd174a4-e462-4f72-b460-2845cd00c0e5
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 15
   TELEMETRY_OFF: True

QUIRK: XAML.UseNewMediaLayoutBehavior
   NAME: XAML.UseNewMediaLayoutBehavior
   FIX_ID: 880c8d52-b44a-4fae-b930-4fffd97e2d7f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 16
   TELEMETRY_OFF: True

QUIRK: XAML.AllowRightTappedEventArgsPositionXAndYSwap
   NAME: XAML.AllowRightTappedEventArgsPositionXAndYSwap
   FIX_ID: 232ee105-bbf7-4638-bc42-1b4ef9ef99b1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 17
   TELEMETRY_OFF: True

QUIRK: XAML.AllowTabNavigationWithCtrlOrAltKeyModifiers
   NAME: XAML.AllowTabNavigationWithCtrlOrAltKeyModifiers
   FIX_ID: 0c4121f1-8049-4a82-8393-a4ced27fa916
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 18
   TELEMETRY_OFF: True

QUIRK: XAML.ColorFontsOnByDefault
   NAME: XAML.ColorFontsOnByDefault
   FIX_ID: 29a2166e-a884-46fd-9300-2199ef589db4
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 19
   TELEMETRY_OFF: True

QUIRK: XAML.DelayLoadResourceDictionary
   NAME: XAML.DelayLoadResourceDictionary
   FIX_ID: 71eccb47-5363-47b8-a21e-a0974d67e330
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 20
   TELEMETRY_OFF: True

QUIRK: XAML.AllowRightTappedEventWithOnlyApplicationsKeyUp
   NAME: XAML.AllowRightTappedEventWithOnlyApplicationsKeyUp
   FIX_ID: e3080c83-6a6e-4c6d-84de-c27448d74a74
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 21
   TELEMETRY_OFF: True

QUIRK: XAML.RespectComboBoxMaxDropDownHeight
   NAME: XAML.RespectComboBoxMaxDropDownHeight
   FIX_ID: 4ed178c8-8a71-448a-8546-b48fe8cd0802
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 22
   TELEMETRY_OFF: True

QUIRK: XAML.WrapGridRecomputeItemsPerLineWhenItemsCountChanges
   NAME: XAML.WrapGridRecomputeItemsPerLineWhenItemsCountChanges
   FIX_ID: 2fc836fa-47bf-4ac2-b7f0-017c91e55fec
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 23
   TELEMETRY_OFF: True

QUIRK: XAML.UseWebViewWindowedHosting
   NAME: XAML.UseWebViewWindowedHosting
   FIX_ID: b16a1dfd-a799-4fda-b214-01a3b86f9dd6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 24
   TELEMETRY_OFF: True

QUIRK: XAML.WebView_ScriptNotifyUrisLimitedToProperty
   NAME: XAML.WebView_ScriptNotifyUrisLimitedToProperty
   FIX_ID: c7a3a1c4-6f06-491f-8f05-5c36ccf21747
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 25
   TELEMETRY_OFF: True

QUIRK: XAML.AutoReloadImagesOnScaleChange
   NAME: XAML.AutoReloadImagesOnScaleChange
   FIX_ID: b1287381-d66b-4b54-bcce-0c1ce93638f4
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 26
   TELEMETRY_OFF: True

QUIRK: XAML.ValidateSelectGroupStyleParameters
   NAME: XAML.ValidateSelectGroupStyleParameters
   FIX_ID: 8b822b82-d4b0-4c1e-a1e4-7f443f893911
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 27
   TELEMETRY_OFF: True

QUIRK: XAML.DWriteLineBreaking
   NAME: XAML.DWriteLineBreaking
   FIX_ID: afd5f8d7-910d-4e68-82b0-74ae4804b456
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 28
   TELEMETRY_OFF: True

QUIRK: XAML.PropagateUidBaseUrisInDeferredXaml
   NAME: XAML.PropagateUidBaseUrisInDeferredXaml
   FIX_ID: ef84d20a-de69-4a0d-af99-17317487996f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 29
   TELEMETRY_OFF: True

QUIRK: XAML.KeepSelectionOfReplacedItem
   NAME: XAML.KeepSelectionOfReplacedItem
   FIX_ID: 48ee8a77-dbae-48c2-ad76-935073519caf
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 30
   TELEMETRY_OFF: True

QUIRK: XAML.ResolveImageBrushUrisBasedOnDefinition
   NAME: XAML.ResolveImageBrushUrisBasedOnDefinition
   FIX_ID: bb792d86-bdda-4d96-9fe9-e356b900ca89
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 31
   TELEMETRY_OFF: True

QUIRK: XAML.FlipViewFocusOnPointerReleased
   NAME: XAML.FlipViewFocusOnPointerReleased
   FIX_ID: 5df35a59-0341-4fdb-8550-97dbf1a5a0c0
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 32
   TELEMETRY_OFF: True

QUIRK: XAML.ManipulationCompletedAfterTapDuringInertia
   NAME: XAML.ManipulationCompletedAfterTapDuringInertia
   FIX_ID: 4bd77ef3-b655-429d-9df6-a8d845d54015
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 33
   TELEMETRY_OFF: True

QUIRK: XAML.UseScratchSurfaceForSIS
   NAME: XAML.UseScratchSurfaceForSIS
   FIX_ID: 12828ffd-972b-4225-9bf1-deaffac52901
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 34
   TELEMETRY_OFF: True

QUIRK: XAML.NumberSubstitution
   NAME: XAML.NumberSubstitution
   FIX_ID: 518133ed-2849-4535-a9c7-0ec8a1660afc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 35
   TELEMETRY_OFF: True

QUIRK: XAML.KeepProgrammaticFocusStateAsKeyboard
   NAME: XAML.KeepProgrammaticFocusStateAsKeyboard
   FIX_ID: 8680633a-38d7-4bb9-a60e-c5cc8de95cad
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 36
   TELEMETRY_OFF: True

QUIRK: XAML.ValidateRetVal
   NAME: XAML.ValidateRetVal
   FIX_ID: f76d9ea8-c70c-41c8-80a8-d32ce4ae48b5
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 37
   TELEMETRY_OFF: True

QUIRK: XAML.BlockSetSwapChainFromBackgroundThread
   NAME: XAML.BlockSetSwapChainFromBackgroundThread
   FIX_ID: cac1a3d8-2039-416e-a550-3eb954f3a5a6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 38
   TELEMETRY_OFF: True

QUIRK: XAML.FlipViewAnimatedSwitching
   NAME: XAML.FlipViewAnimatedSwitching
   FIX_ID: ea5b4f67-4347-4f88-ab5a-54ed06ee3819
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 39
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldSwapChainBackgroundPanelAutoRescale
   NAME: XAML.ShouldSwapChainBackgroundPanelAutoRescale
   FIX_ID: 7b965c08-06bf-493d-a3b5-558bdc1606d0
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 40
   TELEMETRY_OFF: True

QUIRK: XAML.PropagateNonLiveNonNameRegistrationEnterWalk
   NAME: XAML.PropagateNonLiveNonNameRegistrationEnterWalk
   FIX_ID: 5239fe54-a836-446c-bb09-a3d97dfdff93
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 41
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldDependencyPropertyAlwaysUseStrongRef
   NAME: XAML.ShouldDependencyPropertyAlwaysUseStrongRef
   FIX_ID: 49e419c4-ba7d-43ca-bed5-dc48bc5a1cc3
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 42
   TELEMETRY_OFF: True

QUIRK: XAML.DontPropagateLanguageToToolTipAndAppBar
   NAME: XAML.DontPropagateLanguageToToolTipAndAppBar
   FIX_ID: 6bf2cd8d-102e-46fd-9d60-7bc729a5084d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 43
   TELEMETRY_OFF: True

QUIRK: XAML.DontReevaluateIsGroupingFlagForItemContainerGenerator
   NAME: XAML.DontReevaluateIsGroupingFlagForItemContainerGenerator
   FIX_ID: d2a5f8f7-9abe-493a-892b-44b6083f8f41
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 44
   TELEMETRY_OFF: True

QUIRK: XAML.PreserveGridFlags
   NAME: XAML.PreserveGridFlags
   FIX_ID: 4d1445f1-cfa0-4381-84d9-1b77468be7d8
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 45
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldHandleQualifierChangesImmediately
   NAME: XAML.ShouldHandleQualifierChangesImmediately
   FIX_ID: a8f05b74-1a18-4cfe-b54e-e6d2de53101c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 46
   TELEMETRY_OFF: True

QUIRK: XAML.TransferFocusToAnyFocusableElement
   NAME: XAML.TransferFocusToAnyFocusableElement
   FIX_ID: 9f63b19c-ac6c-4112-a1ae-2b84f751fcd9
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 47
   TELEMETRY_OFF: True

QUIRK: XAML.DecodeToRenderSize
   NAME: XAML.DecodeToRenderSize
   FIX_ID: 23925b51-a05b-448b-aa68-b693520f1541
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 48
   TELEMETRY_OFF: True

QUIRK: XAML.ModernCollectionBasePanelAttachScrollViewerDuringLoadedEvent_Desktop
   NAME: XAML.ModernCollectionBasePanelAttachScrollViewerDuringLoadedEvent_Desktop
   FIX_ID: 362c03c3-083e-437e-91eb-95f3673e381a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 49
   TELEMETRY_OFF: True

QUIRK: XAML.ModernCollectionBasePanelAttachScrollViewerDuringLoadedEvent_Phone
   NAME: XAML.ModernCollectionBasePanelAttachScrollViewerDuringLoadedEvent_Phone
   FIX_ID: 6723d9bb-653d-4890-ad98-8f4b022e5239
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 50
   TELEMETRY_OFF: True

QUIRK: XAML.LoadListFooterAfterScrollIntoView_Desktop
   NAME: XAML.LoadListFooterAfterScrollIntoView_Desktop
   FIX_ID: 656192dc-b3f1-45f5-9157-b54195c04705
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 51
   TELEMETRY_OFF: True

QUIRK: XAML.LoadListFooterAfterScrollIntoView_Phone
   NAME: XAML.LoadListFooterAfterScrollIntoView_Phone
   FIX_ID: 7d150dc0-6f4c-4d68-9df7-84f542f26d36
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 52
   TELEMETRY_OFF: True

QUIRK: XAML.RemoveGridFromDefaultContentPresenter_Desktop
   NAME: XAML.RemoveGridFromDefaultContentPresenter_Desktop
   FIX_ID: ae74536b-d1ad-4ccc-94d0-5bb76ad3e8b2
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 53
   TELEMETRY_OFF: True

QUIRK: XAML.RemoveGridFromDefaultContentPresenter_Phone
   NAME: XAML.RemoveGridFromDefaultContentPresenter_Phone
   FIX_ID: 137409f8-639f-4ea2-8dc9-36ce9e7e32fd
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 54
   TELEMETRY_OFF: True

QUIRK: XAML.SliderSubscribeSizeChangedOnRootGrid_Desktop
   NAME: XAML.SliderSubscribeSizeChangedOnRootGrid_Desktop
   FIX_ID: f187e71c-3f72-46c3-a8f2-e5bbd5715fdd
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 55
   TELEMETRY_OFF: True

QUIRK: XAML.SliderSubscribeSizeChangedOnRootGrid_Phone
   NAME: XAML.SliderSubscribeSizeChangedOnRootGrid_Phone
   FIX_ID: 05f7eb9b-3f17-4e7c-8b25-0bb35f6ef299
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 56
   TELEMETRY_OFF: True

QUIRK: XAML.RemovePagesWithDisabledCacheMode
   NAME: XAML.RemovePagesWithDisabledCacheMode
   FIX_ID: d07fa5d1-ec61-4dad-84df-aaaea3ad4f24
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 57
   TELEMETRY_OFF: True

QUIRK: XAML.ItemCollectionNoReentrancyCheckOnCollectionChanged_Desktop
   NAME: XAML.ItemCollectionNoReentrancyCheckOnCollectionChanged_Desktop
   FIX_ID: 4b28fa97-90ee-4eec-ae82-b349f4685008
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 58
   TELEMETRY_OFF: True

QUIRK: XAML.ItemCollectionNoReentrancyCheckOnCollectionChanged_Phone
   NAME: XAML.ItemCollectionNoReentrancyCheckOnCollectionChanged_Phone
   FIX_ID: 0dbe011a-b576-4d76-a89f-c74d81b5c0a0
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 59
   TELEMETRY_OFF: True

QUIRK: XAML.UseWinInetToCrackUris
   NAME: XAML.UseWinInetToCrackUris
   FIX_ID: ef8386b5-1604-4e7a-8971-0b9e4a06f80e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 60
   TELEMETRY_OFF: True

QUIRK: XAML.LayoutRoundUpOnTextBlockFamily_Desktop
   NAME: XAML.LayoutRoundUpOnTextBlockFamily_Desktop
   FIX_ID: 36a0a253-348d-4337-8335-4e37a393103e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 61
   TELEMETRY_OFF: True

QUIRK: XAML.LayoutRoundUpOnTextBlockFamily_Phone
   NAME: XAML.LayoutRoundUpOnTextBlockFamily_Phone
   FIX_ID: e5eb6113-c53d-4755-b689-f97554f02aa1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 62
   TELEMETRY_OFF: True

QUIRK: XAML.TemporaryPhoneBlueStore
   NAME: XAML.TemporaryPhoneBlueStore
   FIX_ID: 6f270165-e8ce-494f-98dd-29a09d95cae7
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745231360
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 63
   TELEMETRY_OFF: True

QUIRK: XAML.TemporaryThresholdStore
   NAME: XAML.TemporaryThresholdStore
   FIX_ID: 3a1cce85-852f-47d2-ab7b-e507974b1960
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 64
   TELEMETRY_OFF: True

QUIRK: XAML.PreserveWin8RCCompatibility
   NAME: XAML.PreserveWin8RCCompatibility
   FIX_ID: e1c6e408-618a-4c2e-800c-7a87f8896dd5
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688858450264064
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 65
   TELEMETRY_OFF: True

QUIRK: XAML.IAutomationPeer2PhoneBlueStore
   NAME: XAML.IAutomationPeer2PhoneBlueStore
   FIX_ID: fea7c721-07e0-444a-917c-b656e7b5c8da
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745231360
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 66
   TELEMETRY_OFF: True

QUIRK: XAML.IAutomationPeer2ThresholdStore
   NAME: XAML.IAutomationPeer2ThresholdStore
   FIX_ID: 4bb56cc9-6a9b-4a0a-87de-ec371b6e1cee
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 67
   TELEMETRY_OFF: True

QUIRK: XAML.TemporaryRoundFloatingPoint
   NAME: XAML.TemporaryRoundFloatingPoint
   FIX_ID: f5daccf3-45ea-4227-a047-5e366b7e3b7e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 68
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotUseDWriteTextLayout
   NAME: XAML.DoNotUseDWriteTextLayout
   FIX_ID: a07212a8-1e3f-479d-92b9-9d69a82a0984
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 69
   TELEMETRY_OFF: True

QUIRK: XAML.CoreWindowSubclassedEvents
   NAME: XAML.CoreWindowSubclassedEvents
   FIX_ID: 1c3db17b-763c-405c-ab4e-662d4a50024e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 70
   TELEMETRY_OFF: True

QUIRK: XAML.UseDCompHitTestVisibility
   NAME: XAML.UseDCompHitTestVisibility
   FIX_ID: 9000a719-0b9a-436c-aec9-9105169d4735
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 71
   TELEMETRY_OFF: True

QUIRK: XAML.UseLegacyVsmBehavior
   NAME: XAML.UseLegacyVsmBehavior
   FIX_ID: f832856b-4188-4245-80e9-27f9544f59f1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 72
   TELEMETRY_OFF: True

QUIRK: XAML.ForceArrangeScrollContentPresenterChildren
   NAME: XAML.ForceArrangeScrollContentPresenterChildren
   FIX_ID: a7161e04-79e7-4c54-8d66-faecd784573e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 73
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotUseSharedD3DDevice
   NAME: XAML.DoNotUseSharedD3DDevice
   FIX_ID: f15f559d-7939-424e-818b-01d72097840a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 74
   TELEMETRY_OFF: True

QUIRK: XAML.RaiseDependencyPropertyChangedEventAsynchronously
   NAME: XAML.RaiseDependencyPropertyChangedEventAsynchronously
   FIX_ID: dbdd1e95-77a4-4158-8048-f52678b8a03f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 75
   TELEMETRY_OFF: True

QUIRK: XAML.PlateauScaledMediaSwapChainSize
   NAME: XAML.PlateauScaledMediaSwapChainSize
   FIX_ID: 2090831c-f9dc-42e1-9858-ed5942ffabfc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 76
   TELEMETRY_OFF: True

QUIRK: XAML.AllowNonClippingInScrollingVirtualizingPanels
   NAME: XAML.AllowNonClippingInScrollingVirtualizingPanels
   FIX_ID: db53faae-6b50-4a35-858e-16d93a07cee9
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 77
   TELEMETRY_OFF: True

QUIRK: XAML.ReturnErrorsFromFrameNavigate
   NAME: XAML.ReturnErrorsFromFrameNavigate
   FIX_ID: b0007f82-c458-44a5-b741-b87811158fa1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 78
   TELEMETRY_OFF: True

QUIRK: XAML.UseDefaultValueForComboBoxPlaceholder
   NAME: XAML.UseDefaultValueForComboBoxPlaceholder
   FIX_ID: 6b2746b4-9cd8-4d4b-a2c3-a95099ea59cd
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745231360
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 79
   TELEMETRY_OFF: True

QUIRK: XAML.CreateLoopbackForDataContext
   NAME: XAML.CreateLoopbackForDataContext
   FIX_ID: 65de2d5a-849c-4062-a417-a3329d39a636
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 80
   TELEMETRY_OFF: True

QUIRK: XAML.ContentControlContentPropertyDoesNotPreserveObjectIdentityForStrings
   NAME: XAML.ContentControlContentPropertyDoesNotPreserveObjectIdentityForStrings
   FIX_ID: aa435da7-1887-4869-a3c5-93038f731509
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 81
   TELEMETRY_OFF: True

QUIRK: XAML.DefaultValueForCustomEnumPropertyIsNull
   NAME: XAML.DefaultValueForCustomEnumPropertyIsNull
   FIX_ID: cad2017d-5c0d-43e4-8c75-c2c10c3a1924
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 82
   TELEMETRY_OFF: True

QUIRK: XAML.DelayedCoreWebViewCreationNotUsed
   NAME: XAML.DelayedCoreWebViewCreationNotUsed
   FIX_ID: 92189c7c-1f77-41aa-a5d6-f178cfa4d988
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 83
   TELEMETRY_OFF: True

QUIRK: XAML.RetainDCompOnDeviceLost
   NAME: XAML.RetainDCompOnDeviceLost
   FIX_ID: fd661cf6-e832-4a81-870f-e6ba8530c74f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 84
   TELEMETRY_OFF: True

QUIRK: XAML.BoxDataContextPropertyValues
   NAME: XAML.BoxDataContextPropertyValues
   FIX_ID: 4d103cbd-f02f-42e0-b14a-6eb418c89083
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 85
   TELEMETRY_OFF: True

QUIRK: XAML.UseLanguageFallbackList
   NAME: XAML.UseLanguageFallbackList
   FIX_ID: b9f2b525-9b0a-47b6-a1b4-6ece418e1967
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 86
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotRestrictXYFocusPropertiesToSearchRoot
   NAME: XAML.DoNotRestrictXYFocusPropertiesToSearchRoot
   FIX_ID: 97075509-a14f-40a4-837f-835c87713e26
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750839341056
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 87
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotUseCompositionPrimitiveGroupRenderer
   NAME: XAML.DoNotUseCompositionPrimitiveGroupRenderer
   FIX_ID: f1097be3-ca79-4a4c-b7c2-54908ade4f9d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 88
   TELEMETRY_OFF: True

QUIRK: XAML.MapServiceTokenConcatenatedDisabled
   NAME: XAML.MapServiceTokenConcatenatedDisabled
   FIX_ID: 65ff8d50-84c0-483a-b3b8-4dc6dfa76b34
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 89
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotAllowSystemColorOverrideViaApplicationResources
   NAME: XAML.DoNotAllowSystemColorOverrideViaApplicationResources
   FIX_ID: d30e8138-9313-465a-bd85-70f1904d2497
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 90
   TELEMETRY_OFF: True

QUIRK: XAML.SkipNamescopeOwnerSemanticsForTemplateNameScopeMembers
   NAME: XAML.SkipNamescopeOwnerSemanticsForTemplateNameScopeMembers
   FIX_ID: 4fc4b2ae-ac55-428b-9375-c78efa513841
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 91
   TELEMETRY_OFF: True

QUIRK: XAML.ScaleRichEditTOMCoordinates
   NAME: XAML.ScaleRichEditTOMCoordinates
   FIX_ID: 67f7dc72-ab74-46ee-aaa7-51b5f7121013
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 92
   TELEMETRY_OFF: True

QUIRK: XAML.ImageEventsRaise
   NAME: XAML.ImageEventsRaise
   FIX_ID: 02984444-c304-4c7f-be63-cd84aa520b1f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 93
   TELEMETRY_OFF: True

QUIRK: XAML.AlwaysSetIsTemplateNameScopeMemberOnTemplateExpansion
   NAME: XAML.AlwaysSetIsTemplateNameScopeMemberOnTemplateExpansion
   FIX_ID: 6465540e-9149-42a2-97fe-13abf95b5fdd
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 94
   TELEMETRY_OFF: True

QUIRK: XAML.IgnoreFrameworkElementRequestedThemeFailures
   NAME: XAML.IgnoreFrameworkElementRequestedThemeFailures
   FIX_ID: 54106a83-dd31-43e6-849a-b9a6413bb4b4
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 95
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotUseBingMapsForJapanAndKorea
   NAME: XAML.DoNotUseBingMapsForJapanAndKorea
   FIX_ID: 06dacc48-6831-4e44-9342-80b303e827f9
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 96
   TELEMETRY_OFF: True

QUIRK: XAML.AllowGoToStateCoreOnNoneControls
   NAME: XAML.AllowGoToStateCoreOnNoneControls
   FIX_ID: 965f394c-55ee-4b0f-8164-c4f03af83066
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 97
   TELEMETRY_OFF: True

QUIRK: XAML.AllowArbitraryBooleanStringsForSparseProperties
   NAME: XAML.AllowArbitraryBooleanStringsForSparseProperties
   FIX_ID: 57d3f7eb-a54b-475a-a20b-8abb40cfb19c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 98
   TELEMETRY_OFF: True

QUIRK: XAML.DisableSetValueFromManagedReentrancySupport
   NAME: XAML.DisableSetValueFromManagedReentrancySupport
   FIX_ID: 5c21b7f3-f469-42a4-95d1-cb26b7f49cc4
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 99
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldInvalidColorMapToBlueColorAssignment
   NAME: XAML.ShouldInvalidColorMapToBlueColorAssignment
   FIX_ID: 6da400a7-040b-49c2-91da-d4b59689b53b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 100
   TELEMETRY_OFF: True

QUIRK: XAML.AppBarShouldInheritDataContext
   NAME: XAML.AppBarShouldInheritDataContext
   FIX_ID: 98d083ef-e938-49f0-8d69-86cfc93ca65c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 101
   TELEMETRY_OFF: True

QUIRK: XAML.ZeroShapeStrokeThicknessWhenNoStrokeBrushAssigned
   NAME: XAML.ZeroShapeStrokeThicknessWhenNoStrokeBrushAssigned
   FIX_ID: b645ce52-cada-4e39-b558-28dac1fd60df
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: -1
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 102
   TELEMETRY_OFF: True

QUIRK: XAML.SetSelectedItemToNullWhenIsSynchronizedWithCurrentItemIsFalse
   NAME: XAML.SetSelectedItemToNullWhenIsSynchronizedWithCurrentItemIsFalse
   FIX_ID: 3de94052-4061-4174-9899-4e1a4acc1a5b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 103
   TELEMETRY_OFF: True

QUIRK: XAML.DisablePartialMediaPlayback
   NAME: XAML.DisablePartialMediaPlayback
   FIX_ID: 55bd1afd-ef64-4ee4-8530-50ee6032529f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 104
   TELEMETRY_OFF: True

QUIRK: XAML.ResourceSetRootInstanceWithTargetResourceDictionary
   NAME: XAML.ResourceSetRootInstanceWithTargetResourceDictionary
   FIX_ID: 5fac0457-1705-4b3e-a163-d980a6215394
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 105
   TELEMETRY_OFF: True

QUIRK: XAML.DelayOnLaunched
   NAME: XAML.DelayOnLaunched
   FIX_ID: fd019917-d17a-4228-be8a-95969d176d2d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 106
   TELEMETRY_OFF: True

QUIRK: XAML.DisableTextBlockLayoutRounding
   NAME: XAML.DisableTextBlockLayoutRounding
   FIX_ID: b6af4a5c-21fe-477a-9b8e-4b424ba4d593
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 107
   TELEMETRY_OFF: True

QUIRK: XAML.ApplyLayoutRoundingAfterDeterminingSizeChanged_AppSpecificQuirk
   NAME: XAML.ApplyLayoutRoundingAfterDeterminingSizeChanged_AppSpecificQuirk
   FIX_ID: aa6f6297-058e-4f0c-9052-5c17c3ed1bef
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: -1
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 108
   TELEMETRY_OFF: True

QUIRK: XAML.CheckForAllAppBarsWithListViewTabbing
   NAME: XAML.CheckForAllAppBarsWithListViewTabbing
   FIX_ID: 015adcbf-3ced-4aed-93e4-40892affdfc7
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 109
   TELEMETRY_OFF: True

QUIRK: XAML.DisableEdgeWebPlatform
   NAME: XAML.ForcePostParseNameRegistration
   FIX_ID: 16c1bc37-c9a9-465f-9a09-7f23ac6ad9cf
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 110
   TELEMETRY_OFF: True

QUIRK: XAML.ApplyLayoutRoundingAfterDeterminingSizeChanged
   NAME: XAML.ApplyLayoutRoundingAfterDeterminingSizeChanged
   FIX_ID: dbca41f0-abf8-4134-ad9a-5754f558878c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 111
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotApplyPageBackgroundRendering
   NAME: XAML.DoNotApplyPageBackgroundRendering
   FIX_ID: b7cfbd65-1b4f-4b0f-aa7a-e0ac597a8f71
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745231360
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 112
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldApplyFixedComboBoxItemPadding
   NAME: XAML.ShouldApplyFixedComboBoxItemPadding
   FIX_ID: 400fcd23-2572-43ce-acd3-daf612250ad3
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 113
   TELEMETRY_OFF: True

QUIRK: XAML.OverwriteModifierValueBeingSetOnReentrancy
   NAME: XAML.OverwriteModifierValueBeingSetOnReentrancy
   FIX_ID: 32b92bdf-d2e8-458f-b9c6-b57b6d6046fe
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 114
   TELEMETRY_OFF: True

QUIRK: XAML.PrioritizeTicksOverInput
   NAME: XAML.PrioritizeTicksOverInput
   FIX_ID: 7477a4b3-1473-4822-a5cf-185343d4df30
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 115
   TELEMETRY_OFF: True

QUIRK: XAML.ApplyMarginCompensationForPivot
   NAME: XAML.ApplyMarginCompensationForPivot
   FIX_ID: af055602-98e9-4ab3-baa5-a32203053303
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: -1
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 116
   TELEMETRY_OFF: True

QUIRK: XAML.UsePageBackgroundBaseMediumBrushForContentDialogOverlay
   NAME: XAML.UsePageBackgroundBaseMediumBrushForContentDialogOverlay
   FIX_ID: 3320705e-0b82-4f90-b143-965c1a86fa02
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750458380288
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 117
   TELEMETRY_OFF: True

QUIRK: XAML.ForceBoundsModeToUseCoreWindowInPagePrepareState
   NAME: XAML.ForceBoundsModeToUseCoreWindowInPagePrepareState
   FIX_ID: ffae4048-c792-43b8-9f48-af7e328ed1d8
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 118
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldFlyoutUseLayoutBounds
   NAME: XAML.ShouldFlyoutUseLayoutBounds
   FIX_ID: 4de71d16-355b-49cf-9736-20508ee9379a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750458380288
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 119
   TELEMETRY_OFF: True

QUIRK: XAML.ListViewBaseItemDelayPressedState
   NAME: XAML.ListViewBaseItemDelayPressedState
   FIX_ID: 0b098556-84b7-47dd-a8a2-e76f6d4075f4
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750458380288
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 120
   TELEMETRY_OFF: True

QUIRK: XAML.CrashOnPostMessageFailure
   NAME: XAML.CrashOnPostMessageFailure
   FIX_ID: ecb6d1c2-293a-451a-9f32-13cee1485157
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 121
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotGenerateCaptureLostOnPointerCancel
   NAME: XAML.DoNotGenerateCaptureLostOnPointerCancel
   FIX_ID: 864cdb03-b109-4107-bd86-b4b4db85e016
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 122
   TELEMETRY_OFF: True

QUIRK: XAML.UseWinRTVisuals
   NAME: XAML.UseWinRTVisuals
   FIX_ID: 673cbc77-9d69-4130-86f2-09f3d6a70b50
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 123
   TELEMETRY_OFF: True

QUIRK: XAML.UsePreRedstoneThemeResources
   NAME: XAML.UsePreRedstoneThemeResources
   FIX_ID: f268f9bb-6f47-41c3-88e7-e050e3b8eeb1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 124
   TELEMETRY_OFF: True

QUIRK: XAML.TreatSameDateTimeAsIdentical
   NAME: XAML.TreatSameDateTimeAsIdentical
   FIX_ID: 3892c7b0-358d-48ac-a608-5314932ca48d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 125
   TELEMETRY_OFF: True

QUIRK: XAML.UseLineServicesForTypographyAndCustomFont
   NAME: XAML.UseLineServicesForTypographyAndCustomFont
   FIX_ID: 12ba9869-0cf4-444e-9311-26d743b8d60a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 126
   TELEMETRY_OFF: True

QUIRK: XAML.UseListViewReorderModeSkuBehavior
   NAME: XAML.UseListViewReorderModeSkuBehavior
   FIX_ID: 085a76b9-148a-449e-afa7-38f793fed14e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 127
   TELEMETRY_OFF: True

QUIRK: XAML.SupportContentDialogWidthAndHeightSnapping
   NAME: XAML.SupportContentDialogWidthAndHeightSnapping
   FIX_ID: 77d93154-0354-48e2-bf8c-4d9ee9f61ee9
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 128
   TELEMETRY_OFF: True

QUIRK: XAML.UsePreRedstoneHoldingGesture
   NAME: XAML.UsePreRedstoneHoldingGesture
   FIX_ID: 362f2794-f8cc-455c-b4e1-f872786659a3
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 129
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotAllowMultipleOpenFlyouts
   NAME: XAML.DoNotAllowMultipleOpenFlyouts
   FIX_ID: 90130920-e64f-4d12-967c-0cf7f4684cbf
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 130
   TELEMETRY_OFF: True

QUIRK: XAML.ListViewBaseDropIntoFolder
   NAME: XAML.ListViewBaseDropIntoFolder
   FIX_ID: b5229228-2de7-4c0f-ae5f-08681d976eba
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 131
   TELEMETRY_OFF: True

QUIRK: XAML.AsynchronouslyApplyVsmSetters
   NAME: XAML.AsynchronouslyApplyVsmSetters
   FIX_ID: c7efdecd-6eea-411a-8d19-34c1aa0c0018
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 132
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotAutoPlayAnimatedBitmapImage
   NAME: XAML.DoNotAutoPlayAnimatedBitmapImage
   FIX_ID: 2f69297f-aca9-4424-956b-57f10e195fb6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 133
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotDelayRunClassConstructor
   NAME: XAML.DoNotDelayRunClassConstructor
   FIX_ID: 1731075d-86b9-4026-bf6f-3cce2b3569bf
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 134
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotSupportContextFlyout
   NAME: XAML.DoNotSupportContextFlyout
   FIX_ID: 67296c2b-2a92-402a-b586-127c7e6516ae
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 135
   TELEMETRY_OFF: True

QUIRK: XAML.CommandBarOverflowButtonShouldAlwaysShow
   NAME: XAML.CommandBarOverflowButtonShouldAlwaysShow
   FIX_ID: bbd4c05d-1649-441c-b836-303f86cf74c1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 136
   TELEMETRY_OFF: True

QUIRK: XAML.PivotWrapWhenInStaticHeadersMode
   NAME: XAML.PivotWrapWhenInStaticHeadersMode
   FIX_ID: c3e1fbe2-d07e-480d-bf54-437b30c1b249
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 137
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotAllowCommandBarDynamicOverflow
   NAME: XAML.DoNotAllowCommandBarDynamicOverflow
   FIX_ID: fabad1c5-8ca6-4a06-8238-00803b01aa18
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 138
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotGetClassInfoForWinRTPropertyOtherType
   NAME: XAML.DoNotGetClassInfoForWinRTPropertyOtherType
   FIX_ID: 50a9af91-b218-490f-80a6-91f92e6a0daa
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 139
   TELEMETRY_OFF: True

QUIRK: XAML.UsePreRedstone4ThemeResources
   NAME: XAML.UsePreRedstone4ThemeResources
   FIX_ID: 79a39615-85c9-4a54-bf79-034f521bf859
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750835343360
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 140
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotUseFocusVisualKindHighVisibility
   NAME: XAML.DoNotUseFocusVisualKindHighVisibility
   FIX_ID: 77296c2c-3a93-502b-c587-227c7e6516af
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 141
   TELEMETRY_OFF: True

QUIRK: XAML.DefaultLightDismissOverlayModeToOff
   NAME: XAML.DefaultLightDismissOverlayModeToOff
   FIX_ID: b92b8b08-1e05-467c-9bf3-8f32b5362551
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 142
   TELEMETRY_OFF: True

QUIRK: XAML.PivotHeaderFocusVisualPlacementDefaultIsItemHeaders
   NAME: XAML.PivotHeaderFocusVisualPlacementDefaultIsItemHeaders
   FIX_ID: ec923051-faa5-4a4c-b12a-cbf2e924f2dc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 143
   TELEMETRY_OFF: True

QUIRK: XAML.ComboBoxTypeAhead
   NAME: XAML.ComboBoxTypeAhead
   FIX_ID: d4bee15b-4b0a-492d-9b60-71c78a7578fd
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 144
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotGenerateTransitionsForVsmSetters
   NAME: XAML.DoNotGenerateTransitionsForVsmSetters
   FIX_ID: d0b87d7d-c8ee-4ee2-8b75-8284951ff3d0
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 145
   TELEMETRY_OFF: True

QUIRK: XAML.DisablePageThemeResources
   NAME: XAML.DisablePageThemeResources
   FIX_ID: 9b644671-9d5a-4cab-a22c-04eb4cee1ab5
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 146
   TELEMETRY_OFF: True

QUIRK: XAML.ListViewBaseItemDataAutomationPeerAlwaysReturnsListItemControlType
   NAME: XAML.ListViewBaseItemDataAutomationPeerAlwaysReturnsListItemControlType
   FIX_ID: 97af5cbf-5524-49b9-a16a-b63956531634
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 147
   TELEMETRY_OFF: True

QUIRK: XAML.SpaceBarDoesNotBehaveLikeEnterInListViewBase
   NAME: XAML.SpaceBarDoesNotBehaveLikeEnterInListViewBase
   FIX_ID: b0837f1e-45c8-44f9-83ac-5a29e77070db
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 148
   TELEMETRY_OFF: True

QUIRK: XAML.SetElementFocusBeforeWindowFocus
   NAME: XAML.SetElementFocusBeforeWindowFocus
   FIX_ID: 57462e10-f546-46e3-92cb-83748e16c9f9
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 149
   TELEMETRY_OFF: True

QUIRK: XAML.ListShouldScrollDueToSelectionChangeOnCollectionChange
   NAME: XAML.ListShouldScrollDueToSelectionChangeOnCollectionChange
   FIX_ID: 15719db4-f8cf-4ac3-9b31-fda7fd6e1d9d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 150
   TELEMETRY_OFF: True

QUIRK: XAML.DisableCrossThreadViewportInteractions
   NAME: XAML.DisableCrossThreadViewportInteractions
   FIX_ID: c9546684-c3c4-4381-a8cb-a564a5e2ace8
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 151
   TELEMETRY_OFF: True

QUIRK: XAML.TextBoxUseCRLFForTextProperty
   NAME: XAML.TextBoxUseCRLFForTextProperty
   FIX_ID: 84389a62-1ab7-4fb0-8d81-1c8c1c32d7b3
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 152
   TELEMETRY_OFF: True

QUIRK: XAML.TextEditableIgnoreTextColorAlphaValue
   NAME: XAML.TextEditableIgnoreTextColorAlphaValue
   FIX_ID: 9b57e059-5a63-4bef-945f-61024c5c0fcf
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 153
   TELEMETRY_OFF: True

QUIRK: XAML.ItemMeasureSizeIgnoresGroupPadding
   NAME: XAML.ItemMeasureSizeIgnoresGroupPadding
   FIX_ID: 94010040-edc3-459c-917d-205bfe91f26f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 154
   TELEMETRY_OFF: True

QUIRK: XAML.PosterSourceStretchDoesNotFollowMediaElement
   NAME: XAML.PosterSourceStretchDoesNotFollowMediaElement
   FIX_ID: 6b20211e-11d1-4795-8182-0cc474977ea5
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 155
   TELEMETRY_OFF: True

QUIRK: XAML.IgnoreListViewBaseItemReadOnlyMode
   NAME: XAML.IgnoreListViewBaseItemReadOnlyMode
   FIX_ID: 34ab2ff4-d981-4e16-9318-674f8a30cd6b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 156
   TELEMETRY_OFF: True

QUIRK: XAML.LoopingSelectorAutomationPeerShouldReportExpandCollapsePattern
   NAME: XAML.LoopingSelectorAutomationPeerShouldReportExpandCollapsePattern
   FIX_ID: c25977f0-b075-4d3f-9fbf-ce9c135bad90
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 157
   TELEMETRY_OFF: True

QUIRK: XAML.ArrangeCoreShouldNotUseRoundedMargin
   NAME: XAML.ArrangeCoreShouldNotUseRoundedMargin
   FIX_ID: 6f03d3a2-08ea-11e6-b512-3e1d05defe78
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 158
   TELEMETRY_OFF: True

QUIRK: XAML.DisableTvSafeCorrectionAndPaddingForBringIntoView
   NAME: XAML.DisableTvSafeCorrectionAndPaddingForBringIntoView
   FIX_ID: 491c3d30-bad9-4c90-896c-92ff5b86c6b8
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 159
   TELEMETRY_OFF: True

QUIRK: XAML.ChildOfCollapsedElementShouldBeAllowedToGainFocus
   NAME: XAML.ChildOfCollapsedElementShouldBeAllowedToGainFocus
   FIX_ID: 323c79a1-41d8-4980-953c-457549ec4d02
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 160
   TELEMETRY_OFF: True

QUIRK: XAML.TrapFocusInAllNonStickyCommandBarsWithOpenedOverflow
   NAME: XAML.TrapFocusInAllNonStickyCommandBarsWithOpenedOverflow
   FIX_ID: 4ca39174-17af-4af1-8fdb-30b1466a0b0c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 161
   TELEMETRY_OFF: True

QUIRK: XAML.UseCoreWindowBoundsOnQualifierContext
   NAME: XAML.UseCoreWindowBoundsOnQualifierContext
   FIX_ID: 8e9acc0b-23bc-4083-b5ce-55696122867f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 162
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotEnableImplicitBoolToVisibilityConverter
   NAME: XAML.DoNotEnableImplicitBoolToVisibilityConverter
   FIX_ID: 792db696-be94-4e7a-bbac-a74190ca1a85
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 163
   TELEMETRY_OFF: True

QUIRK: XAML.VectorOperationsShouldNotCheckBounds
   NAME: XAML.VectorOperationsShouldNotCheckBounds
   FIX_ID: 5aed5c9a-f07f-4c9f-a3c5-d9752938a8b5
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 164
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldUsePlainTextForListViewDragItemCount
   NAME: XAML.ShouldUsePlainTextForListViewDragItemCount
   FIX_ID: 713e29b1-5eb7-4f52-a301-25ada33ffeb1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 165
   TELEMETRY_OFF: True

QUIRK: XAML.RaiseDirectManipulationStartedForNonTouch
   NAME: XAML.RaiseDirectManipulationStartedForNonTouch
   FIX_ID: 6a8d5d9b-f879-4395-a9c9-79052939a8ef
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 166
   TELEMETRY_OFF: True

QUIRK: XAML.DOCollectionShouldExplicitlyRegisterNameScopeParent
   NAME: XAML.DOCollectionShouldExplicitlyRegisterNameScopeParent
   FIX_ID: 04765896-8ab0-4c93-a38a-9a510061f4b8
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 167
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldUse1MBAddMemoryPressureThreshold
   NAME: XAML.ShouldUse1MBAddMemoryPressureThreshold
   FIX_ID: f951a120-4f4a-4cda-bd81-f6c14173cd14
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 168
   TELEMETRY_OFF: True

QUIRK: XAML.SetDefaultFocusStateAsPointer
   NAME: XAML.SetDefaultFocusStateAsPointer
   FIX_ID: 789a1d2b-fc84-484e-9366-2307dbce7da3
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 169
   TELEMETRY_OFF: True

QUIRK: XAML.ListViewBaseItemCheckBoxBrushDoesNotChange
   NAME: XAML.ListViewBaseItemCheckBoxBrushDoesNotChange
   FIX_ID: 57679904-b3a1-41cf-a7ad-f4dfa5baab1f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 170
   TELEMETRY_OFF: True

QUIRK: XAML.UsePreRedstone5ThemeResources
   NAME: XAML.UsePreRedstone5ThemeResources
   FIX_ID: 5f8ebbc0-43b4-4209-9e74-d9b84e4ebd14
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 171
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldApplyContentDialogCommandSpaceMinimumHeight
   NAME: XAML.ShouldApplyContentDialogCommandSpaceMinimumHeight
   FIX_ID: 7b36e74a-b2ac-4607-b09f-22007e67a6cc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 172
   TELEMETRY_OFF: True

QUIRK: XAML.UsePreRedstone2ThemeResources
   NAME: XAML.UsePreRedstone2ThemeResources
   FIX_ID: ae5cc050-7dc1-42dc-8996-43ef911de668
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 173
   TELEMETRY_OFF: True

QUIRK: XAML.UsePreRedstone2InkToobarBehaviors
   NAME: XAML.UsePreRedstone2InkToobarBehaviors
   FIX_ID: cd7497f6-58bc-4718-8fab-528dd2d64487
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 174
   TELEMETRY_OFF: True

QUIRK: XAML.SpriteVisuals
   NAME: XAML.SpriteVisuals
   FIX_ID: abb4152f-54f7-4d3a-bbc4-c1e1b2dd84b8
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 175
   TELEMETRY_OFF: True

QUIRK: XAML.KeyTipsDisabledByDefault
   NAME: XAML.KeyTipsDisabledByDefault
   FIX_ID: e10073ca-a286-48be-947a-0b3169496531
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 176
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotRespectFlowDirectionOnXYFocusProperties
   NAME: XAML.DoNotRespectFlowDirectionOnXYFocusProperties
   FIX_ID: dbfe8cf7-0437-4e44-bb01-097f83f219f8
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 177
   TELEMETRY_OFF: True

QUIRK: XAML.TextEditableBitmapPasteNotSupported
   NAME: XAML.TextEditableBitmapPasteNotSupported
   FIX_ID: d801e323-87bf-4b57-bfc4-0ef919b7cda0
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 178
   TELEMETRY_OFF: True

QUIRK: XAML.UsePhysicalPixelForFindNextFocusableElement
   NAME: XAML.UsePhysicalPixelForFindNextFocusableElement
   FIX_ID: 91d91144-ea1c-415b-9807-56a01fa9a5e1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 179
   TELEMETRY_OFF: True

QUIRK: XAML.UsePreRedstone2ResourceLookupBehavior
   NAME: XAML.UsePreRedstone2ResourceLookupBehavior
   FIX_ID: 5fd13c7c-510a-4a83-9c35-983cd3c612c1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 180
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotLimitOffsetAdjustmentToNextMandatoryScrollSnapPoint
   NAME: XAML.DoNotLimitOffsetAdjustmentToNextMandatoryScrollSnapPoint
   FIX_ID: a0e82233-db2b-504c-8806-6591f1b8b749
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 181
   TELEMETRY_OFF: True

QUIRK: XAML.AllowUseOfParameterXamlObjectsAcrossThreads
   NAME: XAML.AllowUseOfParameterXamlObjectsAcrossThreads
   FIX_ID: 374472e4-4634-41f2-a7fc-d49b7895f16a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750754340864
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 182
   TELEMETRY_OFF: True

QUIRK: XAML.GetEffectiveValueField_ObjectIgnoreFailedLookup
   NAME: XAML.GetEffectiveValueField_ObjectIgnoreFailedLookup
   FIX_ID: d5971792-c84b-47f7-9f67-1c8bc0e83b93
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 183
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotUseSystemThemeForRootVisualBackgroundHC
   NAME: XAML.DoNotUseSystemThemeForRootVisualBackgroundHC
   FIX_ID: 2551e2d7-0e17-4b0a-81ce-6ec88b6dfa30
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 184
   TELEMETRY_OFF: True

QUIRK: XAML.RestoreDirtyPathFlagIfAncestorIsDirty
   NAME: XAML.RestoreDirtyPathFlagIfAncestorIsDirty
   FIX_ID: 0f96d2b6-49c8-41e8-8cb2-00c7e72891c6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 185
   TELEMETRY_OFF: True

QUIRK: XAML.ButtonsShouldLeaveCanExecuteChangedEventSubscribed
   NAME: XAML.ButtonsShouldLeaveCanExecuteChangedEventSubscribed
   FIX_ID: cfbda0e1-b08f-4e90-ae4b-fbae14b80364
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 186
   TELEMETRY_OFF: True

QUIRK: XAML.PreventInputManagerFromRecreatingUnresurrectablePeers
   NAME: XAML.PreventInputManagerFromRecreatingUnresurrectablePeers
   FIX_ID: 9f8bedda-4e03-47bb-844e-980aed45b320
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: -1
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 187
   TELEMETRY_OFF: True

QUIRK: XAML.ComboBoxSelectionChangedTriggerDefaultsToAlways
   NAME: XAML.ComboBoxSelectionChangedTriggerDefaultsToAlways
   FIX_ID: 16efa2b0-939d-4034-bb59-afd4c871cfff
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 188
   TELEMETRY_OFF: True

QUIRK: XAML.RenderTargetBitmapUsingSpriteVisuals
   NAME: XAML.RenderTargetBitmapUsingSpriteVisuals
   FIX_ID: fdb079de-9995-4772-b532-3fe2b32da9ee
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 189
   TELEMETRY_OFF: True

QUIRK: XAML.OnlyUseRootViewportInteraction
   NAME: XAML.OnlyUseRootViewportInteraction
   FIX_ID: 0a8713e5-0b7a-4858-3be9-9c8ba4ccc0b5
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 190
   TELEMETRY_OFF: True

QUIRK: XAML.IgnoreHighContrastAdjustment
   NAME: XAML.IgnoreHighContrastAdjustment
   FIX_ID: 23b832af-66a8-4299-bdb0-da8f44fa61cc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 191
   TELEMETRY_OFF: True

QUIRK: XAML.IgnoreHighContrastOpacityOverride
   NAME: XAML.IgnoreHighContrastOpacityOverride
   FIX_ID: 49150c88-5730-42d1-8ca4-24abff556c13
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 192
   TELEMETRY_OFF: True

QUIRK: XAML.AllowModificationOfLockedCollections
   NAME: XAML.AllowModificationOfLockedCollections
   FIX_ID: 1615b698-1404-450e-9312-ebd14232c9e4
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 193
   TELEMETRY_OFF: True

QUIRK: XAML.FailSISOperationsWhenOffered
   NAME: XAML.FailSISOperationsWhenOffered
   FIX_ID: 91ecf196-c6d6-46d1-b968-744430cae38b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 194
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldAutoSuggestHardCodeGlyphSize
   NAME: XAML.ShouldAutoSuggestHardCodeGlyphSize
   FIX_ID: 7835d81e-6a46-4916-9347-ffb5e11139f3
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 195
   TELEMETRY_OFF: True

QUIRK: XAML.FlattenProjectionMatrices
   NAME: XAML.FlattenProjectionMatrices
   FIX_ID: 0ed5bca8-d7a4-4486-9760-1239ff93838c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 196
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldMoveDynamicAppBarButtonsToPrimaryCollectionOnSizeChanged
   NAME: XAML.ShouldMoveDynamicAppBarButtonsToPrimaryCollectionOnSizeChanged
   FIX_ID: 56775a74-87e0-41d6-be59-25cbb3c51642
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 197
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotPreResolveFullyQualifiedProperties
   NAME: XAML.DoNotPreResolveFullyQualifiedProperties
   FIX_ID: 440e413f-71a4-4d72-b9cd-0704cf1b135c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 198
   TELEMETRY_OFF: True

QUIRK: XAML.UseNormalizedAnchorPointAtTopLeft
   NAME: XAML.UseNormalizedAnchorPointAtTopLeft
   FIX_ID: 3f156859-be7a-4b75-859a-9b02b7164c43
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 199
   TELEMETRY_OFF: True

QUIRK: XAML.IgnoreGeoidAltitudeReference
   NAME: XAML.IgnoreGeoidAltitudeReference
   FIX_ID: 9b43d6b0-16a9-4d20-bfb4-f2ef458fc2bc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 200
   TELEMETRY_OFF: True

QUIRK: XAML.IgnoreSelectedItemSetBeforeItemsSource
   NAME: XAML.IgnoreSelectedItemSetBeforeItemsSource
   FIX_ID: 416bac4f-ac4f-4548-aa4e-4c88a7d02727
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 201
   TELEMETRY_OFF: True

QUIRK: XAML.UsePreRedstone3ThemeResources
   NAME: XAML.UsePreRedstone3ThemeResources
   FIX_ID: e1c3b2c3-11db-402d-a272-446f6b91824f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750754340864
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 202
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotLiftRootScrollViewerLightsToRoot
   NAME: XAML.DoNotLiftRootScrollViewerLightsToRoot
   FIX_ID: 0c80cf16-99f0-43ac-a1aa-14048084cf92
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750754340864
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 203
   TELEMETRY_OFF: True

QUIRK: XAML.IgnoreRichEditBoxFormattingAccelerators
   NAME: XAML.IgnoreRichEditBoxFormattingAccelerators
   FIX_ID: b026bbdb-fa56-4217-8159-81acdf4a876c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750754340864
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 204
   TELEMETRY_OFF: True

QUIRK: XAML.ReplayPointerOnViewUpdate
   NAME: XAML.ReplayPointerOnViewUpdate
   FIX_ID: 81e70d8f-5e41-45ba-8b57-b91f15c0df05
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750754340864
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 205
   TELEMETRY_OFF: True

QUIRK: XAML.UseTSF1OnDesktop
   NAME: XAML.UseTSF1OnDesktop
   FIX_ID: 8e2c6d46-4bf3-40de-81ec-5c68458e4b22
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 206
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotRaiseViewChangingAndChangeZoomFactorDuringDManipSynchronization
   NAME: XAML.DoNotRaiseViewChangingAndChangeZoomFactorDuringDManipSynchronization
   FIX_ID: ac67cf18-f9fb-44ac-aaaa-150c808dcf90
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750754340864
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 207
   TELEMETRY_OFF: True

QUIRK: XAML.DoLiveEntersOnItemCollection
   NAME: XAML.DoLiveEntersOnItemCollection
   FIX_ID: dc3ce624-0c2f-4faf-b90e-0abca214f0ca
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 208
   TELEMETRY_OFF: True

QUIRK: XAML.PenInputTreatedLikeMouse
   NAME: XAML.PenInputTreatedLikeMouse
   FIX_ID: 310c78a7-4ad5-408e-9561-4547806379fc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 209
   TELEMETRY_OFF: True

QUIRK: XAML.LVIPCallGoToElementStateCore
   NAME: XAML.LVIPCallGoToElementStateCore
   FIX_ID: 7047b29b-b713-46b8-a49e-fbb4f59fa8fc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750754340864
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 210
   TELEMETRY_OFF: True

QUIRK: XAML.EnableXamlMemoryPressure
   NAME: XAML.EnableXamlMemoryPressure
   FIX_ID: 85ddca85-e2fc-4009-b18c-dde1b5af001d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 211
   TELEMETRY_OFF: True

QUIRK: XAML.PreventDraggingFromSplitViewPane
   NAME: XAML.PreventDraggingFromSplitViewPane
   FIX_ID: b6a27963-005b-474e-bc52-5428fd192b70
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750754340864
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 212
   TELEMETRY_OFF: True

QUIRK: XAML.XamlOneCoreStrict_DoNotUse
   NAME: XAML.XamlOneCoreStrict_DoNotUse
   FIX_ID: 32ba231b-9d85-4708-ae1c-5a1bc9936f17
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 213
   TELEMETRY_OFF: True

QUIRK: XAML.InvalidateViewWhenWidthExceedsViewport
   NAME: XAML.InvalidateViewWhenWidthExceedsViewport
   FIX_ID: 2e5d8a0b-3ef5-45e8-9213-2b694b054b39
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 214
   TELEMETRY_OFF: True

QUIRK: XAML.FireKeyDownTwiceForAcceleratorKeys
   NAME: XAML.FireKeyDownTwiceForAcceleratorKeys
   FIX_ID: 353906ff-7067-4048-a4e8-c8554623f160
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750754340864
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 215
   TELEMETRY_OFF: True

QUIRK: XAML.SwapChainPanelHitTestFix
   NAME: XAML.SwapChainPanelHitTestFix
   FIX_ID: ae8555dd-5daf-4e3e-aff8-d25baafc127d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 216
   TELEMETRY_OFF: True

QUIRK: XAML.DisableVisualStateForCalendarViewDayItem
   NAME: XAML.DisableVisualStateForCalendarViewDayItem
   FIX_ID: c4b9b5b5-ba6b-4de6-b291-0248980d50f6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750839341056
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 217
   TELEMETRY_OFF: True

QUIRK: XAML.IgnoreBitmapCache
   NAME: XAML.IgnoreBitmapCache
   FIX_ID: 15eecdd2-0e1d-4969-a4ee-e1926af7f105
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750839341056
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 218
   TELEMETRY_OFF: True

QUIRK: XAML.DisableOneCoreTransforms
   NAME: XAML.DisableOneCoreTransforms
   FIX_ID: 662b76e2-7a52-4e85-8097-49ad07049456
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 219
   TELEMETRY_OFF: True

QUIRK: XAML.DisableDefaultNavigationTransition
   NAME: XAML.DisableDefaultNavigationTransition
   FIX_ID: a7135d04-9eb3-4f0a-acf9-7fac902d46f5
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750839341056
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 220
   TELEMETRY_OFF: True

QUIRK: XAML.DisableHandwritingView
   NAME: XAML.DisableHandwritingView
   FIX_ID: 1bb0460f-de0d-4c20-b06e-a057192e54be
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 221
   TELEMETRY_OFF: True

QUIRK: XAML.PivotDoesNotDrawPreviousAndNextItems
   NAME: XAML.PivotDoesNotDrawPreviousAndNextItems
   FIX_ID: 0b805bf1-84de-4537-af5f-ccb1d6bd73e6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750839341056
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 222
   TELEMETRY_OFF: True

QUIRK: XAML.PivotHeaderFocusVisualDoesNotAlwaysUseTemplateValue
   NAME: XAML.PivotHeaderFocusVisualDoesNotAlwaysUseTemplateValue
   FIX_ID: ee62d344-0a46-4aec-8daf-cce9e8c85d63
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750839341056
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 223
   TELEMETRY_OFF: True

QUIRK: XAML.EnableLabelOnRightStyle
   NAME: XAML.EnableLabelOnRightStyle
   FIX_ID: 17c75e85-2f08-4922-bdc7-38c51026d73b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750754340864
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 224
   TELEMETRY_OFF: True

QUIRK: XAML.HostWebViewInSameProcess
   NAME: XAML.HostWebViewInSameProcess
   FIX_ID: 2fc5058b-b807-4933-b3bd-be32f650ce74
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 225
   TELEMETRY_OFF: True

QUIRK: XAML.EnableDestructiveCoercionInRangeBase
   NAME: XAML.EnableDestructiveCoercionInRangeBase
   FIX_ID: 43f50ff5-e434-45a7-90c7-0aacddba3cce
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750839341056
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 226
   TELEMETRY_OFF: True

QUIRK: XAML.ShowDottedLineWhenSystemFocusVisualsAreDisabled
   NAME: XAML.ShowDottedLineWhenSystemFocusVisualsAreDisabled
   FIX_ID: ec3fa937-ca40-4cdf-a0da-76dcd90e94c6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750839341056
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 227
   TELEMETRY_OFF: True

QUIRK: XAML.SplitViewCloseEventsAreAsync
   NAME: XAML.SplitViewCloseEventsAreAsync
   FIX_ID: 5c032056-9952-48b6-ad3c-f2e792b804b5
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750839341056
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 228
   TELEMETRY_OFF: True

QUIRK: XAML.SettingAppResourcesOnlyInvalidatesImplicitStylesOnMainVisualRoot
   NAME: XAML.SettingAppResourcesOnlyInvalidatesImplicitStylesOnMainVisualRoot
   FIX_ID: 25aa84c5-9b47-4b2b-9d64-b4ad4e5c74de
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750839341056
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 229
   TELEMETRY_OFF: True

QUIRK: XAML.DisableFontIconPropertiesFromStyle
   NAME: XAML.DisableFontIconPropertiesFromStyle
   FIX_ID: 54dd82aa-7aa8-47ba-973d-12ee2e9037b2
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750839341056
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 230
   TELEMETRY_OFF: True

QUIRK: XAML.IgnoreLayoutRoundingForPixelValuesInGridDefinitions
   NAME: XAML.IgnoreLayoutRoundingForPixelValuesInGridDefinitions
   FIX_ID: 89b6acd6-2bf2-4015-9b2a-943d23c8b2fb
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750839341056
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 231
   TELEMETRY_OFF: True

QUIRK: XAML.PreserveNavigationViewRS3Behavior
   NAME: XAML.PreserveNavigationViewRS3Behavior
   FIX_ID: 25ee835e-cbee-4117-9f5e-351ee4df899d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750835343360
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 232
   TELEMETRY_OFF: True

QUIRK: XAML.OnlyMenuFlyoutUsesPointBasedPositioningAsContextFlyout
   NAME: XAML.OnlyMenuFlyoutUsesPointBasedPositioningAsContextFlyout
   FIX_ID: da87b89b-96b6-493d-9822-c6e28b32bb9a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 233
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotUseTemplateRootAsContainer
   NAME: XAML.DoNotUseTemplateRootAsContainer
   FIX_ID: 02edcda1-3e38-42df-875f-c53ae9119801
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750922375168
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 234
   TELEMETRY_OFF: True

QUIRK: XAML.UseSilverlightHWShapeRendering
   NAME: XAML.UseSilverlightHWShapeRendering
   FIX_ID: 343c9f2d-7a78-4f27-893d-3c7a14c9d9a0
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 235
   TELEMETRY_OFF: True

QUIRK: XAML.PerformShallowParentCommandBarSearch
   NAME: XAML.PerformShallowParentCommandBarSearch
   FIX_ID: fc7fc746-6152-432c-ace4-5fb72d2d1420
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750839341056
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 236
   TELEMETRY_OFF: True

QUIRK: XAML.SuppressAppBarFlyoutHandling
   NAME: XAML.SuppressAppBarFlyoutHandling
   FIX_ID: 1a447a91-c9a0-4226-886a-42f31a45fbbe
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 237
   TELEMETRY_OFF: True

QUIRK: XAML.TextElementGotFocusLostFocusAreSync
   NAME: XAML.TextElementGotFocusLostFocusAreSync
   FIX_ID: 3a1b558f-4f8f-45a6-890d-52cc0da6cc15
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 238
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotCreateTransitionCollectionPropertiesOnDemand
   NAME: XAML.DoNotCreateTransitionCollectionPropertiesOnDemand
   FIX_ID: 10978728-3fee-486d-9664-cb70fc45ea0d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 239
   TELEMETRY_OFF: True

QUIRK: XAML.AllowNegativeBorderThickness
   NAME: XAML.AllowNegativeBorderThickness
   FIX_ID: 0fbaa27b-7960-4fc3-abb7-9f9d46cfaf80
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 240
   TELEMETRY_OFF: True

QUIRK: XAML.UseRS4ConnectedAnimationDefaults
   NAME: XAML.UseRS4ConnectedAnimationDefaults
   FIX_ID: 57ad9186-5dfd-43e3-b4f7-41299c53b2c4
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 241
   TELEMETRY_OFF: True

QUIRK: XAML.UseLegacyWindows8UI
   NAME: XAML.UseLegacyWindows8UI
   FIX_ID: 1ef22bca-dee8-4c40-97d5-90d7e222a62a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745231360
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 242
   TELEMETRY_OFF: True

QUIRK: XAML.SuppressDateTimePickerNullVisualizations
   NAME: XAML.SuppressDateTimePickerNullVisualizations
   FIX_ID: 36a2888f-13d6-45a1-80fb-5f09081f3b44
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 243
   TELEMETRY_OFF: True

QUIRK: XAML.UseLegacyPopupMenuAsTextControlContextMenu
   NAME: XAML.UseLegacyPopupMenuAsTextControlContextMenu
   FIX_ID: 1d9acf7b-f238-4c22-9f72-bcc143bcf725
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 244
   TELEMETRY_OFF: True

QUIRK: XAML.StyleSetterAllowsNonshareableObject
   NAME: XAML.StyleSetterAllowsNonshareableObject
   FIX_ID: 7a7e05d2-7a63-40dc-bb29-0b8908f8589d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 245
   TELEMETRY_OFF: True

QUIRK: XAML.ForbidNullKeyedResources
   NAME: XAML.ForbidNullKeyedResources
   FIX_ID: dd0f091a-b1c8-4b2c-8353-2131dfcc1043
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 246
   TELEMETRY_OFF: True

QUIRK: XAML.DateTimePickerDefaultsToCurrentDateOrTime
   NAME: XAML.DateTimePickerDefaultsToCurrentDateOrTime
   FIX_ID: 00be9fba-1faf-4c13-9771-74928b7881ce
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 247
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldUseLegacyThemeResourceTreeTraversal
   NAME: XAML.ShouldUseLegacyThemeResourceTreeTraversal
   FIX_ID: 797f7f69-390a-42f5-9f56-e1a4bd0921d1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 248
   TELEMETRY_OFF: True

QUIRK: XAML.StyleGetValueShouldNotReseal
   NAME: XAML.StyleGetValueShouldNotReseal
   FIX_ID: 773202e9-7d94-4493-a4ae-8dc8b96cda93
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 249
   TELEMETRY_OFF: True

QUIRK: XAML.UsePre19H1ThemeResources
   NAME: XAML.UsePre19H1ThemeResources
   FIX_ID: c3caee78-063a-405a-a219-f57d7aac81bc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750959861760
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 250
   TELEMETRY_OFF: True

QUIRK: XAML.RespectVisiblityWhenPassingFocusedElementWhileTabbing
   NAME: XAML.RespectVisiblityWhenPassingFocusedElementWhileTabbing
   FIX_ID: aa12518d-c19e-4b86-a0ae-8ba53f03666b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 251
   TELEMETRY_OFF: True

QUIRK: XAML.IgnoreHitTestVisibilityInTitleBar
   NAME: XAML.IgnoreHitTestVisibilityInTitleBar
   FIX_ID: a67a2b33-165b-4af0-850a-a7bbc9904aad
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 252
   TELEMETRY_OFF: True

QUIRK: XAML.ClearThemeResourcesOnSourceChange
   NAME: XAML.ClearThemeResourcesOnSourceChange
   FIX_ID: 955a91ae-3f7e-448f-89a3-cfad80ca81bc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 253
   TELEMETRY_OFF: True

QUIRK: XAML.ApplicationDotCurrentKeepAlive
   NAME: XAML.ApplicationDotCurrentKeepAlive
   FIX_ID: a7dd7a20-bca6-491f-961b-5e6f790b7c1f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 254
   TELEMETRY_OFF: True

QUIRK: XAML.RenderPageBackgroundOnlyForFullWindowPages
   NAME: XAML.RenderPageBackgroundOnlyForFullWindowPages
   FIX_ID: 168a2b13-ccfc-46c6-b692-9a047df75470
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 255
   TELEMETRY_OFF: True

QUIRK: XAML.SkipLayoutRoundingMarginsDuringMeasure
   NAME: XAML.SkipLayoutRoundingMarginsDuringMeasure
   FIX_ID: 9a286f26-3840-41b1-bdb1-d809ef82a285
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 256
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldLeaveFlyoutOpenOnLostFocus
   NAME: XAML.ShouldLeaveFlyoutOpenOnLostFocus
   FIX_ID: 8d10b66d-28be-4c31-8d55-22f0fe1de8bc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 257
   TELEMETRY_OFF: True

QUIRK: XAML.UseNonBlockingSetSource
   NAME: XAML.UseNonBlockingSetSource
   FIX_ID: b50fa558-88fc-41fa-97d8-05a298f8ca7e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 258
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldControlsUseUnwindowedPopups
   NAME: XAML.ShouldControlsUseUnwindowedPopups
   FIX_ID: 0313d154-cfa0-4603-bd62-b43749fe8d8a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750961565696
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 259
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldDisableShadowOnFlyoutPresenter
   NAME: XAML.ShouldDisableShadowOnFlyoutPresenter
   FIX_ID: 0aa70ba3-7754-463b-aac7-78746b20c5bc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750961565696
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 260
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldNotPropagateTypeInformationForCustomProvideValue
   NAME: XAML.ShouldNotPropagateTypeInformationForCustomProvideValue
   FIX_ID: cc1b7aa5-cc02-4aae-bbed-4629e40e2a94
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750961565696
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 261
   TELEMETRY_OFF: True

QUIRK: XAML.BlockXamlIslands
   NAME: XAML.BlockXamlIslands
   FIX_ID: 57064b35-be7d-4111-a3d0-ff077347f207
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750961565696
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 262
   TELEMETRY_OFF: True

QUIRK: XAML.IgnoreInvalidNumberOfWeeksInViewInMarkup
   NAME: XAML.IgnoreInvalidNumberOfWeeksInViewInMarkup
   FIX_ID: ffaffb48-f122-43b9-9f15-cf7e328ed1dd
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750961565696
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 263
   TELEMETRY_OFF: True

QUIRK: XAML.AllowVisualStateTransitionOnUnsetSetterValue
   NAME: XAML.AllowVisualStateTransitionOnUnsetSetterValue
   FIX_ID: 2baa99e3-080b-4074-b5e5-c2b6677dc674
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750961565696
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 264
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldSkipCutCopyPasteEventRaisingOnTextRangeAPICalls
   NAME: XAML.ShouldSkipCutCopyPasteEventRaisingOnTextRangeAPICalls
   FIX_ID: fa11bfdb-8bfa-49c1-a6c0-c8923caa2758
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750961565696
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 265
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldRecycleDependencyPropertyChangedEventArgs
   NAME: XAML.ShouldRecycleDependencyPropertyChangedEventArgs
   FIX_ID: 299eaa60-3667-4079-9f73-c7341ab5530e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 266
   TELEMETRY_OFF: True

QUIRK: XAML.ShouldSkipCachingIsAnimationsEnabledCheck
   NAME: XAML.ShouldSkipCachingIsAnimationsEnabledCheck
   FIX_ID: 4a789997-e8fb-448c-8a08-b6887e5a550d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 267
   TELEMETRY_OFF: True

QUIRK: XAML.LegacyFocusOffThreadWebView
   NAME: XAML.LegacyFocusOffThreadWebView
   FIX_ID: af2e601e-4716-4e6f-9558-8692448900cc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814751052529664
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 268
   TELEMETRY_OFF: True

QUIRK: XAML.UseDropShadowsByDefault
   NAME: XAML.UseDropShadowsByDefault
   FIX_ID: 91dfef22-00b1-42de-b48a-486225921c0a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814751159812096
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 269
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotUseDWriteTypographicModel
   NAME: XAML.DoNotUseDWriteTypographicModel
   FIX_ID: f0bfe02c-6cbc-4572-b14b-31aeda301ee6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814751159812096
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 270
   TELEMETRY_OFF: True

QUIRK: XAML.UseSegoeMDL2
   NAME: XAML.UseSegoeMDL2
   FIX_ID: 53884456-d6f7-4ecf-a4d5-2e957c400e0c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814751159812096
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 271
   TELEMETRY_OFF: True

QUIRK: XAML.UsePre21H1ThemeResources
   NAME: XAML.UsePre21H1ThemeResources
   FIX_ID: 789ef77d-f857-4635-a283-c98d440d0d3a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814751159222272
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 272
   TELEMETRY_OFF: True

QUIRK: XAML.DoNotUseContentDialogSmokeLayerBackgroundTemplatePart
   NAME: XAML.DoNotUseContentDialogSmokeLayerBackgroundTemplatePart
   FIX_ID: a38f4652-56a1-5ece-b4d9-1eb58cb00c0d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814751159812096
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 273
   TELEMETRY_OFF: True

QUIRK: XAML.AllowToolTipDismissTimer
   NAME: XAML.AllowToolTipDismissTimer
   FIX_ID: b329093c-15cf-4ef2-89f9-b12589325a1c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814751159222272
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 274
   TELEMETRY_OFF: True

QUIRK: XAML.IgnoreFocusedElementLeavingTree
   NAME: XAML.IgnoreFocusedElementLeavingTree
   FIX_ID: a76d7a2a-ac56-5915-9611-1e6f7d0b7d1d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814751159812096
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 275
   TELEMETRY_OFF: True

QUIRK: XAML.InlineAppBarOpensUpByDefault
   NAME: XAML.InlineAppBarOpensUpByDefault
   FIX_ID: 225d09e6-a2d0-4b9d-b242-1d0d1bfdd59c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814751159222272
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 276
   TELEMETRY_OFF: True

QUIRK: XAML.AllowButtonFlyoutReopeningThroughLightDismiss
   NAME: XAML.AllowButtonFlyoutReopeningThroughLightDismiss
   FIX_ID: 7b35256a-c61e-4b28-8872-a98a0cbb0a05
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814751159222272
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 2
   QUIRK_CODE_ID: 277
   TELEMETRY_OFF: True

QUIRK: WRL.PropagateErrorsFromDelegates
   NAME: WRL.PropagateErrorsFromDelegates
   FIX_ID: 788b9d7f-3c18-4fbe-82c9-9b5a8e76f1bb
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 3
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: WRL.PropagateErrorsFromDelegatesOutOfProc
   NAME: WRL.PropagateErrorsFromDelegatesOutOfProc
   FIX_ID: c5a9e717-0b68-4282-b8b6-294d6b78d6ba
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 3
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: WRL.Quirk2
   NAME: WRL.Quirk2
   FIX_ID: 0c2ffdc1-4de3-40c1-8d25-ec093bfeb79b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 3
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: WRL.Quirk3
   NAME: WRL.Quirk3
   FIX_ID: decb67c5-9a2c-43fb-bb8e-9723f29ff7ed
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 3
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: WRL.Quirk4
   NAME: WRL.Quirk4
   FIX_ID: bf9b9614-a01d-4750-acef-906389f100a3
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 3
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: WRL.Quirk5
   NAME: WRL.Quirk5
   FIX_ID: a6631110-63d0-4bd8-ae5f-9d293a9190d7
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 3
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: WRL.Quirk6
   NAME: WRL.Quirk6
   FIX_ID: 30e1cc13-389a-471b-9c90-849a63bfd8d0
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 3
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: WRL.Quirk7
   NAME: WRL.Quirk7
   FIX_ID: d87582f2-238b-41f3-8143-b139757d59b3
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 3
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: WRL.Quirk8
   NAME: WRL.Quirk8
   FIX_ID: a36b07e5-ff60-48c0-9390-bda739343529
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 3
   QUIRK_CODE_ID: 8
   TELEMETRY_OFF: True

QUIRK: NTCore.AllowNestedProcessEvents
   NAME: NTCore.AllowNestedProcessEvents
   FIX_ID: 42e4d7c4-60cc-40f1-b0fe-a38e3a3c2f18
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 4
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: NTCore.MitigateSpuriousMsgWake
   NAME: NTCore.MitigateSpuriousMsgWake
   FIX_ID: 8ea7c056-d947-48fe-a683-96d67b90aba7
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 4
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: NTCore.EnhancedWindowingSupport
   NAME: NTCore.EnhancedWindowingSupport
   FIX_ID: 13d07792-fabc-429b-83c6-ee05f6b9766b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 4
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: NTCore.Quirk4
   NAME: NTCore.Quirk4
   FIX_ID: 8526047e-a24d-443e-8575-bf19e7d39fcb
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 4
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: NTCore.Quirk5
   NAME: NTCore.Quirk5
   FIX_ID: d2ae919f-9836-4f37-9ddd-a48eec9d815e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 4
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: NTCore.Quirk6
   NAME: NTCore.Quirk6
   FIX_ID: ea313484-c0a0-4865-9040-281457caa9f8
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 4
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: NTCore.Quirk7
   NAME: NTCore.Quirk7
   FIX_ID: 6f704a9c-8578-4cd6-9bd9-95b62e118081
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 4
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: NTCore.Quirk8
   NAME: NTCore.Quirk8
   FIX_ID: fdd28a08-b87d-4f4f-99a7-6bcf37d4295f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 4
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: UEX.ImmersiveScaleFactor
   NAME: UEX.ImmersiveScaleFactor
   FIX_ID: dffe01b9-c912-44e1-b558-88465fe3b404
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 5
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: UEX.SecondaryTileDefaultRoamingBehavior
   NAME: UEX.SecondaryTileDefaultRoamingBehavior
   FIX_ID: 1b0ded5a-4048-4d06-b481-2b392579e779
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 5
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: UEX.TileNotificationXMLContent
   NAME: UEX.TileNotificationXMLContent
   FIX_ID: 3de5a8c8-ff74-496c-b4db-749db9e75320
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 5
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: UEX.DeferOnWindowActivatedNotification
   NAME: UEX.DeferOnWindowActivatedNotification
   FIX_ID: f4bf8d0c-a958-44b3-9dfc-93916f360bc5
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 5
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: UEX.IgnoreMinimumSize
   NAME: UEX.IgnoreMinimumSize
   FIX_ID: de5156b7-6ed7-4dfa-8580-bc54a27a2e94
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 5
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: UEX.Quirk5
   NAME: UEX.Quirk5
   FIX_ID: 0f646514-c3b6-4085-83c8-28d3afcd335d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 5
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: UEX.Quirk6
   NAME: UEX.Quirk6
   FIX_ID: 69575625-a2c1-4589-81ac-1a895fc71167
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 5
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: UEX.Quirk7
   NAME: UEX.Quirk7
   FIX_ID: 52bc2d11-0802-4182-a4b5-eb4b262a9b2c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 5
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: UEX.Quirk8
   NAME: UEX.Quirk8
   FIX_ID: dfc3b2e6-391b-4afa-a031-f8dde6149dc1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 5
   QUIRK_CODE_ID: 8
   TELEMETRY_OFF: True

QUIRK: REX.DropOrReorderInputInAsta
   NAME: REX.DropOrReorderInputInAsta
   FIX_ID: 91d7fbae-8061-42bb-9e29-3caf90a52d1a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 6
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: REX.AllowAstaToAstaCalls
   NAME: REX.AllowAstaToAstaCalls
   FIX_ID: 7188ba0e-dc99-4112-95cd-078906f378f9
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 6
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: REX.AppLaunchCOMThresholdPerformanceImprovements
   NAME: REX.AppLaunchCOMThresholdPerformanceImprovements
   FIX_ID: 4243a4fa-1908-4ab4-9466-4d4aed862656
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 6
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: REX.DisableWinrtAsyncChannel
   NAME: REX.DisableWinrtAsyncChannel
   FIX_ID: 9ad9a4d7-e05e-4079-a2b5-648f5f2ffdb1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 6
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: REX.ActivationDEHErrorOverwrite
   NAME: REX.ActivationDEHErrorOverwrite
   FIX_ID: 7c316cad-fb65-4fe7-8905-8e981d6ecc13
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750455758848
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 6
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: REX.Quirk6
   NAME: REX.Quirk6
   FIX_ID: 38ac3eaa-7a5b-4459-9f73-56c15bbe12d6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 6
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: REX.Quirk7
   NAME: REX.Quirk7
   FIX_ID: 94c180a0-3143-45c6-9ba4-d71f5206f1fc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 6
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: REX.Quirk8
   NAME: REX.Quirk8
   FIX_ID: 3e802f34-45de-4a32-bf45-3d90f397e2ac
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 6
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: APPX.LanguageFontMappingUseWin8Data
   NAME: APPX.LanguageFontMappingUseWin8Data
   FIX_ID: ed130755-83ef-45ab-a82c-c45d410cede5
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 7
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: APPX.AppDataBackup
   NAME: APPX.AppDataBackup
   FIX_ID: 9c284ef7-623a-49d6-a604-6bd6afc210bb
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: -1
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 7
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: APPX.DynamicApplicationContentUriRules
   NAME: APPX.DynamicApplicationContentUriRules
   FIX_ID: 733249d7-32bf-44bd-bcc4-5e271d5e4d9f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 7
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: APPX.LicenseInformationIsActive
   NAME: APPX.LicenseInformationIsActive
   FIX_ID: 10b640cf-bae7-48ae-a850-f47d859a9af7
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745231360
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 7
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: APPX.LanguageFontMappingUseWinBlueData
   NAME: APPX.LanguageFontMappingUseWinBlueData
   FIX_ID: ebdfa63c-92d2-45c4-9aa2-5492640a8ff1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 7
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: APPX.CouldMultiUserAppsBehaviorBePossibleForPackage
   NAME: APPX.CouldMultiUserAppsBehaviorBePossibleForPackage
   FIX_ID: fb5f1ec6-e52d-462b-acb2-6f8077719537
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750708203520
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 7
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: APPX.Quirk6
   NAME: APPX.Quirk6
   FIX_ID: 3559f613-f7b2-42c7-8cd8-c16a47d28a18
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 7
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: APPX.Quirk7
   NAME: APPX.Quirk7
   FIX_ID: 56254cec-a1d1-4ec0-989e-0b62ae4e0e1f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 7
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: APPX.Quirk8
   NAME: APPX.Quirk8
   FIX_ID: c050997c-f922-4ab5-99e9-3c98382e6387
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 7
   QUIRK_CODE_ID: 8
   TELEMETRY_OFF: True

QUIRK: UEX_CLX.ToggleBackupFromPackage
   NAME: UEX_CLX.ToggleBackupFromPackage
   FIX_ID: 8d683995-404a-4f1c-8740-933fca97e9f6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 8
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: UEX_CLX.Quirk2
   NAME: UEX_CLX.Quirk2
   FIX_ID: dd633a7c-667c-48ef-9e58-9ba36b1e411d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 8
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: UEX_CLX.Quirk3
   NAME: UEX_CLX.Quirk3
   FIX_ID: 77991ed1-438f-4d99-88e4-42329fa3c28d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 8
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: UEX_CLX.Quirk4
   NAME: UEX_CLX.Quirk4
   FIX_ID: 02998e6b-f263-4fe8-8288-5004850a5100
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 8
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: UEX_CLX.Quirk5
   NAME: UEX_CLX.Quirk5
   FIX_ID: 7630d83b-5143-4019-9297-7fdc29c704d5
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 8
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: UEX_CLX.Quirk6
   NAME: UEX_CLX.Quirk6
   FIX_ID: dcea044c-0b78-437e-8d64-9d808eddaa64
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 8
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: UEX_CLX.Quirk7
   NAME: UEX_CLX.Quirk7
   FIX_ID: b7b9a8d1-81c7-4454-af14-c01866e980dd
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 8
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: UEX_CLX.Quirk8
   NAME: UEX_CLX.Quirk8
   FIX_ID: c175bdee-4a0c-4725-80df-28f4071a4648
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 8
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: SHELL.AppViewStateAndCharms
   NAME: SHELL.AppViewStateAndCharms
   FIX_ID: 19f33f68-7554-4036-8c9e-2271bb00d296
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: SHELL.TerminateAppOnFinalViewClose
   NAME: SHELL.TerminateAppOnFinalViewClose
   FIX_ID: bb5a842e-950d-4ca9-8e76-a31b54620fc9
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: SHELL.FullScreenPortraitViewState
   NAME: SHELL.FullScreenPortraitViewState
   FIX_ID: 7613a2a7-d3d6-4798-8164-96fa3fe71d55
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: SHELL.FullScreen8xLegacyApp
   NAME: SHELL.FullScreen8xLegacyApp
   FIX_ID: 1ff91c01-611d-4ce5-8a33-5929d9db28c0
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: SHELL.HasWin81WindowingBehavior
   NAME: SHELL.HasWin81WindowingBehavior
   FIX_ID: b33d82b6-de77-4de1-8b50-3b4559027775
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: SHELL.UseWin8xCompatibilityScaling
   NAME: SHELL.UseWin8xCompatibilityScaling
   FIX_ID: 8da76d96-7975-41d8-a336-2b5526936a51
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: SHELL.ShowLegacyActionsMenu
   NAME: SHELL.ShowLegacyActionsMenu
   FIX_ID: 32badd80-a05e-402b-a0f9-c3e3fcfd4e2c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: SHELL.UseWindowsPhone81ScalingAlgorithm
   NAME: SHELL.UseWindowsPhone81ScalingAlgorithm
   FIX_ID: 525306bb-b658-45c7-9c58-6e11000ace28
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: SHELL.UseWindows81ScalingAlgorithm
   NAME: SHELL.UseWindows81ScalingAlgorithm
   FIX_ID: d2abae33-f0e3-426f-8a4c-fa474f2a014a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 8
   TELEMETRY_OFF: True

QUIRK: SHELL.DontAllowOnSecondaryDisplay
   NAME: SHELL.DontAllowOnSecondaryDisplay
   FIX_ID: 8566f775-cf37-4f7f-b1f9-8d5b21a978b1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 9
   TELEMETRY_OFF: True

QUIRK: SHELL.UseMobileWebScalingPlateaus
   NAME: SHELL.UseMobileWebScalingPlateaus
   FIX_ID: ade90670-8228-45d3-a269-2ba422eda3e1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 10
   TELEMETRY_OFF: True

QUIRK: SHELL.DoNotAutoRotateApplication
   NAME: SHELL.DoNotAutoRotateApplication
   FIX_ID: 4bbfc277-2c10-487b-98bc-8ea8d675e9b7
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 11
   TELEMETRY_OFF: True

QUIRK: SHELL.IncludeNameWithLogoOnLiveTileNotification
   NAME: SHELL.IncludeNameWithLogoOnLiveTileNotification
   FIX_ID: a946dfc3-3170-48bd-b440-091d235c45e2
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 12
   TELEMETRY_OFF: True

QUIRK: SHELL.Force100PercentScaling
   NAME: SHELL.Force100PercentScaling
   FIX_ID: 20e9bdb3-88d0-48ab-a1a0-3a6ea7ea8c54
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745231359
   EDITION: 2048
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 13
   TELEMETRY_OFF: True

QUIRK: SHELL.IgnoreHighContrastSettings
   NAME: SHELL.IgnoreHighContrastSettings
   FIX_ID: d1169a7b-60d8-4545-9b0c-a4da341b05b4
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: -1
   EDITION: 2048
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 14
   TELEMETRY_OFF: True

QUIRK: SHELL.NoTouchHover
   NAME: SHELL.NoTouchHover
   FIX_ID: 0be7429b-64c2-4280-8f5c-522f96e9986c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 1024
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 15
   TELEMETRY_OFF: True

QUIRK: SHELL.DontCacheTitleBarSettings
   NAME: SHELL.DontCacheTitleBarSettings
   FIX_ID: 7e468304-d3ce-4d66-bdc5-90eda6bb76cb
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750704926720
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 16
   TELEMETRY_OFF: True

QUIRK: SHELL.UsePreferredStandaloneSize
   NAME: SHELL.UsePreferredStandaloneSize
   FIX_ID: 0d496cb7-f13e-454b-9b26-4ae8f89a2d10
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 17
   TELEMETRY_OFF: True

QUIRK: SHELL.ForceNonAgileThemeHandlerCallback
   NAME: SHELL.ForceNonAgileThemeHandlerCallback
   FIX_ID: d8b5e2e6-f102-4a11-b633-f788a2fed270
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 9
   QUIRK_CODE_ID: 18
   TELEMETRY_OFF: True

QUIRK: WinStore.RnRMaxOSVersionOlderthanBlue
   NAME: WinStore.RnRMaxOSVersionOlderthanBlue
   FIX_ID: 5e23102a-74b9-4118-ad7c-e5ebc246e061
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 10
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: WinStore.Quirk2
   NAME: WinStore.Quirk2
   FIX_ID: 13681701-c478-4edf-8f93-06fd29072d88
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 10
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: WinStore.Quirk3
   NAME: WinStore.Quirk3
   FIX_ID: b90282e8-150b-4e17-abeb-2771439eecd3
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 10
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: WinStore.Quirk4
   NAME: WinStore.Quirk4
   FIX_ID: 06e33dcd-e572-484a-88fe-6a0200192b56
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 10
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: WinStore.Quirk5
   NAME: WinStore.Quirk5
   FIX_ID: 59a5e092-d882-4541-b1d4-2b43b6470341
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 10
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: WinStore.Quirk6
   NAME: WinStore.Quirk6
   FIX_ID: e8668f7c-e6b4-4cca-af16-a7eb5862469f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 10
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: WinStore.Quirk7
   NAME: WinStore.Quirk7
   FIX_ID: ca3394a0-031e-4476-ba77-ea26b32125b6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 10
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: WinStore.Quirk8
   NAME: WinStore.Quirk8
   FIX_ID: 179d6686-4d53-4d66-a35c-75d455b94fd1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 10
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: MPT.SupportsProtectedPlaybackFailed
   NAME: MPT.SupportsProtectedPlaybackFailed
   FIX_ID: 7ea30d7b-b07a-4557-9c34-40c4a68616d1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 11
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: MPT.LowLatencyAudioRecord
   NAME: MPT.LowLatencyAudioRecord
   FIX_ID: 6757b38f-828b-4629-90a4-8bbfee2f6f4b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 11
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: MPT.AudioStreamCategories
   NAME: MPT.AudioStreamCategories
   FIX_ID: 420e0663-2aca-41b4-945d-e14cfd1144f7
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 11
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: MPT.IsVirtualAudioClientRequired
   NAME: MPT.IsVirtualAudioClientRequired
   FIX_ID: 10e7b1af-0cd3-4101-b782-f6875e249b40
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 11
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: MPT.DisableAudioCommunicationProcessingMode
   NAME: MPT.DisableAudioCommunicationProcessingMode
   FIX_ID: 9cdf3cb9-8652-432c-8a32-46b659f194b7
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 11
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: MPT.BackgroundAudioEnforceSingleAudioDeclaration
   NAME: MPT.BackgroundAudioEnforceSingleAudioDeclaration
   FIX_ID: 1e886923-0656-4853-b094-914ec1793077
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 11
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: MPT.DisableMediaPlaybackListAutoPlaybackItemReset
   NAME: MPT.DisableMediaPlaybackListAutoPlaybackItemReset
   FIX_ID: 48ff973a-387e-4ece-89f7-04efb8182eca
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 11
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: MPT.Quirk8
   NAME: MPT.Quirk8
   FIX_ID: cada2484-7384-49e3-a340-3bb44630eb05
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 11
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: MPT.Quirk9
   NAME: MPT.Quirk9
   FIX_ID: 21a157e0-f967-4ce8-b709-e897b7aff9a9
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 11
   QUIRK_CODE_ID: 8
   TELEMETRY_OFF: True

QUIRK: DCON.AdjustSensorAxesForPortraitDevices
   NAME: DCON.AdjustSensorAxesForPortraitDevices
   FIX_ID: d67c7ccb-a85c-4bfa-83d9-6111e51824bc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 12
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: DCON.GeolocationPositionHeadingNull
   NAME: DCON.GeolocationPositionHeadingNull
   FIX_ID: 44aacc4e-b92b-4364-8139-5d0e6844545a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 12
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: DCON.GeolocationCivicAddressNull
   NAME: DCON.GeolocationCivicAddressNull
   FIX_ID: 245c03e8-685f-4cbb-b882-c4d88029a0c2
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 12
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: DCON.BluetoothBackgroundTaskCapabilities
   NAME: DCON.BluetoothBackgroundTaskCapabilities
   FIX_ID: 1b2d1a2f-85c0-41d0-a9b9-d3b31389d76e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 12
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: DCON.BluetoothAllowRPALAccess
   NAME: DCON.BluetoothAllowRPALAccess
   FIX_ID: 0e19e564-0632-4a7c-bccd-f0e3be22f48b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 12
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: DCON.BluetoothDeviceServiceNameOverride
   NAME: DCON.BluetoothDeviceServiceNameOverride
   FIX_ID: 908a1f82-5667-43ab-8921-59fa34a8f84f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750488002560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 12
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: DCON.BluetoothUseGattDeviceInterfacesForDeviceId
   NAME: DCON.BluetoothUseGattDeviceInterfacesForDeviceId
   FIX_ID: 167560ae-9124-42ce-ada0-a4328e570867
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 12
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: DCON.BluetoothDontUnpublishGattServiceOnSuspend
   NAME: DCON.BluetoothDontUnpublishGattServiceOnSuspend
   FIX_ID: 54de1a68-57e1-416e-b3ae-cd0503ae50f6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 12
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: KPG.BiStrictEntryPointValidation
   NAME: KPG.BiStrictEntryPointValidation
   FIX_ID: 30432285-7052-4e3e-8432-9d6d7c836779
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 13
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: KPG.PLMSuspendDebouncePeriod
   NAME: KPG.PLMSuspendDebouncePeriod
   FIX_ID: 922b77c6-05ba-42cb-a5ff-eba12acebd5f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 13
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: KPG.AllWWABackgroundTasksInAppProcess
   NAME: KPG.AllWWABackgroundTasksInAppProcess
   FIX_ID: 88d5f968-018d-4213-93bb-490eae77b159
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745231360
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 13
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: KPG.SimpleWWABackgroundTasksInBGProcess
   NAME: KPG.SimpleWWABackgroundTasksInBGProcess
   FIX_ID: 16e081bd-c9f9-440e-9cb1-685a0d1c3c33
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 13
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: KPG.Quirk5
   NAME: KPG.Quirk5
   FIX_ID: 84c9477d-3042-464d-bb5c-db133ed95e4c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 13
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: KPG.Quirk6
   NAME: KPG.Quirk6
   FIX_ID: 15c22c29-9563-44d2-92ba-516db737f586
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 13
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: KPG.Quirk7
   NAME: KPG.Quirk7
   FIX_ID: 71ac0998-0001-4e5b-8fd6-e99846585b4c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 13
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: KPG.Quirk8
   NAME: KPG.Quirk8
   FIX_ID: 39bd2b46-eece-4dd6-b261-b1a7916445c0
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 13
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: ACDCTestQuirkComp.Quirk1
   NAME: ACDCTestQuirkComp.Quirk1
   FIX_ID: 3b174bf4-1550-4fd6-817e-eb788671a9cb
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 14
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: ACDCTestQuirkComp.Quirk2
   NAME: ACDCTestQuirkComp.Quirk2
   FIX_ID: c7d7100b-452d-4ebf-857e-8a0d03f9154e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: -1
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 14
   QUIRK_CODE_ID: 1

QUIRK: ACDCTestQuirkComp.Quirk3
   NAME: ACDCTestQuirkComp.Quirk3
   FIX_ID: 90acc3e7-2665-43b1-a3c4-32bf16ef41e7
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 14
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: ACDCTestQuirkComp.Quirk4
   NAME: ACDCTestQuirkComp.Quirk4
   FIX_ID: 3534d6b5-eba8-4c73-8f66-c64589e1e1c8
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688858450198528
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 14
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: WWAHOST.PreventRedraw
   NAME: WWAHOST.PreventRedraw
   FIX_ID: 29386ec0-4e64-4cc3-9692-5b7c4c652f5c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: WWAHOST.UseStaticUserAgentString
   NAME: WWAHOST.UseStaticUserAgentString
   FIX_ID: de295e56-ade9-436c-b926-ced635aab018
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: WWAHOST.DoPaintBehindSplashScreen
   NAME: WWAHOST.DoPaintBehindSplashScreen
   FIX_ID: b46f47d3-c13e-49ff-8abf-f57ac22b18bc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: WWAHOST.UseSingleWindowMRTResolution
   NAME: WWAHOST.UseSingleWindowMRTResolution
   FIX_ID: 23bac94d-b3ad-466a-a659-10660b38dd7d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: WWAHOST.AllowAllApplicationContentUris
   NAME: WWAHOST.AllowAllApplicationContentUris
   FIX_ID: e9d7f966-3870-4af0-84e7-a6b3c68a4c4b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: WWAHOST.AllowAllIframeNavigations
   NAME: WWAHOST.AllowAllIframeNavigations
   FIX_ID: 0ff0e622-439d-4c27-be45-634ef856f987
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: WWAHOST.DontActivateAllCoreWindows
   NAME: WWAHOST.DontActivateAllCoreWindows
   FIX_ID: 97b0e2e7-6174-4a5f-a465-1941c1e0d795
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: WWAHOST.UseFullScreenLauncherAPI
   NAME: WWAHOST.UseFullScreenLauncherAPI
   FIX_ID: 33e093d6-0eb0-426c-b306-724ed9263393
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: WWAHOST.AllowMixedContent
   NAME: WWAHOST.AllowMixedContent
   FIX_ID: e2f9ec0a-5b1f-4aa3-8bb3-43e3349a8ceb
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 8
   TELEMETRY_OFF: True

QUIRK: WWAHOST.FireResizeOnlyOnChange
   NAME: WWAHOST.FireResizeOnlyOnChange
   FIX_ID: 4ca12f02-26d5-471e-8ad4-5b7c4a7256f7
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 9
   TELEMETRY_OFF: True

QUIRK: WWAHOST.IgnoreTransparentBackgroundColorInWebview
   NAME: WWAHOST.IgnoreTransparentBackgroundColorInWebview
   FIX_ID: ebb14541-3bfb-40a2-9bac-8371ff2f3edb
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 10
   TELEMETRY_OFF: True

QUIRK: WWAHOST.IsTopLevelNavigationRestrictedToPackagedContent
   NAME: WWAHOST.IsTopLevelNavigationRestrictedToPackagedContent
   FIX_ID: e15d41f8-c155-4479-9d63-4de4f9884d26
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 11
   TELEMETRY_OFF: True

QUIRK: WWAHOST.UseLegacyTridentEngineVersion
   NAME: WWAHOST.UseLegacyTridentEngineVersion
   FIX_ID: 9f609f30-a09e-44ed-88cb-f6c6d2da236b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 12
   TELEMETRY_OFF: True

QUIRK: WWAHOST.ActivateCoreWindowInAllActivations
   NAME: WWAHOST.ActivateCoreWindowInAllActivations
   FIX_ID: f612f12f-3263-4a0d-8575-45d99fd1e94c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 13
   TELEMETRY_OFF: True

QUIRK: WWAHOST.OnlyAllowMsAppxUrlsToCloseWindows
   NAME: WWAHOST.OnlyAllowMsAppxUrlsToCloseWindows
   FIX_ID: 54021f34-0a00-45b1-8757-e3e2abd2dda9
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 14
   TELEMETRY_OFF: True

QUIRK: WWAHOST.Quirk15
   NAME: WWAHOST.Quirk15
   FIX_ID: 57fcb043-52a8-4fd0-9ad0-3957d915a4c0
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 15
   TELEMETRY_OFF: True

QUIRK: WWAHOST.Quirk16
   NAME: WWAHOST.Quirk16
   FIX_ID: 3e011be4-70dc-4911-a80e-c75e8bee9e66
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 15
   QUIRK_CODE_ID: 16
   TELEMETRY_OFF: True

QUIRK: DXGI.Quirk5601080x1920As720x1280
   NAME: DXGI.Quirk1080x1920As720x1280
   FIX_ID: b5939a12-8764-4576-8ec0-8e038666d313
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 16
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: DXGI.Quirk540x960As480x800
   NAME: DXGI.Quirk540x960As480x800
   FIX_ID: f1d2af20-8df4-4478-9033-57ed1d90f3ff
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 16
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: DXGI.EmulateSwapEffectDiscard
   NAME: DXGI.EmulateSwapEffectDiscard
   FIX_ID: 1c8a2a18-e4b8-414f-b763-c2f9792ee370
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 16
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: DXGI.EmulateLegacySwapChainLifetime
   NAME: DXGI.EmulateLegacySwapChainLifetime
   FIX_ID: 76d86ac5-f3d0-4061-9ec3-6d0cfea40e9e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 16
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: DXGI.EmulateLegacyBackBufferCount
   NAME: DXGI.EmulateLegacyBackBufferCount
   FIX_ID: dd6ac80c-b61d-473f-90c0-4abef0987267
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 16
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: DXGI.EmulateLegacyDefaultDeviceMaxFrameLatency
   NAME: DXGI.EmulateLegacyDefaultDeviceMaxFrameLatency
   FIX_ID: 52f0c000-b72b-4ac6-af84-b8ee0178d314
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688867040133120
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 16
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: DXGI.Quirk1440x2560As720x1280
   NAME: DXGI.Quirk1440x2560As720x1280
   FIX_ID: 688bc727-a361-4647-ba69-c2bc6e3caafa
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 16
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: DXGI.AlphaTexturesUseIncorrectSwap
   NAME: DXGI.AlphaTexturesUseIncorrectSwap
   FIX_ID: c0be143c-28f8-4da2-982d-30ea59962a7b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 2048
   QUIRK_COMPONENT_CODE_ID: 16
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: DXGI.D3D12EarlyAdopter
   NAME: DXGI.D3D12EarlyAdopter
   FIX_ID: 1ba5a6b9-fb26-425a-9a95-edb12d3cebb4
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 16
   QUIRK_CODE_ID: 8
   TELEMETRY_OFF: True

QUIRK: DXGI.D3D12EarlyAdopterDesktopWorkaround
   NAME: DXGI.D3D12EarlyAdopterDesktopWorkaround
   FIX_ID: cf70bfe4-442a-44da-836b-c56f64597bb3
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 16
   QUIRK_CODE_ID: 9
   TELEMETRY_OFF: True

QUIRK: DXGI.UMAToNUMA
   NAME: DXGI.UMAToNUMA
   FIX_ID: d8ea5c17-c72d-46c5-93b5-d354717f523d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 16
   QUIRK_CODE_ID: 10
   TELEMETRY_OFF: True

QUIRK: AppModel.UseUAPForLegacyImmersiveApplication
   NAME: AppModel.UseUAPForLegacyImmersiveApplication
   FIX_ID: a6c87e07-2a11-4270-8ceb-ac15720cc4e7
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: AppModel.UseEmptyHostLegacyBehavior
   NAME: AppModel.UseEmptyHostLegacyBehavior
   FIX_ID: 0cddf601-f491-4f3b-8ff5-de15559b2035
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: AppModel.UsePickerContinuationAPIs
   NAME: AppModel.UsePickerContinuationAPIs
   FIX_ID: f49325e4-2350-41db-9cb5-69c5bb04f04f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: AppModel.DoNotCallSetForegroundWindow
   NAME: AppModel.DoNotCallSetForegroundWindow
   FIX_ID: 1a49ad53-c091-451d-88fa-153c43354e51
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: AppModel.AppPrelaunchDisabled
   NAME: AppModel.AppPrelaunchDisabled
   FIX_ID: 37dd29ab-4e97-40db-94b6-f77db49576cb
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: AppModel.AllowMultiInstanceForContractActivation
   NAME: AppModel.AllowMultiInstanceForContractActivation
   FIX_ID: 46598d46-ecd1-4e8d-8c61-f089b7293dac
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 81940
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: AppModel.AddTrailingSpaceInToastNotificationDeclineCommand
   NAME: AppModel.AddTrailingSpaceInToastNotificationDeclineCommand
   FIX_ID: 86c756eb-1659-4a11-abc6-dc8d7b0ea739
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: AppModel.RemapGamePadVKeys
   NAME: AppModel.RemapGamePadVKeys
   FIX_ID: 858c4d45-87fb-4952-90de-6ca8cb476e83
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 2048
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: AppModel.AppRequiresContentUpdate
   NAME: AppModel.AppRequiresContentUpdate
   FIX_ID: e8d22e7e-f0c0-4d61-b1dd-9abf54a1f2fc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 2048
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 8
   TELEMETRY_OFF: True

QUIRK: AppModel.RedirectFocusedAppChangedEvent
   NAME: AppModel.RedirectFocusedAppChangedEvent
   FIX_ID: 5d3c6cb4-e875-4323-bd31-bb589082ee8c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 2048
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 9
   TELEMETRY_OFF: True

QUIRK: AppModel.AppIsNoLongerSupportedOnXboxOne
   NAME: AppModel.AppIsNoLongerSupportedOnXboxOne
   FIX_ID: a4bd41f9-cd34-4c3f-abee-df9acae0dd0e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 2048
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 10
   TELEMETRY_OFF: True

QUIRK: AppModel.AppUsesLegacyMemoryLimit
   NAME: AppModel.AppUsesLegacyMemoryLimit
   FIX_ID: 2f79545f-d7ad-4771-bfd1-a2fb46092378
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 2048
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 11
   TELEMETRY_OFF: True

QUIRK: AppModel.MshtmlShouldNotPreserveOnLoadState
   NAME: AppModel.MshtmlShouldNotPreserveOnLoadState
   FIX_ID: 9b0f110a-00b5-49db-91d2-671c621a5770
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 2048
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 12
   TELEMETRY_OFF: True

QUIRK: AppModel.SMTCDisableCapabilityFiltering
   NAME: AppModel.SMTCDisableCapabilityFiltering
   FIX_ID: f1142d23-c4aa-4074-87ee-526b566b938b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 2080
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 13
   TELEMETRY_OFF: True

QUIRK: AppModel.UseTHBackgroundAccessStatusValues
   NAME: AppModel.UseTHBackgroundAccessStatusValues
   FIX_ID: b4d64ee0-d421-4e9d-ab32-f7cfbf87eafc
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750702305280
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 14
   TELEMETRY_OFF: True

QUIRK: AppModel.DisableGamepadAutoBackNavigateForLegacyApp
   NAME: AppModel.DisableGamepadAutoBackNavigateForLegacyApp
   FIX_ID: 60fe272d-12f7-412d-8635-8c815e7f1ee9
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750460936192
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 15
   TELEMETRY_OFF: True

QUIRK: AppModel.DisableGamepadAutoBackNavigateForLegacyXboxApp
   NAME: AppModel.DisableGamepadAutoBackNavigateForLegacyXboxApp
   FIX_ID: 1401fdcb-e084-408e-a113-57298e598801
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: -1
   EDITION: 6144
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 16
   TELEMETRY_OFF: True

QUIRK: AppModel.SupressSuspendResumeHostForBackgroundActivation
   NAME: AppModel.SupressSuspendResumeHostForBackgroundActivation
   FIX_ID: be804874-66fb-449a-b793-37b4f18d498e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750702305280
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 17
   TELEMETRY_OFF: True

QUIRK: AppModel.SuppressEmptyHostCachingForApp
   NAME: AppModel.SuppressEmptyHostCachingForApp
   FIX_ID: 1869b24c-9e01-44d8-b2c4-5f847a5e2477
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750702305280
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 18
   TELEMETRY_OFF: True

QUIRK: AppModel.MemoryUsageLevelLowMediumHighOnly
   NAME: AppModel.MemoryUsageLevelLowMediumHighOnly
   FIX_ID: 6354739a-7d9f-4dc9-acf1-c8dcccf354d9
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750702305280
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 19
   TELEMETRY_OFF: True

QUIRK: AppModel.DisableGamepadAutoSystemBackNavigate
   NAME: AppModel.DisableGamepadAutoSystemBackNavigate
   FIX_ID: b13bb2f8-b92d-4f13-9cec-e98b44f70bdf
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 20
   TELEMETRY_OFF: True

QUIRK: AppModel.DisableHolographicSpaceCreateForCoreWindow
   NAME: AppModel.DisableHolographicSpaceCreateForCoreWindow
   FIX_ID: 4cc8db63-7fc1-4163-b344-600185b236aa
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 21
   TELEMETRY_OFF: True

QUIRK: AppModel.MapDisabledByPolicyToDisabledForStartupTaskState
   NAME: AppModel.MapDisabledByPolicyToDisabledForStartupTaskState
   FIX_ID: 7c8977cc-e336-4415-9449-6e45191ed663
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750754340864
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 22
   TELEMETRY_OFF: True

QUIRK: AppModel.1080pXboxAppScalingFor4k
   NAME: AppModel.1080pXboxAppScalingFor4k
   FIX_ID: 6219d935-7dbf-4966-8ed1-af7722ca9e34
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750754340864
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 23
   TELEMETRY_OFF: True

QUIRK: AppModel.BlockUIForStartupTaskRequestEnableAsync
   NAME: AppModel.BlockUIForStartupTaskRequestEnableAsync
   FIX_ID: acf2a17f-56a0-4897-be0f-77a09051cebb
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750754340864
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 24
   TELEMETRY_OFF: True

QUIRK: AppModel.BlockRegistryAsSourceType
   NAME: AppModel.BlockRegistryAsSourceType
   FIX_ID: 53ee6207-ba83-404e-80a6-e18e688a93eb
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750754340864
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 25
   TELEMETRY_OFF: True

QUIRK: AppModel.MapEnabledByPolicyToEnabledForStartupTaskState
   NAME: AppModel.MapEnabledByPolicyToEnabledForStartupTaskState
   FIX_ID: d0181119-9407-4cf1-ace8-0ea9a338cd94
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750881284096
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 26
   TELEMETRY_OFF: True

QUIRK: AppModel.AllowLauncherUseFromNonUIThread
   NAME: AppModel.AllowLauncherUseFromNonUIThread
   FIX_ID: d5eacb10-b6e4-4004-b340-6048382f9196
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750920540160
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 27
   TELEMETRY_OFF: True

QUIRK: AppModel.RaiseSplashScreenDismissedAsynchronously
   NAME: AppModel.RaiseSplashScreenDismissedAsynchronously
   FIX_ID: 68c0afbb-7f9f-40e9-b433-e2f335a9d5bf
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 17
   QUIRK_CODE_ID: 28
   TELEMETRY_OFF: True

QUIRK: Networking.ReplaceUrlLocales
   NAME: Networking.ReplaceUrlLocales
   FIX_ID: 34940aea-8a30-4482-aee0-0eac3a5f10b2
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688859192328193
   EDITION: 4096
   QUIRK_COMPONENT_CODE_ID: 18
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: Networking.DoNotGenerateSecureDeviceAddressBufferChangedEvents
   NAME: Networking.DoNotGenerateSecureDeviceAddressBufferChangedEvents
   FIX_ID: 0cf63019-e1c4-41d7-937b-0131df7631ec
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688859211333633
   EDITION: 4096
   QUIRK_COMPONENT_CODE_ID: 18
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: Networking.GetHostNamesReturnsLegacyHostname
   NAME: Networking.GetHostNamesReturnsLegacyHostname
   FIX_ID: cbdd460d-721b-486b-8872-7fdea46423e7
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688859211988993
   EDITION: 4096
   QUIRK_COMPONENT_CODE_ID: 18
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: Networking.NetworkConnectivityLevelHasXboxLiveAccessOnSra
   NAME: Networking.NetworkConnectivityLevelHasXboxLiveAccessOnSra
   FIX_ID: 0d58dd75-2a25-4cc6-80f3-c6c158e4f18d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 2048
   QUIRK_COMPONENT_CODE_ID: 18
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: Networking.NetworkConnectivityLevelHasXboxLiveAccessOnEra
   NAME: Networking.NetworkConnectivityLevelHasXboxLiveAccessOnEra
   FIX_ID: cd13ef6d-8190-444b-9f4c-d34887557ad4
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: -1
   EDITION: 4096
   QUIRK_COMPONENT_CODE_ID: 18
   QUIRK_CODE_ID: 4
   TELEMETRY_OFF: True

QUIRK: Networking.InsertXboxLiveAuthorizationToken
   NAME: Networking.InsertXboxLiveAuthorizationToken
   FIX_ID: da4a630d-cb41-4d58-b02c-af16d1ab184d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 2048
   QUIRK_COMPONENT_CODE_ID: 18
   QUIRK_CODE_ID: 5
   TELEMETRY_OFF: True

QUIRK: Networking.DoNotUseExclusiveBind
   NAME: Networking.DoNotUseExclusiveBind
   FIX_ID: 0ef8db2a-d9d9-4331-8fd6-48fcecd6c666
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 10
   QUIRK_COMPONENT_CODE_ID: 18
   QUIRK_CODE_ID: 6
   TELEMETRY_OFF: True

QUIRK: Networking.DoNotSupportXgzipSra
   NAME: Networking.DoNotSupportXgzipSra
   FIX_ID: 767cc17d-3cba-4860-8950-c55298329a04
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 2048
   QUIRK_COMPONENT_CODE_ID: 18
   QUIRK_CODE_ID: 7
   TELEMETRY_OFF: True

QUIRK: Networking.DoNotSupportXgzipEra
   NAME: Networking.DoNotSupportXgzipEra
   FIX_ID: 99eac5fd-376f-4867-9544-448a6433d33b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710368208
   EDITION: 4096
   QUIRK_COMPONENT_CODE_ID: 18
   QUIRK_CODE_ID: 8
   TELEMETRY_OFF: True

QUIRK: Networking.DoNotSupportHttp2Sra
   NAME: Networking.DoNotSupportHttp2Sra
   FIX_ID: 98f6bb95-6712-4dcd-be71-aac9b025e01c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 2048
   QUIRK_COMPONENT_CODE_ID: 18
   QUIRK_CODE_ID: 9
   TELEMETRY_OFF: True

QUIRK: Networking.DoNotSupportHttp2Era
   NAME: Networking.DoNotSupportHttp2Era
   FIX_ID: 794ddb34-616c-4dbb-a4ef-a71e45f208d1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710368208
   EDITION: 4096
   QUIRK_COMPONENT_CODE_ID: 18
   QUIRK_CODE_ID: 10
   TELEMETRY_OFF: True

QUIRK: Networking.ForceTLS10_11_12SRA
   NAME: Networking.ForceTLS10_11_12SRA
   FIX_ID: cbb31962-0d49-40fa-be2a-3be2fc045890
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814751164466152
   EDITION: 2080
   QUIRK_COMPONENT_CODE_ID: 18
   QUIRK_CODE_ID: 11
   TELEMETRY_OFF: True

QUIRK: Networking.ForceTLS10_11_12ERA
   NAME: Networking.ForceTLS10_11_12ERA
   FIX_ID: f07a3f91-b38a-4d48-ae17-7d65f3fc9010
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750890005485
   EDITION: 4096
   QUIRK_COMPONENT_CODE_ID: 18
   QUIRK_CODE_ID: 12
   TELEMETRY_OFF: True

QUIRK: Storage.UseUntrimmedLocalStoragePaths
   NAME: Storage.UseUntrimmedLocalStoragePaths
   FIX_ID: 181bd7c7-3bc5-4bd5-9c89-f975b39c78d6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688859220508673
   EDITION: 4096
   QUIRK_COMPONENT_CODE_ID: 19
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: Storage.LongPathUnaware
   NAME: Storage.LongPathUnaware
   FIX_ID: b20f2107-e3a8-4e04-8685-500d2fc7039d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750835343360
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 19
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: Storage.DoNotExposeSharingViolationsToAppx
   NAME: Storage.DoNotExposeSharingViolationsToAppx
   FIX_ID: 164ceaa6-ee96-4c9c-b7f9-552c46aeab08
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814750710431744
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 19
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: WEBPLATFORM.DisableEdgeWebPlatform
   NAME: WEBPLATFORM.DisableEdgeWebPlatform
   FIX_ID: 1c71bfdd-5074-45d6-b36a-a7b812a49b91
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 20
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: WEBPLATFORM.Quirk2
   NAME: WEBPLATFORM.Quirk2
   FIX_ID: 5bb60e9d-0771-44be-86aa-1f53220d6d99
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 20
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: WEBPLATFORM.Quirk3
   NAME: WEBPLATFORM.Quirk3
   FIX_ID: 428c7cb2-c594-4c7d-976b-a33c76d509fa
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 20
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: WEBPLATFORM.Quirk4
   NAME: WEBPLATFORM.Quirk4
   FIX_ID: 3fe21e11-3b0d-47c2-b46a-7c2fdef3c4f3
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 20
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: COMPONENT21.Quirk1
   NAME: COMPONENT21.Quirk1
   FIX_ID: 45c026ad-7c13-4d15-b439-14ccad656410
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 21
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: COMPONENT21.Quirk2
   NAME: COMPONENT21.Quirk2
   FIX_ID: 25e36228-64f9-4d43-ac94-700c21e86592
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 21
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: COMPONENT21.Quirk3
   NAME: COMPONENT21.Quirk3
   FIX_ID: 1039fb53-47f1-45ad-b90a-b32eaeafeccd
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 21
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: COMPONENT21.Quirk4
   NAME: COMPONENT21.Quirk4
   FIX_ID: 41c0fb6f-ceb2-484e-ba11-bcd1047021ca
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 21
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: COMPONENT22.Quirk1
   NAME: COMPONENT22.Quirk1
   FIX_ID: 68483dd7-e47f-44df-ba06-00af1aab1735
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 22
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: COMPONENT22.Quirk2
   NAME: COMPONENT22.Quirk2
   FIX_ID: 9275b401-cc5f-4c73-a626-0ed24cb57e4b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 22
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: COMPONENT22.Quirk3
   NAME: COMPONENT22.Quirk3
   FIX_ID: cfb66fd7-6a94-478b-85bf-f07180456f36
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 22
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: COMPONENT22.Quirk4
   NAME: COMPONENT22.Quirk4
   FIX_ID: 49adc1fe-df31-4156-b7ba-1dc70f67c29b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 22
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: COMPONENT23.Quirk1
   NAME: COMPONENT23.Quirk1
   FIX_ID: b6573b3b-61c0-404c-a3c9-3d627e3622e4
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 23
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: COMPONENT23.Quirk2
   NAME: COMPONENT23.Quirk2
   FIX_ID: 69fca910-dce0-4197-866f-1b51536acd78
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 23
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: COMPONENT23.Quirk3
   NAME: COMPONENT23.Quirk3
   FIX_ID: b58ed308-d155-4348-b469-0768baa1f9f1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 23
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: COMPONENT23.Quirk4
   NAME: COMPONENT23.Quirk4
   FIX_ID: 50611190-3f84-4932-becc-8f2467c38c6c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 23
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: COMPONENT24.Quirk1
   NAME: COMPONENT24.Quirk1
   FIX_ID: aeca79a9-8abf-4983-b265-d1ff13678a94
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 24
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: COMPONENT24.Quirk2
   NAME: COMPONENT24.Quirk2
   FIX_ID: 7e861262-5a2d-443e-912a-415868d80f79
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 24
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: COMPONENT24.Quirk3
   NAME: COMPONENT24.Quirk3
   FIX_ID: 845b79e5-1dc4-4779-a8cb-020f4eec54bf
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 24
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: COMPONENT24.Quirk4
   NAME: COMPONENT24.Quirk4
   FIX_ID: 06eb9d4d-4f67-4fb9-b71f-ce8a7595acd7
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 24
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: COMPONENT25.Quirk1
   NAME: COMPONENT25.Quirk1
   FIX_ID: c9b4b6ef-07fb-4e9d-b661-732a1918d913
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 25
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: COMPONENT25.Quirk2
   NAME: COMPONENT25.Quirk2
   FIX_ID: a346c729-9ad9-49e2-a03a-778fd320c589
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 25
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: COMPONENT25.Quirk3
   NAME: COMPONENT25.Quirk3
   FIX_ID: 7da7718d-cd0b-44ba-b524-dd60f8b60f98
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 25
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: COMPONENT25.Quirk4
   NAME: COMPONENT25.Quirk4
   FIX_ID: ca7da7d6-62c0-48f1-bfac-76171e0b4639
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 25
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: COMPONENT26.Quirk1
   NAME: COMPONENT26.Quirk1
   FIX_ID: 138f9ffe-fcc2-4b20-a77b-408903bdc18f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 26
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: COMPONENT26.Quirk2
   NAME: COMPONENT26.Quirk2
   FIX_ID: b1a77700-2376-479f-a713-19f68f6989a0
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 26
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: COMPONENT26.Quirk3
   NAME: COMPONENT26.Quirk3
   FIX_ID: 8381b07a-9906-4706-9f9c-90cf9430bf80
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 26
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: COMPONENT26.Quirk4
   NAME: COMPONENT26.Quirk4
   FIX_ID: 87ef555b-78bf-450d-a626-26ccaed4fe85
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 26
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: COMPONENT27.Quirk1
   NAME: COMPONENT27.Quirk1
   FIX_ID: 9d59a55a-d8f4-4687-8534-8d72d6ff9601
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 27
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: COMPONENT27.Quirk2
   NAME: COMPONENT27.Quirk2
   FIX_ID: 6e1909ef-5b5f-4108-97fd-a20806c1d5e6
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 27
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: COMPONENT27.Quirk3
   NAME: COMPONENT27.Quirk3
   FIX_ID: 26c3a108-ac71-4dfd-ad96-947726047759
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 27
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: COMPONENT27.Quirk4
   NAME: COMPONENT27.Quirk4
   FIX_ID: 754249ec-3c70-4a96-8173-5169d2eb1e41
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 27
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: COMPONENT28.Quirk1
   NAME: COMPONENT28.Quirk1
   FIX_ID: 7fa45a08-32a0-4787-84a6-7b6d358da025
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 28
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: COMPONENT28.Quirk2
   NAME: COMPONENT28.Quirk2
   FIX_ID: 33aeafff-20eb-4716-acbf-84e0d39f64ba
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 28
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: COMPONENT28.Quirk3
   NAME: COMPONENT28.Quirk3
   FIX_ID: 7d04c018-dc45-4e09-a47f-0f2263b0de0f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 28
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: COMPONENT28.Quirk4
   NAME: COMPONENT28.Quirk4
   FIX_ID: 07c944dc-dcc5-4e7b-bdd0-987a817e0edf
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 28
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: COMPONENT29.Quirk1
   NAME: COMPONENT29.Quirk1
   FIX_ID: 9863f7c3-88fc-4094-8b95-1885af2f2c2b
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 29
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: COMPONENT29.Quirk2
   NAME: COMPONENT29.Quirk2
   FIX_ID: 9040906d-4b50-45b5-9865-89a4f6b49d2e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 29
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: COMPONENT29.Quirk3
   NAME: COMPONENT29.Quirk3
   FIX_ID: 8979deaa-2862-4c89-bd3b-542aa1f9719c
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 29
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: COMPONENT29.Quirk4
   NAME: COMPONENT29.Quirk4
   FIX_ID: d66938b0-661e-4238-ac11-9b6fd972af1e
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 29
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: COMPONENT30.Quirk1
   NAME: COMPONENT30.Quirk1
   FIX_ID: 0f6f9124-0524-4650-aade-e4ccfb2b9832
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 30
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: COMPONENT30.Quirk2
   NAME: COMPONENT30.Quirk2
   FIX_ID: 8819d8bf-22e1-4828-a6ad-2696b99f1dd1
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 30
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: COMPONENT30.Quirk3
   NAME: COMPONENT30.Quirk3
   FIX_ID: 58a0d5f6-4186-42a8-8796-1df096d12ff0
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 30
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: COMPONENT30.Quirk4
   NAME: COMPONENT30.Quirk4
   FIX_ID: 9c6bf46a-05ed-45b9-a020-c3a9564b7c86
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 30
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True

QUIRK: Input.AllowLegacyXInput1_4
   NAME: Input.AllowLegacyXInput1_4
   FIX_ID: a0ac55ee-b13f-4307-a2ae-d8ca32844f9d
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 2814749767106560
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 31
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: Input.AllowWgiTypeCasting
   NAME: Input.AllowWgiTypeCasting
   FIX_ID: 6561a97c-0829-4e41-953d-0a4459c4c210
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 0
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 31
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: COMPONENT32.Quirk1
   NAME: COMPONENT32.Quirk1
   FIX_ID: a2a145a4-9631-46d2-b6c4-60517e87080a
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 32
   QUIRK_CODE_ID: 0
   TELEMETRY_OFF: True

QUIRK: COMPONENT32.Quirk2
   NAME: COMPONENT32.Quirk2
   FIX_ID: 7da6587c-473f-4988-82c2-4e3ae66c7686
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 32
   QUIRK_CODE_ID: 1
   TELEMETRY_OFF: True

QUIRK: COMPONENT32.Quirk3
   NAME: COMPONENT32.Quirk3
   FIX_ID: 9471fcab-9198-4286-819e-055267d57b33
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 32
   QUIRK_CODE_ID: 2
   TELEMETRY_OFF: True

QUIRK: COMPONENT32.Quirk4
   NAME: COMPONENT32.Quirk4
   FIX_ID: d5d8bc1d-3584-4728-9aaf-672bea99e10f
   QUIRK_ENABLED_UPTO_VERSION_OR_QUIRK_ENABLED_VERSION_LT: 1688862745165824
   EDITION: 262143
   QUIRK_COMPONENT_CODE_ID: 32
   QUIRK_CODE_ID: 3
   TELEMETRY_OFF: True
```

</details>
