# PowerShell

PowerShell has a list of suspicious keywords. If found in a script block an automatic 4104 event will be generated regardless of logging policy (True for both PWSH 5/7).

Look for EID 4104 with Level 3 (Warning)

- **Source Code**: https://github.com/PowerShell/PowerShell/blob/master/src/System.Management.Automation/engine/runtime/CompiledScriptBlock.cs
- **DLL**: System.Management.Automation.dll
- **Reference**: https://twitter.com/nas_bench/status/1646252357020205060

```yml
- Add-Type
- AddSecurityPackage
- AdjustTokenPrivileges
- AllocHGlobal
- BindingFlags
- Bypass
- CloseHandle
- CreateDecryptor
- CreateEncryptor
- CreateProcessWithToken
- CreateRemoteThread
- CreateThread
- CreateType
- CreateUserThread
- Cryptography
- CryptoServiceProvider
- CryptoStream
- DangerousGetHandle
- DeclaringMethod
- DeclaringType
- DefineConstructor
- DefineDynamicAssembly
- DefineDynamicModule
- DefineEnum
- DefineField
- DefineLiteral
- DefinePInvokeMethod
- DefineType
- DeflateStream
- DeviceIoControl
- DllImport
- DuplicateTokenEx
- Emit
- EncodedCommand
- EnumerateSecurityPackages
- ExpandString
- FreeHGlobal
- FreeLibrary
- FromBase64String
- GetAssemblies
- GetAsyncKeyState
- GetConstructor
- GetConstructors
- GetDefaultMembers
- GetDelegateForFunctionPointer
- GetEvent
- GetEvents
- GetField
- GetFields
- GetForegroundWindow
- GetInterface
- GetInterfaceMap
- GetInterfaces
- GetKeyboardState
- GetLogonSessionData
- GetMember
- GetMembers
- GetMethod
- GetMethods
- GetModuleHandle
- GetNestedType
- GetNestedTypes
- GetPowerShell
- GetProcAddress
- GetProcessHandle
- GetProperties
- GetProperty
- GetTokenInformation
- GetTypes
- ILGenerator
- ImpersonateLoggedOnUser
- InteropServices
- IntPtr
- InvokeMember
- kernel32
- LoadLibrary
- LogPipelineExecutionDetails
- MakeArrayType
- MakeByRefType
- MakeGenericType
- MakePointerType
- Marshal
- memcpy
- MemoryStream
- Methods
- MiniDumpWriteDump
- NonPublic
- OpenDesktop
- OpenProcess
- OpenProcessToken
- OpenThreadToken
- OpenWindowStation
- PasswordDeriveBytes
- Properties
- ProtectedEventLogging
- PtrToString
- PtrToStructure
- ReadProcessMemory
- ReflectedType
- RevertToSelf
- RijndaelManaged
- ScriptBlockLogging
- SetInformationProcess
- SetThreadToken
- SHA1Managed
- StructureToPtr
- ToBase64String
- TransformFinalBlock
- TypeHandle
- TypeInitializer
- UnderlyingSystemType
- UnverifiableCodeAttribute
- VirtualAlloc
- VirtualFree
- VirtualProtect
- WriteByte
- WriteInt32
- WriteProcessMemory
- ZeroFreeGlobalAllocUnicode
```