# Curl

## Percent Encoded URL Execution

The curl utility can accept percent encoded URLs, which can be used to bypass certain filters.

Let's take for example the following URL:

```yaml
https://raw.githubusercontent.com/SigmaHQ/sigma/refs/heads/master/.yamllint
```

Encoded, it would look like this:

```batch
https://%72%61%77%2E%67%69%74%68%75%62%75%73%65%72%63%6F%6E%74%65%6E%74%2E%63%6f%6D/%53%69%67%6d%61%48%51/%73%69%67%6d%61/%72%65%66%73/%68%65%61%64%73/%6D%61%73%74%65%72/%2E%79%61%6D%6C%6c%69%6e%74
```

Surprisingly, curl is able to decode and fetch the resource without any issues.

A couple of caveats and tricks to keep in mind:

- Not all characters can be encoded. For example, the slash (/) characters as well as the URL scheme (https://) cannot be percent encoded in this context.

- The URL scheme (https://) can be omitted and curl will still try and fetch the resource using the default scheme (usually http). For example:

```batch
curl -L %72%61%77%2E%67%69%74%68%75%62%75%73%65%72%63%6F%6E%74%65%6E%74%2E%63%6f%6D/%53%69%67%6d%61%48%51/%73%69%67%6d%61/%72%65%66%73/%68%65%61%64%73/%6D%61%73%74%65%72/%2E%79%61%6D%6C%6c%69%6e%74 -o example.txt
```

- Mixed characters (encoded and unencoded) are also supported. In the example below we keep the TLD `.com` unencoded:

```batch
curl -L http://%72%61%77%2E%67%69%74%68%75%62%75%73%65%72%63%6F%6E%74%65%6E%74.com/%53%69%67%6d%61%48%51/%73%69%67%6d%61/%72%65%66%73/%68%65%61%64%73/%6D%61%73%74%65%72/%2E%79%61%6D%6C%6c%69%6e%74 -o example.txt
```

- Finally, be aware that some characters have special meanings in the shell (e.g., `&`, `?`, etc.). Make sure to properly escape or quote the URL to avoid unintended behavior.

From a logging perspective, here is an example of how it will look like in process monitoring logs:

```xml
- <Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
- <System>
  <Provider Name="Microsoft-Windows-Sysmon" Guid="{5770385f-c22a-43e0-bf4c-06f5698ffbd9}" />
  <EventID>1</EventID>
  <Version>5</Version>
  <Level>4</Level>
  <Task>1</Task>
  <Opcode>0</Opcode>
  <Keywords>0x8000000000000000</Keywords>
  <TimeCreated SystemTime="2026-02-02T18:22:35.3382471Z" />
  <EventRecordID>464231107</EventRecordID>
  <Correlation />
  <Execution ProcessID="3768" ThreadID="5228" />
  <Channel>Microsoft-Windows-Sysmon/Operational</Channel>
  <Computer>XXXXX</Computer>
  <Security UserID="S-1-5-18" />
  </System>
- <EventData>
  ---
  ---
  ---
  <Data Name="Description">The curl executable</Data>
  <Data Name="Product">The curl executable</Data>
  <Data Name="Company">curl, https://curl.se/</Data>
  <Data Name="OriginalFileName">curl.exe</Data>
  <Data Name="CommandLine">curl -L http://%%72%%61%%77%%2E%%67%%69%%74%%68%%75%%62%%75%%73%%65%%72%%63%%6F%%6E%%74%%65%%6E%%74.com/%%53%%69%%67%%6d%%61%%48%%51/%%73%%69%%67%%6d%%61/%%72%%65%%66%%73/%%68%%65%%61%%64%%73/%%6D%%61%%73%%74%%65%%72/%%2E%%79%%61%%6D%%6C%%6c%%69%%6e%%74 -o example.txt</Data>
  <Data Name="CurrentDirectory">C:\Users\Administrator\Desktop\testcurl\</Data>
  <Data Name="User">XXXXX</Data>
  <Data Name="LogonGuid">{5aa13a44-60b9-6977-4a5c-0f0000000000}</Data>
  <Data Name="LogonId">0xf5c4a</Data>
  <Data Name="TerminalSessionId">2</Data>
  <Data Name="IntegrityLevel">High</Data>
  ---
  ---
  ---
  <Data Name="ParentImage">C:\Windows\System32\cmd.exe</Data>
  <Data Name="ParentCommandLine">"C:\Windows\system32\cmd.exe"</Data>
  <Data Name="ParentUser">XXXXX</Data>
  </EventData>
  </Event>
```

> Note: Usage in the wild has been observed ;)
> This write-up does not describe all the possible ways this can be abused. This is left to the reader as an exercise ;)

Below is a vibe coded python script that can be used to percent encode a given URL:

```python
import re

SCHEME_RE = re.compile(r"^(https?|ftp)://", re.IGNORECASE)
PORT_RE = re.compile(r":(\d+)")

def percent_encode_except_delimiters_and_scheme(url: str) -> str:
    """
    Percent-encode a URL while:
      - preserving scheme (http://, https://, ftp://) if present
      - preserving ':' and '/' delimiters
      - preserving port numbers (e.g. :8080)
    """

    # Extract scheme if present
    scheme_match = SCHEME_RE.match(url)
    if scheme_match:
        scheme = scheme_match.group(0)
        rest = url[len(scheme):]
    else:
        scheme = ""
        rest = url

    encoded = []
    i = 0

    while i < len(rest):
        ch = rest[i]

        # Preserve delimiters
        if ch in {"/", ":"}:
            encoded.append(ch)

            # If this is a port delimiter, copy digits verbatim
            if ch == ":":
                port_match = PORT_RE.match(rest[i:])
                if port_match:
                    port = port_match.group(1)
                    encoded.append(port)
                    i += len(port)
            i += 1
            continue

        # Encode everything else
        encoded.append(f"%{ord(ch):02X}")
        i += 1

    return scheme + "".join(encoded)
```
