# Tracking Parent/Child Process Relationship Via BAM Registry Key

Reference: https://twitter.com/nas_bench/status/1661692446231633920

You can indirectly track child processes created by a process by monitoring registry set events for the following key `HKLM\System\CurrentControlSet\Services\bam\State\UserSettings\<SID>\<Binary>`

### Examples

- Cmd.EXE Creating Rundll32.EXE

![image](https://github.com/nasbench/Misc-Research/assets/8741929/441ab7b4-d489-43a9-abf1-a5b59ab37340)

- Explorer.EXE Creating Microsoft Paint

![image](https://github.com/nasbench/Misc-Research/assets/8741929/60a2ce76-4335-407d-ab32-9dc986808215)
