# List Of Built-in & Third Party Applications Calling `RegisterApplicationRestart` API

The following is a list of built-in and third party applications that call the `RegisterApplicationRestart` API in order to restart automatically in case of a crash, update, computer shutdown or computer restart.

| Application / DLL   | CommandLine |
| ------------------- | ------- |
|charmap.exe | |
|cofire.exe | |
|CustomShellHost.exe | |
|DFDWiz.exe | |
|dfrgui.exe | |
|diskpart.exe | |
|diskraid.exe | |
|dxdiag.exe | |
|EoAExperiences.exe | |
|eudcedit.exe | |
|explorer.exe | `/LOADSAVEDWINDOWS` |
|fvenotify.exe | |
|fveprompt.exe | |
|ieframe.dll | Application loading this DLL that have the `-embedding` command switch will restart with `-restart /WERRESTART` |
|iscsicli.exe | |
|Magnify.exe | |
|mblctr.exe | `/open` |
|msconfig.exe | `%windir%\system32\msconfig` |
|msedge.dll | |
|msinfo32.exe | |
|msra.exe | `-RecoverDesktop` |
|MultiDigiMon.exe | |
|notepad.exe | `RestartByRestartManager:*` where `*` is a GUID |
|odbcad32.exe | |
|odbcconf.exe | |
|OneDriveSetup.exe | |
|osk.exe | |
|perfmon.exe | `/res` or `/sys` depending on some conditions |
|PresentationSettings.exe | Restart with the same CommandLine of the first execution |
|regedit.exe | |
|rstrui.exe | |
|sdclt.exe | |
|setup_wm.exe | |
|ShellAppRuntime.exe | |
|shrpubw.exe | |
|sigverif.exe | Empty or restart with the same CommandLine of the first execution |
|slui.exe | |
|snmptrap.exe | Restart with the same CommandLine of the first execution |
|tabcal.exe | Restart with empty CommandLine |
|TabTip.exe | `/Crashed` |
|Taskmgr.exe | |
|TpmInit.exe | |
|unregmp2.exe | |
|wab.exe | Empty or restart with the same CommandLine of the first execution |
|wabmig.exe | Empty or restart with the same CommandLine of the first execution |
|wbemtest.exe | |
|wiaacmgr.exe | |
|WinMgmt.exe | |
|WMPDMC.exe | |
|wmpnscfg.exe | |
|wmpshare.exe | |
|wordpad.exe | |
|WpcMon.exe | |
|C:\Program Files\WindowsApps\Microsoft.MicrosoftOfficeHub_18.2306.1061.0_x64__8wekyb3d8bbwe\WebViewHost.exe | `--restore` |
|C:\Program Files\WindowsApps\Microsoft.Paint_11.2311.28.0_x64__8wekyb3d8bbwe\PaintApp\mspaint.exe | |
|C:\Program Files\WindowsApps\Microsoft.WindowsNotepad_11.2311.33.0_x64__8wekyb3d8bbwe\Notepad\Notepad.exe | |
|C:\Program Files\WindowsApps\MicrosoftCorporationII.QuickAssist_2.0.22.0_x64__8wekyb3d8bbwe\Microsoft.RemoteAssistance. | |QuickAssist\QuickAssist.exe
|C:\Program Files\WindowsApps\MicrosoftTeams_23335.205.2559.726_x64__8wekyb3d8bbwe\msteams.exe | |

## Appendix

The following python script was used to look for application importing this function. And then a combination of Static and Dynamic analysis was done to determine the CommandLine options.

```python
import lief
import os

paths = ["C:\\Windows\\", "C:\\Program Files\\", "C:\\Program Files (x86)\\"]

def check_function(bin):
    fct_name = "RegisterApplicationRestart"
    pe = lief.PE.parse(bin)
    if pe == None:
        return None
    if pe.imported_functions:
        try:
            importedFunctions = [i.name for i in pe.imported_functions]
            if fct_name in importedFunctions:
                return bin
        except:
            return None

list_of_paths = []    
for path_ in paths:
    for root, _, files in os.walk(path_):
        for file in files:
            if file.endswith(".exe"):
                list_of_paths.append(os.path.join(root, file))

for i in list_of_paths:
    x = check_function(i)
    if x != None:
        print(x)
```
