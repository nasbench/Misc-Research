# Living Of The SHIMS - Built-In SHIM DB Hijacking

Windows offer a Shimming functionality to provide backward compatibility for older applications. The Shim Infrastructure implements a form of API hooking where it intercept calls that applications make, and redirect them to alternative, compatible functions.

To learn more about how it works, please give the following blog/paper a read

- [Demystifying Shims - or - Using the App Compat Toolkit to make your old stuff work with your new stuff](https://techcommunity.microsoft.com/t5/ask-the-performance-team/demystifying-shims-or-using-the-app-compat-toolkit-to-make-your/ba-p/374947)
- [Malicious Application Compatibility Shims](https://www.blackhat.com/docs/eu-15/materials/eu-15-Pierce-Defending-Against-Malicious-Application-Compatibility-Shims-wp.pdf)

The focus of this writeup is on `sysmain.sdb` a built-in database that Windows uses to store compatibility fixes or shims.

## Inside Of Sysmain.sdb

As we're interested in the content of the database, I'm gonna use eric zimmerman's SDB Explorer in order to dump the content of `sysmain.sdb`.

![image](https://github.com/nasbench/Misc-Research/assets/8741929/2310f3cc-50bf-4e96-bd6a-769d78bebdca)

The database contains references to LAYERs, EXEs, PACKAGES and the SHIM references. For example, an executable that is going to be shimmed will be defined in the following fashion.

```yaml
EXE: trial_dfm*.exe
    NAME: trial_dfm*.exe
    WILDCARD_NAME: trial_dfm*.exe
    APP_NAME: MAGIX Digital Photo Maker
    VENDOR: MAGIX AG
    EXE_ID: 6037b14a-ee27-446c-9337-e8ba8b691f14
    APP_ID: 31fca84b-fa77-4f53-9524-2e4bf74ec407
    RUNTIME_PLATFORM: 37
    MATCHING_FILE: *
        NAME: *
        COMPANY_NAME: MAGIX AG
        FILE_DESCRIPTION: MAGIX Digital Foto Maker*
        UPTO_LINK_DATE: 1232041020
    SHIM_REF: VistaRTMVersionLie
        NAME: VistaRTMVersionLie
        SHIM_TAGID: 0x2F610
```

It defines some metadata information about the executable such as the VENDOR, APP_NAME, EXE_ID, etc. And then a matching condition for this shim to be applied

```yml
MATCHING_FILE: *
    NAME: *
    COMPANY_NAME: MAGIX AG
    FILE_DESCRIPTION: MAGIX Digital Foto Maker*
    UPTO_LINK_DATE: 1232041020
```

As you can see, these condition might not be super strict which could allow an attacker to create binaries that "mimick" these conditions in order to have the same shim applied.

This is not a particularly new technique, as [Adam](https://twitter.com/Hexacorn) [blogged](https://www.hexacorn.com/blog/2020/03/18/shimbad-the-sailor/) about this in 2020 :)

I thought i'd take this a step further by enumerating and creating a list of all the binaries with interesting shims that could be potentially hijacked.

## Enumerating The SHIMs

I wrote a small script to help me find loose binaries that leverage one of the following Shims

- [SHIM_REF: `DisableNX`](#shim-disablenx) - This compatibility fix disables execution protection (NX) for a process. This is useful for applications that decide to execute from memory region marked with NX attribute (like stack, heap etc.).

- [SHIM_REF: `InjectDLL`](#shim-injectdll) - Allows the injection of DLL, works only on 32bit applications

- [SHIM_REF: `IgnoreChromeSandbox`](#shim-ignorechromesandbox)

- [SHIM_REF: `OpenDirectoryAcl`](#shim-opendirectoryacl) - Gives builtin\USERS full permission to the directory specified on the command line.

- [SHIM_REF: `RedirectEXE`](#shim-redirectexe) - Allows you to redirect execution to another binary

- [SHIM_REF: `RegisterAppRestart`]() - This shim calls RegisterApplicationRestart so the app can restart after a user signs out and back in.

- [SHIM_REF: `RemoveReadOnlyAttribute`](#shim-removereadonlyattribute) - This compatibility fix will remove the Read-Only attribute from all directories. This may be helpful to applications that don’t expect the shell folders to be set to Read-Only.

- [SHIM_REF: `ReturnAdminGroupSidTrue`](#shim-returnadmingroupsidtrue)

Below is a list of all the binaries that can "theoretically" be hijacked and currently found in `sysmain.sdb`.

> **Note**
>
> I didn't test **all** of the variations. So results might differ for some of them.

### SHIM: IgnoreChromeSandbox

Didn't actually dig deep into the meaning behind this shim, but the name sounds super interesting and there are entries thata could easily be hijacked. 

<details>
    <summary>Expand Full List</summary>

```yml
EXE: AcroRd32.exe
   NAME: AcroRd32.exe
   APP_NAME: Adobe Reader X
   VENDOR: Adobe
   EXE_ID: e6c6da61-3a6e-45dc-9006-1cdd95b63e45
   APP_ID: 7e9102ab-d75e-4e7d-8823-bf68af23f58a
   RUNTIME_PLATFORM: 36
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Adobe Systems Incorporated
      PRODUCT_NAME: Adobe Reader
      BIN_PRODUCT_VERSION: 2814749767172095
   SHIM_REF: IgnoreChromeSandbox
      NAME: IgnoreChromeSandbox
      SHIM_TAGID: 0x2B190
```

```yml
EXE: chrome.exe
   NAME: chrome.exe
   APP_NAME: Google Chrome
   VENDOR: Google
   EXE_ID: 57bd1f71-67ba-4145-be0c-7a3a33e18ade
   APP_ID: 3db347ab-fb9b-441e-9bfe-8ccb4d646845
   RUNTIME_PLATFORM: 36
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Google Inc.
      FILE_DESCRIPTION: Google Chrome
      UPTO_LINK_DATE: 1293800399
   MATCHING_FILE: wow_helper.exe
      NAME: wow_helper.exe
      UPTO_LINK_DATE: 1233688619
   SHIM_REF: IgnoreChromeSandbox
      NAME: IgnoreChromeSandbox
      SHIM_TAGID: 0x2B190
```

```yml
EXE: flock.exe
   NAME: flock.exe
   APP_NAME: Flock Browser
   VENDOR: Flock
   EXE_ID: 74a07e1e-3481-4003-9fb0-33d99f0f6f4c
   APP_ID: 0c354576-0387-4016-8c82-d03363ff28e4
   RUNTIME_PLATFORM: 36
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Flock Inc. and The Chromium Authors
      FILE_DESCRIPTION: Flock
      UPTO_BIN_FILE_VERSION: 844450699935743
   SHIM_REF: IgnoreChromeSandbox
      NAME: IgnoreChromeSandbox
      SHIM_TAGID: 0x2B190
```

</details>

### SHIM: DisableNX

These are pretty straightforward. Simply create a binary with similar PE metadata and it'll have NX protection disabled

<details>
    <summary>Expand Full List</summary>

```yml
EXE: 3DMark2001SE.exe
   NAME: 3DMark2001SE.exe
   APP_NAME: 3DMark2001 SE
   VENDOR: MadOnion
   EXE_ID: 8ae20d91-4a78-4380-929e-5055239e41b5
   APP_ID: 0b302be2-1229-4ae2-81ed-af4afbcc23eb
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      PRODUCT_NAME: 3DMark Application
      FILE_DESCRIPTION: 3DMark MFC Application
      UPTO_LINK_DATE: 1022849199
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: ACDSee6.exe
   NAME: ACDSee6.exe
   APP_NAME: ACDSee
   VENDOR: ACD Systems Ltd.
   EXE_ID: 12322048-0d7f-467b-b7a3-228b5e54ff05
   APP_ID: b0acc928-e39f-4b04-a9d5-e3a52cd7c748
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      UPTO_BIN_PRODUCT_VERSION: 1688849860395022
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: aom.exe
   NAME: aom.exe
   APP_NAME: Age of Mythology
   VENDOR: Microsoft
   EXE_ID: 953cb140-3719-4cf3-82de-05a59677a7dd
   APP_ID: 8bdd4ad3-9b2b-45ac-91f8-78a63d22e50e
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Ensemble Studios
      PRODUCT_NAME: Microsoft Ensemble Studios Age of Mythology
      FILE_DESCRIPTION: Age of Mythology
      UPTO_BIN_FILE_VERSION: 1125899906842623
   SHIM_REF: AOMAdminCheck
      NAME: AOMAdminCheck
      SHIM_TAGID: 0x26DF4
   SHIM_REF: CUASAppFix
      NAME: CUASAppFix
      SHIM_TAGID: 0x28032
      COMMAND_LINE: IgnoreSetContextLPARAM EnableIMEonProtectedCode
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: CFMX_61_Updater_windows.exe
   NAME: CFMX_61_Updater_windows.exe
   APP_NAME: ColdFusion MX
   VENDOR: Macromedia
   EXE_ID: 8c67d23c-dc79-4c38-bb31-79e536554d4d
   APP_ID: 67055b8d-51c6-45ed-a920-5dfd483da1a0
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Zero G Software, Inc.
      FILE_DESCRIPTION: InstallAnywhere Self Extractor
      UPTO_BIN_FILE_VERSION: 1688849860263935
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
   LAYER: WinXPSP2VersionLie
      NAME: WinXPSP2VersionLie
      LAYER_TAGID: 0x3F694
```

```yml
EXE: CF_Client_Installer.exe
   NAME: CF_Client_Installer.exe
   APP_NAME: ColdFusion MX
   VENDOR: Macromedia
   EXE_ID: 3e94d802-c590-4c47-b515-069741273fe3
   APP_ID: 67055b8d-51c6-45ed-a920-5dfd483da1a0
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Zero G Software, Inc.
      FILE_DESCRIPTION: InstallAnywhere Self Extractor
      UPTO_BIN_FILE_VERSION: 1688849860263935
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: coldfusion-j2ee-win-en.exe
   NAME: coldfusion-j2ee-win-en.exe
   APP_NAME: ColdFusion MX
   VENDOR: Macromedia
   EXE_ID: 2d51462b-44e1-4e51-9ff3-30b8403dbed9
   APP_ID: 67055b8d-51c6-45ed-a920-5dfd483da1a0
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Zero G Software, Inc.
      FILE_DESCRIPTION: InstallAnywhere Self Extractor
      UPTO_BIN_FILE_VERSION: 1688849860263935
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: crtmqm.exe
   NAME: crtmqm.exe
   APP_NAME: IBM WebSphere MQ for Windows
   VENDOR: IBM
   EXE_ID: e5d3d765-6192-46aa-bebf-30a031d01745
   APP_ID: 65fdd208-00d1-4a7a-aecf-432050d5d692
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: IBM Corporation
      PRODUCT_NAME: IBM WebSphere MQ for Windows
      UPTO_BIN_PRODUCT_VERSION: 281474976776191
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: eventserver.exe
   NAME: eventserver.exe
   APP_NAME: Crystal Enterprise
   VENDOR: Crystal Decisions
   EXE_ID: 07f76d6f-4b67-49d7-ad58-f250bf246ef6
   APP_ID: c79b20f9-57b5-40ac-b567-f83a410454f6
   RUNTIME_PLATFORM: 36
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Crystal Decisions
      PRODUCT_NAME: Crystal Enterprise
      BIN_PRODUCT_VERSION: 2533279085363199
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: inputfileserver.exe
   NAME: inputfileserver.exe
   APP_NAME: Crystal Enterprise
   VENDOR: Crystal Decisions
   EXE_ID: 7ffe6c7b-2725-481c-baab-79a4946d2fc4
   APP_ID: c79b20f9-57b5-40ac-b567-f83a410454f6
   RUNTIME_PLATFORM: 36
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Crystal Decisions
      PRODUCT_NAME: Crystal Enterprise
      BIN_PRODUCT_VERSION: 2533279085363199
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: install.exe
   NAME: install.exe
   APP_NAME: InstallAnywhere
   VENDOR: Zero G Software
   EXE_ID: 71e8e6da-2583-4b7e-a3ab-113156ed12db
   APP_ID: 553d2b59-533d-4ba6-80a7-a54c6d69f793
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Zero G Software, Inc.
      FILE_DESCRIPTION: InstallAnywhere Self Extractor
      UPTO_BIN_FILE_VERSION: 1407374883618815
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: Jeopardy.exe
   NAME: Jeopardy.exe
   APP_NAME: Jeopardy 2003
   VENDOR: Infogrames
   EXE_ID: c02e1d7a-2d83-46e1-a95b-23d150c9445d
   APP_ID: 10fb569b-78dc-4c89-86a8-ab540086af0e
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Infogrames Interactive, Inc.
      PRODUCT_NAME: Jeopardy! 2003
   SHIM_REF: VirtualRegistry
      NAME: VirtualRegistry
      SHIM_TAGID: 0x2F540
      COMMAND_LINE: INDEO5
   SHIM_REF: WinXPSP2VersionLie
      NAME: WinXPSP2VersionLie
      SHIM_TAGID: 0x30BEA
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: jobserver.exe
   NAME: jobserver.exe
   APP_NAME: Crystal Enterprise
   VENDOR: Crystal Decisions
   EXE_ID: 8ae41d7b-8908-4fe2-95c4-938422ab6b33
   APP_ID: c79b20f9-57b5-40ac-b567-f83a410454f6
   RUNTIME_PLATFORM: 36
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Crystal Decisions
      PRODUCT_NAME: Crystal Enterprise
      BIN_PRODUCT_VERSION: 2533279085363199
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: MpfTray.exe
   NAME: MpfTray.exe
   APP_NAME: McAfee 2004
   VENDOR: McAfee
   EXE_ID: 3033a15a-e3de-4ab8-8ad0-4eb6a71d97fc
   APP_ID: d65c742a-78c9-4a75-9446-1343a821a6ce
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: McAfee Security
      FILE_DESCRIPTION: McAfee Personal Firewall Tray Monitor
      UPTO_BIN_PRODUCT_VERSION: 1407379178520575
   SHIM_REF: WinXPSP2VersionLie
      NAME: WinXPSP2VersionLie
      SHIM_TAGID: 0x30BEA
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: NeroVision.exe
   NAME: NeroVision.exe
   APP_NAME: Nero Vision Express
   VENDOR: Ahead Software
   EXE_ID: 2725b69f-7f78-4919-a6cb-d6d19eb3ec97
   APP_ID: c22a6150-1d3e-46fb-b7e8-28f7e7e54f2b
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Ahead Software*
      FILE_DESCRIPTION: NeroVision Express
      UPTO_BIN_FILE_VERSION: 562958543355903
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: Setup.exe
   NAME: Setup.exe
   APP_NAME: Nero Express
   VENDOR: Ahead
   EXE_ID: 3f655e27-29e6-4a5e-ad09-8947344a2f2f
   APP_ID: 9254cc42-1e1c-42f0-9bd1-7e03cba90cd3
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Ahead Software AG
      PRODUCT_NAME: NeroWebEngine Application
      UPTO_BIN_PRODUCT_VERSION: 281487861612543
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: XSI.exe
   NAME: XSI.exe
   APP_NAME: XSI 5.0
   VENDOR: Softimage
   EXE_ID: 56feb88d-5104-4cb9-a7cc-cdd91f0bbb72
   APP_ID: e2a9d38b-146c-4d14-af31-e0e7965c006e
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Softimage Co.
      UPTO_BIN_FILE_VERSION: 1407375015018495
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

```yml
EXE: webcompserver.exe
   NAME: webcompserver.exe
   APP_NAME: Crystal Enterprise
   VENDOR: Crystal Decisions
   EXE_ID: a615c8ec-c5c4-4b6a-a907-e76a294d488c
   APP_ID: c79b20f9-57b5-40ac-b567-f83a410454f6
   RUNTIME_PLATFORM: 36
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Crystal Decisions
      PRODUCT_NAME: Crystal Enterprise
      BIN_PRODUCT_VERSION: 2533279085363199
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
```

</details>

### SHIM: InjectDLL

A simple example would be the same described in Adam blog. Create a binary with the metadata `COMPANY: America Online, Inc.` and `PRODUCT NAME: AOL Instant Messenger` and it'll load `RTvideo.dll`


<details>
    <summary>Expand Full List</summary>

```yml
EXE: aim.exe
   NAME: aim.exe
   APP_NAME: AOL Instant Messenger
   VENDOR: AOL
   EXE_ID: 96530b9d-e9b5-4021-a074-77f22571265c
   APP_ID: d1591404-7c1c-4a8e-9395-083889ff63bb
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: America Online, Inc.
      PRODUCT_NAME: AOL Instant Messenger
      UPTO_BIN_PRODUCT_VERSION: 1407417833226239
   SHIM_REF: InjectDll
      NAME: InjectDll
      SHIM_TAGID: 0x2B716
      COMMAND_LINE: RTvideo.dll
```

```yml
EXE: GLJ*.tmp
      NAME: GLJ*.tmp
      WILDCARD_NAME: GLJ*.tmp
      APP_NAME: AOL Instant Messenger
      VENDOR: AOL
      EXE_ID: f83a0fcd-6d48-4714-8a38-d06d376aa7a0
      APP_ID: d1591404-7c1c-4a8e-9395-083889ff63bb
      RUNTIME_PLATFORM: 37
      MATCHING_FILE: *
         NAME: *
         SIZE: 2560
         CHECKSUM: 1229221402
         EXPORT_NAME: OCXREG32.EXE
      SHIM_REF: InjectDll
         NAME: InjectDll
         SHIM_TAGID: 0x2B716
         COMMAND_LINE: RTvideo.dll
```

</details>

### SHIM: RedirectEXE

An interesting example is from `regsvr32.exe`

```yml
EXE: REGSVR32.EXE
   NAME: REGSVR32.EXE
   APP_NAME: RegSvr32
   VENDOR: Microsoft
   EXE_ID: 2c7437c1-7105-40d3-bf84-d493a4f62ddb
   APP_ID: 254bf5e2-09f9-4dee-aaaa-a9860b154cac
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      UPTO_BIN_PRODUCT_VERSION: 1125904201809919
   SHIM_REF: RedirectEXE
      NAME: RedirectEXE
      SHIM_TAGID: 0x2DAB6
      COMMAND_LINE: +%windir%\system32\regsvr32.exe
```

This shim only focuses on any binary named `regvr32` up to a certain version. Since the redirection is using an env variable, we can hijack it by overriding it to a custom directory

```bash
mkdir system32
copy C:\Windows\System32\calc.exe system32\calc.exe
set windir=[custom_directory]
```

This will spawn a calc from a binary that doesn't even reference calc.

Below is the list of other SHIMs that have loose conditions.

<details>
    <summary>Expand Full List</summary>

```yml
EXE: D3D.exe
   NAME: D3D.exe
   APP_NAME: Freestyle BMX
   VENDOR: Headgames
   EXE_ID: dfabcc09-448b-43a6-93bf-dd8f90198dfc
   APP_ID: c00964ab-7228-464a-9088-800bceaeefd4
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Silverfish Studios, L.L.C.
      UPTO_BIN_PRODUCT_VERSION: 281474976710657
   MATCHING_FILE: BMX.exe
      NAME: BMX.exe
   SHIM_REF: RedirectEXE
      NAME: RedirectEXE
      SHIM_TAGID: 0x2DAB6
      COMMAND_LINE: .\Software.exe
```


```yml
EXE: BShipL.exe
   NAME: BShipL.exe
   APP_NAME: Battleship 1.0
   VENDOR: Hasbro
   EXE_ID: 1919ea5d-7b5c-4214-93d4-1ea48a045dd1
   APP_ID: 0d665e68-eef3-4a44-b012-408ea3d3517d
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
   MATCHING_FILE: ..\SFX\BATTSINK\BATTSINK.SEQ
      NAME: ..\SFX\BATTSINK\BATTSINK.SEQ
   MATCHING_FILE: ..\SFX\BATMINE\BATMINE.SEQ
      NAME: ..\SFX\BATMINE\BATMINE.SEQ
   MATCHING_FILE: ..\SFX\CARRSINK\CARRSINK.SEQ
      NAME: ..\SFX\CARRSINK\CARRSINK.SEQ
   SHIM_REF: RedirectEXE
      NAME: RedirectEXE
      SHIM_TAGID: 0x2DAB6
      COMMAND_LINE: ..\bs.exe
   SHIM_REF: Battleship
      NAME: Battleship
      SHIM_TAGID: 0x27206
```


```yml
EXE: FLIP32.EXE
   NAME: FLIP32.EXE
   APP_NAME: Flipper
   VENDOR: Interplay
   EXE_ID: d04ab8f0-3f7a-4495-9e4b-265851d417b0
   APP_ID: 20228be2-021c-473a-821a-070aab946d93
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      PRODUCT_NAME: Macromedia Director
   MATCHING_FILE: FLIP16.EXE
      NAME: FLIP16.EXE
   MATCHING_FILE: ARALERT.DXR
      NAME: ARALERT.DXR
   MATCHING_FILE: XTRAS\PMATIC.X32
      NAME: XTRAS\PMATIC.X32
   SHIM_REF: RedirectEXE
      NAME: RedirectEXE
      SHIM_TAGID: 0x2DAB6
      COMMAND_LINE: Flip16.exe
```


```yml
EXE: GFWLive.exe
   NAME: GFWLive.exe
   APP_NAME: Games for Windows Live
   VENDOR: Microsoft
   EXE_ID: 3655714e-b5f5-41a4-b325-2ec306b2fef4
   APP_ID: c9906937-5734-4f62-b3a3-eddb0e55847b
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Microsoft Corporation
      PRODUCT_NAME: Microsoft* Games for Windows* - LIVE
      FILE_DESCRIPTION: Games for Windows Marketplace Client Splash Screen
      UPTO_BIN_FILE_VERSION: 844446408245248
   MATCHING_FILE: GFWLClient.exe
      NAME: GFWLClient.exe
      COMPANY_NAME: Microsoft* Corporation
      PRODUCT_NAME: Microsoft* Games for Windows* - LIVE
      FILE_DESCRIPTION: Games for Windows* Marketplace
      UPTO_BIN_FILE_VERSION: 844446408245248
   SHIM_REF: RedirectExe
      NAME: RedirectExe
      SHIM_TAGID: 0x2DAB6
      COMMAND_LINE: .\GFWLClient.exe
```


```yml
EXE: setup.exe
   NAME: setup.exe
   APP_NAME: TurboTax 2009
   VENDOR: Intuit, Inc.
   EXE_ID: 9f4b0457-2dab-4abd-8276-78ab7ed93240
   APP_ID: a132ff41-cbf8-4156-9162-0edcae99e208
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Intuit Inc, 2009
      PRODUCT_NAME: TurboTax 2009 Installer
      UPTO_BIN_PRODUCT_VERSION: 565764703188418559
   MATCHING_FILE: TurboTax 2009\TurboTax 2009 Installer.exe
      NAME: TurboTax 2009\TurboTax 2009 Installer.exe
      COMPANY_NAME: Intuit
      PRODUCT_NAME: TurboTax 2009 Installer
      UPTO_BIN_PRODUCT_VERSION: 565764703188418559
   SHIM_REF: RedirectEXE
      NAME: RedirectEXE
      SHIM_TAGID: 0x2DAB6
      COMMAND_LINE: TurboTax 2009\TurboTax 2009 Installer.exe
```


```yml
EXE: setup.exe
   NAME: setup.exe
   APP_NAME: TurboTax 2010
   VENDOR: Intuit, Inc.
   EXE_ID: 366acfaf-2156-4fac-b2c8-4e50a19da138
   APP_ID: 2a4ce97e-94f7-4632-a062-201515fbc03e
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Intuit Inc, 2010
      PRODUCT_NAME: TurboTax 2010 Installer
      UPTO_BIN_PRODUCT_VERSION: 566046178165129215
   MATCHING_FILE: TurboTax 2010\TurboTax 2010 Installer.exe
      NAME: TurboTax 2010\TurboTax 2010 Installer.exe
      COMPANY_NAME: Intuit
      PRODUCT_NAME: TurboTax 2010 Installer
      UPTO_BIN_PRODUCT_VERSION: 566046178165129215
   SHIM_REF: RedirectEXE
      NAME: RedirectEXE
      SHIM_TAGID: 0x2DAB6
      COMMAND_LINE: TurboTax 2010\TurboTax 2010 Installer.exe
```


```yml
EXE: Setuppol.exe
   NAME: Setuppol.exe
   APP_NAME: Playonline
   VENDOR: Square Enix
   EXE_ID: cd15a511-149c-4c72-a1ff-0182ce56080b
   APP_ID: 581ed7ad-edba-4db2-98e7-d51fd516454c
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
   MATCHING_FILE: PolSystemInfo.exe
      NAME: PolSystemInfo.exe
      COMPANY_NAME: SQUARE ENIX*
      PRODUCT_NAME: PlayOnline System Information
      UPTO_BIN_PRODUCT_VERSION: 562949953421311
   SHIM_REF: DisableNX
      NAME: DisableNX
      SHIM_TAGID: 0x287CA
   SHIM_REF: RedirectEXE
      NAME: RedirectEXE
      SHIM_TAGID: 0x2DAB6
      COMMAND_LINE: ..\PlayOnline\setup.exe
```


```yml
EXE: xmb-d3d.exe
   NAME: xmb-d3d.exe
   APP_NAME: Extreme Mountain Biking
   VENDOR: Headgames
   EXE_ID: 60f797cd-e213-47ce-8241-78925859a5df
   APP_ID: ec3901b7-57f5-4f63-89ac-540d18f0419d
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Creative Carnage, LLC.
      PRODUCT_NAME: Extreme Mountain Biking
      UPTO_BIN_PRODUCT_VERSION: 281474976710657
   SHIM_REF: RedirectEXE
      NAME: RedirectEXE
      SHIM_TAGID: 0x2DAB6
      COMMAND_LINE: .\xmb-soft.exe
```

</details>

### SHIM: OpenDirectoryAcl

I wasn't able to really make use of this or to test heavily but the description sounded super nice for potential privilege escalation and there were many hijackable entries for files and directory.

<details>
    <summary>Expand Full List</summary>

```yml
EXE: IKernel.exe
   NAME: IKernel.exe
   APP_NAME: Empire Earth
   VENDOR: Sierra Entertainment, Inc.
   EXE_ID: e7def8bb-920d-41ef-9b94-2464e2815b42
   APP_ID: 3aafa7c2-393b-43ea-b9b2-610f2c82338a
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
   MATCHING_FILE: DATA1.CAB
      NAME: DATA1.CAB
      SIZE: 5622462
      CHECKSUM: 1215966497
   MATCHING_FILE: DATA2.CAB
      NAME: DATA2.CAB
      SIZE: 401139395
      CHECKSUM: -265740305
   MATCHING_FILE: MEDIA\EEIcon.ico
      NAME: MEDIA\EEIcon.ico
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -f %SystemDir%\SIntf16.dll -f %SystemDir%\SIntf32.dll -f %SystemDir%\SIntfNT.dll
```

```yml
EXE: instalar.exe
   NAME: instalar.exe
   APP_NAME: Pipo
   VENDOR: Cibal Multimedia
   EXE_ID: 9f9fc79b-713b-4318-ba45-41ca2bf0067b
   APP_ID: 2bf9afdc-36c0-4fb0-9411-a53900191b54
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Cibal Multimedia.
      PRODUCT_NAME: Pipo
      FILE_DESCRIPTION: Instalación
      UPTO_BIN_PRODUCT_VERSION: 562949953421311
   MATCHING_FILE: PIPOING\pipoin.exe
      NAME: PIPOING\pipoin.exe
   MATCHING_FILE: PIPOING\pipoincd.EXE
      NAME: PIPOING\pipoincd.EXE
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d %SystemDrive%\PIPOING
```

```yml
EXE: Install.exe
   NAME: Install.exe
   APP_NAME: Explzh
   VENDOR: Pon Software
   EXE_ID: 9ffe0554-4ba8-4504-90cf-3cc8f3ea7f51
   APP_ID: 4bf6faea-ac48-475d-b134-03834e4e6cbf
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      UPTO_LINK_DATE: 1162339200
   MATCHING_FILE: EXPLZH.EXE
      NAME: EXPLZH.EXE
      COMPANY_NAME: Pon Software
      FILE_DESCRIPTION: Explzh for Windows
      UPTO_BIN_PRODUCT_VERSION: 1407374883553279
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d %ProgramFiles%\ArchiverDLL
```

```yml
EXE: Installer.exe
   NAME: Installer.exe
   APP_NAME: World of Warcraft
   VENDOR: Blizzard
   EXE_ID: 21371792-c38a-4f33-8cbd-fc95a9dd1120
   APP_ID: 24ed0c28-ec7f-4a6f-addc-416dd64fa2d9
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      UPTO_BIN_PRODUCT_VERSION: 562949953421311
      UPTO_BIN_FILE_VERSION: 844424930131967
   MATCHING_FILE: Installer.ico
      NAME: Installer.ico
   MATCHING_FILE: Installer Tome.mpq
      NAME: Installer Tome.mpq
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d "%ProgramFiles%\World of Warcraft" -d "%ProgramFiles%\Common Files\Blizzard Entertainment"
```

```yml
EXE: NATEON20.exe
   NAME: NATEON20.exe
   APP_NAME: NateOn
   VENDOR: SK Communications
   EXE_ID: 5ceffad9-a72d-4ad7-bcd2-1acef35f1502
   APP_ID: 68c429df-2fbe-4ca7-bca1-a96f278cc72d
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: SK Communications
      PRODUCT_NAME: 네이트온
      ORIGINAL_FILENAME: stub32i.exe
      UPTO_BIN_PRODUCT_VERSION: 1407374883553279
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d %ProgramFiles%\NATEON\Addin
```

```yml
EXE: Prayer370.exe
   NAME: Prayer370.exe
   APP_NAME: Bilal Prayer
   VENDOR: Bilal Team
   EXE_ID: e3dbb058-0aaa-4ca8-aea7-4b39d7cd571a
   APP_ID: 27e50a32-0cdf-4e6f-9cf7-d317d50c0152
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Bilal Team
      PRODUCT_NAME: Bilal Prayer
      FILE_DESCRIPTION: Setup Launcher
      UPTO_BIN_PRODUCT_VERSION: 3096224743817215
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d %ProgramFiles%\Prayer
```

```yml
EXE: setup.exe
   NAME: setup.exe
   APP_NAME: Baby Newton Fun With Shapes
   VENDOR: Buena Vista Interactive
   EXE_ID: bc936371-8fff-4187-a0a8-0781737fcc88
   APP_ID: 3c03b3ec-6bd3-4079-8aba-15e9a54c5655
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      SIZE: 166912
      CHECKSUM: -171624715
      UPTO_BIN_PRODUCT_VERSION: 1688978709282816
      UPTO_BIN_FILE_VERSION: 1688978715837671
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d "%CSIDL_PROGRAM_FILES_COMMON%\SWF Studio"
   SHIM_REF: PreInitApplication
      NAME: PreInitApplication
      SHIM_TAGID: 0x2D4B8
      COMMAND_LINE: BabyEinstein
```

```yml
EXE: Setup.exe
   NAME: Setup.exe
   APP_NAME: Kefalaio 4
   VENDOR: ALTEC
   EXE_ID: e1ad5e6b-f661-434a-96a5-312194800013
   APP_ID: 9c46a1a8-5ece-4aa8-8476-32914fdb2b45
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      UPTO_BIN_PRODUCT_VERSION: 1970324836974591
   MATCHING_FILE: Support\Images\Kef4.ico
      NAME: Support\Images\Kef4.ico
   MATCHING_FILE: Support\Images\Kef.ico
      NAME: Support\Images\Kef.ico
   MATCHING_FILE: data1.cab
      NAME: data1.cab
      SIZE: 547713
      CHECKSUM: 1215966497
   MATCHING_FILE: data2.cab
      NAME: data2.cab
      SIZE: 12357981
      CHECKSUM: 1385245641
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -f %ProgramFiles%\KEF4DEMO\system.inf
```

```yml
EXE: Setup.exe
   NAME: Setup.exe
   APP_NAME: Knight Online
   VENDOR: K2Network
   EXE_ID: f37555d7-516c-45f9-ad2f-4d2238a7ce4b
   APP_ID: eeae3305-6af3-4ca0-9d02-def6045a273a
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
   MATCHING_FILE: ikernel.ex_
      NAME: ikernel.ex_
      SIZE: 347127
      CHECKSUM: -2065388122
   MATCHING_FILE: setup.inx
      NAME: setup.inx
      SIZE: 131318
      CHECKSUM: 980417311
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d %programfiles%\KnightOnline
```

```yml
EXE: setup.exe
   NAME: setup.exe
   APP_NAME: Kurzweil 3000
   VENDOR: Kurzweil Educational Systems
   EXE_ID: 37d8fe7c-3329-4761-8a58-06cdd9f73c29
   APP_ID: b4973877-2c82-414e-b892-44bdb56df00e
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
   MATCHING_FILE: Dragon\DNSCompatibility.exe
      NAME: Dragon\DNSCompatibility.exe
   MATCHING_FILE: KESIPrnt\Router.exe
      NAME: KESIPrnt\Router.exe
      COMPANY_NAME: Kurzweil Educational Systems, Inc.
      PRODUCT_NAME: Router Application
      UPTO_BIN_PRODUCT_VERSION: 281479271677951
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d "%ProgramFiles%\Kurzweil Educational Systems" -d "%ProgramFiles%\Kurzweil Educational Systems\Kurzweil 3000" -d "%ProgramFiles%\Kurzweil Educational Systems\Kurzweil 3000\Patches"
```

```yml
EXE: setup.exe
   NAME: setup.exe
   APP_NAME: Pipo
   VENDOR: Cibal Multimedia
   EXE_ID: 05cefcc3-764f-454c-8d25-55917751357f
   APP_ID: 2bf9afdc-36c0-4fb0-9411-a53900191b54
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Cibal Multimedia.
      PRODUCT_NAME: Pipo
      FILE_DESCRIPTION: Instalación
      UPTO_BIN_PRODUCT_VERSION: 562949953421311
   MATCHING_FILE: PIPOMATE\pipoma.exe
      NAME: PIPOMATE\pipoma.exe
   MATCHING_FILE: PIPOMATE\PIPOMATE.EXE
      NAME: PIPOMATE\PIPOMATE.EXE
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d %SystemDrive%\PIPOMATE
```

```yml
EXE: setup.exe
   NAME: setup.exe
   APP_NAME: Quake IV
   VENDOR: Id Software
   EXE_ID: b0aacb1e-2420-4dfb-8a1d-05dca33b0c17
   APP_ID: 87d18fc2-8355-4054-b410-c5a00eaa97d7
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Activision*
      PRODUCT_NAME: Quake 4(TM)*
      FILE_DESCRIPTION: Setup Launcher*
      UPTO_BIN_PRODUCT_VERSION: 2814749767106559
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d "%ProgramFiles%\id Software\Quake 4\q4base"
```

```yml
EXE: SETUP.EXE
   NAME: SETUP.EXE
   APP_NAME: RealFlight R/C Flight Simulator
   VENDOR: Knife Edge Software
   EXE_ID: 975e6050-40a5-4d9e-aeec-dfe94650bc40
   APP_ID: 1745eb43-7322-4fe5-93bf-91c1417f7862
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Knife Edge Software
      FILE_DESCRIPTION: Installer Application
      UPTO_BIN_PRODUCT_VERSION: 562949953421311
      UPTO_LINK_DATE: 1124928000
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d %CSIDL_PROGRAM_FILES_COMMON%\KnifeEdge -f %SystemDrive%\rfserial.txt -f %SystemDrive%\launcheroutput.txt
```

```yml
EXE: setup.exe
   NAME: setup.exe
   APP_NAME: Streets And Trips 2000
   VENDOR: Microsoft
   EXE_ID: 16ecf02d-a741-4f6c-8c21-d4679d1e3d56
   APP_ID: bfd09e86-2039-4b4e-9c59-72701a597374
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Microsoft Corporation
      FILE_DESCRIPTION: Microsoft Streets & Trips Setup
      UPTO_BIN_PRODUCT_VERSION: 281479271677951
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d "%CSIDL_PROGRAM_FILES_COMMON%\Microsoft Shared\pushpins"
```

```yml
EXE: setup.exe
   NAME: setup.exe
   APP_NAME: TETA Biznes Partner
   VENDOR: TETA
   EXE_ID: 3600aed6-bc35-4aec-bfcd-e870b43a2ad9
   APP_ID: 152f4c01-f9d4-4909-a108-7713e40f6e7c
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: TETA S.A
      FILE_DESCRIPTION: Setup Launcher
      UPTO_BIN_PRODUCT_VERSION: 2533274790395903
      VER_LANGUAGE: 1045
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d %SystemDrive%\TETA
```

```yml
EXE: Setup.exe
   NAME: Setup.exe
   APP_NAME: Throne of Darkness
   VENDOR: Sierra
   EXE_ID: 6cabaafc-74d5-4c25-b622-ff6755375bdf
   APP_ID: f80486c4-52df-48f2-acbb-16e37aed2440
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Click Entertainment Inc.
      FILE_DESCRIPTION: Throne of Darkness
      UPTO_BIN_PRODUCT_VERSION: 30064771071
   MATCHING_FILE: Menu.exe
      NAME: Menu.exe
      COMPANY_NAME: Click Entertianment
      FILE_DESCRIPTION: ToD Menu
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -f %SystemDir%\SIntf16.dll -f %SystemDir%\SIntf32.dll -f %SystemDir%\SIntfNT.dll -md "\Throne of Darkness\saved"
```

```yml
EXE: setup.exe
   NAME: setup.exe
   APP_NAME: Clarify CRM
   VENDOR: Amdocs
   EXE_ID: 1b0db5af-370a-436d-ac45-7f669cba2a68
   APP_ID: 6905e1e3-6aed-4ae8-9c55-54ea7493624e
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      UPTO_BIN_PRODUCT_VERSION: 844424930131967
   MATCHING_FILE: program files\Clarify\clarify.exe
      NAME: program files\Clarify\clarify.exe
      COMPANY_NAME: Amdocs Software Systems  Limited
      PRODUCT_NAME: Amdocs ClarifyCRM
      UPTO_BIN_PRODUCT_VERSION: 3659174697238527
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d %ProgramFiles%\Clarify
```

```yml
EXE: setup.exe
   NAME: setup.exe
   APP_NAME: Roller Coaster Tycoon 2 Triple Thrill Pack
   VENDOR: Atari
   EXE_ID: d4abe35c-c280-4d03-a6a1-a5884c7ff077
   APP_ID: 04f1c21e-f553-43a7-bc2e-62607f438639
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: InstallShield Software Corporation
      PRODUCT_NAME: InstallShield (R)
      FILE_DESCRIPTION: InstallShield (R) Setup Launcher
      UPTO_BIN_PRODUCT_VERSION: 1970329131941888
      UPTO_BIN_FILE_VERSION: 1970329138496736
   MATCHING_FILE: Scenarios\Six Flags Magic Mountain.SC6
      NAME: Scenarios\Six Flags Magic Mountain.SC6
      SIZE: 1448614
      CHECKSUM: -598008130
   MATCHING_FILE: RCT2.dat
      NAME: RCT2.dat
      SIZE: 6913491
      CHECKSUM: -989891067
   MATCHING_FILE: rct2.ico
      NAME: rct2.ico
      SIZE: 2238
      CHECKSUM: -305010578
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d "%ProgramFiles%\Atari\RollerCoaster Tycoon 2 Triple Thrill Pack"
```

```yml
EXE: SETUP.EXE
   NAME: SETUP.EXE
   APP_NAME: Canvas 9
   VENDOR: Deneba Software
   EXE_ID: cb2e1116-db45-4598-8c64-53ccba85cadd
   APP_ID: 8f7c727c-7ec4-431c-9eb1-965d1f8bbfde
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      UPTO_LINK_DATE: 1162339200
   MATCHING_FILE: Autorun.exe
      NAME: Autorun.exe
      COMPANY_NAME: AutoRun
      PRODUCT_NAME: Deneba Canvas
      FILE_DESCRIPTION: AutoRun program for Deneba Canvas
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -f "%ProgramFiles%\Deneba\Canvas 9\Canvas Tools\CVPatch.exe"
```

```yml
EXE: setup.exe
   NAME: setup.exe
   APP_NAME: Doom3 V 1.0
   VENDOR: Activision
   EXE_ID: b7281d32-18d3-4477-8af5-703779293f40
   APP_ID: 93694922-d8b0-4360-9c93-0709b7c75647
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Activision
      PRODUCT_NAME: Doom 3
      FILE_DESCRIPTION: Setup Launcher
      UPTO_BIN_PRODUCT_VERSION: 2814749767106559
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d "%ProgramFiles%\DOOM 3"
```

```yml
EXE: setup.exe
   NAME: setup.exe
   APP_NAME: Kodak EasyShare
   VENDOR: Kodak
   EXE_ID: 3dc997d6-403a-4dd1-9bca-b6a6b34843ec
   APP_ID: e856b0da-2547-4c27-9102-3b63ad35685d
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Eastman Kodak Company
      PRODUCT_NAME: EasyShare Software
      FILE_DESCRIPTION: EasyShare System Setup Platform
      UPTO_BIN_PRODUCT_VERSION: 1970324836974591
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d "%ProgramFiles%\Kodak\Kodak EasyShare software\bin\catalog"
```

```yml
EXE: setup.exe
   NAME: setup.exe
   APP_NAME: Prey
   VENDOR: Take Two Interactive
   EXE_ID: a50d2538-b205-4e67-9161-2210ad052c9b
   APP_ID: 502dbe76-20e1-4480-bd1a-8388810faafa
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Macrovision Corporation
      PRODUCT_NAME: InstallShield (R)
      UPTO_BIN_PRODUCT_VERSION: 3096224743817216
      UPTO_BIN_FILE_VERSION: 3096224743846060
   MATCHING_FILE: cdkey.dll
      NAME: cdkey.dll
      COMPANY_NAME: TODO: &lt;Company name&gt;
      PRODUCT_NAME: TODO: &lt;Product name&gt;
      UPTO_BIN_PRODUCT_VERSION: 281474976710657
      UPTO_BIN_FILE_VERSION: 281474976710657
   MATCHING_FILE: PreyLauncher.exe
      NAME: PreyLauncher.exe
      COMPANY_NAME: Human Head Studios
      PRODUCT_NAME: PREY Launcher
      UPTO_BIN_PRODUCT_VERSION: 281474976710657
      UPTO_BIN_FILE_VERSION: 281474976710657
   MATCHING_FILE: Setup\Data\prey.exe
      NAME: Setup\Data\prey.exe
      COMPANY_NAME: Human Head Studios
      PRODUCT_NAME: PREY
      UPTO_BIN_PRODUCT_VERSION: 281474976710657
      UPTO_BIN_FILE_VERSION: 281474976710657
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -d "%ProgramFiles%\Prey"
```

```yml
EXE: _INS5576._MP
   NAME: _INS5576._MP
   APP_NAME: Microsoft SQL Server 2000a
   VENDOR: Microsoft Corporation
   EXE_ID: 015fa635-f295-4423-937a-4bf71ace71cf
   APP_ID: a7782d5d-d956-4fb9-8594-eded9d41fd64
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
   MATCHING_FILE: setupsql.exe
      NAME: setupsql.exe
      COMPANY_NAME: Microsoft Corporation
      PRODUCT_NAME: Microsoft SQL Server
      FILE_DESCRIPTION: SQL Server Setup Stub
      UPTO_BIN_PRODUCT_VERSION: 2533274790395903
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -mpr "\Microsoft SQL Server\MSSQL\*|D:P(A;OICI;FA;;;BA)(A;OICI;FRFX;;;BU)"
```

```yml
EXE: _INS576._MP
   NAME: _INS576._MP
   APP_NAME: NASCAR Racing 4
   VENDOR: Papyrus
   EXE_ID: e313fb07-affa-4dc7-a8df-866c059071db
   APP_ID: 5513dcd4-aa4f-4a2e-95ad-3855209f3098
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
   MATCHING_FILE: NASCAR4.ICO
      NAME: NASCAR4.ICO
   MATCHING_FILE: NR4\n4config.exe
      NAME: NR4\n4config.exe
   MATCHING_FILE: NR4\NASCAR Racing 4.exe
      NAME: NR4\NASCAR Racing 4.exe
   MATCHING_FILE: NR4\n4server.exe
      NAME: NR4\n4server.exe
   SHIM_REF: CorrectFilePaths
      NAME: CorrectFilePaths
      SHIM_TAGID: 0x27C8A
   SHIM_REF: OpenDirectoryAcl
      NAME: OpenDirectoryAcl
      SHIM_TAGID: 0x2CEF0
      COMMAND_LINE: -f %SystemDir%\SIntf16.dll -f %SystemDir%\SIntf32.dll -f %SystemDir%\SIntfNT.dll
```

</details>

### SHIM: RemoveReadOnlyAttribute

<details>
    <summary>Expand Full List</summary>

```yml
EXE: mmjb.exe
   NAME: mmjb.exe
   APP_NAME: MusicMatch Jukebox
   VENDOR: MusicMatch
   EXE_ID: 3ec4d21c-5c30-4c4c-885c-ee86854bfe32
   APP_ID: f2ef647f-7ebe-4310-9a94-b0fa17aa19d6
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: MusicMatch
      PRODUCT_NAME: MusicMatch Jukebox
      PRODUCT_VERSION: 5.*
   SHIM_REF: RemoveReadOnlyAttribute
      NAME: RemoveReadOnlyAttribute
      SHIM_TAGID: 0x2DEF0
```

```yml
EXE: mmjb.exe
   NAME: mmjb.exe
   APP_NAME: MusicMatch Jukebox
   VENDOR: MusicMatch
   EXE_ID: fd10d4c3-d5d0-443d-847d-96d099dde1a3
   APP_ID: f2ef647f-7ebe-4310-9a94-b0fa17aa19d6
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: MusicMatch
      PRODUCT_NAME: MusicMatch Jukebox
      PRODUCT_VERSION: 6.*
   SHIM_REF: RemoveReadOnlyAttribute
      NAME: RemoveReadOnlyAttribute
      SHIM_TAGID: 0x2DEF0
```

```yml
EXE: mmjb.exe
   NAME: mmjb.exe
   APP_NAME: MusicMatch Jukebox
   VENDOR: MusicMatch
   EXE_ID: 0d81173c-ab66-4f81-b692-39894ef90a39
   APP_ID: f2ef647f-7ebe-4310-9a94-b0fa17aa19d6
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: MUSICMATCH, Inc.
      PRODUCT_NAME: MUSICMATCH Jukebox
      PRODUCT_VERSION: 7.*
   SHIM_REF: RemoveReadOnlyAttribute
      NAME: RemoveReadOnlyAttribute
      SHIM_TAGID: 0x2DEF0
```

```yml
EXE: MSHAGAKI.EXE
   NAME: MSHAGAKI.EXE
   APP_NAME: Hagaki
   VENDOR: Microsoft
   EXE_ID: fed1b0e8-ef24-4c23-b22e-a79780757cc6
   APP_ID: 92589327-73cd-40cf-91e0-7f526aeef429
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
   MATCHING_FILE: MSHAGAKI.OCX
      NAME: MSHAGAKI.OCX
   MATCHING_FILE: MSHAGAKI.CNT
      NAME: MSHAGAKI.CNT
   MATCHING_FILE: WORKS\MSHSLG.BMP
      NAME: WORKS\MSHSLG.BMP
   SHIM_REF: RemoveReadOnlyAttribute
      NAME: RemoveReadOnlyAttribute
      SHIM_TAGID: 0x2DEF0
```

```yml
EXE: realjbox.exe
   NAME: realjbox.exe
   APP_NAME: Real Jukebox
   VENDOR: Real Networks
   EXE_ID: caccee90-19bc-46f2-ae37-4d004bf3ff68
   APP_ID: 24c553bc-f52a-4dbf-abae-afa2778f2770
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: RealNetworks
      PRODUCT_NAME: RealNetworks RealJukebox
      UPTO_BIN_PRODUCT_VERSION: 281474976907263
   SHIM_REF: RemoveReadOnlyAttribute
      NAME: RemoveReadOnlyAttribute
      SHIM_TAGID: 0x2DEF0
   SHIM_REF: DisableThemes
      NAME: DisableThemes
      SHIM_TAGID: 0x288E6
```

```yml
EXE: Trellix.exe
   NAME: Trellix.exe
   APP_NAME: WordPerfect 9.0
   VENDOR: Corel
   EXE_ID: 56bdd3d2-7aff-4ddf-aca7-b7897d31d59d
   APP_ID: 2d95dfe0-2070-4455-a548-b9b154d2b61c
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
   MATCHING_FILE: TlxLauncher.exe
      NAME: TlxLauncher.exe
   MATCHING_FILE: Trellix_startup.exe
      NAME: Trellix_startup.exe
   MATCHING_FILE: TRELLIX.HLP
      NAME: TRELLIX.HLP
   SHIM_REF: RemoveReadOnlyAttribute
      NAME: RemoveReadOnlyAttribute
      SHIM_TAGID: 0x2DEF0
      INEXCLUDE
         INCLUDE: True
         MODULE: MSVBVM50.dll
      INEXCLUDE
         MODULE: *
```

```yml
EXE: WksCal.exe
   NAME: WksCal.exe
   APP_NAME: Works 2001
   VENDOR: Microsoft
   EXE_ID: 416a8191-2ff4-4491-86e5-7301affb118c
   APP_ID: f1561f75-cf44-4625-91df-4b330c39fa3e
   RUNTIME_PLATFORM: 37
   MATCHING_FILE: *
      NAME: *
      PRODUCT_NAME: Microsoft® Works 6.0
      FILE_DESCRIPTION: Microsoft® Works Calendar
      UPTO_BIN_PRODUCT_VERSION: 1688854155231231
   SHIM_REF: RemoveReadOnlyAttribute
      NAME: RemoveReadOnlyAttribute
      SHIM_TAGID: 0x2DEF0
   SHIM_REF: EmulateHeap
      NAME: EmulateHeap
      SHIM_TAGID: 0x2918A
```

</details>

### SHIM: ReturnAdminGroupSidTrue

This one also made the list just because of the interesting name. If you have time to play with please let me know

<details>
    <summary>Expand Full List</summary>

```yml
EXE: RealTimes*.exe
   NAME: RealTimes*.exe
   WILDCARD_NAME: RealTimes*.exe
   APP_NAME: RealPlayer
   VENDOR: RealNetworks
   EXE_ID: 35f68b49-4356-42ca-959a-ee5ee77d3826
   APP_ID: ad03d2f1-c8a4-424b-8f08-fa3dec436a25
   24630: 20H1
   MATCHING_FILE: *
      NAME: *
   SHIM_REF: ReturnAdminGroupSidTrue
      NAME: ReturnAdminGroupSidTrue
      SHIM_TAGID: 0x2E112
      INEXCLUDE
         INCLUDE: True
         MODULE: *
```

```yml
EXE: rnsetup*.exe
   NAME: rnsetup*.exe
   WILDCARD_NAME: rnsetup*.exe
   APP_NAME: RealPlayer
   VENDOR: RealNetworks
   EXE_ID: 6988d877-9c79-4dd0-b06b-e89582319df4
   APP_ID: ad03d2f1-c8a4-424b-8f08-fa3dec436a25
   24630: 20H1
   MATCHING_FILE: *
      NAME: *
   SHIM_REF: ReturnAdminGroupSidTrue
      NAME: ReturnAdminGroupSidTrue
      SHIM_TAGID: 0x2E112
      INEXCLUDE
         INCLUDE: True
         MODULE: *
```

</details>

### SHIM: RegisterAppRestart

<details>
    <summary>Expand Full List</summary>

```yml
EXE: 7zFM.exe
   NAME: 7zFM.exe
   APP_NAME: 7-Zip
   VENDOR: Igor Pavlov
   EXE_ID: cd25920f-de96-4960-9ba9-2842eedeca36
   APP_ID: a524371d-7f28-44c5-bcde-e253532b622c
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Igor Pavlov
      FILE_DESCRIPTION: 7-Zip File Manager
      FROM_BIN_PRODUCT_VERSION: 4222124650659840
      UPTO_BIN_PRODUCT_VERSION: 6192449487634431
   MATCHING_FILE: 7z.dll
      NAME: 7z.dll
   SHIM_REF: RegisterAppRestart
      NAME: RegisterAppRestart
      SHIM_TAGID: 0x2DC30
      COMMAND_LINE: |COPY_COMMAND_LINE|
```

```yml
EXE: CodeFlow.exe
   NAME: CodeFlow.exe
   APP_NAME: CodeFlow code review tool
   VENDOR: Microsoft
   EXE_ID: 0bcbaea6-c7b9-4fc6-a88c-8e4d86a4b7eb
   APP_ID: 543cf430-0d6f-4952-a9c2-d38718839608
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Microsoft
      FILE_DESCRIPTION: CodeFlow
      FROM_BIN_FILE_VERSION: 563031557799936
      UPTO_BIN_FILE_VERSION: 844424930131967
   MATCHING_FILE: Microsoft.CodeFlow.Client.Core.dll
      NAME: Microsoft.CodeFlow.Client.Core.dll
   SHIM_REF: RegisterAppRestart
      NAME: RegisterAppRestart
      SHIM_TAGID: 0x2DC30
      COMMAND_LINE: |COPY_COMMAND_LINE|
```

```yml
EXE: notepad++.exe
   NAME: notepad++.exe
   APP_NAME: Notepad++
   VENDOR: Don HO don.h@free.fr
   EXE_ID: b38c7ca0-382f-4e68-84b2-20bc6f9bd0d1
   APP_ID: 04841447-307d-47a8-a62d-d21ca44e6c99
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Don HO don.h@free.fr
      PRODUCT_NAME: Notepad++
      UPTO_BIN_PRODUCT_VERSION: 2251799813685247
   SHIM_REF: RegisterAppRestart
      NAME: RegisterAppRestart
      SHIM_TAGID: 0x2DC30
```

```yml
EXE: opera.exe
   NAME: opera.exe
   APP_NAME: Opera
   VENDOR: Opera Software
   EXE_ID: 6c274e45-2cc5-47d5-8ff0-dc87e1dc115a
   APP_ID: 0f35d1c7-c88b-4ac5-acaa-df0bd46f7eac
   MATCHING_FILE: *
      NAME: *
      COMPANY_NAME: Opera Software
      PRODUCT_NAME: Opera Internet Browser
      FROM_BIN_PRODUCT_VERSION: 19421773393035264
      UPTO_BIN_PRODUCT_VERSION: -281474976710657
   SHIM_REF: RegisterAppRestart
      NAME: RegisterAppRestart
      SHIM_TAGID: 0x2DC30
```

```yml
EXE: XMind.exe
   NAME: XMind.exe
   APP_NAME: XMind 8
   VENDOR: XMind LTD.
   EXE_ID: 9f2fc66f-63ab-4e9b-a8dc-1b389a0106bf
   APP_ID: 008e73af-9383-4f35-be33-c0a4e773b9d1
   MATCHING_FILE: *
      NAME: *
   MATCHING_FILE: *
      NAME: *
      MATCH_LOGIC_NOT: True
      EXPORT_NAME: electron.exe
   MATCHING_FILE: xmindshell.dll
      NAME: xmindshell.dll
      FILE_DESCRIPTION: XMind Shell Module
   SHIM_REF: RegisterAppRestart
      NAME: RegisterAppRestart
      SHIM_TAGID: 0x2DC30
```
</details>

## Detection

The Event Log `Microsoft-Windows-Application-Experience` (Microsoft-Windows-Application-Experience%4Program-Telemetry.evtx) offers EIDs `500`, `502` and `505` to detect any fixes applied to applications. We can monitor the fields `FixName`, `FixID`, `ExePath`