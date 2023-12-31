# Notepad History / TabState Location

In recent versions of Windows 11, notepad added the ability to create tabs and save the history when closed. In order to achieve this it uses a concept called TabState stored inside of `.bin` files inside of the notepad package folder.

## Location

```
%localappdata%\Packages\Microsoft.WindowsNotepad_8wekyb3d8bbwe\LocalState\TabState
```

Contains files with a the name `<Random-GUID>.bin`.

## Header 

```
4E 50
```

## Reference

https://twitter.com/nas_bench/status/1725658060104913019
