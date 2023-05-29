# RemblexApp
This is a project created because of my master's thesis. It uses Python library TTS and Whisper to enable simple demonstration of STT, TTS and STS tasks. The whole application is made with PySimpleGui. It is devided into three main windows – STT, TTS and STS – and two supplementary windows that are Main Menu and Dictaphone.

## Installation Guide
These steps of instalation were tested on Windows 10 in Visual Studio Code editor.

1. Save the repo as a one folder to your computer.
2. Check the version of your Python. It should be at least version 3.7 and lower than 3.11. You can check it with this command:
```cmd
>> python -V
```
3. Open your saved repository and terminal in a VS Code.
4. Use the following commands to set up Python virtual environment.
```cmd
>> cd remblexVenv
>> python -m venv .
>> ./Scripts/Activate.ps1
>> cd..
```
If an error occured after launching the third command, it can be connected to a Windows Execution Policy. You can fix it by typing the following command for current user and reverse the policy by switching Bypass to Restricted (more in [PowerShell Documentation](https://learn.microsoft.com/cs-cz/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-7.3)):
```cmd
>> Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
```
5. Install a few basic modules.
```cmd
>> pip install setuptools wheel pip -U
```
6. Install library TTS and list libraries to check if a version of TTS is 0.10.0 or higher.
```cmd
>> pip install tts
>> pip list
```
7. Install the remaining libraries and launch the application.
```cmd
>> pip install -r requirements.txt
>> python main.py
```
8. The following error may occure while launching the app. You may not have an ffmpeg module in PATH or you might have to install it. You can follow [this guide](https://www.videoproc.com/resource/how-to-install-ffmpeg.htm).
```
...\lib\site-packages\pydub\utils.py:170: RuntimeWarning: Couldn't find ffmpeg or avconv
```
