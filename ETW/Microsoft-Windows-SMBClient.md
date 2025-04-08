
# Microsoft-Windows-SMBClient

The following tries to document the meaning behind some events and fields provided by this provider.

## Address Fields

The `Address`, `RemoteAddress`, or `LocalAddress` fields found in Event IDs such as **30804**, **30803**, **30806**, **30833**, etc., use a built-in structure to represent IP socket addresses. When leveraging or analyzing these events (especially for detection engineering), it's useful to understand how these fields are encoded. This format embeds the **address family**, **port number**, and **IP address**, with some padding / reserved fields.

#### `SOCKADDR_IN` (IPv4)
```c
typedef struct sockaddr_in {
#if ...
  short          sin_family;
#else
  ADDRESS_FAMILY sin_family;
#endif
  USHORT         sin_port;
  IN_ADDR        sin_addr;
  CHAR           sin_zero[8];
} SOCKADDR_IN, *PSOCKADDR_IN;
```

#### `SOCKADDR_IN6_LH` (IPv6)
```c
typedef struct sockaddr_in6 {
  ADDRESS_FAMILY sin6_family;
  USHORT         sin6_port;
  ULONG          sin6_flowinfo;
  IN6_ADDR       sin6_addr;
  union {
    ULONG    sin6_scope_id;
    SCOPE_ID sin6_scope_struct;
  };
} SOCKADDR_IN6_LH, *PSOCKADDR_IN6_LH, *LPSOCKADDR_IN6_LH;
```

#### For IPv4 (AF_INET) - [SOCKADDR_IN](https://learn.microsoft.com/en-us/windows/win32/api/ws2def/ns-ws2def-sockaddr_in) :

| Bytes (offset) | Length | Description               |
|----------------|--------|---------------------------|
| `00–01`        | 2      | Address family (usually `02 00` for IPv4) |
| `02–03`        | 2      | Port (little endian)      |
| `04–07`        | 4      | IPv4 address (big endian) |
| `08–15`        | 8      | Padding / Reserved        |

#### For IPv6 (AF_INET6) - [SOCKADDR_IN6_LH](https://learn.microsoft.com/en-us/windows/win32/api/ws2ipdef/ns-ws2ipdef-sockaddr_in6_lh) :

| Bytes (offset) | Length | Description               |
|----------------|--------|---------------------------|
| `00–01`        | 2      | Address family (`17 00` for IPv6) |
| `02–03`        | 2      | Port (little endian)      |
| `04–07`        | 4      | Flow info or padding      |
| `08–23`        | 16     | IPv6 address (big endian) |
| `24–27`        | 16     | Scope ID                  |

---

### Examples 

#### IPv4 Example

**Field (hex):**
```
02 00 BD 01 0A 00 00 01 00 00 00 00 00 00 00 00
```

**Decoded:**
- Address family: `02 00` → IPv4
- Port: `BD 01` → `0x01BD` = **445**
- IP Address: `0A 00 00 01` → **10.0.0.1**
- Padding: 8 null bytes

Results: `10.2.0.50:445`

#### IPv6 Loopback

**Field (hex):**
```
17 00 BD 01 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00
```

**Decoded:**
- Address family: `17 00` → IPv6
- Port: `BD 01` → **445**
- IPv6: `0000:0000:0000:0000:0000:0000:0000:0001` → **[::1]**

Results: `[::1]:445`

#### IPv6 Link-Local

**Field (hex):**
```
17 00 BD 01 00 00 00 00 FE 80 00 00 00 00 00 00 76 E4 CE 6A 17 77 4C AA 0B 00 00 00
```
 fe80::210:5aff:feaa:20a2
**Decoded:**
- Address family: `17 00` → IPv6
- Port: `BD 01` → **445**
- IPv6: `fe80::76e4:ce6a:1777:4caa`

Results : `[fe80::76e4:ce6a:1777:4caa]:445`

#### Common IPv4 Address Ranges in Hex

| IP Prefix     | Example Address | Encoded (hex bytes 4–7) |
|---------------|------------------|--------------------------|
| `10.`         | `10.0.0.1`       | `0A 00 00 01`            |
| `127.`        | `127.0.0.1`      | `7F 00 00 01`            |
| `169.254.`    | `169.254.0.1`    | `A9 FE 00 01`            |
| `172.`        | `172.16.0.1`     | `AC 10 00 01`            |
| `192.168.`    | `192.168.1.1`    | `C0 A8 01 01`            |
