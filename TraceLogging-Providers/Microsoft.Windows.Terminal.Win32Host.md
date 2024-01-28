# Microsoft.Windows.Terminal.Win32Host

Created: 21/01/2024

ProviderGUID: 56c06166-2e2e-5f4d-7ff3-74f4b78c87d6
ProviderName: Microsoft.Windows.Terminal.Win32Host
ProviderGroupGUID: 4f50731a-89cf-4782-b3e0-dce8c90476ba

Definition:
    - https://github.com/microsoft/terminal/blob/92f9ff948b7531d9446ba3c72f805576589a0217/src/cascadia/WindowsTerminal/WindowEmperor.cpp
    - https://github.com/microsoft/terminal/blob/92f9ff948b7531d9446ba3c72f805576589a0217/src/cascadia/WindowsTerminal/IslandWindow.cpp

### Events

#### EndSession

- Description: `Emitted when the OS has sent a WM_ENDSESSION`
- Level: `WINEVENT_LEVEL_VERBOSE`
- Keyword: `TIL_KEYWORD_TRACE` # 0x0000000100000000

#### AppHost_SaveWindowLayouts_Collect

- Description: `Logged when collecting window state`
- Level: `WINEVENT_LEVEL_VERBOSE`
- Keyword: `TIL_KEYWORD_TRACE` # 0x0000000100000000


#### AppHost_SaveWindowLayouts_Save

- Description: `Logged when writing window state`
- Level: `WINEVENT_LEVEL_VERBOSE`
- Keyword: `TIL_KEYWORD_TRACE` # 0x0000000100000000


#### AppHost_SaveWindowLayouts_Failed

- Description: `An error occurred when collecting or writing window state`
- Level: `WINEVENT_LEVEL_VERBOSE`
- Keyword: `TIL_KEYWORD_TRACE` # 0x0000000100000000

#### AppHost_requestGetLayout

- Description: `Logged when triggering a throttled write of the window state`
- Level: `WINEVENT_LEVEL_VERBOSE`
- Keyword: `TIL_KEYWORD_TRACE` # 0x0000000100000000

#### RegisterHotKey
                
- Description: `Emitted when setting hotkeys`
- Fields:
    - `index`: `the index of the hotkey to add`
    - `vkey`: `the key`
    - `win`: `is WIN in the modifiers`
    - `alt`: `is ALT in the modifiers`
    - `control`: `is CONTROL in the modifiers`
    - `shift`: `is SHIFT in the modifiers`
    - `succeeded`: `true if we succeeded`
- Level: `WINEVENT_LEVEL_VERBOSE`
- Keyword: `TIL_KEYWORD_TRACE` # 0x0000000100000000


#### UnregisterHotKey

- Description: `Emitted when clearing previously set hotkeys`
- Fields:
    - `index`: `the index of the hotkey to remove`
- Level: `WINEVENT_LEVEL_VERBOSE`
- Keyword: `TIL_KEYWORD_TRACE` # 0x0000000100000000


#### AppHost_setupGlobalHotkey

- Description: `Emitted when setting a single hotkey`
- Fields:
    - `index`: `the index of the hotkey to add`
    - `name`: `the name of the command`
    - `succeeded`: `true if we succeeded`
- Level: `WINEVENT_LEVEL_VERBOSE`
- Keyword: `TIL_KEYWORD_TRACE` # 0x0000000100000000

