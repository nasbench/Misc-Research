# Undocumented CLI Flags - Sdbinst.EXE

### Registry Cleaning - `-f`

The `-f` flag will clean/delete the following registry keys and their values related to AppCompat

- `HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Persisted`
- `HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Store`
- `HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers`
- `HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers`

### SDB Cache Flush - `-c`

The `-c` flag will call an internal function called `FlushCache` that flushes the cash by calling the API function [ShimFlushCache](https://learn.microsoft.com/en-us/windows/win32/devnotes/shimflushcache) from the `apphelp.dll`.

### Testing Flag - `-t`

The `-t` must be combined with the `w` flag. The purpose of this flag is to set an internal global variable called `g_msdbOperations` to the value of `0x20` (Hex) / `32` (Decimal)

```bash
case 't':
    if ( *((_WORD *)*v11 + 2) != 119 )
    {
LABEL_68:
        PrintMessage(0x3FEu);
        goto LABEL_284;
    }
    g_msdbOperations |= 0x20u;
    break;
```

When this value is set, the program will sleep for 20 seconds and then exit.

### SDB Merges - `-m`

The `-m` flag is used to initate the process of merging SBDs.

During merge operations a temporary file might get created in the `%TEMP%` directory with the format `temp.{16-Random-Hex-Chars}.sdb` (Example: `temp.01DA2456E502A0F0.sdb`)

Usually this flag is called by the `PcaSvc` service from `svchost` in the following form

```bash
sdbinst.exe -mm
sdbinst.exe  -m -bg
```

Information about the merged SDBs and others are stored in the registry key `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\SdbUpdates`

Internally this operation is via a function called `MergeSdb_FindAndMergeForTarget` called from `HandleCheckForMergeUpdate`.

### Background Execution - `-b`

he `-b` must be combined with the `g` flag. The purpose is to set an internal global variable called `g_msdbFlags` to the value of `4`. Which is later used to call [SetPriorityClass](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-setpriorityclass) in order to set the process mode to background or `PROCESS_MODE_BACKGROUND_BEGIN`.

```bash
case 'b':
    if ( *((_WORD *)*v11 + 2) != 103 )
        goto LABEL_68;
    g_msdbFlags |= 4u;
    goto LABEL_61
```
