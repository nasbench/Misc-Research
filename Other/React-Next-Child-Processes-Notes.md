# React/Next.js Detection Notes

The following notes summarize the behavior of React / Next.js when spawning child processes, particularly in development and production modes with a focus on how the Node.js `child_process` functions would look like from a process tree perspective, and was inspired by the React2Shell vulnerability.

## Shell Defaults in Node.js child_process

### Hardcoded Shell Values

**[Windows](https://github.com/nodejs/node/blob/6e474c024c85d9a93db40020dacd20a768c62369/lib/child_process.js#L654-L665):**

```javascript
if (process.platform === 'win32') {
    if (typeof options.shell === 'string')
    file = options.shell;
    else
    file = process.env.comspec || 'cmd.exe';
    // '/d /s /c' is used only for cmd.exe.
    if (RegExpPrototypeExec(/^(?:.*\\)?cmd(?:\.exe)?$/i, file) !== null) {
    args = ['/d', '/s', '/c', `"${command}"`];
    windowsVerbatimArguments = true;
    } else {
    args = ['-c', command];
    ....
```

**[Linux/Unix](https://github.com/nodejs/node/blob/6e474c024c85d9a93db40020dacd20a768c62369/lib/child_process.js#L666C1-L676C41):**

```javascript
else {
    if (typeof options.shell === 'string')
    file = options.shell;
    else if (process.platform === 'android')
    file = '/system/bin/sh';
    else
    file = '/bin/sh';
    args = ['-c', command];
}
```

The docs also points some of this information out in the [Shell Requirements](https://nodejs.org/api/child_process.html#default-windows-shell) and [Default Windows shell](https://nodejs.org/api/child_process.html#default-windows-shell) sections.

**Key Points:**

- Windows: `process.env.comspec` (usually `C:\Windows\System32\cmd.exe`) or fallback to `cmd.exe`
- cmd.exe gets special args: `/d /s /c "<command>"`
- Linux/macOS: `/bin/sh` (usually symlinked to bash/dash)
- Custom shells can override via the `shell` option

## Next.js Child Process Spawning Patterns

### Development Mode (`npm run dev`)

**Process Chain:**

```conf
cmd.exe/bash
    └─> node.exe npm-cli.js run dev
        └─> cmd.exe /d /s /c next dev
            └─> node <app_name>\node_modules\dist\bin\next dev
                └─> node.exe <app_name>\node_modules\next\dist\server\lib\start-server.js
                    └─> cmd.exe /d /s /c "<command>"
                    └─> "<binary>"
```

**Key Code Path (from next-dev.js):**

```javascript
const startServerPath = require.resolve('../server/lib/start-server');
...
...
...
child = (0, _child_process.fork)(startServerPath, {
    stdio: 'inherit',
    env: {
        ...defaultEnv,
        ...bundler === _bundler.Bundler.Turbopack ? {
            TURBOPACK: process.env.TURBOPACK
        } : undefined,
        NEXT_PRIVATE_WORKER: '1',
        NEXT_PRIVATE_TRACE_ID: _shared.traceId,
        NODE_EXTRA_CA_CERTS: startServerOptions.selfSignedCertificate ? startServerOptions.selfSignedCertificate.rootCA : defaultEnv.NODE_EXTRA_CA_CERTS,
        NODE_OPTIONS: (0, _utils.formatNodeOptions)(nodeOptions),
        // There is a node.js bug on MacOS which causes closing file watchers to be really slow.
        // This limits the number of watchers to mitigate the issue.
        // https://github.com/nodejs/node/issues/29949
        WATCHPACK_WATCHER_LIMIT: _os.default.platform() === 'darwin' ? '20' : undefined
    }
});
```

**Detection Indicators:**

If we are tracing child processes spawned by the `child_process` module in dev mode, we can look for:

- Child processes from `node` parent where the parent command-line contains `start-server.js`.
- By default if an `Asynchronous` function such as `child_process.spawn` or `child_process.exec` is called, commands passed to it will be executed via the default system shell (cmd.exe on Windows, /bin/sh on Linux/macOS). If a `Synchronous` function is used, then the binary passed is executed directly without a shell. (check out the [following notes](https://gist.github.com/swachchhanda000/a0228130f86a2dedfbcebb415b47f870) for examples logs on this behavior)

If you have access to environment variables, you can also look for the following variable in child processes:

- Env var: `NODE_ENV=development`

---

### Production Mode (`npm start`)

**Process Chain:**

```conf
cmd.exe/bash
    └─> node.exe npm-cli.js start
        └─> cmd.exe /d /s /c next start
            └─> node <app_name>\node_modules\dist\bin\next dev
                └─> cmd.exe /d /s /c "<command>"
                └─> "<binary>"
```

**Key Code Path (from next-start.js):**

```javascript
const _startserver = require("../server/lib/start-server");
...
...
...
/**
 * Start the Next.js server
 *
 * @param options The options for the start command
 * @param directory The directory to start the server in
 */ const nextStart = async (options, directory)=>{
    const dir = (0, _getprojectdir.getProjectDir)(directory);
    const hostname = options.hostname;
    const port = options.port;
    const keepAliveTimeout = options.keepAliveTimeout;
    if ((0, _getreservedport.isPortIsReserved)(port)) {
        (0, _utils.printAndExit)((0, _getreservedport.getReservedPortExplanation)(port), 1);
    }
    await (0, _startserver.startServer)({
        dir,
        isDev: false,
        hostname,
        port,
        keepAliveTimeout
    });
};
```

**Detection Indicators:**

- Look for child processes from `node` parent where the parent command-line contains a variation of `next start`.
- By default if an `Asynchronous` function such as `child_process.spawn` or `child_process.exec` is called, commands passed to it will be executed via the default system shell (cmd.exe on Windows, /bin/sh on Linux/macOS). If a `Synchronous` function is used, then the binary passed is executed directly without a shell.

If you have access to environment variables, you can also look for the following variable in child processes:

- Env var: `NODE_ENV=production`

## Other Notes

- I've seen cases where the `next` script is called with the CommandLine: `<app>\node_modules\.bin\\..\next\dist\bin\next`.
- When looking for suspicious command-lines from child-processes, avoid to match on the default shells `cmd` or `sh` (`bash` / `dash`) alone as those are as the name suggests "default" and will be used by node itself. Instead try to look for variants that are different. For example `cmd.exe` with `/d /s /c` or `cmd /d /s /c` with a suspicious looking string or command.

## False Positive Scenarios

### 1. Port Detection via netstat/lsof

When starting the Next.js server, it checks if the desired port is already in use. This is done by spawning system commands like `netstat` on Windows or `lsof` on Linux/macOS.

**Code from start-server.js:**

```javascript
try {
    // Use lsof on Unix-like systems (macOS, Linux)
    if (process.platform !== 'win32') {
        (0, _child_process.exec)(`lsof -ti:${port} -sTCP:LISTEN`, {
            signal: processLookupController.signal
        }, (error, stdout)=>{
            if (error) {
                handleError(error);
                return;
            }
            // `-sTCP` will ensure there's only one port, clean up output
            const pid = stdout.trim();
            resolve(pid || null);
        });
    } else {
        // Use netstat on Windows
        (0, _child_process.exec)(`netstat -ano | findstr /C:":${port} " | findstr LISTENING`, {
            signal: processLookupController.signal
        }, (error, stdout)=>{
            if (error) {
                handleError(error);
                return;
            }
            // Clean up output and extract PID
            const cleanOutput = stdout.replace(/\s+/g, ' ').trim();
            if (cleanOutput) {
                const lines = cleanOutput.split('\n');
                const firstLine = lines[0].trim();
                if (firstLine) {
                    const parts = firstLine.split(' ');
                    const pid = parts[parts.length - 1];
                    resolve(pid || null);
                } else {
                    resolve(null);
                }
            } else {
                resolve(null);
            }
        });
    }
....
....
....
```

This would look like this in a process tree:

- **Windows:** `cmd.exe /d /s /c "netstat -ano | findstr /C:":3000 " | findstr LISTENING"`
- **Linux:** `/bin/sh -c 'lsof -ti:3000 -sTCP:LISTEN'`

### 2. HTTPS Certificate Generation (mkcert)

**Code from next-dev.js:**

```javascript
const runDevServer = async (reboot)=>{
        try {
            if (!!options.experimentalHttps) {
                _log.warn('Self-signed certificates are currently an experimental feature, use with caution.');
                let certificate;
                const key = options.experimentalHttpsKey;
                const cert = options.experimentalHttpsCert;
                const rootCA = options.experimentalHttpsCa;
                if (key && cert) {
                    certificate = {
                        key: _path.default.resolve(key),
                        cert: _path.default.resolve(cert),
                        rootCA: rootCA ? _path.default.resolve(rootCA) : undefined
                    };
                } else {
                    certificate = await (0, _mkcert.createSelfSignedCertificate)(host);
                }
                await startServer({
                    ...devServerOptions,
                    selfSignedCertificate: certificate
                });
            } else {
                await startServer(devServerOptions);
            }
            await preflight(reboot);
        } catch (err) {
            console.error(err);
            process.exit(1);
        }
    };
    await runDevServer(false);
};
```

In practice the `createSelfSignedCertificate` will spawn a binary to generate the certs:

- Spawns `mkcert.exe` on Windows or `mkcert` on Linux
- The commands will look something like this on windows
  - `"C:\Users\Administrator\AppData\Local\mkcert\mkcert-v1.4.4-windows-amd64.exe" -CAROOT`
  - `"C:\Users\Administrator\AppData\Local\mkcert\mkcert-v1.4.4-windows-amd64.exe" -install -key-file "C:\Users\Administrator\react123\certificates\localhost-key.pem" -cert-file "C:\Users\Administrator\react123\certificates\localhost.pem" localhost 127.0.0.1 ::1`

This should only occur when the `--experimental-https` flag and its variants is used.
