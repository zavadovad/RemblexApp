# IMPORT
# Import - knihovny
import PySimpleGUI as sg

from pygame import mixer
from time import sleep
from os import getcwd

# Import - funkce
from remblexPyFiles.stt import stt
from remblexPyFiles.tts import tts
from remblexPyFiles.sts import sts

# Hlavní menu ------------------------------------------------------------------------
def mainMenu(textColor, basicFont):
    # Proměnné
    buttSize = (18, 2)
    
    # Globální nastavení okna
    sg.theme("BlueMono")
    sg.set_options(text_color = textColor, font = basicFont)

    # Celkové zobrazení
    mainMenuLayout = [
        [sg.Text("REMBLEX", font = ("Copperplate Gothic Bold", 27), pad = (45, (25, 0)))],
        [sg.Text("HLAVNÍ MENU", font = ("", 12, "bold"), pad = (0, (0, 25)))],

        [sg.Button("Speech-To-Text\nSTT", key = "-optStt-", size = buttSize, pad = (0, (0, 7.5)))],
        [sg.Button("Text-To-Speech\nTTS", key = "-optTts-", size = buttSize, pad = (0, (0, 7.5)))],
        [sg.Button("Speech-To-Speech\nSTS", key = "-optSts-", size = buttSize, pad = 0)],
        [sg.Button("KONEC", key = "-optFin-", size = (18, 1), pad = (0, (30, 45)))]
    ]

    # Generování okna
    mainMenuWin = sg.Window("REMBLEX - Menu",
                            mainMenuLayout,
                            text_justification = "c",
                            element_justification = "c",
                            resizable = False,
                            finalize = True)

    # Smyčka
    while True:
        event, values = mainMenuWin.read()
        
        if event == sg.WIN_CLOSED or event == "-optFin-":   # Zavření aplikace
            opt = "finish"
            break
        
        # Možnosti z hlavního menu
        elif event == "-optStt-":
            opt = "stt"
            break
        
        elif event == "-optTts-":
            opt = "tts"
            break
        
        elif event == "-optSts-":
            opt = "sts"
            break
    
    mainMenuWin.Close()  # Zavře hlavní menu
    return opt
# ------------------------------------------------------------------------------------

# MAIN -------------------------------------------------------------------------------
if __name__ == "__main__":
    # Proměnné
    # Barvy
    textColor = "midnight blue"
    
    # Fonty
    basicFont = ("", 10, "bold")
    inputFont = ("", 10)
    titleFont = ("Copperplate Gothic Bold", 32)
    subTitleFont = ("", 17, "bold")
    frameTitleFont = ("", 11, "bold")
    
    # Veliosti
    buttSize = (10, 1)
    inputWinSize = (50, 1)

    # Aktuální a defaultní adresář
    savesDir = getcwd().replace("\\", "/") + "/saves/"

    # Iniciace "mixer"
    mixer.init()
    
    # Rozcestník
    win = mainMenu(textColor, basicFont)
    
    # Smyčka aplikace
    while win != "finish":
        if win == "stt":
            sleep(0.25)
            win = stt(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize, savesDir)
        
        elif win == "tts":
            sleep(0.25)
            win = tts(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize, savesDir)
        
        elif win == "sts":
            sleep(0.25)
            win = sts(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize, savesDir)
# ------------------------------------------------------------------------------------