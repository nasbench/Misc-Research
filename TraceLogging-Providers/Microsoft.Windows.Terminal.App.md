# Microsoft.Windows.Terminal.App

Created: 21/01/2024

ProviderGUID: 24a1622f-7da7-5c77-3303-d850bd1ab2ed
ProviderName: Microsoft.Windows.Terminal.App
ProviderGroupGUID: TBD

Definition:
    - https://github.com/microsoft/terminal/blob/0d47c862c2d8e4733ed8bcc6d57a90105d4d1712/src/cascadia/TerminalApp/AppLogic.cpp
    - https://github.com/microsoft/terminal/blob/0d47c862c2d8e4733ed8bcc6d57a90105d4d1712/src/cascadia/TerminalApp/SuggestionsControl.cpp
    - https://github.com/microsoft/terminal/blob/0d47c862c2d8e4733ed8bcc6d57a90105d4d1712/src/cascadia/TerminalApp/CommandPalette.cpp
    - https://github.com/microsoft/terminal/blob/0d47c862c2d8e4733ed8bcc6d57a90105d4d1712/src/cascadia/TerminalApp/TerminalWindow.cpp

### Events

#### AppCreated

- Description: `Event emitted when the application is started`
- Fields:
    - `TabsInTitlebar` (boolean)
- Level: `N/A`
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### AppInitialized

- Description: `Event emitted once the app is initialized`
- Fields:
    - `latency` (float32)
- Level:
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### CommandPaletteOpened

- Description: `Event emitted when the Command Palette is opened`
- Fields:
    - `Mode`: `which mode the palette was opened in` (always returns `Action`)
- Level:
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### CommandPaletteDispatchedAction

- Description: `Event emitted when the user selects an action in the Command Palette`
- Fields:
    - `SearchTextLength`: `Number of characters in the search string`
    - `NestedCommandDepth`: `the depth in the tree of commands for the dispatched action`
- Level:
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### CommandPaletteDispatchedCommandline

- Description: `Event emitted when the user runs a commandline in the Command Palette`
- Fields: `N/A`
- Level: `N/A`
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### CommandPaletteDismissed

- Description: `Event emitted when the user dismisses the Command Palette without selecting an action`
- Fields: `N/A`
- Level: `N/A`
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### Jumplist_UpdateJumplist_NullSettings

- Description: `N/A`
- Fields: `N/A`
- Level: `WINEVENT_LEVEL_VERBOSE`
- Keyword: `TIL_KEYWORD_TRACE` # 0x0000000100000000

#### SuggestionsControlOpened

- Description: `Event emitted when the Command Palette is opened`
- Fields:
    - `Mode`: `which mode the palette was opened in` (always returns `Action`)
- Level:
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### SuggestionsControlDispatchedAction

- Description: `Event emitted when the user selects an action in the Command Palette`
- Fields:
    - `SearchTextLength`: `Number of characters in the search string`
    - `NestedCommandDepth`: `the depth in the tree of commands for the dispatched action`
- Level:
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### SuggestionsControlDismissed

- Description: `Event emitted when the user dismisses the Command Palette without selecting an action`
- Fields: `N/A`
- Level: `N/A`
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### TabRenamerOpened

- Description: `Event emitted when the tab renamer is opened`
- Fields: `N/A`
- Level: `N/A`
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### TabRenamerClosed

- Description: `Event emitted when the tab renamer is closed`
- Fields:
    - `CancelledRename`: `True if the user cancelled the rename, false if they committed.`
- Level: `N/A`
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### NewTabByDragDrop

- Description: `Event emitted when the user drag&drops onto the new tab button`
- Fields: `N/A`
- Level: `N/A`
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### ConnectionCreated

- Description: `Event emitted upon the creation of a connection`
- Fields:
    - `ConnectionTypeGuid`: `The type of the connection`
    - `ProfileGuid`: `The profile's GUID`
    - `SessionGuid`: `The WT_SESSION's GUID`
- Level:
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### SetAsDefaultTipDismissed

- Description: `N/A`
- Fields: `N/A`
- Level: `N/A`
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### SetAsDefaultTipInteracted

- Description: `N/A`
- Fields: `N/A`
- Level: `N/A`
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0

#### WindowCreated

- Description: `Event emitted when the window is started`
- Fields: `N/A`
- Level: `N/A`
- Keyword: `MICROSOFT_KEYWORD_MEASURES` # 0x0
