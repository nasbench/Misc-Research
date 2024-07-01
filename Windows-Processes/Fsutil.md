# Fsutil.EXE

The following will describe how some flags of the "fsutil" utility actually works behind the scenes. From API calls to registry keys and everything in between. If you're interested follow along :)

## devdrv

### query

```bash
fsutil devdrv query
```

The query functionality is handled internally by `DevdrvQuery` function which calls the `DevdrvGetEnableRegValue` function. From the name we can guess that it should query the registry value to obtain the state of the "Dev Drive". But in reality it just calls [GetDeveloperDriveEnablementState](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-getdeveloperdriveenablementstate) which is implemented in `kernelBase.dll` (redirected from the API set `api-ms-win-core-sysinfo-l1-2-6.dll`).

The `GetDeveloperDriveEnablementState` function is the one performing the query to the registry and checks the following locations.

- `HKEY_LOCAL_MACHINE\System\CurrentControlSet\Policies\FsEnableDevDrive`
- `HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\FileSystem\FsEnableDevDrive`

`FsEnableDevDrive` is of type `DWORD` where `1` indicates that it's enabled, and `0` means it's disabled.

### enable

```bash
fsutil devdrv enable
fsutil devdrv enable /allowAv
fsutil devdrv enable /disallowAv
```

Enabling the "Dev Drive" will update the registry values talked about in the [query](#query) section. Internally this is handled by the `DevdrvEnable` function. Which will call `DevdrvSetEnableRegKey`
