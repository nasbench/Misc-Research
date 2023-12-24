# Symantec Endpoint Protection Manager (SEPM)

- **Reference**: https://twitter.com/nas_bench/status/1483402513193881600

## WinExec

If you have a #Symantec Endpoint Protection Manager (SEPM) instance installed. You can use the signed "WinExec" binary to launch arbitrary commands. It'll execute the command(s) in question using `cmd.exe /c <Command>`

### Example

```powershell
WinExec.exe <Command>
```

![image](https://user-images.githubusercontent.com/8741929/233515664-ee4f78b0-db0a-4397-bdd5-dcc7fa6f0159.png)
