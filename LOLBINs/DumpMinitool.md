# DumpMinitool.exe LOLBIN

This binary can be used as a LOLBIN as described [here](https://lolbas-project.github.io/lolbas/OtherMSBinaries/DumpMinitool/)

### Addtional Info

- The arguments flags are meaningless only the order is important. This means as long as you provide exactly 6 flags and their value the binary will still work. Here are the exact positions for reference:

```c#
// Usage: --file <fullyResolvedPath> --processId <processId> --dumpType <dumpType>

args[0] // --file 
args[1] // <fullyResolvedPath>
args[2] // --processId
args[3] // <processId>
args[4] // --dumpType
args[5] //<dumpType>
```

- The `processId` argument must be an intereger as it's type casted before storage

```c#
int processId = int.Parse(args[3], (IFormatProvider) CultureInfo.InvariantCulture);
```

- There are three types of dump type options:

```c#
internal enum MiniDumpTypeOption
{
  Full,
  WithHeap,
  Mini,
}
```

- The dump type value are case sensitive since they are used in a switch case for comparaison

```c#
switch (type)
{
  case MiniDumpTypeOption.Full:
    // Code
  case MiniDumpTypeOption.WithHeap:
    // Code
  case MiniDumpTypeOption.Mini:
    // Code
  default:
    // Code
}
```

- The binary is using `MiniDumpWriteDump` from `Dbghelp.dll`.
- If a dump type other than the ones specified in the ENUM is provided. It will default to using the `MiniDumpNormal` - https://learn.microsoft.com/en-us/windows/win32/api/minidumpapiset/ne-minidumpapiset-minidump_type 

```c#
switch (type)
{
  case MiniDumpTypeOption.Full:
    minidumpType = MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithDataSegs | MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithFullMemory | MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithHandleData | MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithUnloadedModules | MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithFullMemoryInfo | MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithThreadInfo | MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithTokenInformation;
    break;
  case MiniDumpTypeOption.WithHeap:
    minidumpType = MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithDataSegs | MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithHandleData | MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithUnloadedModules | MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithPrivateReadWriteMemory | MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithFullMemoryInfo | MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithThreadInfo | MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithTokenInformation;
    break;
  case MiniDumpTypeOption.Mini:
    minidumpType = MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpWithThreadInfo;
    break;
  default:
    minidumpType = MiniDumpWriteDump.NativeMethods.MinidumpType.MiniDumpNormal;
    break;
}
...
...
...
[Flags]
      public enum MinidumpType : uint
      {
        MiniDumpNormal = 0,
        MiniDumpWithDataSegs = 1,
        MiniDumpWithFullMemory = 2,
...
...
...
```

- The dump is performed by calling `MiniDumpWriteDump` https://learn.microsoft.com/en-us/windows/win32/api/minidumpapiset/nf-minidumpapiset-minidumpwritedump

```c#
for (int index = 0; index < 5 && !MiniDumpWriteDump.NativeMethods.MiniDumpWriteDump(process.Handle, (uint) process.Id, fileStream.SafeFileHandle, dumpType, ref exceptionParam, IntPtr.Zero, IntPtr.Zero); ++index)
{
  int forLastWin32Error = Marshal.GetHRForLastWin32Error();
  if (forLastWin32Error != -2147024597)
    Marshal.ThrowExceptionForHR(forLastWin32Error);
}
```
