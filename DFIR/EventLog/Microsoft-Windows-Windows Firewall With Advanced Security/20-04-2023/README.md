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

## References

If you want the full list of events pleas check this [CSV](https://github.com/nasbench/EVTX-ETW-Resources/blob/main/ETWEventsList/CSV/Windows11/22H2/W11_22H2_Pro_20220920_22621.382/Providers/Microsoft-Windows-Windows%20Firewall%20With%20Advanced%20Security.csv) provided via the [EVTX-ETW-Resources](https://github.com/nasbench/EVTX-ETW-Resources) project.

> **Note**
>
> Fun fact. Both EID 2093 and 2094 seem to have a typo in the their event message. Specifically the word "occured" is misspelt ^^
