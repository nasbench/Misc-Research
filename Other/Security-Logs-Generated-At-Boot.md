# Security Logs Generated At Boot

The following logs are generated on a Windows machine at boot time even if no audit policy is configured

```powershell
C:\Users\Administrator>auditpol /get /category:*
```

```yaml
System audit policy
Category/Subcategory                      Setting
System
  Security System Extension               No Auditing
  System Integrity                        No Auditing
  IPsec Driver                            No Auditing
  Other System Events                     No Auditing
  Security State Change                   No Auditing
Logon/Logoff
  Logon                                   No Auditing
  Logoff                                  No Auditing
  Account Lockout                         No Auditing
  IPsec Main Mode                         No Auditing
  IPsec Quick Mode                        No Auditing
  IPsec Extended Mode                     No Auditing
  Special Logon                           No Auditing
  Other Logon/Logoff Events               No Auditing
  Network Policy Server                   No Auditing
  User / Device Claims                    No Auditing
  Group Membership                        No Auditing
Object Access
  File System                             No Auditing
  Registry                                No Auditing
  Kernel Object                           No Auditing
  SAM                                     No Auditing
  Certification Services                  No Auditing
  Application Generated                   No Auditing
  Handle Manipulation                     No Auditing
  File Share                              No Auditing
  Filtering Platform Packet Drop          No Auditing
  Filtering Platform Connection           No Auditing
  Other Object Access Events              No Auditing
  Detailed File Share                     No Auditing
  Removable Storage                       No Auditing
  Central Policy Staging                  No Auditing
Privilege Use
  Non Sensitive Privilege Use             No Auditing
  Other Privilege Use Events              No Auditing
  Sensitive Privilege Use                 No Auditing
Detailed Tracking
  Process Creation                        No Auditing
  Process Termination                     No Auditing
  DPAPI Activity                          No Auditing
  RPC Events                              No Auditing
  Plug and Play Events                    No Auditing
  Token Right Adjusted Events             No Auditing
Policy Change
  Audit Policy Change                     No Auditing
  Authentication Policy Change            No Auditing
  Authorization Policy Change             No Auditing
  MPSSVC Rule-Level Policy Change         No Auditing
  Filtering Platform Policy Change        No Auditing
  Other Policy Change Events              No Auditing
Account Management
  Computer Account Management             No Auditing
  Security Group Management               No Auditing
  Distribution Group Management           No Auditing
  Application Group Management            No Auditing
  Other Account Management Events         No Auditing
  User Account Management                 No Auditing
DS Access
  Directory Service Access                No Auditing
  Directory Service Changes               No Auditing
  Directory Service Replication           No Auditing
  Detailed Directory Service Replication  No Auditing
Account Logon
  Kerberos Service Ticket Operations      No Auditing
  Other Account Logon Events              No Auditing
  Kerberos Authentication Service         No Auditing
  Credential Validation                   No Auditing
```

## Events

### EventID 4688

```xml
<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
    <System>
        <Provider Name='Microsoft-Windows-Security-Auditing'
            Guid='{54849625-5478-4994-a5ba-3e3b0328c30d}' />
        <EventID>4688</EventID>
        <Version>2</Version>
        <Level>0</Level>
        <Task>13312</Task>
        <Opcode>0</Opcode>
        <Keywords>0x8020000000000000</Keywords>
        <TimeCreated SystemTime='2025-02-28T13:57:41.223498800Z' />
        <EventRecordID>171399</EventRecordID>
        <Correlation />
        <Execution ProcessID='4' ThreadID='104' />
        <Channel>Security</Channel>
        <Computer>ar-win-dc.attackrange.local</Computer>
        <Security />
    </System>
    <EventData>
        <Data Name='SubjectUserSid'>S-1-5-18</Data>
        <Data Name='SubjectUserName'>-</Data>
        <Data Name='SubjectDomainName'>-</Data>
        <Data Name='SubjectLogonId'>0x3e7</Data>
        <Data Name='NewProcessId'>0x270</Data>
        <Data Name='NewProcessName'>C:\Windows\System32\lsass.exe</Data>
        <Data Name='TokenElevationType'>%%1936</Data>
        <Data Name='ProcessId'>0x1cc</Data>
        <Data Name='CommandLine'></Data>
        <Data Name='TargetUserSid'>S-1-0-0</Data>
        <Data Name='TargetUserName'>-</Data>
        <Data Name='TargetDomainName'>-</Data>
        <Data Name='TargetLogonId'>0x0</Data>
        <Data Name='ParentProcessName'>C:\Windows\System32\wininit.exe</Data>
        <Data Name='MandatoryLabel'>S-1-16-16384</Data>
    </EventData>
</Event>
```

```xml
<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
    <System>
        <Provider Name='Microsoft-Windows-Security-Auditing'
            Guid='{54849625-5478-4994-a5ba-3e3b0328c30d}' />
        <EventID>4688</EventID>
        <Version>2</Version>
        <Level>0</Level>
        <Task>13312</Task>
        <Opcode>0</Opcode>
        <Keywords>0x8020000000000000</Keywords>
        <TimeCreated SystemTime='2025-02-28T13:57:41.141307000Z' />
        <EventRecordID>171398</EventRecordID>
        <Correlation />
        <Execution ProcessID='4' ThreadID='116' />
        <Channel>Security</Channel>
        <Computer>ar-win-dc.attackrange.local</Computer>
        <Security />
    </System>
    <EventData>
        <Data Name='SubjectUserSid'>S-1-5-18</Data>
        <Data Name='SubjectUserName'>-</Data>
        <Data Name='SubjectDomainName'>-</Data>
        <Data Name='SubjectLogonId'>0x3e7</Data>
        <Data Name='NewProcessId'>0x25c</Data>
        <Data Name='NewProcessName'>C:\Windows\System32\services.exe</Data>
        <Data Name='TokenElevationType'>%%1936</Data>
        <Data Name='ProcessId'>0x1cc</Data>
        <Data Name='CommandLine'></Data>
        <Data Name='TargetUserSid'>S-1-0-0</Data>
        <Data Name='TargetUserName'>-</Data>
        <Data Name='TargetDomainName'>-</Data>
        <Data Name='TargetLogonId'>0x0</Data>
        <Data Name='ParentProcessName'>C:\Windows\System32\wininit.exe</Data>
        <Data Name='MandatoryLabel'>S-1-16-16384</Data>
    </EventData>
```

```xml
</Event>
<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
    <System>
        <Provider Name='Microsoft-Windows-Security-Auditing'
            Guid='{54849625-5478-4994-a5ba-3e3b0328c30d}' />
        <EventID>4688</EventID>
        <Version>2</Version>
        <Level>0</Level>
        <Task>13312</Task>
        <Opcode>0</Opcode>
        <Keywords>0x8020000000000000</Keywords>
        <TimeCreated SystemTime='2025-02-28T13:57:40.994106800Z' />
        <EventRecordID>171397</EventRecordID>
        <Correlation />
        <Execution ProcessID='4' ThreadID='116' />
        <Channel>Security</Channel>
        <Computer>ar-win-dc.attackrange.local</Computer>
        <Security />
    </System>
    <EventData>
        <Data Name='SubjectUserSid'>S-1-5-18</Data>
        <Data Name='SubjectUserName'>-</Data>
        <Data Name='SubjectDomainName'>-</Data>
        <Data Name='SubjectLogonId'>0x3e7</Data>
        <Data Name='NewProcessId'>0x224</Data>
        <Data Name='NewProcessName'>C:\Windows\System32\winlogon.exe</Data>
        <Data Name='TokenElevationType'>%%1936</Data>
        <Data Name='ProcessId'>0x1c4</Data>
        <Data Name='CommandLine'></Data>
        <Data Name='TargetUserSid'>S-1-0-0</Data>
        <Data Name='TargetUserName'>-</Data>
        <Data Name='TargetDomainName'>-</Data>
        <Data Name='TargetLogonId'>0x0</Data>
        <Data Name='ParentProcessName'>C:\Windows\System32\smss.exe</Data>
        <Data Name='MandatoryLabel'>S-1-16-16384</Data>
    </EventData>
</Event>
```

```xml
<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
    <System>
        <Provider Name='Microsoft-Windows-Security-Auditing'
            Guid='{54849625-5478-4994-a5ba-3e3b0328c30d}' />
        <EventID>4688</EventID>
        <Version>2</Version>
        <Level>0</Level>
        <Task>13312</Task>
        <Opcode>0</Opcode>
        <Keywords>0x8020000000000000</Keywords>
        <TimeCreated SystemTime='2025-02-28T13:57:40.923863300Z' />
        <EventRecordID>171396</EventRecordID>
        <Correlation />
        <Execution ProcessID='4' ThreadID='256' />
        <Channel>Security</Channel>
        <Computer>ar-win-dc.attackrange.local</Computer>
        <Security />
    </System>
    <EventData>
        <Data Name='SubjectUserSid'>S-1-5-18</Data>
        <Data Name='SubjectUserName'>-</Data>
        <Data Name='SubjectDomainName'>-</Data>
        <Data Name='SubjectLogonId'>0x3e7</Data>
        <Data Name='NewProcessId'>0x1d4</Data>
        <Data Name='NewProcessName'>C:\Windows\System32\csrss.exe</Data>
        <Data Name='TokenElevationType'>%%1936</Data>
        <Data Name='ProcessId'>0x1c4</Data>
        <Data Name='CommandLine'></Data>
        <Data Name='TargetUserSid'>S-1-0-0</Data>
        <Data Name='TargetUserName'>-</Data>
        <Data Name='TargetDomainName'>-</Data>
        <Data Name='TargetLogonId'>0x0</Data>
        <Data Name='ParentProcessName'>C:\Windows\System32\smss.exe</Data>
        <Data Name='MandatoryLabel'>S-1-16-16384</Data>
    </EventData>
</Event>
```
```xml
<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
    <System>
        <Provider Name='Microsoft-Windows-Security-Auditing'
            Guid='{54849625-5478-4994-a5ba-3e3b0328c30d}' />
        <EventID>4688</EventID>
        <Version>2</Version>
        <Level>0</Level>
        <Task>13312</Task>
        <Opcode>0</Opcode>
        <Keywords>0x8020000000000000</Keywords>
        <TimeCreated SystemTime='2025-02-28T13:57:40.905827800Z' />
        <EventRecordID>171395</EventRecordID>
        <Correlation />
        <Execution ProcessID='4' ThreadID='256' />
        <Channel>Security</Channel>
        <Computer>ar-win-dc.attackrange.local</Computer>
        <Security />
    </System>
    <EventData>
        <Data Name='SubjectUserSid'>S-1-5-18</Data>
        <Data Name='SubjectUserName'>-</Data>
        <Data Name='SubjectDomainName'>-</Data>
        <Data Name='SubjectLogonId'>0x3e7</Data>
        <Data Name='NewProcessId'>0x1cc</Data>
        <Data Name='NewProcessName'>C:\Windows\System32\wininit.exe</Data>
        <Data Name='TokenElevationType'>%%1936</Data>
        <Data Name='ProcessId'>0x178</Data>
        <Data Name='CommandLine'></Data>
        <Data Name='TargetUserSid'>S-1-0-0</Data>
        <Data Name='TargetUserName'>-</Data>
        <Data Name='TargetDomainName'>-</Data>
        <Data Name='TargetLogonId'>0x0</Data>
        <Data Name='ParentProcessName'>C:\Windows\System32\smss.exe</Data>
        <Data Name='MandatoryLabel'>S-1-16-16384</Data>
    </EventData>
</Event>
```
```xml
<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
    <System>
        <Provider Name='Microsoft-Windows-Security-Auditing'
            Guid='{54849625-5478-4994-a5ba-3e3b0328c30d}' />
        <EventID>4688</EventID>
        <Version>2</Version>
        <Level>0</Level>
        <Task>13312</Task>
        <Opcode>0</Opcode>
        <Keywords>0x8020000000000000</Keywords>
        <TimeCreated SystemTime='2025-02-28T13:57:40.902901900Z' />
        <EventRecordID>171394</EventRecordID>
        <Correlation />
        <Execution ProcessID='4' ThreadID='256' />
        <Channel>Security</Channel>
        <Computer>ar-win-dc.attackrange.local</Computer>
        <Security />
    </System>
    <EventData>
        <Data Name='SubjectUserSid'>S-1-5-18</Data>
        <Data Name='SubjectUserName'>-</Data>
        <Data Name='SubjectDomainName'>-</Data>
        <Data Name='SubjectLogonId'>0x3e7</Data>
        <Data Name='NewProcessId'>0x1c4</Data>
        <Data Name='NewProcessName'>C:\Windows\System32\smss.exe</Data>
        <Data Name='TokenElevationType'>%%1936</Data>
        <Data Name='ProcessId'>0x118</Data>
        <Data Name='CommandLine'></Data>
        <Data Name='TargetUserSid'>S-1-0-0</Data>
        <Data Name='TargetUserName'>-</Data>
        <Data Name='TargetDomainName'>-</Data>
        <Data Name='TargetLogonId'>0x0</Data>
        <Data Name='ParentProcessName'>C:\Windows\System32\smss.exe</Data>
        <Data Name='MandatoryLabel'>S-1-16-16384</Data>
    </EventData>
</Event>
```
```xml
<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
    <System>
        <Provider Name='Microsoft-Windows-Security-Auditing'
            Guid='{54849625-5478-4994-a5ba-3e3b0328c30d}' />
        <EventID>4688</EventID>
        <Version>2</Version>
        <Level>0</Level>
        <Task>13312</Task>
        <Opcode>0</Opcode>
        <Keywords>0x8020000000000000</Keywords>
        <TimeCreated SystemTime='2025-02-28T13:57:40.710151000Z' />
        <EventRecordID>171393</EventRecordID>
        <Correlation />
        <Execution ProcessID='4' ThreadID='104' />
        <Channel>Security</Channel>
        <Computer>ar-win-dc.attackrange.local</Computer>
        <Security />
    </System>
    <EventData>
        <Data Name='SubjectUserSid'>S-1-5-18</Data>
        <Data Name='SubjectUserName'>-</Data>
        <Data Name='SubjectDomainName'>-</Data>
        <Data Name='SubjectLogonId'>0x3e7</Data>
        <Data Name='NewProcessId'>0x180</Data>
        <Data Name='NewProcessName'>C:\Windows\System32\csrss.exe</Data>
        <Data Name='TokenElevationType'>%%1936</Data>
        <Data Name='ProcessId'>0x178</Data>
        <Data Name='CommandLine'></Data>
        <Data Name='TargetUserSid'>S-1-0-0</Data>
        <Data Name='TargetUserName'>-</Data>
        <Data Name='TargetDomainName'>-</Data>
        <Data Name='TargetLogonId'>0x0</Data>
        <Data Name='ParentProcessName'>C:\Windows\System32\smss.exe</Data>
        <Data Name='MandatoryLabel'>S-1-16-16384</Data>
    </EventData>
</Event>
```
```xml
<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
    <System>
        <Provider Name='Microsoft-Windows-Security-Auditing'
            Guid='{54849625-5478-4994-a5ba-3e3b0328c30d}' />
        <EventID>4688</EventID>
        <Version>2</Version>
        <Level>0</Level>
        <Task>13312</Task>
        <Opcode>0</Opcode>
        <Keywords>0x8020000000000000</Keywords>
        <TimeCreated SystemTime='2025-02-28T13:57:40.531172600Z' />
        <EventRecordID>171392</EventRecordID>
        <Correlation />
        <Execution ProcessID='4' ThreadID='104' />
        <Channel>Security</Channel>
        <Computer>ar-win-dc.attackrange.local</Computer>
        <Security />
    </System>
    <EventData>
        <Data Name='SubjectUserSid'>S-1-5-18</Data>
        <Data Name='SubjectUserName'>-</Data>
        <Data Name='SubjectDomainName'>-</Data>
        <Data Name='SubjectLogonId'>0x3e7</Data>
        <Data Name='NewProcessId'>0x178</Data>
        <Data Name='NewProcessName'>C:\Windows\System32\smss.exe</Data>
        <Data Name='TokenElevationType'>%%1936</Data>
        <Data Name='ProcessId'>0x118</Data>
        <Data Name='CommandLine'></Data>
        <Data Name='TargetUserSid'>S-1-0-0</Data>
        <Data Name='TargetUserName'>-</Data>
        <Data Name='TargetDomainName'>-</Data>
        <Data Name='TargetLogonId'>0x0</Data>
        <Data Name='ParentProcessName'>C:\Windows\System32\smss.exe</Data>
        <Data Name='MandatoryLabel'>S-1-16-16384</Data>
    </EventData>
</Event>
```

```xml
<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
    <System>
        <Provider Name='Microsoft-Windows-Security-Auditing'
            Guid='{54849625-5478-4994-a5ba-3e3b0328c30d}' />
        <EventID>4688</EventID>
        <Version>2</Version>
        <Level>0</Level>
        <Task>13312</Task>
        <Opcode>0</Opcode>
        <Keywords>0x8020000000000000</Keywords>
        <TimeCreated SystemTime='2025-02-28T13:57:39.673608200Z' />
        <EventRecordID>171391</EventRecordID>
        <Correlation />
        <Execution ProcessID='4' ThreadID='116' />
        <Channel>Security</Channel>
        <Computer>ar-win-dc.attackrange.local</Computer>
        <Security />
    </System>
    <EventData>
        <Data Name='SubjectUserSid'>S-1-5-18</Data>
        <Data Name='SubjectUserName'>-</Data>
        <Data Name='SubjectDomainName'>-</Data>
        <Data Name='SubjectLogonId'>0x3e7</Data>
        <Data Name='NewProcessId'>0x140</Data>
        <Data Name='NewProcessName'>C:\Windows\System32\autochk.exe</Data>
        <Data Name='TokenElevationType'>%%1936</Data>
        <Data Name='ProcessId'>0x118</Data>
        <Data Name='CommandLine'></Data>
        <Data Name='TargetUserSid'>S-1-0-0</Data>
        <Data Name='TargetUserName'>-</Data>
        <Data Name='TargetDomainName'>-</Data>
        <Data Name='TargetLogonId'>0x0</Data>
        <Data Name='ParentProcessName'>C:\Windows\System32\smss.exe</Data>
        <Data Name='MandatoryLabel'>S-1-16-16384</Data>
    </EventData>
</Event>
```

```xml
<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
    <System>
        <Provider Name='Microsoft-Windows-Security-Auditing'
            Guid='{54849625-5478-4994-a5ba-3e3b0328c30d}' />
        <EventID>4688</EventID>
        <Version>2</Version>
        <Level>0</Level>
        <Task>13312</Task>
        <Opcode>0</Opcode>
        <Keywords>0x8020000000000000</Keywords>
        <TimeCreated SystemTime='2025-02-28T13:57:38.859262700Z' />
        <EventRecordID>171390</EventRecordID>
        <Correlation />
        <Execution ProcessID='4' ThreadID='32' />
        <Channel>Security</Channel>
        <Computer>ar-win-dc.attackrange.local</Computer>
        <Security />
    </System>
    <EventData>
        <Data Name='SubjectUserSid'>S-1-5-18</Data>
        <Data Name='SubjectUserName'>-</Data>
        <Data Name='SubjectDomainName'>-</Data>
        <Data Name='SubjectLogonId'>0x3e7</Data>
        <Data Name='NewProcessId'>0x118</Data>
        <Data Name='NewProcessName'>C:\Windows\System32\smss.exe</Data>
        <Data Name='TokenElevationType'>%%1936</Data>
        <Data Name='ProcessId'>0x4</Data>
        <Data Name='CommandLine'></Data>
        <Data Name='TargetUserSid'>S-1-0-0</Data>
        <Data Name='TargetUserName'>-</Data>
        <Data Name='TargetDomainName'>-</Data>
        <Data Name='TargetLogonId'>0x0</Data>
        <Data Name='ParentProcessName'></Data>
        <Data Name='MandatoryLabel'>S-1-16-16384</Data>
    </EventData>
</Event>
```

```xml
<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
    <System>
        <Provider Name='Microsoft-Windows-Security-Auditing'
            Guid='{54849625-5478-4994-a5ba-3e3b0328c30d}' />
        <EventID>4688</EventID>
        <Version>2</Version>
        <Level>0</Level>
        <Task>13312</Task>
        <Opcode>0</Opcode>
        <Keywords>0x8020000000000000</Keywords>
        <TimeCreated SystemTime='2025-02-28T13:57:38.852151300Z' />
        <EventRecordID>171387</EventRecordID>
        <Correlation />
        <Execution ProcessID='4' ThreadID='32' />
        <Channel>Security</Channel>
        <Computer>ar-win-dc.attackrange.local</Computer>
        <Security />
    </System>
    <EventData>
        <Data Name='SubjectUserSid'>S-1-5-18</Data>
        <Data Name='SubjectUserName'>-</Data>
        <Data Name='SubjectDomainName'>-</Data>
        <Data Name='SubjectLogonId'>0x3e7</Data>
        <Data Name='NewProcessId'>0x60</Data>
        <Data Name='NewProcessName'>Registry</Data>
        <Data Name='TokenElevationType'>%%1936</Data>
        <Data Name='ProcessId'>0x4</Data>
        <Data Name='CommandLine'></Data>
        <Data Name='TargetUserSid'>S-1-0-0</Data>
        <Data Name='TargetUserName'>-</Data>
        <Data Name='TargetDomainName'>-</Data>
        <Data Name='TargetLogonId'>0x0</Data>
        <Data Name='ParentProcessName'></Data>
        <Data Name='MandatoryLabel'>S-1-16-16384</Data>
    </EventData>
</Event>
```

### EventID 4696

```xml
<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
        <System>
            <Provider Name='Microsoft-Windows-Security-Auditing'
                Guid='{54849625-5478-4994-a5ba-3e3b0328c30d}' />
            <EventID>4696</EventID>
            <Version>0</Version>
            <Level>0</Level>
            <Task>13312</Task>
            <Opcode>0</Opcode>
            <Keywords>0x8020000000000000</Keywords>
            <TimeCreated SystemTime='2025-02-28T13:57:38.852157000Z' />
            <EventRecordID>171388</EventRecordID>
            <Correlation />
            <Execution ProcessID='4' ThreadID='32' />
            <Channel>Security</Channel>
            <Computer>ar-win-dc.attackrange.local</Computer>
            <Security />
        </System>
        <EventData>
            <Data Name='SubjectUserSid'>S-1-5-18</Data>
            <Data Name='SubjectUserName'>-</Data>
            <Data Name='SubjectDomainName'>-</Data>
            <Data Name='SubjectLogonId'>0x3e7</Data>
            <Data Name='TargetUserSid'>S-1-0-0</Data>
            <Data Name='TargetUserName'>-</Data>
            <Data Name='TargetDomainName'>-</Data>
            <Data Name='TargetLogonId'>0x3e7</Data>
            <Data Name='TargetProcessId'>0x60</Data>
            <Data Name='TargetProcessName'>Registry</Data>
            <Data Name='ProcessId'>0x4</Data>
            <Data Name='ProcessName'></Data>
        </EventData>
    </Event>
```

### EventID 4826

```xml
<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
    <System>
        <Provider Name='Microsoft-Windows-Security-Auditing'
            Guid='{54849625-5478-4994-a5ba-3e3b0328c30d}' />
        <EventID>4826</EventID>
        <Version>0</Version>
        <Level>0</Level>
        <Task>13573</Task>
        <Opcode>0</Opcode>
        <Keywords>0x8020000000000000</Keywords>
        <TimeCreated SystemTime='2025-02-28T13:57:38.852162300Z' />
        <EventRecordID>171389</EventRecordID>
        <Correlation />
        <Execution ProcessID='4' ThreadID='32' />
        <Channel>Security</Channel>
        <Computer>ar-win-dc.attackrange.local</Computer>
        <Security />
    </System>
    <EventData>
        <Data Name='SubjectUserSid'>S-1-5-18</Data>
        <Data Name='SubjectUserName'>-</Data>
        <Data Name='SubjectDomainName'>-</Data>
        <Data Name='SubjectLogonId'>0x3e7</Data>
        <Data Name='LoadOptions'>-</Data>
        <Data Name='AdvancedOptions'>%%1843</Data>
        <Data Name='ConfigAccessPolicy'>%%1846</Data>
        <Data Name='RemoteEventLogging'>%%1843</Data>
        <Data Name='KernelDebug'>%%1843</Data>
        <Data Name='VsmLaunchType'>%%1848</Data>
        <Data Name='TestSigning'>%%1843</Data>
        <Data Name='FlightSigning'>%%1843</Data>
        <Data Name='DisableIntegrityChecks'>%%1843</Data>
        <Data Name='HypervisorLoadOptions'>-</Data>
        <Data Name='HypervisorLaunchType'>%%1848</Data>
        <Data Name='HypervisorDebug'>%%1843</Data>
    </EventData>
</Event>
```


