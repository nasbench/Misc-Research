# Compatibility Application Layers

This table lists all documented application layers as extracted from the `Microsoft Application Compatibility Database` (Compatadmin.exe) and `sysmain.sdb`

Some of the Shims are also documented in MSDN
    - [Windows Vista, Windows 7, and Windows 8 Operating Systems](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-7/cc722305(v=ws.10)#compatibility-modes)
    - [Windows XP and Earlier](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-7/cc709672(v=ws.10))


> **Note**
>
> Some layers that such as ``ARM64CHPEOnlyNtdll`` and ``ARM64BarriersX87_SIMD_Atomic`` were omitted for ease of classification

| Layers (Compatibility Modes)                        | SHIMs / FLAGS Used |
| --------------------------------------------------- | ------- |
| CloudFilesFullHydration | CloudFilesFullHydration |
| DisableDXMaximizedWindowedMode | DXMaximizedWindowedMode, DXGICompat |
| HighDpiAware | HighDpiAware |
| TransformLegacyColorManaged | TransformLegacyColorManagedWindows |
| Windows8RC | WinRTTestShim, WinRTTestFlag |
| 16BitColor | ForceDisplayMode |
| 256Color | Force8BitColor, DisableThemes |
| 640X480 | Force640x480 |
| 8And16BitAggregateBlts | 8And16BitAggregateBlts |
| 8And16BitDXMaxWinMode | 8And16BitDXMaxWinMode |
| 8And16BitGDIRedraw | 8And16BitGDIRedraw |
| 8And16BitTimedPriSync | 8And16BitTimedPriSync |
| AppRecorder | AppRecorder |
| CentennialOffice | VirtualRegistry |
| CentennialOfficex64 | VirtualRegistry |
| CloudFilesFullHydrationOnOpen | CloudFilesFullHydrationOnOpen |
| CloudFilesHydrationDisallowed | CloudFilesHydrationDisallowed |
| Disable8And16BitD3D | Disable8And16BitD3D |
| Disable8And16BitModes | Disable8And16BitModes |
| DisableCicero | DisableCicero |
| DisableFadeAnimations | DisableFadeAnimations |
| DisableNXHideUI | DisableNX |
| DisableNXShowUI | DisableNX |
| DisableThemeMenus | DisableThemeMenus |
| DisableThemes | DisableThemes |
| DisableTransformLegacyColorManaged | DisableTransformLegacyColorManagedWindows |
| DisableUserCallbackException | AddProcessParametersFlags |
| DisguisePlaceholders | DisguisePlaceholders |
| DPIUnaware | DPIUnaware |
| DWM8And16BitMitigation | DetectorDWM8And16Bit |
| DwmAutoParenting | DwmAutoParenting |
| DXMaximizedWindowedMode | DXMaximizedWindowedMode |
| EmulateSorting | EmulateSorting |
| EmulateSortingServer2008 | EmulateSortingServer2008 |
| EmulateSortingVista | EmulateSortingVista |
| EmulateSortingWindows61 | EmulateSortingWindows61 |
| EnableLegacyTls | EnableLegacyTls |
| EnableNXShowUI |
| FDR | FDR |
| FixDisplayChangeRefreshRate | FixDisplayChangeRefreshRate |
| FontMigration | FontMigration |
| ForceDxSetupSuccess | ForceDxSetupSuccess |
| ForcePaddedBorder | ForceLegacyResizeCM |
| GdiDPIScaling | GdiDPIScaling |
| IgnoreAdobeKMPrintDriverMessageBox | IgnoreMessageBox |
| Installer | Installer |
| IntelLockFile | IntelLockFile |
| International | HandleDBCSUserName, HandleDBCSUserName2, IgnoreOemToChar, RedirectDBCSTempPath, CorrectFarEastFont |
| iTunesAutoplay | iTunesAutoplay |
| LoadLibraryRedirect | LoadLibraryRedirectFlag |
| LowLevelHooksTimeout | LowLevelHooksTimeout |
| MsiAuto |
| NT4SP5 | WinNT4SP5VersionLie, VirtualRegistry, DuplicateHandleFix, ElevateCreateProcess, EmulateSorting, FailObsoleteShellAPIs,  |FaultTolerantHeap, LoadLibraryCWD, HandleBadPtr, RedirectBDE, RedirectMP3Codec, WRPDllRegister, WRPMitigation, DetectorDWM8And16Bit, GiveupForeground, NoGhost, FTMFromCurrentAPI, EnableLegacyExceptionHandlinginOLE, HardwareAudioMixer
| NullEnvironment | NullEnvironment |
| PerProcessSystemDPIForceOff | PerProcessSystemDPIForceOff |
| PerProcessSystemDPIForceOn | PerProcessSystemDPIForceOn |
| PreventBlockedShutdown | WMQueryEndSessionToTerminateProcess |
| ProfilesSetup | ProfilesEnvStrings, ProfilesGetFolderPath, ProfilesRegQueryValueEx |
| RedirectCHHlocaletoCHT | RedirectCHHlocaletoCHT |
| RegisterAppRestart | RegisterAppRestart |
| RunAsAdmin | RunAsAdmin |
| RunAsHighest | RunAsHighest |
| RunAsInvoker | RunAsInvoker |
| Splwow64CompatLayer | Splwow64Compat |
| VerifyVersionInfoLiteLayer | VerifyVersionInfoLite |
| VirtualizeDeleteFileLayer | VirtualizeDeleteFile |
| VistaRTM | ElevateCreateProcess, EmulateSortingVista, FailObsoleteShellAPIs, GlobalMemoryStatus2GB, HandleBadPtr, RedirectBDE,  |RedirectMP3Codec, SyncSystemAndSystem32, VistaRTMVersionLie, VirtualRegistry, FaultTolerantHeap, WRPDllRegister, WRPMitigation, DXMaximizedWindowedMode, DetectorDWM8And16Bit, VirtualizeDesktopPainting, FixDisplayChangeRefreshRate, NoGhost, NoPaddedBorder, AllocDebugInfoForCritSections
| VistaSP1 | ElevateCreateProcess, EmulateSortingVista, FailObsoleteShellAPIs, GlobalMemoryStatus2GB, HandleBadPtr, RedirectBDE,  |RedirectMP3Codec, SyncSystemAndSystem32, VistaSP1VersionLie, VirtualRegistry, FaultTolerantHeap, WRPDllRegister, WRPMitigation, DXMaximizedWindowedMode, DetectorDWM8And16Bit, VirtualizeDesktopPainting, FixDisplayChangeRefreshRate, NoGhost, NoPaddedBorder, AllocDebugInfoForCritSections
| VistaSP1VersionLie | VistaSP1VersionLie |
| VistaSP2 | ElevateCreateProcess, EmulateSortingVista, FailObsoleteShellAPIs, GlobalMemoryStatus2GB, HandleBadPtr, RedirectBDE,  |RedirectMP3Codec, SyncSystemAndSystem32, VistaSP2VersionLie, VirtualRegistry, FaultTolerantHeap, WRPDllRegister, WRPMitigation, DXMaximizedWindowedMode, DetectorDWM8And16Bit, VirtualizeDesktopPainting, FixDisplayChangeRefreshRate, NoGhost, NoPaddedBorder, AllocDebugInfoForCritSections
| VistaSP2VersionLie | VistaSP2VersionLie |
| Win2000 | DirectXVersionLie, Win2000VersionLie, VirtualRegistry, DuplicateHandleFix, ElevateCreateProcess, EmulateSorting,  |FailObsoleteShellAPIs, FaultTolerantHeap, LoadLibraryCWD, HandleBadPtr, RedirectBDE, RedirectMP3Codec, WRPDllRegister, WRPMitigation, DetectorDWM8And16Bit, NoGhost, EnableLegacyExceptionHandlinginOLE, HardwareAudioMixer
| Win2000Sp2 | DirectXVersionLie, Win2000Sp2VersionLie, VirtualRegistry, DuplicateHandleFix, ElevateCreateProcess, EmulateSorting,  |FailObsoleteShellAPIs, FaultTolerantHeap, LoadLibraryCWD, HandleBadPtr, RedirectBDE, RedirectMP3Codec, WRPDllRegister, WRPMitigation, DetectorDWM8And16Bit, NoGhost, EnableLegacyExceptionHandlinginOLE, HardwareAudioMixer
| Win2000Sp3 | DirectXVersionLie, Win2000Sp3VersionLie, VirtualRegistry, DuplicateHandleFix, ElevateCreateProcess, EmulateSorting,  |FailObsoleteShellAPIs, LoadLibraryCWD, HandleBadPtr, RedirectBDE, RedirectMP3Codec, WRPDllRegister, WRPMitigation, DetectorDWM8And16Bit, NoGhost, EnableLegacyExceptionHandlinginOLE, HardwareAudioMixer
| Win7RTM | ElevateCreateProcess, EmulateSortingWindows61, FailObsoleteShellAPIs, GlobalMemoryStatus2GB, HandleBadPtr, RedirectBDE,  |RedirectMP3Codec, SyncSystemAndSystem32, Win7RTMVersionLie, VirtualRegistry, FaultTolerantHeap, WRPDllRegister, WRPMitigation, DXMaximizedWindowedMode, DetectorDWM8And16Bit, FixDisplayChangeRefreshRate, NoGhost, NoPaddedBorder, AllocDebugInfoForCritSections
| Win7RTMVersionLie | Win7RTMVersionLie |
| Win81RTMVersionLie | Win81RTMVersionLie |
| Win8RTM | ElevateCreateProcess, EmulateSortingWindows61, FailObsoleteShellAPIs, GlobalMemoryStatus2GB, HandleBadPtr, RedirectBDE,  |RedirectMP3Codec, SyncSystemAndSystem32, Win8RTMVersionLie, VirtualRegistry, FaultTolerantHeap, WRPDllRegister, WRPMitigation, DXMaximizedWindowedMode, DetectorDWM8And16Bit, FixDisplayChangeRefreshRate, NoGhost, NoPaddedBorder, AllocDebugInfoForCritSections
| Win8RTMVersionLie | Win8RTMVersionLie |
| Win95 | WinExecRaceConditionFix, Win95VersionLie, VirtualizeDesktopPainting, AddWritePermissionsToDeviceFiles,  |ChangeAuthenticationLevel, CorrectBitmapHeader, CorrectCreateEventName, CorrectFilePaths, CorrectSoundDeviceId, CustomNCRender, DirectPlayEnumOrder, DirectXVersionLie, DisableBoostThread, DXMaximizedWindowedMode, ElevateCreateProcess, EmulateCDFS, EmulateCreateFileMapping, EmulateCreateProcess, EmulateDeleteObject, EmulateDirectDrawSync, EmulateDrawText, EmulateFindHandles, EmulateGetCommandLine, EmulateGetDeviceCaps, EmulateGetDiskFreeSpace, EmulateGetProfileString, EmulateHeap, EmulateJoystick, EmulateMissingEXE, EmulatePlaySound, EmulatePrinter, EmulateSlowCPU, EmulateSorting, EmulateTextColor, EmulateToolHelp32, EmulateUSER, EmulateVerQueryValue, EmulateWriteFile, EnableRestarts, FailObsoleteShellAPIs, FileVersionInfoLie, ForceAnsiGetDisplayNameOf, ForceCDStop, ForceCoInitialize, ForceDXSetupSuccess, ForceKeepFocus, ForceShellLinkResolveNoUI, GlobalMemoryStatusLie, HandleRegExpandSzRegistryKeys, HandleWvsprintfExceptions, HideDisplayModes, IgnoreException, IgnoreLoadLibrary, IgnoreScheduler, LoadLibraryCWD, MapMemoryB0000, ProfilesEnvStrings, ProfilesGetFolderPath, ProfilesRegQueryValueEx, RedirectBDE, RedirectMP3Codec, SingleProcAffinity, SyncSystemAndSystem32, VirtualRegistry, WRPDllRegister, WRPMitigation, HandleAPIExceptions, DetectorDWM8And16Bit, FixDisplayChangeRefreshRate, AdditiveRunAsHighest, GiveupForeground, NoGhost, EnableLegacyExceptionHandlinginOLE, HardwareAudioMixer, NoPaddedBorder, AllocDebugInfoForCritSections
| Win98 | WinExecRaceConditionFix, Win98VersionLie, VirtualizeDesktopPainting, AddWritePermissionsToDeviceFiles,  |ChangeAuthenticationLevel, CorrectBitmapHeader, CorrectCreateEventName, CorrectFilePaths, CorrectSoundDeviceId, CustomNCRender, DirectPlayEnumOrder, DirectXVersionLie, DisableBoostThread, DXMaximizedWindowedMode, ElevateCreateProcess, EmulateCDFS, EmulateCreateFileMapping, EmulateCreateProcess, EmulateDeleteObject, EmulateDirectDrawSync, EmulateDrawText, EmulateFindHandles, EmulateGetCommandLine, EmulateGetDeviceCaps, EmulateGetDiskFreeSpace, EmulateGetProfileString, EmulateHeap, EmulateJoystick, EmulateMissingEXE, EmulatePlaySound, EmulatePrinter, EmulateSlowCPU, EmulateSorting, EmulateTextColor, EmulateToolHelp32, EmulateUSER, EmulateVerQueryValue, EmulateWriteFile, EnableRestarts, FailObsoleteShellAPIs, FileVersionInfoLie, ForceAnsiGetDisplayNameOf, ForceCDStop, ForceCoInitialize, ForceDXSetupSuccess, ForceKeepFocus, ForceShellLinkResolveNoUI, GlobalMemoryStatusLie, HandleRegExpandSzRegistryKeys, HandleWvsprintfExceptions, HideDisplayModes, IgnoreException, IgnoreLoadLibrary, IgnoreScheduler, LoadLibraryCWD, MapMemoryB0000, ProfilesEnvStrings, ProfilesGetFolderPath, ProfilesRegQueryValueEx, RedirectBDE, RedirectMP3Codec, SingleProcAffinity, SyncSystemAndSystem32, VirtualRegistry, WRPDllRegister, WRPMitigation, HandleAPIExceptions, DetectorDWM8And16Bit, FixDisplayChangeRefreshRate, AdditiveRunAsHighest, GiveupForeground, NoGhost, EnableLegacyExceptionHandlinginOLE, HardwareAudioMixer, NoPaddedBorder, AllocDebugInfoForCritSections
| WinSrv03 | Win2k3RTMVersionLie, VirtualRegistry, ElevateCreateProcess, EmulateSorting, FailObsoleteShellAPIs, FaultTolerantHeap,  |LoadLibraryCWD, HandleBadPtr, RedirectBDE, RedirectMP3Codec, WRPDllRegister, WRPMitigation, DetectorDWM8And16Bit, EnableLegacyExceptionHandlinginOLE, HardwareAudioMixer
| WinSrv03Sp1 | Win2k3Sp1VersionLie, VirtualRegistry, ElevateCreateProcess, EmulateSorting, FailObsoleteShellAPIs, FaultTolerantHeap,  |LoadLibraryCWD, HandleBadPtr, RedirectBDE, RedirectMP3Codec, WRPDllRegister, WRPMitigation, DetectorDWM8And16Bit, EnableLegacyExceptionHandlinginOLE, HardwareAudioMixer
| WinSrv08R2RTM | ElevateCreateProcess, EmulateSortingWindows61, FailObsoleteShellAPIs, GlobalMemoryStatus2GB, HandleBadPtr,  |RedirectBDE, RedirectMP3Codec, SyncSystemAndSystem32, Win7RTMVersionLie, VirtualRegistry, FaultTolerantHeap, WRPDllRegister, WRPMitigation, DetectorDWM8And16Bit, NoGhost
| WinSrv08SP1 | ElevateCreateProcess, EmulateSortingServer2008, FailObsoleteShellAPIs, GlobalMemoryStatus2GB, HandleBadPtr,  |RedirectBDE, RedirectMP3Codec, SyncSystemAndSystem32, VistaSP1VersionLie, VirtualRegistry, FaultTolerantHeap, WRPDllRegister, WRPMitigation, DetectorDWM8And16Bit, NoGhost
| WinXP | VirtualizeDesktopPainting, DirectXVersionLie, WinXPVersionLie, VirtualRegistry, ElevateCreateProcess, EmulateSorting,  |FailObsoleteShellAPIs, FaultTolerantHeap, LoadLibraryCWD, HandleBadPtr, GlobalMemoryStatus2GB, RedirectBDE, RedirectMP3Codec, SyncSystemAndSystem32, WRPDllRegister, WRPMitigation, DetectorDWM8And16Bit, AccelGdipFlush, EnableLegacyExceptionHandlinginOLE, NoGhost, HardwareAudioMixer, AdditiveRunAsHighest
| WinXPSp1 | VirtualizeDesktopPainting, DirectXVersionLie, WinXPSp1VersionLie, VirtualRegistry, ElevateCreateProcess, EmulateSorting,  |FailObsoleteShellAPIs, FaultTolerantHeap, LoadLibraryCWD, HandleBadPtr, GlobalMemoryStatus2GB, RedirectBDE, RedirectMP3Codec, SyncSystemAndSystem32, WRPDllRegister, WRPMitigation, DetectorDWM8And16Bit, AccelGdipFlush, EnableLegacyExceptionHandlinginOLE, NoGhost, HardwareAudioMixer, AdditiveRunAsHighest
| WinXPSp2 | CustomNCRender, VirtualizeDesktopPainting, DirectXVersionLie, WinXPSP2VersionLie, VirtualRegistry, ElevateCreateProcess,  |EmulateSorting, FailObsoleteShellAPIs, FaultTolerantHeap, LoadLibraryCWD, HandleBadPtr, GlobalMemoryStatus2GB, RedirectBDE, RedirectMP3Codec, SyncSystemAndSystem32, WRPDllRegister, WRPMitigation, DetectorDWM8And16Bit, AccelGdipFlush, DXMaximizedWindowedMode, FixDisplayChangeRefreshRate, EnableLegacyExceptionHandlinginOLE, NoGhost, HardwareAudioMixer, AdditiveRunAsHighest, NoPaddedBorder, AllocDebugInfoForCritSections
| WinXPSP2VersionLie | WinXPSP2VersionLie |
| WinXPSp3 | CustomNCRender, VirtualizeDesktopPainting, DirectXVersionLie, WinXPSP3VersionLie, VirtualRegistry, ElevateCreateProcess,  |EmulateSorting, FailObsoleteShellAPIs, FaultTolerantHeap, LoadLibraryCWD, HandleBadPtr, GlobalMemoryStatus2GB, RedirectBDE, RedirectMP3Codec, SyncSystemAndSystem32, WRPDllRegister, WRPMitigation, DetectorDWM8And16Bit, AccelGdipFlush, DXMaximizedWindowedMode, FixDisplayChangeRefreshRate, EnableLegacyExceptionHandlinginOLE, NoGhost, HardwareAudioMixer, AdditiveRunAsHighest, NoPaddedBorder, AllocDebugInfoForCritSections
| WinXPSP3VersionLie | WinXPSP3VersionLie |
| ApiLogLayer | LogShim |
| ApplicationMonitor | DetectorDWM8And16Bit |
| Arm64WowOnAmd64 | Arm64WowProcessLie |
| DW | DWmigration |
| ElevateCreateProcess | ElevateCreateProcess |
| FaultTolerantHeap | FaultTolerantHeap |
| VistaSetup | DeprecatedServiceShim, MakeShortcutRunAs, RedirectHKCUKeys, RedirectShortCut, WRPDllRegister, WRPMitigation |
| ShimEngineBasicTestLayer | CorrectFilePaths |
| Layer_Force640x480x8 | Force640x480x8 |
| Layer_ForceDirectDrawEmulation | ForceDirectDrawEmulation |
| Layer_Win95VersionLie | Win95VersionLie |
| RunAsHighest_GW | AdditiveRunAsHighest |
| VistaRTM_GW | ElevateCreateProcess, FailObsoleteShellAPIs, GlobalMemoryStatus2GB, HandleBadPtr, RedirectBDE, RedirectMP3Codec,  |SyncSystemAndSystem32, VistaRTMVersionLie, VirtualRegistry, FaultTolerantHeap, WRPDllRegister, WRPMitigation, NoGhost
| WinXPSp2_GW | DirectXVersionLie, WinXPSP2VersionLie, VirtualRegistry, ElevateCreateProcess, EmulateSorting, FailObsoleteShellAPIs,  |FaultTolerantHeap, LoadLibraryCWD, HandleBadPtr, GlobalMemoryStatus2GB, RedirectBDE, RedirectMP3Codec, SyncSystemAndSystem32, WRPDllRegister, WRPMitigation, EnableLegacyExceptionHandlinginOLE, NoGhost, HardwareAudioMixer, AdditiveRunAsHighest
| DetectorsAppHealth | DetectorMessageBox, DetectorShortRuntime, DetectorDeviceIoControl |
| DetectorsShimLog | DetectorPrivLogMicrophone, DetectorPrivLogCamera |
| DetectorsVista | DetectorDWM8And16Bit, DetectorException, DetectorShortRuntime |
| DetectorsWin7 | DetectorDWM8And16Bit, DetectorException, DetectorShortRuntime |
| DetectorsWin8 | DetectorException, DetectorShortRuntime |
| DetectorsXP | DetectorAccessDenied, DetectorDWM8And16Bit, DetectorException, DetectorGlobalObject, DetectorPrivilegeCheck,  |DetectorShortRuntime, DetectorRegExpandSz
| HandleRegExpandSzRegistryKeys | HandleRegExpandSzRegistryKeys |
| IgnoreFreeLibrary | IgnoreFreeLibrary |
| Installer | Installer |
| WRPMitigation | WRPMitigation |