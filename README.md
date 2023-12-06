# Daemon
 Simple task scheduler. You can schedule tasks on daily, weekly, montly and quarterly basis. Examples in the .time file.
 The .time file should be in the same directory as the .py file, and their names should be the same as well.
 This program does not run the tasks exactly on time, but within the range of the SLEEP_TIME variable. This is sufficient for almost all use cases.
 SLEEP_TIME should be lower than the granularity in the ".time" file. Otherwise you could experience unwanted behaviour of the program.
 Multiple tasks can be run at once. The program will always print which procedures it will run next, and when.

 Please feel free to share any bugs you may encounter so that I may improve the code. It's just a personal project of mine that I wanted to share.
