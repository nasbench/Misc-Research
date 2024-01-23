# Shim Database XML Format

> **Note**
>
> The following research is still a work in progress and some of the information might be slightly or perhaps completely inaccurate in some areas.
> Please provide feedback if you find such cases :)

The following is the XML format to construct a SHIM database (.sdb) using ``shimdbc``. The format was extracted from dynamic and static analysis of the `fixApp.exe` binary, which is basically a wrapper for `shimdbc`. It contains functions that parse the XML format in order to construct the SDB file. Namely the `XXX::ReadFromXML` type functions as they contain the parsing logic that will read from our XML.

For additional information about shimdbc please give [Another Way For Finding ShimDBC](./Finding-ShimDBC.md) writeup a read.

> **Note**
>
> In addition to above, the XML schema for the SHIM database part of leaked WindowsXP source was also used as a general guideline and is linked [below](#appendix).

### QUIRKS XML Definition

A quirk needs to be part of a quirk component

```xml
<ElementType name="QUIRK_COMPONENT">
    <attribute name="CODE_ID" required="yes"/>
    <attribute name="NAME"/>
    <element type="QUIRK"/>
</ElementType>
```

```xml
<ElementType name="QUIRK">
        <attribute name="ID"/>
        <attribute name="PURPOSE" dt:type="enumeration" dt:values="GENERAL SPECIFIC"/>
        <attribute type="ENABLED_VERSION_LT"/>
        <attribute type="ENABLED" dt:type="enumeration" dt:values="YES NO"/>
        <attribute type="EDITION" required="yes" dt:type="enumeration" dt:values="<See Constants Section>"/>
        <attribute type="TELEMETRY" dt:type="enumeration" dt:values="YES NO"/>
        <attribute type="CODE_ID" required="yes"/>
        <attribute type="COMMAND_LINE"/>
        <attribute type="DESCRIPTION_RC_ID" required="yes"/>
        <attribute type="CONTACT_ALIAS" required="yes"/>
        <element type="DESCRIPTION"/>
</ElementType>
```

An example QUIRK would look something like this

```xml
<QUIRK_COMPONENT CODE_ID="0x0">
    <QUIRK NAME="CustomQuirk1" EDITION="UAP" ID="{563230E5-74AC-4D82-8686-B8897F0F4225}" ENABLED="NO" CONTACT_ALIAS="1" CODE_ID="0x0">
    </QUIRK>
    <QUIRK NAME="CustomQuirk2" EDITION="DESKTOP" ID="{263230E4-74AC-4D82-8686-B8897F0F4225}" ENABLED="YES" CODE_ID="0x1" DESCRIPTION_RC_ID="1" CONTACT_ALIAS="1">
        <DESCRIPTION>
            - This is an example QUIRK entry.
        </DESCRIPTION>
    </QUIRK>
    <QUIRK NAME="CustomQuirk3" EDITION="MOBILE" ID="{563230E4-74AC-4D82-8686-B8897F0F4225}" ENABLED_VERSION_LT="6.0" CODE_ID="0x2" DESCRIPTION_RC_ID="1" CONTACT_ALIAS="1">
</QUIRK_COMPONENT>
```

A couple of notes regarding the structure of the QUIRK

- The `CODE_ID` values for both ``<QUIRK_COMPONENT>`` and `<QUIRK>` needs to be sequential with no jumps. Or else ``shimdbc`` would complain during compilation.
- A ``QUIRK_COMPONENT`` NAME attribute must be unique
- A ``QUIRK_COMPONENT`` CODE_ID attribute must be unique
- A ``QUIRK`` tag cannot specify both ``ENABLED_VERSION_LT`` and ``ENABLED`` attributes but must specify one
- `CODE_ID` must start with `0x` and cannot exceed `0xFFFF`.

### FLAG XML Definition

TBD

### KDriver XML Definition

TBD

### KDevice XML Definition

TBD

### ReinstallUpgrade XML Definition

TBD

### Migration XML Definition

TBD

### Xap XML Definition

TBD

### Patch XML Definition

TBD

### Defined Constants

The following are constants that can be used with the different XML tags. I'll update the list with their values and their corresponding tags as I go along with this research :)

#### EDITION

```yaml
- UAP: 1
- DESKTOP: 10
- XBOX: 32
- TEAM: 64
- IOT: 128
- IOTHEADLESS: 256
- HOLOGRAPHIC: 1024
- XBOXSRA: 2048
- XBOXERA: 4096
- XBOX_ALL: 6176
- SERVER: 8704
- DESKTOP_ALL: 8778
- 8828080: 16384
- 7067329: 32768
- WINDOWSCORE: 65536
- MOBILE: 81940
- WINDOWSCOREHEADLESS: 131072
- NO_DESKTOP: 253365
```

#### SdbCompressionMode

```yaml 
- NONE: 1
- ZDB: 2
```

#### OSKindType

```yaml
- CLIENT: 1
- SERVER: 2
- ALL: 3
```

#### ModuleType

```yaml
- NONE
- UNKNOWN
- WIN16
- WIN32
- DOS
```

#### MatchModeType

```yaml
- NORMAL
- EXCLUSIVE
- ADDITIVE
```

#### UxBlocktypeOverride

```yaml
- NONE
- NO_BLOCK
- REINSTALL_BLOCK
- SOFT_BLOCK
- HARD_BLOCK
- UPGRADE_BLOCK
- MIG_FIXED
- MIG_REINSTALL
- MIG_REMOVED
- MIG_ASK_WER
- UPGRADE_CAN_REINSTALL_BLOCK
- UPGRADE_UNTIL_UPDATE_BLOCK
- REINSTALL_INFO_BLOCK
- REINSTALL_WARN_BLOCK
```

#### PackageIdArch

```yaml
- ARM: 5
- X86: 8
- AMD64: 9
- NEUTRAL: 11
- ARM64: 12
```

#### Filter

```yaml
- FIX: 4
- APPHELP: 8
- HEADER: 8
- MSI: 16
- DRIVER: 32
- QUIRK: 64
- OSUPGRADEAPPS
- OSUPGRADEDEVICES
- XAP
- CUSTOM: 4294967295 (0xFFFFFFFF)
```

#### FileEncodingType

```yaml
- ASCII: 1
- UTF8: 2
- UTF16: 3
```

#### RoutingMode

```yaml
- IAT
- EAT
```

#### ExeType

```yaml
- NORMAL
- SYSTEM
- DEPRECATED_COM
- DEPRECATED_DLL
- SHIMMED_DLL
- SHIMMED_SHELL
- SHIMMED_IME
- REDIRECTED_DLL
- COMPONENT_ON_DEMAND_BINARY
- SHIMMED_PRNDRV
```

#### MigrationDataType

```yaml
- REMOVED
- FIXED
- NEEDS_REINSTALL
- HARD_BLOCKED
- SOFT_BLOCKED
- ASK_WER
```

#### RegValueType

```yaml
- REG_SZ
- REG_MULTI_SZ
- REG_EXPAND_SZ
- REG_DWORD
- REG_QWORD
- REG_BINARY
```

#### StringDataType

```yml
- DWORD
- QWORD
- STRING
- BINARY
- NONE
```

### Appendix

- The following is the SHIM XML schema from the WindowsXP. The schema is missing some of the modern features of appcompat such as QUIRKS and KSHIM as they were not introduced at the time. But the rest is still valid to be used as a reference.

<details>
    <summary>Expand Details</summary>

```xml
<?xml version="1.0"?>
<Schema name="DATABASE" xmlns="urn:schemas-microsoft-com:xml-data" xmlns:dt="urn:schemas-microsoft-com:datatypes">

    <ElementType name="DATABASE" content="eltOnly" model="closed">
        <AttributeType name="NAME"/>
        <AttributeType name="ID"/>
        <AttributeType name="LANGID"/>
        <AttributeType name="MAX_HTMLHELPID"/>
        <attribute type="NAME"/>
        <attribute type="ID"/>
        <attribute type="LANGID" required="no"/>
        <attribute type="MAX_HTMLHELPID" required="no"/>
        <element type="LIBRARY" maxOccurs="*" minOccurs="0"/>
        <element type="LAYER" maxOccurs="*" minOccurs="0"/>
        <element type="APP" maxOccurs="*" minOccurs="0"/>
        <element type="HTMLHELP_TEMPLATE" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="LIBRARY" content="eltOnly" model="closed" order="many">
        <element type="INCLUDE" maxOccurs="*" minOccurs="0"/>
        <element type="SHIM" maxOccurs="*" minOccurs="0"/>
        <element type="PATCH" maxOccurs="*" minOccurs="0"/>
        <element type="FILE" maxOccurs="*" minOccurs="0"/>
        <element type="LAYER" maxOccurs="*" minOccurs="0"/>
        <element type="FLAG" maxOccurs="*" minOccurs="0"/>
        <element type="MESSAGE" maxOccurs="*" minOccurs="0"/>
        <element type="TEMPLATE" maxOccurs="*" minOccurs="0"/>
        <element type="CONTACT_INFO" maxOccurs="*" minOccurs="0"/>
        <element type="MSI_TRANSFORM" maxOccurs="*" minOccurs="0"/>
        <element type="LOCALIZED_APP_NAME" maxOccurs="*" minOccurs="0"/>
        <element type="LOCALIZED_VENDOR_NAME" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="APP" content="eltOnly" model="closed" order="many">
        <AttributeType name="VENDOR"/>
        <AttributeType name="NAME"/>
        <AttributeType name="ID"/>
        <attribute type="NAME" required="yes"/>
        <attribute type="VENDOR" required="yes"/>
        <attribute type="ID"/>
        <element type="PTOLEMY" maxOccurs="*" minOccurs="0"/>
        <element type="KEYWORD" maxOccurs="*" minOccurs="0"/>
        <element type="HISTORY" maxOccurs="*" minOccurs="0"/>
        <element type="EXE_LINK" maxOccurs="*" minOccurs="0"/>
        <element type="BUG" maxOccurs="*" minOccurs="0"/>
        <element type="EXE" maxOccurs="*" minOccurs="0"/>
        <element type="MSI_PACKAGE" maxOccurs="*" minOccurs="0"/>
        <element type="WIN9X_MIGRATION" maxOccurs="*" minOccurs="0"/>
        <element type="WINNT_UPGRADE" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="EXE" content="eltOnly" model="closed" order="many">
        <AttributeType name="NAME"/>
        <AttributeType name="MODULE_NAME"/>
        <AttributeType name="SIZE"/>
        <AttributeType name="CHECKSUM"/>
        <AttributeType name="COMPANY_NAME"/>
        <AttributeType name="PRODUCT_NAME"/>
        <AttributeType name="PRODUCT_VERSION"/>
        <AttributeType name="FILE_DESCRIPTION"/>
        <AttributeType name="BIN_FILE_VERSION"/>
        <AttributeType name="BIN_PRODUCT_VERSION"/>
        <AttributeType name="MODULE_TYPE"/>
        <AttributeType name="VERFILEDATELO"/>
        <AttributeType name="VERFILEDATEHI"/>
        <AttributeType name="VERFILEOS"/>
        <AttributeType name="VERFILETYPE"/>
        <AttributeType name="PE_CHECKSUM"/>
        <AttributeType name="LINKER_VERSION"/>
        <AttributeType name="FILE_VERSION"/>
        <AttributeType name="ORIGINAL_FILENAME"/>
        <AttributeType name="INTERNAL_NAME"/>
        <AttributeType name="LEGAL_COPYRIGHT"/>
        <AttributeType name="S16BIT_DESCRIPTION"/>
        <AttributeType name="UPTO_BIN_PRODUCT_VERSION"/>
        <AttributeType name="UPTO_BIN_FILE_VERSION"/>
        <AttributeType name="LINK_DATE"/>
        <AttributeType name="UPTO_LINK_DATE"/>
        <AttributeType name="VER_LANGUAGE"/>
        <AttributeType name="PREVOSMAJORVERSION"/>
        <AttributeType name="PREVOSMINORVERSION"/>
        <AttributeType name="PREVOSPLATFORMID"/>
        <AttributeType name="PREVOSBUILDNO"/>
        <AttributeType name="ID"/>
        <AttributeType name="ENGINE" dt:type="enumeration" dt:values="VEH IAT"/>
        <AttributeType name="OS_VERSION"/>
        <AttributeType name="OS_SKU"/>
        <AttributeType name="MATCH_MODE" dt:type="enumeration" dt:values="NORMAL EXCLUSIVE ADDITIVE"/>
        <AttributeType name="RUNTIME_PLATFORM"/>
        <AttributeType name="OS_PLATFORM"/>
        <attribute type="NAME"/>
        <attribute type="MODULE_NAME"/>
        <attribute type="SIZE"/>
        <attribute type="CHECKSUM"/>
        <attribute type="COMPANY_NAME"/>
        <attribute type="PRODUCT_NAME"/>
        <attribute type="PRODUCT_VERSION"/>
        <attribute type="FILE_DESCRIPTION"/>
        <attribute type="BIN_FILE_VERSION"/>
        <attribute type="BIN_PRODUCT_VERSION"/>
        <attribute type="MODULE_TYPE"/>
        <attribute type="VERFILEDATELO"/>
        <attribute type="VERFILEDATEHI"/>
        <attribute type="VERFILEOS"/>
        <attribute type="VERFILETYPE"/>
        <attribute type="PE_CHECKSUM"/>
        <attribute type="LINKER_VERSION"/>
        <attribute type="FILE_VERSION"/>
        <attribute type="ORIGINAL_FILENAME"/>
        <attribute type="INTERNAL_NAME"/>
        <attribute type="LEGAL_COPYRIGHT"/>
        <attribute type="S16BIT_DESCRIPTION"/>
        <attribute type="UPTO_BIN_PRODUCT_VERSION"/>
        <attribute type="UPTO_BIN_FILE_VERSION"/>
        <attribute type="LINK_DATE"/>
        <attribute type="UPTO_LINK_DATE"/>
        <attribute type="VER_LANGUAGE"/>
        <attribute type="PREVOSMAJORVERSION"/>
        <attribute type="PREVOSMINORVERSION"/>
        <attribute type="PREVOSPLATFORMID"/>
        <attribute type="PREVOSBUILDNO"/>
        <attribute type="ID"/>
        <attribute type="ENGINE"/>
        <attribute type="OS_VERSION"/>
        <attribute type="OS_SKU"/>
        <attribute type="MATCH_MODE"/>
        <attribute type="RUNTIME_PLATFORM"/>
        <attribute type="OS_PLATFORM"/>
        <element type="MATCHING_FILE" maxOccurs="*" minOccurs="0"/>
        <element type="SHIM" maxOccurs="*" minOccurs="0"/>
        <element type="PATCH" maxOccurs="*" minOccurs="0"/>
        <element type="LAYER" maxOccurs="*" minOccurs="0"/>
        <element type="FLAG" maxOccurs="*" minOccurs="0"/>
        <element type="APPHELP" maxOccurs="*" minOccurs="0"/>
        <element type="SXS" maxOccurs="*" minOccurs="0"/>
        <element type="DRIVER_POLICY" maxOccurs="*" minOccurs="0"/>
        <element type="DATA" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="CUSTOM_ACTION" content="eltOnly" model="closed" order="many">
        <AttributeType name="NAME"/>
        <attribute type="NAME"/>
        <element type="SHIM" maxOccurs="*" minOccurs="0"/>
        <element type="LAYER" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="MATCHING_FILE" content="textOnly" model="closed">
        <AttributeType name="NAME"/>
        <AttributeType name="SIZE"/>
        <AttributeType name="CHECKSUM"/>
        <AttributeType name="COMPANY_NAME"/>
        <AttributeType name="PRODUCT_NAME"/>
        <AttributeType name="PRODUCT_VERSION"/>
        <AttributeType name="FILE_DESCRIPTION"/>
        <AttributeType name="BIN_FILE_VERSION"/>
        <AttributeType name="BIN_PRODUCT_VERSION"/>
        <AttributeType name="MODULE_TYPE"/>
        <AttributeType name="VERFILEDATELO"/>
        <AttributeType name="VERFILEDATEHI"/>
        <AttributeType name="VERFILEOS"/>
        <AttributeType name="VERFILETYPE"/>
        <AttributeType name="PE_CHECKSUM"/>
        <AttributeType name="LINKER_VERSION"/>
        <AttributeType name="FILE_VERSION"/>
        <AttributeType name="ORIGINAL_FILENAME"/>
        <AttributeType name="INTERNAL_NAME"/>
        <AttributeType name="LEGAL_COPYRIGHT"/>
        <AttributeType name="S16BIT_DESCRIPTION"/>
        <AttributeType name="UPTO_BIN_PRODUCT_VERSION"/>
        <AttributeType name="UPTO_BIN_FILE_VERSION"/>
        <AttributeType name="LINK_DATE"/>
        <AttributeType name="UPTO_LINK_DATE"/>
        <AttributeType name="VER_LANGUAGE"/>
        <AttributeType name="PREVOSMAJORVERSION"/>
        <AttributeType name="PREVOSMINORVERSION"/>
        <AttributeType name="PREVOSPLATFORMID"/>
        <AttributeType name="PREVOSBUILDNO"/>
        <AttributeType name="SERVICE_NAME"/>
        <AttributeType name="REGISTRY_ENTRY"/>
        <AttributeType name="LOGIC" dt:type="enumeration" dt:values="NOT"/>
        <attribute type="NAME" required="yes"/>
        <attribute type="SIZE"/>
        <attribute type="CHECKSUM"/>
        <attribute type="COMPANY_NAME"/>
        <attribute type="PRODUCT_NAME"/>
        <attribute type="PRODUCT_VERSION"/>
        <attribute type="FILE_DESCRIPTION"/>
        <attribute type="BIN_FILE_VERSION"/>
        <attribute type="BIN_PRODUCT_VERSION"/>
        <attribute type="MODULE_TYPE"/>
        <attribute type="VERFILEDATELO"/>
        <attribute type="VERFILEDATEHI"/>
        <attribute type="VERFILEOS"/>
        <attribute type="VERFILETYPE"/>
        <attribute type="PE_CHECKSUM"/>
        <attribute type="LINKER_VERSION"/>
        <attribute type="FILE_VERSION"/>
        <attribute type="ORIGINAL_FILENAME"/>
        <attribute type="INTERNAL_NAME"/>
        <attribute type="LEGAL_COPYRIGHT"/>
        <attribute type="S16BIT_DESCRIPTION"/>
        <attribute type="UPTO_BIN_PRODUCT_VERSION"/>
        <attribute type="UPTO_BIN_FILE_VERSION"/>
        <attribute type="LINK_DATE"/>
        <attribute type="UPTO_LINK_DATE"/>
        <attribute type="VER_LANGUAGE"/>
        <attribute type="PREVOSMAJORVERSION"/>
        <attribute type="PREVOSMINORVERSION"/>
        <attribute type="PREVOSPLATFORMID"/>
        <attribute type="PREVOSBUILDNO"/>
        <attribute type="SERVICE_NAME"/>
        <attribute type="REGISTRY_ENTRY"/>
        <attribute type="LOGIC"/>
    </ElementType>

    <ElementType name="WIN9X_MIGRATION" model="closed">
        <AttributeType name="SECTION"
            dt:type="enumeration" dt:values="COMPATIBLEFILES COMPATIBLESHELLMODULES COMPATIBLERUNKEYMODULES COMPATIBLEDOSMODULES COMPATIBLEHLPFILES IGNORE BADDVDFILE MINORPROBLEMS MINORPROBLEMS_NOLINKREQUIRED REINSTALL REINSTALL_NOLINKREQUIRED REINSTALL_SOFTBLOCK REINSTALL_AUTOUNINSTALL INCOMPATIBLE INCOMPATIBLE_NOLINKREQUIRED INCOMPATIBLE_PREINSTALLEDUTILITIES INCOMPATIBLE_SIMILAROSFUNCTIONALITY INCOMPATIBLE_HARDWAREUTILITY BLOCKINGFILES NONE"/>
        <AttributeType name="MESSAGE"/>
        <AttributeType name="SHOW_IN_SIMPLIFIED_VIEW" dt:type="enumeration" dt:values="YES NO"/>
        <AttributeType name="ID"/>
        <attribute type="SECTION"/>
        <attribute type="MESSAGE"/>
        <attribute type="SHOW_IN_SIMPLIFIED_VIEW"/>
        <attribute type="ID"/>
        <element type="MATCHING_FILE" maxOccurs="*" minOccurs="0"/>
        <element type="MATCH_ANY" maxOccurs="*" minOccurs="0"/>
        <element type="MATCH_ALL" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="MATCH_ANY" model="closed">
        <element type="MATCHING_FILE" maxOccurs="*" minOccurs="0"/>
        <element type="MATCH_ANY" maxOccurs="*" minOccurs="0"/>
        <element type="MATCH_ALL" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="MATCH_ALL" model="closed">
        <element type="MATCHING_FILE" maxOccurs="*" minOccurs="0"/>
        <element type="MATCH_ANY" maxOccurs="*" minOccurs="0"/>
        <element type="MATCH_ALL" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="MATCHING_REGISTRY_ENTRY" model="closed">
        <AttributeType name="KEY"/>
        <AttributeType name="VALUE_NAME"/>
        <AttributeType name="VALUE"/>
        <attribute type="KEY" required="yes"/>
        <attribute type="VALUE_NAME"/>
        <attribute type="VALUE"/>
    </ElementType>

    <ElementType name="WINNT_UPGRADE" model="closed">
        <AttributeType name="ID"/>
        <attribute type="ID"/>
        <element type="MATCHING_FILE" maxOccurs="1" minOccurs="0"/>
        <element type="MATCHING_REGISTRY_ENTRY" maxOccurs="1" minOccurs="0"/>
        <element type="APPHELP" maxOccurs="1" minOccurs="0"/>
    </ElementType>

    <ElementType name="MSI_PACKAGE" model="closed">
        <AttributeType name="NAME"/>
        <AttributeType name="ID"/>
        <AttributeType name="OS_SKU"/>
        <AttributeType name="PRODUCT_CODE"/>
        <AttributeType name="RUNTIME_PLATFORM"/>
        <attribute type="NAME"/>
        <attribute type="ID"/>
        <attribute type="OS_SKU"/>
        <attribute type="PRODUCT_CODE" required="yes"/>
        <attribute type="RUNTIME_PLATFORM"/>
        <element type="DATA" maxOccurs="*" minOccurs="0"/>
        <element type="MSI_TRANSFORM" maxOccurs="*" minOccurs="0"/>
        <element type="APPHELP" maxOccurs="*" minOccurs="0"/>
        <element type="CUSTOM_ACTION" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="EXE_LINK" content="textOnly" model="closed">
        <AttributeType name="ID"/>
        <attribute type="ID" required="yes"/>
    </ElementType>

    <ElementType name="LAYER" content="eltOnly" model="closed">
        <AttributeType name="NAME"/>
        <attribute type="NAME" required="yes"/>
        <AttributeType name="ID"/>
        <attribute type="ID"/>
        <element type="SHIM" maxOccurs="*" minOccurs="0"/>
        <element type="FLAG" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="API" content="textOnly" model="closed">
        <AttributeType name="NAME"/>
        <AttributeType name="MODULE"/>
        <attribute type="NAME" required="yes"/>
        <attribute type="MODULE" required="yes"/>
    </ElementType>

    <ElementType name="SHIM" content="eltOnly" model="closed" order="many">
        <AttributeType name="FILE"/>
        <AttributeType name="PURPOSE" dt:type="enumeration" dt:values="GENERAL SPECIFIC"/>
        <AttributeType name="NAME"/>
        <AttributeType name="COMMAND_LINE"/>
        <AttributeType name="APPLY_ALL_SHIMS"/>
        <AttributeType name="ID"/>
        <AttributeType name="OS_PLATFORM"/>
        <attribute type="NAME" required="yes"/>
        <attribute type="FILE"/>
        <attribute type="PURPOSE"/>
        <attribute type="COMMAND_LINE"/>
        <attribute type="APPLY_ALL_SHIMS"/>
        <attribute type="ID" />
        <attribute type="OS_PLATFORM"/>
        <element type="DESCRIPTION" maxOccurs="*" minOccurs="0"/>
        <element type="EXCLUDE" maxOccurs="*" minOccurs="0"/>
        <element type="INCLUDE" maxOccurs="*" minOccurs="0"/>
        <element type="API" maxOccurs="*" minOccurs="0"/>
        <element type="DATA" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="MSI_TRANSFORM" content="eltOnly" model="closed" order="many">
        <AttributeType name="NAME"/>
        <attribute type="NAME" required="yes"/>
        <element type="DESCRIPTION" maxOccurs="*" minOccurs="0"/>
        <element type="FILE" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="FLAG" content="eltOnly" model="closed">
        <AttributeType name="NAME"/>
        <attribute type="NAME" required="yes"/>
        <AttributeType name="MASK"/>
        <attribute type="MASK"/>
        <AttributeType name="TYPE"/>
        <attribute type="TYPE"/>
        <AttributeType name="PURPOSE" dt:type="enumeration" dt:values="GENERAL SPECIFIC"/>
        <attribute type="PURPOSE"/>
        <AttributeType name="COMMAND_LINE"/>
        <attribute type="COMMAND_LINE"/>
        <AttributeType name="ID"/>
        <attribute type="ID" />
        <AttributeType name="OS_PLATFORM"/>
        <attribute type="OS_PLATFORM"/>
        <element type="DESCRIPTION" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="SXS" model="open">
        <element type="assembly" maxOccurs="*" minOccurs="0"/>
    </ElementType>

<!-- Driver policy and data are one and the same, there is no difference -->

    <ElementType name="DRIVER_POLICY" model="closed" order="many">
        <AttributeType name="NAME"/>
        <AttributeType name="VALUETYPE" dt:type="enumeration" dt:values="DWORD STRING BINARY QWORD"/>
        <AttributeType name="VALUE"/>
        <attribute type="NAME" required="yes"/>
        <attribute type="VALUETYPE"/>
        <attribute type="VALUE"/>
    </ElementType>

    <ElementType name="DATA" model="closed" order="many">
        <AttributeType name="NAME"/>
        <AttributeType name="VALUETYPE" dt:type="enumeration" dt:values="DWORD STRING BINARY QWORD NONE"/>
        <AttributeType name="VALUE"/>
        <attribute type="NAME" required="yes"/>
        <attribute type="VALUETYPE"/>
        <attribute type="VALUE"/>
        <element type="DATA" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="PATCH" content="eltOnly" model="closed" order="many">
        <AttributeType name="NAME"/>
        <AttributeType name="ID"/>
        <AttributeType name="OS_PLATFORM"/>
        <attribute type="NAME" required="yes"/>
        <attribute type="ID" />
        <attribute type="OS_PLATFORM" required="no"/>
        <element type="DESCRIPTION" maxOccurs="*" minOccurs="0"/>
        <element type="MATCH_BYTES" maxOccurs="*" minOccurs="0"/>
        <element type="WRITE_BYTES" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="FILE">
        <AttributeType name="NAME"/>
        <attribute type="NAME" required="yes"/>
        <AttributeType name="FILTER"/>
        <attribute type="FILTER"/>
    </ElementType>

    <ElementType name="WRITE_BYTES" content="textOnly" model="closed">
        <AttributeType name="OFFSET"/>
        <AttributeType name="MODULE"/>
        <attribute type="OFFSET" required="yes"/>
        <attribute type="MODULE" required="yes"/>
    </ElementType>

    <ElementType name="MATCH_BYTES" content="textOnly" model="closed">
        <AttributeType name="OFFSET"/>
        <AttributeType name="MODULE"/>
        <attribute type="MODULE" required="yes"/>
        <attribute type="OFFSET" required="yes"/>
    </ElementType>

    <ElementType name="INCLUDE" content="textOnly" model="closed">
        <AttributeType name="MODULE"/>
        <attribute type="MODULE" required="yes"/>
    </ElementType>

    <ElementType name="EXCLUDE" content="textOnly" model="closed">
        <AttributeType name="MODULE"/>
        <attribute type="MODULE" required="yes"/>
    </ElementType>

    <ElementType name="PTOLEMY" content="textOnly" model="closed">
        <AttributeType name="ID" dt:type="int"/>
        <attribute type="ID" required="yes"/>
    </ElementType>

    <ElementType name="KEYWORD" content="textOnly" model="closed">
        <AttributeType name="NAME"/>
        <AttributeType name="DATE"/>
        <attribute type="NAME" required="yes"/>
        <attribute type="DATE" required="yes"/>
    </ElementType>

    <ElementType name="HISTORY" content="eltOnly" model="closed">
        <AttributeType name="KEYWORDS"/>
        <AttributeType name="DATE"/>
        <AttributeType name="ALIAS"/>
        <AttributeType name="TEAM"/>
        <attribute type="ALIAS" required="yes"/>
        <attribute type="TEAM" required="no"/>
        <attribute type="DATE" required="yes"/>
        <attribute type="KEYWORDS"/>
        <element type="DESCRIPTION" maxOccurs="*" minOccurs="1"/>
        <element type="BUG" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="BUG" content="textOnly" model="closed">
        <AttributeType name="RESOLUTION" dt:type="enumeration" dt:values="APPHELP PROFILES"/>
        <AttributeType name="NUMBER" dt:type="int"/>
        <AttributeType name="DATABASE" dt:type="enumeration" dt:values="WIN2K WHISTLER WINSE"/>
        <attribute type="NUMBER" required="yes"/>
        <attribute type="DATABASE" required="yes"/>
        <attribute type="RESOLUTION"/>
    </ElementType>

    <ElementType name="DESCRIPTION" content="textOnly" model="closed"/>

    <ElementType name="APPHELP" model="closed">
        <AttributeType name="BLOCK" dt:type="enumeration" dt:values="YES NO"/>
        <AttributeType name="BLOCK_UPGRADE" dt:type="enumeration" dt:values="YES NO"/>
        <AttributeType name="HTMLHELPID"/>
        <AttributeType name="MESSAGE"/>
        <AttributeType name="DETAILS_URL"/>
        <attribute type="BLOCK"/>
        <attribute type="BLOCK_UPGRADE"/>
        <attribute type="HTMLHELPID"/>
        <attribute type="MESSAGE"/>
        <attribute type="DETAILS_URL"/>
    </ElementType>

    <ElementType name="MESSAGE" model="closed">
        <AttributeType name="NAME"/>
        <AttributeType name="TEMPLATE"/>
        <AttributeType name="ID"/>
        <attribute type="NAME"/>
        <attribute type="TEMPLATE"/>
        <attribute type="ID"/>
        <element type="FIELD" maxOccurs="*" minOccurs="0"/>
        <element type="CONTACT_INFO" maxOccurs="*" minOccurs="0"/>
        <element type="SUMMARY" maxOccurs="*" minOccurs="0"/>
        <element type="DETAILS" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="LOCALIZED_APP_NAME">
        <AttributeType name="NAME"/>
        <attribute type="NAME"/>
        <AttributeType name="LANGID"/>
        <attribute type="LANGID"/>
        <AttributeType name="ID"/>
        <attribute type="ID"/>
    </ElementType>

    <ElementType name="LOCALIZED_VENDOR_NAME">
        <AttributeType name="NAME"/>
        <attribute type="NAME"/>
        <AttributeType name="LANGID"/>
        <attribute type="LANGID"/>
        <AttributeType name="ID"/>
        <attribute type="ID"/>
    </ElementType>

    <ElementType name="CONTACT_INFO">
        <AttributeType name="VENDOR"/>
        <AttributeType name="ID"/>
        <attribute type="VENDOR"/>
        <attribute type="ID"/>
    </ElementType>

    <ElementType name="TEMPLATE">
        <AttributeType name="NAME"/>
        <attribute type="NAME" required="yes"/>
        <element type="SUMMARY" maxOccurs="*" minOccurs="0"/>
        <element type="DETAILS" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="SUMMARY" model="open">
        <element type="FIELD" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="DETAILS" model="open">
        <element type="FIELD" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="FIELD" model="open">
        <AttributeType name="NAME"/>
        <attribute type="NAME" required="yes"/>
    </ElementType>

    <ElementType name="HTMLHELP_TEMPLATE" model="open" order="many"/>

    <ElementType name="HTMLHELP_FIRST_SCREEN" model="open" order="many"/>

    <ElementType name="assembly" model="open">
        <AttributeType name="manifestVersion"/>
        <attribute type="manifestVersion"/>
        <element type="assemblyIdentity" maxOccurs="*" minOccurs="0"/>
        <element type="description" maxOccurs="*" minOccurs="0"/>
        <element type="file" maxOccurs="*" minOccurs="0"/>
    </ElementType>

    <ElementType name="assemblyIdentity" model="open">
        <AttributeType name="type"/>
        <AttributeType name="name"/>
        <AttributeType name="version"/>
        <AttributeType name="processorArchitecture"/>
        <attribute type="type"/>
        <attribute type="name"/>
        <attribute type="version"/>
        <attribute type="processorArchitecture"/>
    </ElementType>

    <ElementType name="file" model="open">
        <AttributeType name="name"/>
        <AttributeType name="loadfrom"/>
        <attribute type="name"/>
        <attribute type="loadfrom"/>
    </ElementType>

    <ElementType name="description" content="textOnly" model="open"/>

</Schema>

```
</details>
