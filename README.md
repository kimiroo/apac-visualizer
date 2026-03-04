# APAC Visualizer++
![MOL?LU](assets/mollu.webp)

Visualizer for partner and plant overview

## Requirements
- Python 3.10+
- Git (Optional)


## Setting up requirements

### Installing Python 3
1. Open `cmd` or `PowerShell`
2. Type following commands:
```cmd
winget install -e --id 9NQ7512CXL7T
py install 3
```
3. Type `SystemPropertiesAdvanced.exe` to open Advanced System Settings
4. Click `Environment Variables`
5. Double click `Path` under `User variables for [USERNAME]`
6. Click `New` and paste `%LocalAppData%\Python\bin`
7. Save and close the dialogs

### Alternative way to install Python 3
If your organization doesn't allow Microsoft Store or you can't use `winget`,
you should manually install Python from [python.org](python.org).
1. Head to [https://www.python.org/downloads/windows](https://www.python.org/downloads/windows)
and click latest **Python 3 Release**. (Not Python install manager)
2. Scroll down and download **Windows installer (64-bit)** (Or whatever python.org recommends)\
(DO NOT download Python install manager)
3. Install Python 3 with default options
4. Proceed from the third item in **Installing Python 3**

### Installing Git
If you want to easily copy and update source code, you should install Git.
1. Open `cmd` or `PowerShell`
2. Type following commands:
```cmd
winget install -e --id Git.Git --source winget
```

### Alternative way to install Git
If you previously have used alternate method to install Python 3, you should follow this method to install Git as well.
1. Head to [https://git-scm.com/install/windows](https://git-scm.com/install/windows) and download Git installer
2. Install Git with default options

## Launching APAC Visualizer++
1. If you have installed Git, open `cmd` or `PowerShell` and `cd` into desired location.\
(e.g. If you want to store files at Desktop, type `cd "C:\Users\[USERNAME]\Desktop"`. `[USERNAME]` is your username.)\
2. Run `git clone https://github.com/kimiroo/apac-visualizer` in your command prompt to retrieve latest files.
3. Launch `run.bat` to start the main application. Python will automatically open a web app in your browser's new tab.

If you haven't installed Git, follow this guide instead.
1. Navigate to [https://github.com/kimiroo/apac-visualizer](https://github.com/kimiroo/apac-visualizer)
2. Click `Code` then click `Download ZIP` to download files
3. Extract contents and launch `run.bat` to start the main application.

## Updating geodata
If geodata (e.g. province) is outdated, run `get_geodata.bat` to retrieve latest geodata.