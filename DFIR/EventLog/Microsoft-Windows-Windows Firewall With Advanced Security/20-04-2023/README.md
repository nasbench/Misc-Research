# Microsoft-Windows-Windows Firewall With Advanced Security

Created: 20-04-2023

This document describes new updates added to the `Microsoft-Windows-Windows Firewall With Advanced Security` ETW provider

## Metadata

**GUID**: {d1bc9aff-2abf-4d71-9146-ecb2a986eb85}
**Provider**: Microsoft-Windows-Windows Firewall With Advanced Security

## Summary

New Event IDs were added to Windows11 starting from version 22H2 Build 22621.382

### New Event IDs Windows 11 Only

- `EID 2052`: A rule has been deleted in the Windows Defender Firewall exception list.
- `EID 2053`: A connection security rule was deleted from IPsec settings.
- `EID 2054`: A main mode rule has been deleted in the IPsec settings.
- `EID 2055`: A phase 1 crypto set was deleted from IPsec settings.
- `EID 2056`: A phase 2 crypto set was deleted from IPsec settings.
- `EID 2057`: All connection security rules have been deleted from the IPsec configuration on this computer.
- `EID 2058`: All main mode rules have been deleted from the IPsec configuration on this computer.
- `EID 2059`: All rules have been deleted from the Windows Defender Firewall configuration on this computer.
- `EID 2060`: Windows Defender Firewall has been reset to its default configuration.
- `EID 2061`: A connection security rule was added to IPsec settings.
- `EID 2062`: A connection security rule was modified in IPsec settings.
- `EID 2063`: A connection security rule was added to IPsec settings when Windows Defender Firewall started.
- `EID 2064`: An authentication set has been added to IPsec settings.
- `EID 2065`: An authentication set has been modified in IPsec settings.
- `EID 2066`: An authentication set has been added to IPsec settings when Windows Defender Firewall started.
- `EID 2067`: An authentication set has been deleted from IPsec settings.
- `EID 2068`: A main mode rule has been added in the IPsec settings.
- `EID 2069`: A main mode rule has been modified in the IPsec settings.
- `EID 2070`: A main mode rule was added to the IPsec settings when Windows Defender Firewall started.
- `EID 2071`: A rule has been added to the Windows Defender Firewall exception list.
- `EID 2072`: A rule has been listed when the Windows Defender Firewall started.
- `EID 2073`: A rule has been modified in the Windows Defender Firewall exception list.
- `EID 2074`: All authentication sets have been deleted from the IPsec configuration on this computer.
- `EID 2075`: All crypto sets have been deleted from the IPsec configuration on this computer.
- `EID 2076`: A phase 1 crypto set was added to IPsec settings.
- `EID 2077`: A phase 1 crypto set was modified in IPsec settings.
- `EID 2078`: A phase 1 crypto set was added to IPsec settings when Windows Defender Firewall started.
- `EID 2079`: A phase 2 crypto set was added to IPsec settings.
- `EID 2080`: A phase 2 crypto set was modified in IPsec settings.
- `EID 2081`: A phase 2 crypto set was added to IPsec settings when Windows Defender Firewall started.
- `EID 2082`: A Windows Defender Firewall setting in the {Profiles} profile has changed.
- `EID 2083`: A Windows Defender Firewall setting has changed.
- `EID 2084`: Added a Duplicate Rule
- `EID 2085`: Created Hyper-V Port.
- `EID 2086`: Updated Hyper-V Port.
- `EID 2087`: Deleted Hyper-V Port.
- `EID 2088`: A Hyper-V Firewall VM Setting has changed.
- `EID 2089`: A Hyper-V Firewall VM Setting has reset.
- `EID 2090`: A Hyper-V rule has been added.
- `EID 2091`: A Hyper-V rule has been updated.
- `EID 2092`: A Hyper-V rule has been deleted.
- `EID 2093`: A error occured while initializing a Hyper-V port.
- `EID 2094`: A error occured while processing a Hyper-V rule.
- `EID 2095`: A Hyper-V VM Creator has been registered with the firewall service.
- `EID 2096`: A Hyper-V VM Creator has been unregistered with the firewall service.

## Interesting Changes

While it seems all events are new (at least their ID). A lot of them have are describing the same behavior based on their messages as some older events. Here are a couple of example:

- Both `EID 2052` and `EID 2006` have the same event message. The new addition that `EID 2052` brings is a new field called `ErrorCode` and that's pretty much it, nothing else was added from a field perspective.

- If we take `EID 2071` and `EID 2004`. Similar to the previous example, the only field added was `ErrorCode`.

So what's the catch? Why create events that looks practically the same but with different IDs?

First of all this not uncommon of event ids at all in ETW. Events are generated for specific activities and sometimes new ones are added with small tweaks for compatibility, consistency or any other reason.

## What's the catch

In this case though and at least what to the extent of what I tested. It seems like the older events such as `2004` and `2006` no longer trigger on Windows 11 but instead we're getting their new replacements that I mentioned above.

This is important because if you're doing DFIR or building detection around this Provider/EventLog you might think there were no events (as I did at first)

```xml
- <Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
- <System>
  <Provider Name="Microsoft-Windows-Windows Firewall With Advanced Security" Guid="{d1bc9aff-2abf-4d71-9146-ecb2a986eb85}" /> 
  <EventID>2052</EventID> 
  <Version>0</Version> 
  <Level>4</Level> 
  <Task>0</Task> 
  <Opcode>0</Opcode> 
  <Keywords>0x8000020000000000</Keywords> 
  <TimeCreated SystemTime="2023-04-17T23:52:38.7709205Z" /> 
  <EventRecordID>53804</EventRecordID> 
  <Correlation /> 
  <Execution ProcessID="4080" ThreadID="21304" /> 
  <Channel>Microsoft-Windows-Windows Firewall With Advanced Security/Firewall</Channel> 
  <Computer>XXXX</Computer> 
  <Security UserID="S-1-5-19" /> 
  </System>
- <EventData>
  <Data Name="RuleId">{4E14EE69-D455-42A6-9130-B06697D46C3C}</Data> 
  <Data Name="RuleName">Chrome Sandbox</Data> 
  <Data Name="ModifyingUser">XXXX</Data> 
  <Data Name="ModifyingApplication">C:\WINDOWS\System32\svchost.exe</Data> 
  <Data Name="ErrorCode">0</Data> 
  </EventData>
  </Event>
```

```xml
- <Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
- <System>
  <Provider Name="Microsoft-Windows-Windows Firewall With Advanced Security" Guid="{d1bc9aff-2abf-4d71-9146-ecb2a986eb85}" /> 
  <EventID>2071</EventID> 
  <Version>0</Version> 
  <Level>4</Level> 
  <Task>0</Task> 
  <Opcode>0</Opcode> 
  <Keywords>0x8000020000000000</Keywords> 
  <TimeCreated SystemTime="2023-04-18T21:52:38.7735987Z" /> 
  <EventRecordID>53806</EventRecordID> 
  <Correlation /> 
  <Execution ProcessID="4080" ThreadID="21304" /> 
  <Channel>Microsoft-Windows-Windows Firewall With Advanced Security/Firewall</Channel> 
  <Computer>XXXXX</Computer> 
  <Security UserID="S-1-5-19" /> 
  </System>
- <EventData>
  <Data Name="RuleId">{B14BAFDE-5BDC-4657-924F-037D92FC8017}</Data> 
  <Data Name="RuleName">Chrome Sandbox</Data> 
  <Data Name="Origin">1</Data> 
  <Data Name="ApplicationPath" /> 
  <Data Name="ServiceName" /> 
  <Data Name="Direction">2</Data> 
  <Data Name="Protocol">256</Data> 
  <Data Name="LocalPorts" /> 
  <Data Name="RemotePorts" /> 
  <Data Name="Action">2</Data> 
  <Data Name="Profiles">XXXXXX</Data> 
  <Data Name="LocalAddresses">*</Data> 
  <Data Name="RemoteAddresses">*</Data> 
  <Data Name="RemoteMachineAuthorizationList" /> 
  <Data Name="RemoteUserAuthorizationList" /> 
  <Data Name="EmbeddedContext">Chrome Sandbox</Data> 
  <Data Name="Flags">1</Data> 
  <Data Name="Active">1</Data> 
  <Data Name="EdgeTraversal">0</Data> 
  <Data Name="LooseSourceMapped">0</Data> 
  <Data Name="SecurityOptions">0</Data> 
  <Data Name="ModifyingUser">XXXXX</Data> 
  <Data Name="ModifyingApplication">C:\WINDOWS\System32\svchost.exe</Data> 
  <Data Name="SchemaVersion">544</Data> 
  <Data Name="RuleStatus">65536</Data> 
  <Data Name="LocalOnlyMapped">0</Data> 
  <Data Name="ErrorCode">0</Data> 
  </EventData>
  </Event>
```

## References

This research was made possible thanks to the [EVTX-ETW-Resources](https://github.com/nasbench/EVTX-ETW-Resources) project.

If you want the full list of events pleas check this [CSV](https://github.com/nasbench/EVTX-ETW-Resources/blob/main/ETWEventsList/CSV/Windows11/22H2/W11_22H2_Pro_20220920_22621.382/Providers/Microsoft-Windows-Windows%20Firewall%20With%20Advanced%20Security.csv) provided via the [EVTX-ETW-Resources](https://github.com/nasbench/EVTX-ETW-Resources) project.

> **Note**
>
> Fun fact. Both EID 2093 and 2094 seem to have a typo in the their event message. Specifically the word "occured" is misspelt ^^
