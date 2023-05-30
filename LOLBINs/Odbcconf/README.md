# Odbcconf.exe LOLBIN

This binary can be used as a LOLBIN as described [here](https://lolbas-project.github.io/lolbas/Binaries/Odbcconf/)

## Additional Info

### Non-Required Action Flag "/a"

While most of the example in the wild are using the `/a` when leveraging `odbcconf` as a LOLBIN to execute an action. It's actually no required and you can call actions directly as it's hinted in the LOLBAS document with the `INSTALLDRIVER` example. So the following example will work. Keep this in mind while building detections for the CLI.

```powershell
odbcconf.exe regsvr C:\path\to\malicious.dll
```

### Persistence Via RunOnce

- Requirements: Admin Privileges

`Odbcconf` offers the flag `/r` which basically allows the app to register a command to be executed on the next reboot.

Example: `odbcconf.exe /r regsvr malicious.dll`

This will create a temporary file called `odbcconf.tmp` in the `C:\WINDOWS\system32\` directory that will contain the payload that was inputted via the command above.

Followed by the creation of a registry key in `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce\Setup` with the name `Configuring Data Access Components` and value `C:\Windows\System32\odbcconf.exe /E /F "C:\WINDOWS\system32\odbcconf.tmp"`

```xml
- <Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
- <System>
  <Provider Name="Microsoft-Windows-Sysmon" Guid="{5770385f-c22a-43e0-bf4c-06f5698ffbd9}" /> 
  <EventID>13</EventID> 
  <Version>2</Version> 
  <Level>4</Level> 
  <Task>13</Task> 
  <Opcode>0</Opcode> 
  <Keywords>0x8000000000000000</Keywords> 
  <TimeCreated SystemTime="2023-05-20T13:54:23.6199028Z" /> 
  <EventRecordID>1704341945</EventRecordID> 
  <Correlation /> 
  <Execution ProcessID="6488" ThreadID="8544" /> 
  <Channel>Microsoft-Windows-Sysmon/Operational</Channel> 
  <Computer>XXXXXXX</Computer> 
  <Security UserID="S-1-5-18" /> 
  </System>
- <EventData>
  <Data Name="RuleName">-</Data> 
  <Data Name="EventType">SetValue</Data> 
  <Data Name="UtcTime">2023-05-20 13:54:23.619</Data> 
  <Data Name="ProcessGuid">{9a08371b-ae8f-6474-d570-020000002800}</Data> 
  <Data Name="ProcessId">37628</Data> 
  <Data Name="Image">C:\Windows\System32\odbcconf.exe</Data> 
  <Data Name="TargetObject">HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce\Setup\Configuring Data Access Components</Data> 
  <Data Name="Details">C:\Windows\System32\odbcconf.exe /E /F "C:\WINDOWS\system32\odbcconf.tmp"</Data> 
  <Data Name="User">XXXXXX</Data> 
  </EventData>
  </Event>
```

The runonce command is basically running `odbcconf` with a response file with the `/f` and deleting the file after execution with the `/e`

### (Useless) Persistence Via RunOnce, Again?

- Requirements: Admin Privileges

An interesting thing with the `/r` flag is that the binary portion of the registry value isn't hardcoded. Meaning the  `C:\Windows\System32\odbcconf.exe` above is actually the path of the binary we executed.

If we simply copy it to another path or even rename it, it'll create the key with our binary.

```xml
<Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
- <System>
  <Provider Name="Microsoft-Windows-Sysmon" Guid="{5770385f-c22a-43e0-bf4c-06f5698ffbd9}" /> 
  <EventID>13</EventID> 
  <Version>2</Version> 
  <Level>4</Level> 
  <Task>13</Task> 
  <Opcode>0</Opcode> 
  <Keywords>0x8000000000000000</Keywords> 
  <TimeCreated SystemTime="2023-05-20T23:08:16.4700820Z" /> 
  <EventRecordID>1720667362</EventRecordID> 
  <Correlation /> 
  <Execution ProcessID="6488" ThreadID="8544" /> 
  <Channel>Microsoft-Windows-Sysmon/Operational</Channel> 
  <Computer>XXXXXXX</Computer> 
  <Security UserID="S-1-5-18" /> 
  </System>
- <EventData>
  <Data Name="RuleName">-</Data> 
  <Data Name="EventType">SetValue</Data> 
  <Data Name="UtcTime">2023-05-20 23:08:16.469</Data> 
  <Data Name="ProcessGuid">{9a08371b-81e0-6476-29f6-020000002800}</Data> 
  <Data Name="ProcessId">18580</Data> 
  <Data Name="Image">C:\LabStuff\odbcStuff\pwsh.exe</Data> 
  <Data Name="TargetObject">HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce\Setup\Configuring Data Access Components</Data> 
  <Data Name="Details">C:\LabStuff\odbcStuff\pwsh.exe /E /F "C:\WINDOWS\system32\odbcconf.tmp"</Data> 
  <Data Name="User">XXXXXXX</Data> 
  </EventData>
```

You can then replace the renamed/moved `odbcconf.exe` with another one for a useless persistence :)
