# AgentExecutor

Intune Management Extension included on Intune Managed Devices.

This binary can be used as a LOLBIN as described [here](https://lolbas-project.github.io/lolbas/OtherMSBinaries/Agentexecutor/). Below is a writeup describing the details from the source code on how we can achieve execution.

This writeup looks at version ["AgentExecutor" 1.80.133.0](https://www.virustotal.com/gui/file/8ded7e544f8a7f5ccda90e971d7a8a25dd4e390e2d08731676a3875d57c3ef46/details) and ["Microsoft.Management.Clients.IntuneManagementExtension.WinGetLibrary.dll" 1.79.160.0](https://www.virustotal.com/gui/file/ff554678192fbe990945e283ab185895544d3c3a9b2dd0592ecad032b59121bf/details)

Path:
    - `C:\Program Files (x86)\Microsoft Intune Management Extension\agentexecutor.exe`

Additional Info:
    - https://twitter.com/nas_bench/status/1618198975072604161

## Main

The program choose its path of execution depending on the first argument and the number of argument being passed. The following is a list of allowed and expected flags.

- [-powershell](#-powershell)
- [-powershellDetection](#-powershelldetection)
- [-remediationScript](#-remediationscript)
- [-proxy](#-proxy)
- [-toast](#-toast)
- [-remotehelplaunch](#-remotehelplaunch)
- [-EPM](#-epm)
- [-detect](#-detect)
- [-require](#-require)
- [-presentationMode](#-presentationmode)
- [-executeWinGet](#-executewinget)

I also will described 2 additional internal functions that are related to this 

- [PowerShellExecutor.Run2](#powershellexecutorrun2)
- [WinGetOperation.ExecuteAsync](#wingetoperationexecuteasync)

### `-powershell`

```c#
if (args != null && args.Length > 8 && args[0] == "-powershell")
{
    List<string> list = new List<string>();
    try
    {
        ExecutorLog.TraceInformation("Powershell option gets invoked");
        if (string.IsNullOrEmpty(args[1]) || string.IsNullOrEmpty(args[2]) || string.IsNullOrEmpty(args[3]))
        {
            ExecutorLog.TraceInformation("empty or null parameter detected, exit ...");
            return;
        }
        string text = args[1]; // scriptPath
        string text2 = args[2]; // outputFilePath
        string text3 = args[3]; // errorFilePath
        string text4 = args[4]; // timeoutFilePath
        int num = (string.IsNullOrEmpty(args[5]) ? 60000 : int.Parse(args[5])); // timeoutSeconds
        string text5 = args[6]; // powershellPath
        string text6 = args[7]; // enforceSignatureCheck
        bool flag = !(args[8] == "1"); // runAs32BitOn64
        ExecutorLog.TraceInformation(text);
        ExecutorLog.TraceInformation(text2);
        ExecutorLog.TraceInformation(text3);
        ExecutorLog.TraceInformation(text4);
        // Run2(
        //    powershellPath, 
        //    scriptPath, 
        //    outputFilePath, 
        //    errorFilePath, 
        //    timeoutFilePath, 
        //    scriptParams, 
        //    timeoutSeconds,  
        //    enforceSignatureCheck, 
        //    dumpExitCode = false, 
        //    exitCodeFilePath = null, 
        //    runAs32BitOn64 = true, 
        //    proactiveRemediation = false
        // )
        PowershellExecutor.Run2(text5, text, text2, text3, text4, string.Empty, num, text6, false, null, flag, false);
        ExecutorLog.TraceInformation("Agent executor completed.");
        return;
    }
    catch (Exception ex)
    {
        list.ForEach(delegate(string t)
        {
            ExecutorLog.TraceInformation(t);
        });
        ExecutorLog.TraceInformation("Error occurs when running command via agent executor, ex = {0}", new object[] { ex });
        return;
    }
}
```

If the "-powershell" flag is passed first, another 8 arguments are expected to be passed in order to enter this code path.

Example:

```powershell
AgentExecutor.exe -powershell [scriptPath] [outputFilePath] [errorFilePath] [timeoutFilePath] [timeoutSeconds] [powershellPath] [enforceSignatureCheck (bool)] [runAs32BitOn64 (bool)]
```

The arguments passed in the command line are assigned to different variables and then passed to the "Run2" function that's part of the "PowershellExecutor" class. This function is responsible for executing "powershell" and its the one that we can "abuse" to achieve arbitrary "code execution". See the [PowerShellExecutor.Run2](#powershellexecutorrun2) section for more details.

### `-powershellDetection`

```c#
if (args != null && args.Length > 9 && args[0] == "-powershellDetection")
{
    List<string> list2 = new List<string>();
    try
    {
        ExecutorLog.TraceInformation("PowershellDetection option gets invoked");
        if (string.IsNullOrEmpty(args[1]) || string.IsNullOrEmpty(args[2]) || string.IsNullOrEmpty(args[3]))
        {
            ExecutorLog.TraceInformation("empty or null parameter detected, exit ...");
            return;
        }
        string text7 = args[1]; // scriptPath
        string text8 = args[2]; // outputFilePath
        string text9 = args[3]; // errorFilePath
        string text10 = args[4]; // timeoutFilePath
        int num2 = (string.IsNullOrEmpty(args[5]) ? 60000 : int.Parse(args[5])); // timeoutSeconds
        string text11 = args[6]; // powershellPath
        string text12 = args[7]; // enforceSignatureCheck
        string text13 = args[8]; // exitCodeFilePath
        bool flag2 = true;
        if (!bool.TryParse(args[9], out flag2)) // runAs32BitOn64
        {
            flag2 = true;
        }
        ExecutorLog.TraceInformation(text7);
        ExecutorLog.TraceInformation(text8);
        ExecutorLog.TraceInformation(text9);
        ExecutorLog.TraceInformation(text10);
        ExecutorLog.TraceInformation(text13);
        // Run2(
        //    powershellPath, 
        //    scriptPath, 
        //    outputFilePath, 
        //    errorFilePath, 
        //    timeoutFilePath, 
        //    scriptParams, 
        //    timeoutSeconds,  
        //    enforceSignatureCheck, 
        //    dumpExitCode = false, 
        //    exitCodeFilePath = null, 
        //    runAs32BitOn64 = true, 
        //    proactiveRemediation = false
        // )
        PowershellExecutor.Run2(text11, text7, text8, text9, text10, string.Empty, num2, text12, true, text13, flag2, false);
        ExecutorLog.TraceInformation("Agent executor completed.");
        return;
    }
    catch (Exception ex2)
    {
        list2.ForEach(delegate(string t)
        {
            ExecutorLog.TraceInformation(t);
        });
        ExecutorLog.TraceInformation("Error occurs when running command via agent executor, ex = {0}", new object[] { ex2 });
        return;
    }
}
```

If the "-powershellDetection" flag is passed first, another 9 arguments are expected to be passed in order to enter this code path.

Example:

```powershell
AgentExecutor.exe -powershellDetection [scriptPath] [outputFilePath] [errorFilePath] [timeoutFilePath] [timeoutSeconds] [powershellPath] [enforceSignatureCheck (bool)] [exitCodeFilePath] [runAs32BitOn64 (bool)]
```

And similar to the "-powershell" flag, the arguments passed in the command line are assigned to different variables and then passed to the "Run2" function that's part of the "PowershellExecutor" class. This function is responsible for executing "powershell" and its the one that we can "abuse" to achieve arbitrary "code execution". See the [PowerShellExecutor.Run2](#powershellexecutorrun2) section for more details.

### `-remediationScript`

```c#
if (args != null && args.Length > 10 && args[0] == "-remediationScript")
{
    List<string> list3 = new List<string>();
    try
    {
        ExecutorLog.TraceInformation("remediation script option gets invoked");
        if (string.IsNullOrEmpty(args[1]) || string.IsNullOrEmpty(args[2]) || string.IsNullOrEmpty(args[3]))
        {
            ExecutorLog.TraceInformation("empty or null parameter detected, exit ...");
            return;
        }
        string text14 = args[1]; // scriptPath
        string text15 = args[2]; // outputFilePath
        string text16 = args[3]; // errorFilePath
        string text17 = args[4]; // timeoutFilePath
        int num3 = (string.IsNullOrEmpty(args[5]) ? 60000 : int.Parse(args[5])); // timeoutSeconds
        string text18 = args[6]; // powershellPath
        string text19 = args[7]; // enforceSignatureCheck
        string text20 = args[8]; // exitCodeFilePath
        bool flag3 = true;
        if (!bool.TryParse(args[9], out flag3)) // runAs32BitOn64
        {
            flag3 = true;
        }
        string text21 = args[10]; // scriptParams
        ExecutorLog.TraceInformation(text14);
        ExecutorLog.TraceInformation(text15);
        ExecutorLog.TraceInformation(text16);
        ExecutorLog.TraceInformation(text17);
        ExecutorLog.TraceInformation(text20);
        // Run2(
        //    powershellPath, 
        //    scriptPath, 
        //    outputFilePath, 
        //    errorFilePath, 
        //    timeoutFilePath, 
        //    scriptParams, 
        //    timeoutSeconds,  
        //    enforceSignatureCheck, 
        //    dumpExitCode = false, 
        //    exitCodeFilePath = null, 
        //    runAs32BitOn64 = true, 
        //    proactiveRemediation = false
        // )
        Environment.Exit(PowershellExecutor.Run2(text18, text14, text15, text16, text17, text21, num3, text19, false, text20, flag3, true));
        ExecutorLog.TraceInformation("Agent executor completed.");
        return;
    }
    catch (Exception ex3)
    {
        list3.ForEach(delegate(string t)
        {
            ExecutorLog.TraceInformation(t);
        });
        ExecutorLog.TraceInformation("Error occurs when running command via agent executor, ex = {0}", new object[] { ex3 });
        return;
    }
}
```

If the "-remediationScript" flag is passed first, another 10 arguments are expected to be passed in order to enter this code path.

Example:

```powershell
AgentExecutor.exe -powershellDetection [scriptPath] [outputFilePath] [errorFilePath] [timeoutFilePath] [timeoutSeconds] [powershellPath] [enforceSignatureCheck (bool)] [exitCodeFilePath] [runAs32BitOn64 (bool)] [scriptParams]
```

And similar to both of the "-powershell" and "powershellDetection" flags, the arguments passed in the command line are assigned to different variables and then passed to the "Run2" function that's part of the "PowershellExecutor" class. This function is responsible for executing "powershell" and its the one that we can "abuse" to achieve arbitrary "code execution". See the [PowerShellExecutor.Run2](#powershellexecutorrun2) section for more details.

### `-proxy`

TBD

```c#
if (args != null && args.Length == 3 && args[0] == "-proxy")
{
    try
    {
        string text22 = args[1];
        string text23 = args[2];
        ExecutorLog.TraceInformation("[proxy poller] Getting proxy info. url is {0}", new object[] { text23 });
        ProxySetting[] currentUserProxySettings = new WebProxyHelper().GetCurrentUserProxySettings();
        bool flag4 = false;
        string text24 = string.Empty;
        string text25 = string.Empty;
        string text26 = string.Empty;
        foreach (ProxySetting proxySetting in currentUserProxySettings)
        {
            if (proxySetting.SettingType == ProxySettingType.InternetPerConnectionOptions && ((ProxyConnectionOptions)proxySetting.NumericValue).ToString().ToLower().Contains("autodetect"))
            {
                flag4 = true;
            }
            if (proxySetting.SettingType == ProxySettingType.InternetPerConnectionAutomaticConfigurationUrl)
            {
                text24 = proxySetting.StringValue;
            }
            if (proxySetting.SettingType == ProxySettingType.InternetPerConnectionProxyBypass)
            {
                text26 = proxySetting.StringValue;
            }
            if (proxySetting.SettingType == ProxySettingType.InternetPerConnectionProxyServer)
            {
                text25 = proxySetting.StringValue;
            }
        }
        ExecutorLog.TraceInformation("autodetect=" + flag4.ToString());
        ExecutorLog.TraceInformation("autoconfiguration url=" + text24);
        ExecutorLog.TraceInformation("bypasslist=" + text26);
        ExecutorLog.TraceInformation("static proxy=" + text25);
        string autoDetectProxySetting = WebProxyHelper.GetAutoDetectProxySetting(text24, text23);
        string tempPath = Path.GetTempPath();
        text22 = text22.Replace('\\', '_');
        string text27 = string.Format(CultureInfo.InvariantCulture, "IntuneWindowsAgent_Proxy_{0}.txt", text22);
        string text28 = Path.Combine(tempPath, text27);
        ExecutorLog.TraceInformation(text28);
        using (StreamWriter streamWriter = new StreamWriter(text28, false))
        {
            if (!string.IsNullOrEmpty(autoDetectProxySetting))
            {
                streamWriter.WriteLine("autoProxy=" + autoDetectProxySetting);
            }
            if (!string.IsNullOrEmpty(text25))
            {
                streamWriter.WriteLine("staticProxy=" + text25);
            }
        }
        return;
    }
    catch (Exception ex4)
    {
        ExecutorLog.TraceError("Hit exceptions when trying to get the proxy, exception is " + ex4.ToString());
        return;
    }
}
```

### `-toast`

TBD

```c#
if (args != null && args.Length == 5 && args[0] == "-toast")
{
    ToastHelper.PopToastForExecution(args[1], args[2], args[3], args[4], "");
    return;
}
if (args != null && args.Length == 6 && args[0] == "-toast")
{
    ToastHelper.PopToastForExecution(args[1], args[2], args[3], args[4], args[5]);
    return;
}
```

### `-remotehelplaunch`

TBD

```c#
if (args != null && args.Length == 2 && args[0] == "-remotehelplaunch")
{
    ToastHelper.PopToastForRemoteHelp(args[1]);
    return;
}
```

### `-EPM`

TBD

```c#
if (args != null && args.Length == 3 && args[0] == "-EPM")
{
    try
    {
        EPMToastHelper.PopToastForEPMPolicy(args);
        return;
    }
    catch (Exception ex5)
    {
        ExecutorLog.TraceError(string.Format("[EPMPolicyNotification] Error occured for agent executor, ex = {0}", ex5));
        Environment.Exit(1);
        return;
    }
}
```

### `-detect`

TBD

```c#
if (args != null && args.Length == 4 && args[0] == "-detect")
{
    ExecutorLog.TraceInformation("{0} starts", new object[] { "-detect" });
    try
    {
        int num4 = int.Parse(args[1]);
        Dictionary<int, object> dictionary = new Dictionary<int, object>();
        IDetectionManager detectionManager;
        if (num4 == 0)
        {
            detectionManager = new SideCarRegistryDetectionManager();
        }
        else if (num4 == 1)
        {
            detectionManager = new SideCarProductCodeDetectionManager();
        }
        else
        {
            if (num4 != 2)
            {
                ExecutorLog.TraceError("Unexpected detectionType: {0}", new object[] { num4 });
                return;
            }
            detectionManager = new SideCarFileDetectionManager();
        }
        string text29 = args[2];
        SideCarDetectionRuleMetadata sideCarDetectionRuleMetadata = null;
        if (!string.IsNullOrEmpty(args[2]))
        {
            byte[] array2 = Convert.FromBase64String(text29);
            string @string = Encoding.UTF8.GetString(array2);
            sideCarDetectionRuleMetadata = new JavaScriptSerializer().Deserialize<SideCarDetectionRuleMetadata>(@string);
        }
        if (detectionManager != null && sideCarDetectionRuleMetadata != null)
        {
            ExecutorLog.TraceInformation("{0} starts detecting", new object[] { detectionManager.GetType().Name });
            bool flag5 = detectionManager.Detect(sideCarDetectionRuleMetadata, dictionary);
            string text30 = args[3];
            ExecutorLog.TraceInformation("{0} writting result: {1} to resultFilePath: {2}", new object[]
            {
                detectionManager.GetType().Name,
                flag5,
                text30
            });
            using (StreamWriter streamWriter2 = new StreamWriter(text30, false, Encoding.UTF8))
            {
                streamWriter2.Write(flag5);
            }
        }
        return;
    }
    catch (Exception ex6)
    {
        ExecutorLog.TraceError("{0} failed with {1}", new object[] { "-detect", ex6.StackTrace });
        return;
    }
}
```

### `-require`

TBD

```c#
if (args != null && args.Length == 4 && args[0] == "-require")
{
    ExecutorLog.TraceInformation("{0} starts", new object[] { "-require" });
    try
    {
        int num5 = int.Parse(args[1]);
        IRequirementManager requirementManager;
        if (num5 == 0)
        {
            requirementManager = new SideCarRegistryRequirementManager();
        }
        else
        {
            if (num5 != 2)
            {
                ExecutorLog.TraceError("Unexpected ExtendedRequirementRule detectionType: {0}", new object[] { num5 });
                return;
            }
            requirementManager = new SideCarFileRequirementManager();
        }
        string text31 = args[2];
        ExtendedRequirementRuleMetadata extendedRequirementRuleMetadata = null;
        if (!string.IsNullOrEmpty(args[2]))
        {
            byte[] array3 = Convert.FromBase64String(text31);
            string string2 = Encoding.UTF8.GetString(array3);
            extendedRequirementRuleMetadata = new JavaScriptSerializer().Deserialize<ExtendedRequirementRuleMetadata>(string2);
        }
        if (requirementManager != null && extendedRequirementRuleMetadata != null)
        {
            ExecutorLog.TraceInformation("{0} starts detecting", new object[] { requirementManager.GetType().Name });
            bool flag6 = requirementManager.Detect(extendedRequirementRuleMetadata);
            string text32 = args[3];
            ExecutorLog.TraceInformation("{0} writting result: {1} to resultFilePath: {2}", new object[]
            {
                requirementManager.GetType().Name,
                flag6,
                text32
            });
            using (StreamWriter streamWriter3 = new StreamWriter(text32, false, Encoding.UTF8))
            {
                streamWriter3.Write(flag6);
            }
        }
        return;
    }
    catch (Exception ex7)
    {
        ExecutorLog.TraceError("{0} failed with {1}", new object[] { "-require", ex7.StackTrace });
        return;
    }
}
```

### `-presentationMode`

TBD

```c#
if (args != null && args.Length == 1 && args[0] == "-presentationMode")
{
    ExecutorLog.TraceInformation("PresentationMode option gets invoked");
    NativeMethods.UserNotificationState userNotificationState;
    NativeMethods.SHQueryUserNotificationState(out userNotificationState);
    ExecutorLog.TraceInformation(string.Format("RebootCoordinatorPresentationModeDetectionForAgentExecutor {0}", userNotificationState));
    int num6 = -1;
    switch (userNotificationState)
    {
    case NativeMethods.UserNotificationState.NotPresent:
    case NativeMethods.UserNotificationState.AcceptsNotifications:
        num6 = 0;
        break;
    case NativeMethods.UserNotificationState.Busy:
    case NativeMethods.UserNotificationState.RunningDirect3dFullScreen:
    case NativeMethods.UserNotificationState.QuietTime:
    case NativeMethods.UserNotificationState.App:
        num6 = 1;
        break;
    case NativeMethods.UserNotificationState.PresentationMode:
        num6 = 2;
        break;
    default:
        ExecutorLog.TraceError("RebootCoordinatorPresentationModeDetectionForAgentExecutor DisplayState is not mapped");
        break;
    }
    ExecutorLog.TraceInformation(string.Format("RebootCoordinatorPresentationModeDetectionForAgentExecutor set exit code with DisplayState {0}", num6));
    Environment.Exit(num6);
    ExecutorLog.TraceInformation("Agent executor completed.");
    return;
}
```

### `-executeWinGet`

```c#
if (namedParameters.ContainsKey("executeWinGet"))
{
    try
    {
        ExecutorLog.TraceInformation("Creating new WinGet Oepration for package: " + namedParameters["packageId"]);
        foreach (string text33 in namedParameters.Keys)
        {
            ExecutorLog.TraceInformation(string.Concat(new string[]
            {
                "Argument ",
                text33,
                " with value of ",
                namedParameters[text33],
                "."
            }));
        }
        WinGetOperationRequest winGetOperationRequest = new WinGetOperationRequest
        {
            PackageId = namedParameters["packageId"]
        };
        WinGetOperationType winGetOperationType;
        WinGetRepositoryType winGetRepositoryType;
        WinGetPackageInstallScope winGetPackageInstallScope;
        if (Enum.TryParse<WinGetOperationType>(namedParameters["operationType"], out winGetOperationType) && Enum.TryParse<WinGetRepositoryType>(namedParameters["repositoryType"], out winGetRepositoryType) && Enum.TryParse<WinGetPackageInstallScope>(namedParameters["installScope"], out winGetPackageInstallScope))
        {
            winGetOperationRequest.OperationType = winGetOperationType;
            winGetOperationRequest.RepositoryType = winGetRepositoryType;
            winGetOperationRequest.InstallScope = winGetPackageInstallScope;
            int num7;
            int num8;
            if (winGetOperationRequest.OperationType == 2 && int.TryParse(namedParameters["installTimeout"], out num7) && int.TryParse(namedParameters["installVisibility"], out num8))
            {
                winGetOperationRequest.InstallExperience = new WinGetInstallExperience();
                winGetOperationRequest.InstallExperience.InstallProgramVisibility = num8;
                winGetOperationRequest.InstallExperience.MaxRunTimeInMinutes = num7;
            }
            WinGetLibraryLogger winGetLibraryLogger = new WinGetLibraryLogger();
            AppPackageManager appPackageManager = new AppPackageManager(winGetLibraryLogger, new PackageManager(), new SystemEnvironment());
            WinGetOperation winGetOperation = new WinGetOperation(winGetLibraryLogger, new SystemTime(), appPackageManager);
            using (WinGetRemoteProgressAndResultSender winGetRemoteProgressAndResultSender = new WinGetRemoteProgressAndResultSender(namedParameters["pipeHandle"]))
            {
                WinGetOperationResult result = winGetOperation.ExecuteAsync(winGetOperationRequest, winGetRemoteProgressAndResultSender).Result;
            }
            return;
        }
        throw new ArgumentException(string.Concat(new string[]
        {
            "Invalid values provided for WinGet operation.\r\nOperation type: ",
            namedParameters["operationType"],
            "\r\nRepository type: ",
            namedParameters["repositoryType"],
            "\r\nInstall scope: ",
            namedParameters["installScope"]
        }));
    }
    catch (Exception ex8)
    {
        ExecutorLog.TraceError("-executeWinGet failed with error: " + ex8.StackTrace);
        return;
    }
}
```

The "executeWinGet" flag can be used to call "WinGet" via the "AgentExecutor" binary. This uses the `Microsoft.Management.Clients.IntuneManagementExtension.WinGetLibrary.dll` library behind the scene, which will allow for the usage of some of "winget" features without having winget installed on the end system.

Some parameters are required in order to use this functionality, we can see them being checked via the "namedParameters" dictionary. Below is the list of expected parameters and their values.

- packageId 
- operationType
    - Detection
    - ApplicabilityCheck
    - Install
    - Uninstall
- repositoryType
    - MicrosoftStore
    - WindowsPackageManagerCommunity
- installScope
    - Any
    - User
    - System
- pipeHandle

The following flags are exclusive to the "Install" operation type:

- installTimeout: Defines the maximum runtime in minutes (MaxRunTimeInMinutes)
- installVisibility

All of these flags are stored in an `WinGetOperationRequest` object and passed on to the `ExecuteAsync` function that's part of the `WinGetOperation` class.

Knowing this we can use the AgentExecutor to install/uninstall different packages directly from the CLI without relying on the Winget binary being installed. (See example command below)

```powershell
AgentExecutor.exe -executeWinGet -packageId ["ID"] -operationType ["Detection", "ApplicabilityCheck", "Install", "Uninstall"] -repositoryType ["MicrosoftStore", "WindowsPackageManagerCommunity"] -installScope ["Any", "User", "System"] -pipeHandle "pipeName"
```

For a bit more details on the internals of the `ExecuteAsync` and a small tidbit regarding the accepted "repositoryType" please see the [WinGetOperation.ExecuteAsync](#wingetoperationexecuteasync) section.

> **Note**
>
> In previous versions of "AgentExecutor", the named parameters were positional arguments, meaning that we only need to provide the value and not the flag names. See the following [blog](https://call4cloud.nl/2022/12/hotel-microsoft-store-apps-transformania/) for an example.

## `PowerShellExecutor.Run2`

```c#
public static int Run2(string powershellPath, string scriptPath, string outputFilePath, string errorFilePath, string timeoutFilePath, string scriptParams, int timeoutSeconds, string enforceSignatureCheck, bool dumpExitCode = false, string exitCodeFilePath = null, bool runAs32BitOn64 = true, bool proactiveRemediation = false)
{
	ExecutorLog.TraceInformation("Prepare to run Powershell Script ..");
	int num = int.MaxValue;
	Process process = new Process();
	StringBuilder outputStringBuilder = new StringBuilder();
	StringBuilder errorStringBuilder = new StringBuilder();
	string text = string.Empty;
	ExecutorLog.TraceInformation("scriptParams is {0}", new object[] { scriptParams });
	if (enforceSignatureCheck == null || enforceSignatureCheck == "1")
	{
		text = string.Format(CultureInfo.InvariantCulture, "{0} \"{1}\" {2}", "-NoProfile -executionPolicy allsigned -file ", scriptPath, scriptParams);
	}
	else
	{
		text = string.Format(CultureInfo.InvariantCulture, "{0} \"{1}\" {2}", "-NoProfile -executionPolicy bypass -file ", scriptPath, scriptParams);
	}
	ExecutorLog.TraceInformation("cmd line for running powershell is {0}", new object[] { text });
	IntPtr intPtr = 0;
	bool flag = false;
	int num2;
	try
	{
		if (!Directory.Exists(powershellPath))
		{
			throw new ArgumentException("invalid argument " + powershellPath);
		}
		if (!runAs32BitOn64)
		{
			ExecutorLog.TraceInformation(string.Format("runAs32BitOn64 = {0}, so Disable Wow64FsRedirection", runAs32BitOn64));
			flag = NativeMethods.Wow64DisableWow64FsRedirection(ref intPtr);
		}
		process.StartInfo.FileName = Path.Combine(powershellPath, "powershell.exe");
		ExecutorLog.TraceInformation("PowerShell path is " + process.StartInfo.FileName);
		process.StartInfo.Arguments = text;
		process.StartInfo.RedirectStandardError = true;
		process.StartInfo.RedirectStandardOutput = true;
		process.StartInfo.WindowStyle = ProcessWindowStyle.Hidden;
		process.StartInfo.CreateNoWindow = true;
		process.StartInfo.UseShellExecute = false;
		process.EnableRaisingEvents = false;
		process.OutputDataReceived += delegate(object sender, DataReceivedEventArgs eventArgs)
		{
			outputStringBuilder.AppendLine(eventArgs.Data);
		};
		process.ErrorDataReceived += delegate(object sender, DataReceivedEventArgs eventArgs)
		{
			errorStringBuilder.AppendLine(eventArgs.Data);
		};
		for (int i = 0; i < 3; i++)
		{
			if (process.Start())
			{
				try
				{
					ExecutorLog.TraceInformation(string.Format("[Executor] created powershell with process id {0}", process.Id));
					break;
				}
				catch (InvalidOperationException ex)
				{
					ExecutorLog.TraceError("Hit an expcetion when printing the pid, ex = " + ex.ToString());
					break;
				}
			}
			ExecutorLog.TraceWarning("[Executor] process is re-used.");
			process.Kill();
			process.WaitForExit();
		}
		process.BeginOutputReadLine();
		process.BeginErrorReadLine();
		if (!process.WaitForExit(timeoutSeconds * 1000))
		{
			ExecutorLog.TraceInformation(string.Format("Error:Powershell script execution timed out. timeout = {0} seconds", timeoutSeconds));
			process.Kill();
			PowershellExecutor.UpdateTimeoutFile(timeoutFilePath, "1");
		}
		else
		{
			num = process.ExitCode;
			ExecutorLog.TraceInformation("Powershell exit code is {0}", new object[] { num });
			string text2 = "lenth of out=";
			num2 = outputStringBuilder.ToString().Length;
			ExecutorLog.TraceInformation(text2 + num2.ToString());
			string text3 = "lenth of error=";
			num2 = errorStringBuilder.ToString().Length;
			ExecutorLog.TraceInformation(text3 + num2.ToString());
			ExecutorLog.TraceInformation("error from script =" + errorStringBuilder.ToString());
			if (num == 0)
			{
				ExecutorLog.TraceInformation("Powershell script is successfully executed.");
			}
			else
			{
				ExecutorLog.TraceInformation("Powershell script is failed to execute");
			}
			PowershellExecutor.DumpResultsToFile(outputFilePath, errorFilePath, outputStringBuilder.ToString(), errorStringBuilder.ToString());
			if (dumpExitCode && !string.IsNullOrEmpty(exitCodeFilePath))
			{
				StringBuilder errorStringBuilder2 = errorStringBuilder;
				if (errorStringBuilder2 != null && errorStringBuilder2.ToString().Trim(Environment.NewLine.ToCharArray()).Length > 0 && num == 0)
				{
					num = -1;
				}
				PowershellExecutor.DumpExitCodeToFile(exitCodeFilePath, num);
			}
			if (proactiveRemediation)
			{
				PowershellExecutor.DumpExitCodeToFile(exitCodeFilePath, num);
			}
		}
		num2 = num;
	}
	catch (Exception ex2)
	{
		ExecutorLog.TraceInformation("Exception happens in Run2, ex = " + ex2.ToString());
		throw;
	}
	finally
	{
		process.Close();
		if (flag)
		{
			ExecutorLog.TraceInformation("Revert Wow64FsRedirection");
			NativeMethods.Wow64RevertWow64FsRedirection(intPtr);
		}
	}
	return num2;
}

```
The ``Run2`` function takes 12 arguments and is responsible for executing the PowerShell scripts passed on by the 3 flags

- [-powershell](#-powershell)
- [-powershellDetection](#-powershelldetection)
- [-remediationScript](#-remediationscript)

The first important thing in this function (at least from a LOLBin perspective) is the following section.

```c#
if (enforceSignatureCheck == null || enforceSignatureCheck == "1")
{
    text = string.Format(CultureInfo.InvariantCulture, "{0} \"{1}\" {2}", "-NoProfile -executionPolicy allsigned -file ", scriptPath, scriptParams);
}
else
{
    text = string.Format(CultureInfo.InvariantCulture, "{0} \"{1}\" {2}", "-NoProfile -executionPolicy bypass -file ", scriptPath, scriptParams);
}
```

Where depending on the value of `enforceSignatureCheck` we either execute "powershell.exe" with the `allsigned` execution policy if it is not set (null) or set to "1", or we execute it with `bypass` execution policy if its either.

```powershell
[powershellPath] -NoProfile -executionPolicy allsigned -file [scriptPath] [scriptParams]

[powershellPath]-NoProfile -executionPolicy bypass -file [scriptPath] [scriptParams]
```

After that a check is made on the `powershellPath` variable in order to check if the directory exist. This is important to note down, because the check isn't looking for a specific set of paths but simply if the path exists (we can abuse this later).

```c#
if (!Directory.Exists(powershellPath))
{
    throw new ArgumentException("invalid argument " + powershellPath);
}
```

Once the path is validated (i.e exists). It is simply concatenated to the string `powershell.exe` and assigned to the FileName field of the StartInfo process structure as such.

```c#
process.StartInfo.FileName = Path.Combine(powershellPath, "powershell.exe");
```

The process windows style is also set to hidden.

```c#
process.StartInfo.WindowStyle = ProcessWindowStyle.Hidden;
```

Without any additional checks the process is executed.

```c#
for (int i = 0; i < 3; i++)
    {
        if (process.Start())
        {
            ...
            ...
            ...
```

This opens up 2 areas of abuse:

- The first being the ability to use AgentExecutor with any of the 3 flags described above (1 of them is already listed in the LOLBAS entry) to proxy the execution of arbitrary powershell scripts.
- THe second leverages the fact that there are no checks on the ``powershellPath`` variable. This allows us to point the binary to any directory that contains a binary named `powershell.exe` and it'll get executed by proxy.

## `WinGetOperation.ExecuteAsync`

```c#
public async Task<WinGetOperationResult> ExecuteAsync(
    WinGetOperationRequest winGetOperationRequest,
    IProgressAndResultSender progressAndResultSender)
{
    Guard.ArgumentNotNull((object) winGetOperationRequest, nameof (winGetOperationRequest));
    if (winGetOperationRequest.RepositoryType != WinGetRepositoryType.MicrosoftStore)
        throw new InvalidOperationException(string.Format("Unsupported WinGet repository type: {0}.", (object) winGetOperationRequest.RepositoryType));
    Func<Task> operationAction = (Func<Task>) null;
    switch (winGetOperationRequest.OperationType)
    {
        case WinGetOperationType.Detection:
            operationAction = (Func<Task>) (async () => await Task.Run((Action) (() => this.appPackageManager.EvaluateDetection(progressAndResultSender))));
            break;
        case WinGetOperationType.ApplicabilityCheck:
            operationAction = (Func<Task>) (async () => await Task.Run((Action) (() => this.appPackageManager.EvaluateApplicability(winGetOperationRequest.InstallScope, progressAndResultSender))));
            break;
        case WinGetOperationType.Install:
            operationAction = (Func<Task>) (async () => await this.appPackageManager.InstallAppAsync(winGetOperationRequest.InstallScope, progressAndResultSender));
            break;
        case WinGetOperationType.Uninstall:
            operationAction = (Func<Task>) (async () =>
            {
                await this.appPackageManager.UninstallAppAsync(winGetOperationRequest.UninstallScope, progressAndResultSender);
                await this.systemTime.Delay(3000);
            });
            break;
        default:
            throw new NotImplementedException("The operation type provided does not have any implementations.");
    }
    WinGetOperationResult winGetOperationResult = new WinGetOperationResult();
    try
    {
        this.logger.TraceInformation(string.Format("[Win32App][WinGetApp][{0}] Starting {1} for app with id: {2} and package id: {3}.", (object) nameof (WinGetOperation), (object) winGetOperationRequest.OperationType, (object) winGetOperationRequest.AppId, (object) winGetOperationRequest.PackageId));
        await initialAction();
        await operationAction();
        winGetOperationResult = this.appPackageManager.GetResult();
    }
    catch (Exception ex)
    {
        winGetOperationResult.ResultCode = WinGetOperationResultCode.UnknownError;
        winGetOperationResult.InstallerErrorCode = new int?(ex.HResult);
        winGetOperationResult.ExtendedErrorCode = new int?(ex.HResult);
    }
    finally
    {
        this.logger.TraceInformation(string.Format("[Win32App][WinGetApp][{0}] Completed {1} for app with id: {2} and package id: {3}.", (object) nameof (WinGetOperation), (object) winGetOperationRequest.OperationType, (object) winGetOperationRequest.AppId, (object) winGetOperationRequest.PackageId) + string.Format("\r\nResult: {0}", (object) winGetOperationResult.ResultCode));
    }
    WinGetOperationResult getOperationResult = winGetOperationResult;
    operationAction = (Func<Task>) null;
    winGetOperationResult = (WinGetOperationResult) null;
    return getOperationResult;

    async Task initialAction()
    {
        await this.appPackageManager.InitializeAsync(winGetOperationRequest.RepositoryType, winGetOperationRequest.InstallScope, winGetOperationRequest.PackageId);
        await this.appPackageManager.SearchAppPackageAsync();
    }
}
```

While the function is somewhat straightforward, an interesting thing to notice (at least in this version of the DLL). Is that the only accepted repository type is "MicrosoftStore".

```c#
if (winGetOperationRequest.RepositoryType != WinGetRepositoryType.MicrosoftStore)
    throw new InvalidOperationException(string.Format("Unsupported WinGet repository type: {0}.", (object) winGetOperationRequest.RepositoryType));
```
