# Built-In SHIM DB Hijacking

The idea is to look for abusable entries in the `sysmain.sdb` database and similar.

An abusable entry is an entry that meets the following conditions:

- Doesn't perform enough checks for the binary that's being shimmed. For example, the checks are only for PE metadata and the name. As these can be easily copied this can be dangerous.

- The Application is referencing an interesting Shim that lets us do something interesting. Examples include:
    - CreateDummyProcess
    - DisableWindowsDefender
    - TerminateExe
    - NoSignatureCheck

## Malicious Shime DB Generator/Framework

Microsoft provide a lot of built-in shims that have "great" (potentially abusable) functionalities. The idea is to build a wrapper framework around this using the AppCompat DB [API](https://learn.microsoft.com/en-us/windows/win32/devnotes/sdbcreatedatabase). This would allows us to create a DB and its entries in a stealthy way avoiding any calls to ``sdbinst.exe`` for example.

We could also expan this same idea to KernelShims by allowing the user to add driver entries they want to shim. Abusing the fact described in Alex Ionescu's [talk](https://www.youtube.com/watch?v=qCa9icMqBNM&ab_channel=ReactOSCommunity). Which is that the shims `atofail` and `kmatofail` do not exists on the system and can be hijacked.

The idea is to abuse the fact that we can add entries to the `\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Compatibility\Driver` registry key and apply shims that might disrupt the flow of some drivers.

By adding an entry an asigning it a value of `KernelPadSectionsOverride` for example. Which by its description from Windows Internals is the following: `Prevents discardable sections of any kernel module to be freed by the memory manager and blocks the loading of the target driver (where the shim is applied).`

### Interesting App Shims

These are but a couple of the Shims that we can leverage to achieve malicious or defensive effects.

- ``APILogger``
- ``CorrectFilePath``
- ``CreateDummyProcess``
- ``DisableWindowsDefender``
- ``ForceTerminateProcess``
- ``IgnoreLoadLibrary``
- ``InjecDll``
- ``LoadLibraryCWD``
- ``NoSignatureCheck``
- ``RedirectEXE``
- ``RedirectShortcut``
- ``TerminateExe``

### Detection

- The Event Log `Microsoft-Windows-Application-Experience` has EIDs `500`, `502` and `505` to detect any fixes applied to applications. We can monitor the fields `FixName`, `FixID`, `ExePath`

- Monitoring for SDB registry entries is also a must.
    - `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\InstalledSDB` for custom installed DBs
    - `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Custom` for currently patched applications

- For kernel Shims, monitoring for uncommon entries in `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Compatibility\Driver` and uncommon `Shims` values that try to prevent drivers from doing its work.

- The `Microsoft-Windows-Kernel-ShimEngine` event log `EID 3` will provide information on kernel shims applied to drivers. Monitor for uncommon values

- The `Microsoft-Windows-Kernel-ShimEngine` event log `EID 10 -> 24` also provide ETW events if you apply the ``DriverScope`` shim on a driver (See Windows 7 Internals Part 2 for more information)

## Release

TBD

## References

- Internal Research
- https://files.brucon.org/2015/Tomczak_and_Ballenthin_Shims_for_the_Win.pdf
- https://www.youtube.com/watch?v=k9kDO2w91fE&list=PLlo54QX--Ad70lWSeo_hSB6CEjaBno-7x&index=13&ab_channel=AllHackingCons
- https://www.geoffchappell.com/studies/windows/km/ntoskrnl/api/kshim/ksecore/index.htm
- https://www.geoffchappell.com/studies/windows/km/ntoskrnl/api/kshim/drvmain.htm
- https://www.youtube.com/watch?v=qCa9icMqBNM&ab_channel=ReactOSCommunity
