# IMPORT
# Import - knihovny
import PySimpleGUI as sg

from sounddevice import InputStream
from soundfile import SoundFile
from threading import Thread, Event
from pydub import AudioSegment
from queue import Queue
from regex import search, sub
from time import time
from os import listdir

# FUNKCE
# Blokování oken ---------------------------------------------------------------------
def disableWin(win, disableList):
    for element in disableList:
        win[element].update(disabled = True)
# ------------------------------------------------------------------------------------

# Odblokování oken -------------------------------------------------------------------
def enableWin(win, enableList):
    for element in enableList:
        win[element].update(disabled = False)
# ------------------------------------------------------------------------------------

# Číslování shodujícího se názvu -----------------------------------------------------
def enumerateName(name, folder):
    num = 1

    if name.find("(") != -1 and name.find(")") != -1 and search("\(([^\)]+)\)[^\(]*$", name).group(1).isnumeric():
        pass
    else:
        name = name + "(1)"

    while name + ".wav" in listdir(folder):
        num += 1
        name = name.replace(search("\(([^\)]+)\)[^\(]*$", name).group(1), str(num))
        
    return name
# ------------------------------------------------------------------------------------

# Blokování znaků v názvu ------------------------------------------------------------
def signBlock(win, elementList, string, key):
    badChars = [".", ",", ":", "\\", "/", "<", ">", "*"]
    
    for char in badChars:
        if string.find(char) != -1:
            win[key].update(sub(r".$", "", string))
            errorPopup(win, elementList, "Název nesmí obsahovat žádný z následujících znaků:\n. , : \\ / < > *")
            break
# ------------------------------------------------------------------------------------

# Oprava audia -----------------------------------------------------------------------
def audioCorrection(path):
    wav = AudioSegment.from_wav(path)
    wav.export(path, format = "wav")
# ------------------------------------------------------------------------------------

# OKNA
# Vyskakovací chybová hláška ---------------------------------------------------------
def errorPopup(win, disableList, popupText):
    disableWin(win, disableList)

    # Zobrazení
    popupLayout = [
        [sg.Text(popupText, background_color = "midnight blue", text_color = "white", pad = (20, (20, 10)))],
        [sg.Button("OK", key = "-ok-", size = (10, 1), button_color = "midnight blue on white", font = ("", 10, "bold"), pad = (60, 20), bind_return_key = True)]
    ]

    # Generuje okno
    popupWin = sg.Window(
        "Error",
        popupLayout,
        element_justification = "c",
        background_color = "midnight blue",
        resizable = False,
        keep_on_top = True,
        disable_minimize = True
    )

    # Smyčka
    while True:
        event, values = popupWin.read()

        if event == sg.WIN_CLOSED or "-ok-":
            break

    enableWin(win, disableList)
    popupWin.Close()
# ------------------------------------------------------------------------------------

# Diktafon ---------------------------------------------------------------------------
def dict(mainWin, elementList, textColor, basicFont, inputFont, subTitleFont, frameTitleFont, buttSize, inputWinSize, savesDir):
    # Globální proměnná pro funkci dict
    q = Queue()
        
    def callback(indata, frames, time, status):
        q.put(indata)

    def rec(path, te):
        # Proměnné
        fs = 44100
        channels = 2

        with SoundFile(file = path, mode = "x", samplerate = fs, channels = channels) as file:
            with InputStream(samplerate = fs, channels = channels, callback = callback):
                while not te.is_set():
                    file.write(q.get())

    def dictGui(mainWin, elementList):
        # Proměnné
        isRecording = False
        recIsPlaying = False
        dictelementList = ["-recName-", "-recFolder-", "-recFolderBrowse-", "-start-", "-stop-", "-text-", "-recPath-", "-use-"]

        disableWin(mainWin, elementList)

        # Globální nastavení okna
        sg.theme("BlueMono")
        sg.set_options(
            font = basicFont,
            text_color = textColor,
            input_text_color = textColor,
            button_element_size = buttSize,
            auto_size_buttons = False
        )

        # Zobrazení menu
        menuCol = [[sg.Button("ZPĚT", key = "-back-")]]

        # Prostor pro nastavení názvu a adresáře na výstupu
        saveAsCol = [
            [sg.Column([
                [sg.Text("Zadejte název výsledného audio souboru a kam se má uložit:")],
                [sg.Text("Název:", size = buttSize),
                 sg.Input("", key = "-recName-", font = inputFont, size = inputWinSize, enable_events = True, disabled_readonly_background_color = "#F1F4FC"),
                 sg.Text(".wav", pad = (3, 0))],

                [sg.Text("Složka:", size = buttSize),
                 sg.Input(savesDir + "recordings", key = "-recFolder-", font = inputFont, size = inputWinSize, disabled_readonly_background_color = "#F1F4FC"),
                 sg.FolderBrowse("Vyhledat", key = "-recFolderBrowse-")],
            ], pad = 0, justification = "c", element_justification = "l")]
        ]

        # Časovač
        timerCol = [
            [sg.Column([
                [sg.Frame("", [[sg.Text(text = "00:00.00", key = "-timer-", background_color = "midnight blue", text_color = "white", font = ("", 13))]],
                 background_color = "midnight blue", size = (190, 32), element_justification = "c")],
                [sg.Button("Start", key = "-start-"),
                 sg.Push(),
                 sg.Button("Stop", key = "-stop-")]                
            ], pad = 0, justification = "c", element_justification = "c")]
        ]

        # Zobrazení hlavního bloku
        recordCol = [
            [sg.Column([
                [sg.Column(timerCol, justification = "c", element_justification = "c", pad = (0, 10))],
                [sg.Multiline("", sg.InputText(), key = "-text-", font = inputFont, size = (90, 12), pad = (15, (0, 15)))]                
            ], pad = 0, justification = "c", element_justification = "c")]
        ]

        pathCol = [
             [sg.Column([
                [sg.Text("Nahraný wav soubor:")],
                [sg.Text("Cesta:", size = buttSize),
                 sg.Input("", key = "-recPath-", font = inputFont, size = inputWinSize, readonly = True, disabled_readonly_background_color = "#F1F4FC"),
                 sg.Button("Použít", key = "-use-")] 
            ], pad = 0, justification = "c", element_justification = "l")]
        ]

        # Celkové zobrazení bloků
        dictLayout = [
            [sg.Column(menuCol, justification = "r", pad = 20)],
            [sg.Text("Diktafon", font = subTitleFont, pad = 0)],
            [sg.Column(saveAsCol, justification = "c", element_justification = "l", pad = (0, (20, 0)))],
            [sg.Frame("Nahrávání", [[sg.Column(recordCol)]], font = frameTitleFont, title_color = textColor, title_location = "n", pad = (23, 20))],
            [sg.Column(pathCol, justification = "c", element_justification = "l", pad = (0, (0, 25)))]
        ]

        # Generuje okno
        dictWin = sg.Window("REMBLEX - Diktafon", dictLayout, element_justification = "c", resizable = False, finalize = True)

        # Smyčka
        while True:
            if isRecording == True:
                event, values = dictWin.read(timeout = 10)

                currentTime = int(round(time() * 100)) - startTime
                dictWin["-timer-"].update("{:02d}:{:02d}.{:02d}".format((currentTime // 100) // 60, (currentTime // 100) % 60, currentTime % 100))
            else:
                event, values = dictWin.read()

            # Zavření okna
            if event == sg.WIN_CLOSED or event == "-back-":
                recPath = ""
                break
            
            elif event == "-recName-":
                signBlock(dictWin, dictelementList, values["-recName-"], "-recName-")

            # Spuštění nahrávání
            elif event == "-start-":
                recName = values["-recName-"]
                recFolder = values["-recFolder-"]

                if recName == "" or recFolder == "":
                    errorPopup(dictWin, dictelementList, "Aby bylo nahrávání možné, musíte zadat název výsledného\nwav souboru a jeho umístění.")
                
                elif isRecording == True or recIsPlaying == True:
                    pass
                
                else:
                    try:
                        isRecording = True

                        # Soubor wav již se stejným názvem existuje - až funkční, přesunout dolů pod try
                        if recName + ".wav" in listdir(recFolder):
                            recName = enumerateName(recName, recFolder)

                        recPath = recFolder + "/" + recName + ".wav"
                        dictWin["-recPath-"].update(recPath)
                        
                        startTime = 0
                        startTime = int(round(time() * 100))

                        recTE = Event()
                        recThread = Thread(name = "rec", target = rec, args = (recPath, recTE))
                        recThread.start()
                    except:
                        isRecording = False
                        errorPopup(dictWin, dictelementList, "Chyba při nahrávání.")

            # Zastavení nahrávání
            elif event == "-stop-":
                if isRecording == False:
                    pass
                
                else:
                    try:
                        isRecording = False
                        recTE.set()
                        recThread.join()
                    except:
                        errorPopup(dictWin, dictelementList, "Chyba při pokusu ukončit nahrávání.")
            
            elif event == "-use-":
                if values["-recPath-"] == "":
                    errorPopup(dictWin, dictelementList, "Nejprve musíte nahrát audio.")

                else:
                    break

        enableWin(mainWin, elementList)
        dictWin.Close()
        return recPath

    return dictGui(mainWin, elementList)
# ------------------------------------------------------------------------------------