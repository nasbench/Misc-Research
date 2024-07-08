# WinExec - Symantec Endpoint Protection Manager (SEPM)

Reference:

- https://twitter.com/nas_bench/status/1483402513193881600

## Summary

Having an instance of Symantec Endpoint Protection Manager (SEPM) installed would give user access to the binary "WinExec.EXE". It can be used to launch arbitrary commands.

It offers to mode of execution.

- If the `-c` the flag is provided. The next argument will be called directly by the `CreateProcessW` API.
- Otherwise the provided argument is passed to `cmd.exe /c <Command>`.

### Example

```powershell
WinExec.exe <Command>
WinExec.exe -c <Binary>
```

![image](https://user-images.githubusercontent.com/8741929/233515664-ee4f78b0-db0a-4397-bdd5-dcc7fa6f0159.png)

### Additional Details

Taking a look behind the scene we can see the following decompiled main function.

```c++
int __stdcall wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPWSTR lpCmdLine, int nShowCmd)
{
  HMODULE LibraryA; // eax
  HMODULE v5; // esi
  BOOL (__stdcall *HeapSetInformation)(HANDLE, HEAP_INFORMATION_CLASS, PVOID, SIZE_T); // eax
  wchar_t Destination[1024]; // [esp+8h] [ebp-804h] BYREF

  LibraryA = LoadLibraryA("kernel32.dll");
  v5 = LibraryA;
  if ( LibraryA )
  {
    HeapSetInformation = (BOOL (__stdcall *)(HANDLE, HEAP_INFORMATION_CLASS, PVOID, SIZE_T))GetProcAddress(
                                                                                              LibraryA,
                                                                                              "HeapSetInformation");
    if ( HeapSetInformation )
      HeapSetInformation(0, HeapEnableTerminationOnCorruption, 0, 0);
    FreeLibrary(v5);
  }
  if ( dword_11D9B24 < 2 )
    return -1;
  if ( !wcscmp(*(const unsigned __int16 **)(dword_11D9B2C + 4), L"-c") )
  {
    if ( dword_11D9B24 < 3 )
      return -1;
    return sub_11D5290(*(LPWSTR *)(dword_11D9B2C + 8));
  }
  else
  {
    wcscpy_s(Destination, 0x3FFu, L"cmd.exe /c ");
    wcscat_s(Destination, 0x3E8u, *(const wchar_t **)(dword_11D9B2C + 4));
    return sub_11D5290(Destination);
  }
}
```

From a LOLBIN perspective we're going to focus on the following section

```c++
  if ( dword_11D9B24 < 2 )
    return -1;
  if ( !wcscmp(*(const unsigned __int16 **)(dword_11D9B2C + 4), L"-c") )
  {
    if ( dword_11D9B24 < 3 )
      return -1;
    return sub_11D5290(*(LPWSTR *)(dword_11D9B2C + 8));
  }
  else
  {
    wcscpy_s(Destination, 0x3FFu, L"cmd.exe /c ");
    wcscat_s(Destination, 0x3E8u, *(const wchar_t **)(dword_11D9B2C + 4));
    return sub_11D5290(Destination);
  }
```

In this case the `dword_11D9B24` variable represent the number of argument being passed. The first ensures that there's at least 1 argument being passed. Then another check is made to see if a `-c` passed. If that's the case then the program makes sure that there is another argument after `-c`. If there is then the latter is passed directly to `sub_11D5290` (which we'll look at later) else the programs terminates.

If there is not `-c` flag being passed, then all the arguments passed to "WinExec.EXE" are concatenated to the string `cmd.exe /c` and passed to `sub_11D5290`.

This translates to the following:

- If `dword_11D9B24` is less than 2, the program exits.
- Checks if the first command line argument is `-c`:
    - If true, checks if `dword_11D9B24` is at least 3. If not, returns -1 (exit).
    - Calls `sub_11D5290` with the subsequent argument.
- If the argument is not `-c`, constructs a command to execute via `cmd.exe /c` and calls `sub_11D5290` with this command.

Now let's look at the `sub_11D5290` function.

```c++
int __cdecl sub_11D5290(LPWSTR lpCommandLine)
{
  struct _STARTUPINFOW StartupInfo; // [esp+0h] [ebp-54h] BYREF
  struct _PROCESS_INFORMATION ProcessInformation; // [esp+44h] [ebp-10h] BYREF

  GetStartupInfoW(&StartupInfo);
  memset(&ProcessInformation, 0, sizeof(ProcessInformation));
  if ( !CreateProcessW(0, lpCommandLine, 0, 0, 0, 0x8000000u, 0, 0, &StartupInfo, &ProcessInformation) )
    return -1;
  WaitForSingleObject(ProcessInformation.hProcess, 0xFFFFFFFF);
  return 0;
}
```

The most interesting thing for our case is that the `lpCommandLine` argument is passed directly to `CreateProcessW`. This means that anything we pass from the CLI either via the `-c` flag or other will be executed via WinExec by proxy.
