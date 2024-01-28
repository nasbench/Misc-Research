# At.EXE

The following are research notes that are the results of reversing the `At.EXE` binary. If you're interested into how the binary works or how some functionalities are implemented read along.

Default location:

- C:\Windows\System32\at.exe
- C:\Windows\SysWOW64\at.exe

### Loading `netmsg.dll`

The `at.exe` binary tries to load `netmsg.dll` as one of the first things in its main function. This is done via the following piece of code.

```c
if ( !ExpandEnvironmentStringsW(L"%systemroot%\\system32\\netmsg.dll", Dst, 0x105u)
    || (GlobalMessageHandle = (__int64)LoadLibraryExW(Dst, 0i64, 0x802u)) == 0 )
```

It will expand the string `%systemroot%\\system32\\netmsg.dll` and will try to load the value via `LoadLibraryExW`. If either of them return `false` the program will "exit"

> **Note**
>
> While this might seem vulnerable to DLL side loading via environment variable tampering. If we inspect the parameters of `LoadLibraryExW` we can see some flags being passed in the third param, namely `0x802`. From [MSDN](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryexw) we can gather the following
>- `LOAD_LIBRARY_AS_DATAFILE` - 0x00000002
>- `LOAD_LIBRARY_SEARCH_SYSTEM32` - 0x00000800
> This will load the DLL in question not as a module but only as a "resource". You can read more [here](https://bytepointer.com/resources/old_new_thing/20141120_271_a_library_loaded_via_load_library_as_datafile_or_similar_flags_doesnt_get_to_pla.htm)

### Using Old Parsing

The `at.exe` binary can switch the parsing of the arguments to the old NT 3.51 parsing via a registry value. This checked by the internal function `UseOldParsing`. This function is called from `ValidateCommand` and it'll check if the value `UseOldParsing` is defined and has the data `DWORD (0x00000001)`

```c
  cbData = 4;
v0 = 0;
Data = 0;
if ( !RegOpenKeyExW(
        HKEY_LOCAL_MACHINE,
        L"System\\CurrentControlSet\\Services\\Schedule\\Parameters",
        0,
        0x20019u,
        &hKey) )
{
if ( !RegQueryValueExW(hKey, L"UseOldParsing", 0i64, &Type, (LPBYTE)&Data, &cbData) && Type == 4 )
    v0 = Data == 1;
RegCloseKey(hKey);
}
```

The following is the registry path checked

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\Schedule\Parameters\UseOldParsing
```

Example on how the old parsing handled things in the following resources:

- https://www.itprotoday.com/compute-engines/jsi-tip-0694-command-parses-differently-nt-351-vs-nt-40
- https://www.itprotoday.com/windows-8/command-works-differently-under-nt-40-nt-351
