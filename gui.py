# Import
import PySimpleGUI as sg
import whisper as w

from sounddevice import InputStream
from soundfile import SoundFile
from threading import Thread, Event
from TTS.api import TTS
from pygame import mixer
from pydub import AudioSegment
from queue import Queue
from regex import search, sub
from time import sleep, time
from os import listdir, system

# Blokování oken
def disableWin(win, disableList):
    for element in disableList:
        win[element].update(disabled = True)

# Odblokování oken
def enableWin(win, enableList):
    for element in enableList:
        win[element].update(disabled = False)

# Číslování shodujícího se názvu
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

# Blokování znaků v názvu
def signBlock(win, elementList, string, key):
    badChars = [".", ",", ":", "\\", "/", "<", ">", "*"]
    
    for char in badChars:
        if string.find(char) != -1:
            win[key].update(sub(r".$", "", string))
            errorPopup(win, elementList, "Název nesmí obsahovat žádný z následujících znaků:\n. , : \\ / < > *")
            break

# Oprava audia
def audioCorrection(path):
    wav = AudioSegment.from_wav(path)
    wav.export(path, format = "wav")

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
def dict(mainWin, elementList, textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize):
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

        saveAsCol = [
            [sg.Column([
                [sg.Text("Zadejte název výsledného audio souboru a kam se má uložit:")],
                [sg.Text("Název:", size = buttSize),
                 sg.Input("", key = "-recName-", font = inputFont, size = inputWinSize, enable_events = True, disabled_readonly_background_color = "#F1F4FC"),
                 sg.Text(".wav", pad = (3, 0))],

                [sg.Text("Složka:", size = buttSize),
                 sg.Input("", key = "-recFolder-", font = inputFont, size = inputWinSize, disabled_readonly_background_color = "#F1F4FC"),
                 sg.FolderBrowse("Vyhledat", key = "-recFolderBrowse-")],
            ], pad = 0, justification = "c", element_justification = "l")]
        ]

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
                [sg.Multiline(open("textToRead-en.txt").read(), sg.InputText(), key = "-text-", font = inputFont, size = (90, 12), pad = (15, (0, 15)))]                
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

        #dictWin.move(0, 50) #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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
#                elif (currentTime // 100) // 60 < 1:
#                    errorPopup(dictWin, "Audio musí být delší než 1 min.\nČím bude delší, tím bude výstup kvalitnější.")
                else:
                    break

        enableWin(mainWin, elementList)

        dictWin.Close()
        return recPath

    return dictGui(mainWin, elementList)
# ------------------------------------------------------------------------------------

# Hlavní menu ------------------------------------------------------------------------
def mainMenu(textColor, basicFont):
    # Proměnné
    buttSize = (18, 2)
    
    # Globální nastavení okna
    sg.theme("BlueMono")                        # Barevný motiv okna
    sg.set_options(text_color = textColor, font = basicFont)    # Hromadné nastavení okna

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

# STT  -------------------------------------------------------------------------------
def stt(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize):
    # Lokální proměnné
    languageList = {
        "ar":"Arabský",     "be":"Běloruský",   "zh":"Čínský",  "cs":"Český",       "en":"Anglický",
        "fr":"Francouzský", "de":"Německý",     "el":"Řecký",   "he":"Hebrejský",   "hi":"Hindi",
        "ja":"Japonský",    "ko":"Korejský",    "pl":"Polský",  "ro":"Rumunský",    "ru":"Ruský",
        "sk":"Slovenský",   "es":"Španělský",   "th":"Thajský", "uk":"Ukrajinský",
    }
    elementList = [
        "-optStt-", "-optTts-", "-optSts-",
        "-wavIn-", "-wavInBrowse-", "-record-", "-playWavIn-", "-pauseWavIn-", "-stopWavIn-",
        "-txtOutName-", "-txtOutFolder-", "-txtOutFolderBrowse-",
        "-transcribe-", "-txtOut-", "-text-"
    ]
    updateList = [
        "-language-", "-wavIn-",
        "-txtOutName-", "-txtOutFolder-",
        "-txtOut-", "-text-"
    ]

    # Proměnné pygame.mixer
    soundIsPlaying = False
    soundChannel = mixer.Channel(2)

    model = w.load_model("base")

    # Globální nastavení okna
    sg.theme("BlueMono")
    sg.set_options(
        font = basicFont,
        text_color = textColor,
        input_text_color = textColor,
        button_element_size = buttSize,
        auto_size_buttons = False
    )

    # Zobrazení bloků
    # Menu
    menu = [
        [sg.Button("STT",  key = "-optStt-",  pad = ((0, 15), 0)),
         sg.Button("TTS",  key = "-optTts-",  pad = ((0, 15), 0)),
         sg.Button("STS",  key = "-optSts-",  pad = (0, 0))]
    ]

    # Nadpisy
    headlines = [
        [sg.Text("REMBLEX", font = titleFont)],
        [sg.Text("STT", font = subTitleFont)]
    ]

    # Levý horní blok
    leftUpCol = [   
        [sg.Column([
            [sg.Text("Vyberte audio soubor pro přepis nebo nahrajte nový:")],
            [sg.Input("", key = "-wavIn-", font = inputFont, size = inputWinSize, disabled_readonly_background_color = "#F1F4FC", enable_events = True),
             sg.FileBrowse("Vyhledat", key = "-wavInBrowse-", file_types = (("Audio Files", "*.wav"),),),
             sg.Button("Diktafon", key = "-record-")],
            [sg.Button("Přehrát", key = "-playWavIn-"),
             sg.Button("Pauza", key = "-pauseWavIn-", pad = (40, 4)),
             sg.Button("Stop", key = "-stopWavIn-")]
        ], pad = 0)],

        [sg.Column([
            [sg.Text("Jazyk vstupního audia:")],
            [sg.Input("", key = "-language-", font = inputFont, size = (20, 1), disabled = True, disabled_readonly_background_color = "#F1F4FC")],
        ], pad = (0, (15, 0)))],

    ]

    # Levý dolní blok
    leftDownCol = [
        [sg.Column([
            [sg.Text("Zadejte název výsledného textového souboru a kam se má uložit:")],
                    
            [sg.Text("Název:", size = buttSize),
             sg.Input("", key = "-txtOutName-", font = inputFont, size = inputWinSize, enable_events = True, disabled_readonly_background_color = "#F1F4FC"),
             sg.Text(".txt")],
            
            [sg.Text("Složka:", size = buttSize),
             sg.Input("", key = "-txtOutFolder-", font = inputFont, size = inputWinSize, disabled_readonly_background_color = "#F1F4FC"),
             sg.FolderBrowse("Vyhledat", key = "-txtOutFolderBrowse-")],
        ], pad = 0)]
    ]

    # Pravý dolní blok
    rightCol = [
        [sg.Column([
            [sg.Button("PŘEPSAT AUDIO", key = "-transcribe-", size = (30, 2), pad = (0, 40))],

            [sg.Text("Cesta k výslednému txt souboru:")],
            [sg.Input("", key = "-txtOut-", font = inputFont, size = inputWinSize, readonly = True, disabled_readonly_background_color = "#F1F4FC")],

            [sg.Text("Přepis audio souboru:", pad = (0, (40, 0)))],
            [sg.Multiline("", sg.InputText(), key = "-text-", font = inputFont, size = (76, 13), disabled = True)], 
        ], pad = 0, justification = "c", element_justification = "c")]
    ]

    # Celkové zobrazení bloků
    sttLayout = [
        [sg.Column(menu, justification = "r", pad = 20)],
        [sg.Column(headlines, justification = "c", element_justification = "c")],
        [sg.Column([
            # Levý sloupec
            [sg.Column([
                # Horní
                [sg.Frame("Vstup", [
                    [sg.Column(leftUpCol, pad = (20, (10, 20)))]
                ], font = frameTitleFont, title_color = textColor, title_location = "n", size = (604, 256), pad = ((0, 6), (0, 15)))],
                # Dolní
                [sg.Frame("Výstup", [
                    [sg.Column(leftDownCol, pad = (20, (10, 20)))]
                ], font = frameTitleFont, title_color = textColor, title_location = "n", size = (604, 256), pad = ((0, 6), 0))]
            ]),
            # Pravý sloupec
             sg.Column([
                [sg.Frame("Přepisování", [
                    [sg.Column(rightCol, pad = (20, (0, 20)), justification = "c", element_justification = "c")]
                ], font = frameTitleFont, title_color = textColor, title_location = "n", size = (604, 526), pad = ((6, 0), 0))]
             ])]
        ], key = "-mainBlock-", justification = "c", element_justification = "c", pad = (15, (10, 20)))]        # scrollable = True, size = (?, ?) !!!!!!!!!!!!!!!!!!!!
    ]

    # Generování okna
    sttWin = sg.Window("REMBLEX - STT", sttLayout, element_justification = "c", resizable = True, finalize = True)
    sttWin.Maximize()

    sttWin.set_min_size((1290, 735))        # !!!!!!!!!!!!!!!!!!!!

    # Smyčka
    while True:
        event, values = sttWin.read()

        # Zavření okna
        if event == sg.WIN_CLOSED:
            menuOpt = "finish"
            break

        # Stisknutí možností v menu
        elif event == "-optStt-":       # Obnovení STT
            for element in updateList:
                sttWin[element].update("")
                
        elif event == "-optTts-":       # Přechod na TTS
            menuOpt = "tts"
            break

        elif event == "-optSts-":       # Přechod na STS
            menuOpt = "sts"
            break

        # Vyplnění "Jazyk"
        elif event == "-wavIn-":
            try:
                audio = w.load_audio(values["-wavIn-"])
                audio = w.pad_or_trim(audio)
                mel = w.log_mel_spectrogram(audio).to(model.device)
                _, probs = model.detect_language(mel)
                language = max(probs, key = probs.get)

                if language in languageList:
                    sttWin["-language-"].update(languageList[language])
                else:
                    sttWin["-language-"].update(language)

            except:
                errorPopup(sttWin, elementList, "Chyba při určování jazyku.")

        # Stisknutí "Diktafon"
        elif event == "-record-":
            wavIn = dict(sttWin, elementList, textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize)
            
            if wavIn == "":
                pass

            else:
                sttWin["-wavIn-"].update(wavIn)

                try:
                    audio = w.load_audio(wavIn)
                    audio = w.pad_or_trim(audio)
                    mel = w.log_mel_spectrogram(audio).to(model.device)
                    _, probs = model.detect_language(mel)
                    language = max(probs, key = probs.get)

                    if language in languageList:
                        sttWin["-language-"].update(languageList[language])
                    else:
                        sttWin["-language-"].update(language)

                except:
                    errorPopup(sttWin, elementList, "Chyba při určování jazyku.")

        # Vyplňování "-txtOutName-" - omezení možných znaků
        elif event == "-txtOutName-":
            signBlock(sttWin, elementList, values["-txtOutName-"], "-txtOutName-")

        # Stisknutí "Přepsat audio"     !!!!!!!!!!!!!!!!!!!!! DOPLNIT !!!!!!!!!!!!!!!!!!
        elif event == "-transcribe-":
            wavIn = values["-wavIn-"]
            txtOutName = values["-txtOutName-"]
            txtOutFolder = values["-txtOutFolder-"]

            # Kontrola vyplnění oken
            if wavIn == "" or txtOutName == "" or txtOutFolder == "":
                errorPopup(sttWin, elementList, "Aby byl přepis možný, zadejte audio k přepisu, název\nvýsledného txt souboru a jeho umístění.")
            
            # Vše ok => přepisování
            else:
                try:
                    # Soubor txt již se stejným názvem existuje
                    if txtOutName + ".txt" in listdir(txtOutFolder):
                        txtOutName = enumerateName(txtOutName, txtOutFolder)

                    txtOutPath = txtOutFolder + "/" + txtOutName + ".txt"
                    txtFile = open(txtOutPath, "w")
                    
                    # Přepisování
                    result = model.transcribe(wavIn)
                    sttWin["-text-"].update(result["text"])

                    txtFile.write(result["text"])
                    txtFile.close()

                    sttWin["-txtOut-"].update(txtOutPath)

                except:
                    errorPopup(sttWin, elementList, "Chyba při přepisování.")

        # Přehrávání audia
        # Stisknutí "Přehrát"
        elif event == "-playWavIn-":
            wavPath = values["-wavIn-"]

            if wavPath == "":
                errorPopup(sttWin, elementList, "Zadejte soubor, který chete přehrát.")
            else:
                try:
                    soundIsPlaying = True
                    audioCorrection(wavPath)

                    sound = mixer.Sound(wavPath)
                    soundChannel.play(sound)
                except:
                    soundIsPlaying = False
                    errorPopup(sttWin, elementList, "Chyba při přehrávání.")
        
        # Stisknutí "Pause"
        elif event == "-pauseWavIn-":
            if not soundIsPlaying:
                soundIsPlaying = True
                soundChannel.unpause()
            else:
                soundIsPlaying = False
                soundChannel.pause()

        # Stisknutí "Stop"
        elif event == "-stopWavIn-":
            soundIsPlaying = False
            soundChannel.stop()

    sttWin.Close()
    return menuOpt
# ------------------------------------------------------------------------------------

# TTS  -------------------------------------------------------------------------------
def tts(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize):
    # Lokální proměnné
    languageList = [
        "Anglický",
        "Anglický - vlastní hlas",
        "Německý",
        "Slovenský",
        "Ukrajinský"
    ] 
    elementList = [
        "-optStt-", "-optTts-", "-optSts-",
        "-language-", "-txtFile-", "-txtBrowse-", "-text-", "-clear-",
        "-record-", "-wavIn-", "-wavInBrowse-", "-playWavIn-", "-pauseWavIn-", "-stopWavIn-",
        "-wavOutName-", "-wavOutFolder-", "-wavOutFolderBrowse-", "-playAsap-",
        "-generate-", "-wavOut-", "-playWavOut-", "-pauseWavOut-", "-stopWavOut-"
    ]
    updateList = [
        "-language-", "-txtFile-", "-text-", "-wavIn-",
        "-wavOutName-", "-wavOutFolder-", "-playAsap-",
        "-wavOut-"
    ]

    # Proměnné pygame.mixer
    soundIsPlaying = False
    soundChannel = mixer.Channel(2)

    # Globální nastavení okna
    sg.theme("BlueMono")
    sg.set_options(
        font = basicFont,
        text_color = textColor,
        input_text_color = textColor,
        button_element_size = buttSize,
        auto_size_buttons = False
    )

    # Zobrazení bloků
    # Menu
    menu = [
        [sg.Button("STT",  key = "-optStt-",  pad = ((0, 15), 0)),
         sg.Button("TTS",  key = "-optTts-",  pad = ((0, 15), 0)),
         sg.Button("STS",  key = "-optSts-",  pad = (0, 0))]
    ]

    # Nadpisy
    headlines = [
        [sg.Text("REMBLEX", font = titleFont)],
        [sg.Text("TTS", font = subTitleFont)]
    ]

    # Levý blok
    leftCol = [
        [sg.Column([
            [sg.Text("Jazyk:")],
            [sg.Combo(languageList,
                      key = "-language-",
                      font = inputFont,
                      size = (20, 1),
                      default_value = languageList[0],
                      readonly = True,
                      enable_events = True)],
        ], pad = 0)],
        
        [sg.Column([
            [sg.Text("Vyberte soubor s textem, ze kterého chcete generovat audio:")],
            [sg.Input("", key = "-txtFile-", font = inputFont, size = inputWinSize, disabled_readonly_background_color = "#F1F4FC", enable_events = True),
             sg.FileBrowse("Vyhledat", key = "-txtBrowse-", file_types = (("Text Files", "*.txt"),),)]
        ], pad = (0, (15, 0)))],
        
        [sg.Column([
            [sg.Text("Nebo text zadejte manuálně:")],
            [sg.Multiline("", sg.InputText(), key = "-text-", font = inputFont, size = (76, 10))],
            [sg.Push(),
             sg.Button("Vymazat", key = "-clear-")],
        ], pad = (0, (15, 0)))],
                
        [sg.Column([
            [sg.Text("Vyberte soubor s hlasem, který chete klonovat nebo svůj hlas nahrajte:")],
            [sg.Input("", key = "-wavIn-", font = inputFont, size = inputWinSize, disabled_readonly_background_color = "#F1F4FC"),
             sg.FileBrowse("Vyhledat", key = "-wavInBrowse-", file_types = (("Audio Files", "*.wav"),),),
             sg.Button("Diktafon", key = "-record-")],
            [sg.Button("Přehrát", key = "-playWavIn-"),
             sg.Button("Pauza", key = "-pauseWavIn-", pad = (40, 4)),
             sg.Button("Stop", key = "-stopWavIn-")]
        ], key = "-recordCol-", pad = (0, (15, 0)), visible = False)],
    ]

    # Pravý horní blok
    rightUpCol = [
        [sg.Column([
            [sg.Text("Zadejte název výsledného audio souboru a kam se má uložit:")],
                    
            [sg.Text("Název:", size = buttSize),
             sg.Input("", key = "-wavOutName-", font = inputFont, size = inputWinSize, enable_events = True, disabled_readonly_background_color = "#F1F4FC"),
             sg.Text(".wav")],
            
            [sg.Text("Složka:", size = buttSize),
             sg.Input("", key = "-wavOutFolder-", font = inputFont, size = inputWinSize, disabled_readonly_background_color = "#F1F4FC"),
             sg.FolderBrowse("Vyhledat", key = "-wavOutFolderBrowse-")],
            
            [sg.Checkbox("Přehrát ihned po vygenerování", key = "-playAsap-", default = True)]
        ], pad = 0)]
    ]

    # Pravý dolní blok
    rightDownCol = [
        [sg.Column([
            [sg.Button("GENEROVAT AUDIO", key = "-generate-", size = (30, 2), pad = (0, 40))],

            [sg.Text("Cesta k výslednému wav souboru:")],
            [sg.Input("", key = "-wavOut-", font = inputFont, size = inputWinSize, readonly = True, disabled_readonly_background_color = "#F1F4FC")],
            [sg.Button("Přehrát", key = "-playWavOut-"),
             sg.Button("Pauza", key = "-pauseWavOut-", pad = (40, 4)),
             sg.Button("Stop", key = "-stopWavOut-")]
        ], pad = 0, justification = "c", element_justification = "c")]
    ]

    # Celkové zobrazení bloků
    ttsLayout = [
        [sg.Column(menu, justification = "r", pad = 20)],
        [sg.Column(headlines, justification = "c", element_justification = "c")],
        [sg.Column([
            # Levý sloupec
            [sg.Column([
                [sg.Frame("Vstup", [
                    [sg.Column(leftCol, pad = (20, (10, 20)))]
                ], font = frameTitleFont, title_color = textColor, title_location = "n", size = (604, 526), pad = ((0, 6), 0))]
            ]),
            # Pravý sloupec
             sg.Column([
                # Horní
                [sg.Frame("Výstup", [
                    [sg.Column(rightUpCol, pad = (20, (10, 20)))]
                ], font = frameTitleFont, title_color = textColor, title_location = "n", size = (604, 256), pad = ((6, 0), (0, 15)))],
                [sg.Frame("Generování", [
                    [sg.Column(rightDownCol, pad = (20, (0, 20)), justification = "c", element_justification = "c")]
                ], font = frameTitleFont, title_color = textColor, title_location = "n", size = (604, 256), pad = ((6, 0), 0))]
             ])]
        ], key = "-mainBlock-", justification = "c", element_justification = "c", pad = (15, (10, 20)))]        # scrollable = True, size = (?, ?) !!!!!!!!!!!!!!!!!!!!
    ]

    # Generování okna
    ttsWin = sg.Window("REMBLEX - TTS", ttsLayout, element_justification = "c", resizable = True, finalize = True)
    ttsWin.Maximize()

    ttsWin.set_min_size((1290, 735))        # !!!!!!!!!!!!!!!!!!!!

    # Smyčka
    while True:
        event, values = ttsWin.read()

        # Zavření okna
        if event == sg.WIN_CLOSED:
            menuOpt = "finish"
            break

        # Stisknutí možností v menu
        elif event == "-optStt-":       # Přechod na STT
            menuOpt = "stt"
            break

        elif event == "-optTts-":       # Obnovení TTS
            for element in updateList:
                if element != "-language-" and element != "-playAsap-":
                    ttsWin[element].update("")
                elif element == "-language-":
                    ttsWin[element].update(languageList[0])
                elif element == "-playAsap-":
                    ttsWin[element].update(True)

        elif event == "-optSts-":       # Přechod na STS
            menuOpt = "sts"
            break
        
        # Změna hodnoty "-language-"
        elif event == "-language-":
            if values["-language-"] == "Anglický - vlastní hlas":
                ttsWin["-recordCol-"].update(visible = True)
            else:
                ttsWin["-recordCol-"].update(visible = False)

        # Vyplnění "txtFile"
        elif event == "-txtFile-":
            try:
                txtFile = open(values["-txtFile-"])
                ttsWin["-text-"].Update(txtFile.read())
            except:
                errorPopup(ttsWin, elementList, "Chyba při nahrávání souboru.")

        # Stisknutí "Vymazat"
        elif event == "-clear-":
            ttsWin["-text-"].Update("")

        # Stisknutí "Diktafon"
        elif event == "-record-":
            ttsWin["-wavIn-"].update(dict(ttsWin, elementList, textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize))
            
        # Vyplňování "-wavOutName-" - omezení možných znaků
        elif event == "-wavOutName-":
            signBlock(ttsWin, elementList, values["-wavOutName-"], "-wavOutName-")

        # Stisknutí "Generovat"
        elif event == "-generate-":
            language = values["-language-"]
            text = values["-text-"]
            wavOutName = values["-wavOutName-"]
            wavOutFolder = values["-wavOutFolder-"]

            # Bez vlastního hlasu
            if language != languageList[1]:
                
                # Kontrola vyplnění oken
                if text == "" or wavOutName == "" or wavOutFolder == "":
                    errorPopup(ttsWin, elementList, "Aby bylo generování možné, text ke generování, název výsledného\nwav souboru a jeho umístění.")

                # Vše ok => generování
                else:
                    try:
                        # Soubor wav již se stejným názvem existuje
                        if wavOutName + ".wav" in listdir(wavOutFolder):
                            wavOutName = enumerateName(wavOutName, wavOutFolder)

                        wavOutPath = wavOutFolder + "/" + wavOutName + ".wav"
                        
                        # UrČení modelu dle jazyku
                        if language == languageList[0]:         # En
                            model = "tts_models/en/ljspeech/vits"
                        elif language == languageList[2]:       # De
                            model = "tts_models/de/thorsten/vits"
                        elif language == languageList[3]:       # Sk
                            model = "tts_models/sk/cv/vits"
                        elif language == languageList[4]:       # Uk
                            model = "tts_models/uk/mai/vits"

                        # Generování audia
                        tts = TTS(model_name = model)
                        tts.tts_to_file(text = text, file_path = wavOutPath)

                        ttsWin["-wavOut-"].update(wavOutPath)

                        # Přehrát ihned po vygenerování
                        if values["-playAsap-"] == True:
                            try:
                                sleep(1)
                                soundIsPlaying = True
                                sound = mixer.Sound(wavOutPath)
                                soundChannel.play(sound)
                            except:
                                soundIsPlaying = False
                                errorPopup(ttsWin, elementList, "Chyba při přehrávání.")
                    except:
                        errorPopup(ttsWin, elementList, "Chyba při generování.")
            
            # Vlastní hlas
            else:
                wavInPath = values["-wavIn-"]
                # Kontrola vyplnění oken
                if text == "" or wavInPath == "" or wavOutName == "" or wavOutFolder == "":
                    errorPopup(ttsWin, elementList, "Aby bylo generování možné, musíte zadat jazyk, text ke generování,\naudio hlasu ke klonovéní, název výsledného wav souboru a jeho umístění.")                

                # Vše ok => generování
                else:
                    try:
                        # Soubor wav již se stejným názvem existuje - až funkční, přesunout dolů pod try
                        if wavOutName + ".wav" in listdir(wavOutFolder):
                            wavOutName = enumerateName(wavOutName, wavOutFolder)

                        wavOutPath = wavOutFolder + "/" + wavOutName + ".wav"

                        # Generování audia
                        command = 'tts --text \"' + text + '\" --model_name tts_models/multilingual/multi-dataset/your_tts  --speaker_wav ' + wavInPath + ' --language_idx \"en\" --out_path ' + wavOutPath
                        system(command)

                        ttsWin["-wavOut-"].update(wavOutPath)

                        # Přehrát ihned po vygenerování
                        if values["-playAsap-"] == True:
                            try:
                                sleep(1)
                                soundIsPlaying = True
                                sound = mixer.Sound(wavOutPath)
                                soundChannel.play(sound)
                            except:
                                soundIsPlaying = False
                                errorPopup(ttsWin, elementList, "Chyba při přehrávání.")
                    except:
                        errorPopup(ttsWin, elementList, "Chyba při generování.")

        # Přehrávání audia          
        # Stisknutí "Přehrát" (jakéhokoliv)
        elif event == "-playWavIn-" or event == "-playWavOut-":
            if event == "-playWavOut-":
                wavPath = values["-wavOut-"]
            else:
                wavPath = values["-wavIn-"]
            
            if wavPath == "":
                errorPopup(ttsWin, elementList, "Zadejte soubor, který chcete přehrát.")
            else:
                try:
                    soundIsPlaying = True
                    audioCorrection(wavPath)

                    sound = mixer.Sound(wavPath)
                    soundChannel.play(sound)
                except:
                    soundIsPlaying = False
                    errorPopup(ttsWin, elementList, "Chyba při přehrávání.")
        
        # Stisknutí "Pause" (jakéhokoliv)
        elif event == "-pauseWavIn-" or event == "-pauseWavOut-":
            if not soundIsPlaying:
                soundIsPlaying = True
                soundChannel.unpause()
            else:
                soundIsPlaying = False
                soundChannel.pause()

        # Stisknutí "Stop" (jakéhokoliv)
        elif event == "-stopWavIn-" or event == "-stopWavOut-":
            soundIsPlaying = False
            soundChannel.stop()

    ttsWin.Close()
    return menuOpt
# ------------------------------------------------------------------------------------

# STS  -------------------------------------------------------------------------------
def sts(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize):
    # Lokální proměnné
    languageList = [
        "Anglický - vlastní hlas"
    ]
    elementList = [
        "-optStt-", "-optTts-", "-optSts-",
        "-language-", "-refWav-", "-refWavBrowse-", "-playRefWav-", "-pauseRefWav-", "-stopRefWav-",
        "-record-", "-voiceWav-", "-voiceWavBrowse-", "-playVoiceWav-", "-pauseVoiceWav-", "-stopVoiceWav-",
        "-wavOutName-", "-wavOutFolder-", "-wavOutFolderBrowse-", "-playAsap-",
        "-generate-", "-wavOut-", "-playWavOut-", "-pauseWavOut-", "-stopWavOut-"
    ]
    updateList = [
        "-language-", "-refWav-", "-voiceWav-",
        "-wavOutName-", "-wavOutFolder-", "-playAsap-",
        "-wavOut-"
    ]

    # Proměnné pygame.mixer
    soundIsPlaying = False
    soundChannel = mixer.Channel(2)
    
    # Globální nastavení okna
    sg.theme("BlueMono")
    sg.set_options(
        font = basicFont,
        text_color = textColor,
        input_text_color = textColor,
        button_element_size = buttSize,
        auto_size_buttons = False,
    )

    # Zobrazení bloků
    # Menu
    menu = [
        [sg.Button("STT",  key = "-optStt-",  pad = ((0, 15), 0)),
         sg.Button("TTS",  key = "-optTts-",  pad = ((0, 15), 0)),
         sg.Button("STS",  key = "-optSts-",  pad = (0, 0))]
    ]

    # Nadpisy
    headlines = [
        [sg.Text("REMBLEX", font = titleFont)],
        [sg.Text("STS", font = subTitleFont)]
    ]
    
    # Levý blok
    leftCol = [
        [sg.Column([
            [sg.Text("Jazyk referenčního audia a audia na výstupu:")],
            [sg.Combo(languageList,
                      key = "-language-",
                      font = inputFont,
                      size = (20, 1),
                      default_value = languageList[0],
                      readonly = True)],
        ], pad = 0)],

        [sg.Column([
            [sg.Text("Vyberte wav soubor s obsahem, který chcete na výstupu:")],
            [sg.Input("", key = "-refWav-", font = inputFont, size = inputWinSize, disabled_readonly_background_color = "#F1F4FC"),
             sg.FileBrowse("Vyhledat", key = "-refWavBrowse-", file_types = (("Audio Files", "*.wav"),),),],
            [sg.Button("Přehrát", key = "-playRefWav-"),
             sg.Button("Pauza", key = "-pauseRefWav-", pad = (40, 4)),
             sg.Button("Stop", key = "-stopRefWav-")],
        ], pad = (0, (15, 0)))],

        [sg.Column([
            [sg.Text("Vyberte wav soubor s hlasem, který chcete na výstupu nebo svůj hlas nahrajte:")],
            [sg.Input("", key = "-voiceWav-", font = inputFont, size = inputWinSize, disabled_readonly_background_color = "#F1F4FC"),
             sg.FileBrowse("Vyhledat", key = "-voiceWavBrowse-", file_types = (("Audio Files", "*.wav"),),),
             sg.Button("Diktafon", key = "-record-")],
            [sg.Button("Přehrát", key = "-playVoiceWav-"),
             sg.Button("Pauza", key = "-pauseVoiceWav-", pad = (40, 4)),
             sg.Button("Stop", key = "-stopVoiceWav-")]
        ], pad = (0, (15, 0)))]
    ]

    # Pravý horní blok
    rightUpCol = [
        [sg.Column([
            [sg.Text("Zadejte název výsledného audio souboru a kam se má uložit:")],                  
        
            [sg.Text("Název:", size = buttSize),
             sg.Input("", key = "-wavOutName-", font = inputFont, size = inputWinSize, enable_events = True, disabled_readonly_background_color = "#F1F4FC"),
             sg.Text(".wav")],
            
            [sg.Text("Složka:", size = buttSize),
             sg.Input("", key = "-wavOutFolder-", font = inputFont, size = inputWinSize, disabled_readonly_background_color = "#F1F4FC"),
             sg.FolderBrowse("Vyhledat", key = "-wavOutFolderBrowse-")],
            
            [sg.Checkbox("Přehrát ihned po vygenerování", key = "-playAsap-", default = True)]
        ], pad = 0)]
    ]

    # Pravý dolní blok
    rightDownCol = [
        [sg.Column([
            [sg.Button("GENEROVAT AUDIO", key = "-generate-", size = (30, 2), pad = (0, 40))],

            [sg.Text("Cesta k výslednému wav souboru:")],
            [sg.Input("", key = "-wavOut-", font = inputFont, size = inputWinSize, readonly = True, disabled_readonly_background_color = "#F1F4FC")],
            [sg.Button("Přehrát", key = "-playWavOut-"),
             sg.Button("Pauza", key = "-pauseWavOut-", pad = (40, 4)),
             sg.Button("Stop", key = "-stopWavOut-")]
        ], pad = 0, justification = "c", element_justification = "c")]
    ]

    # Celkové zobrazení bloků
    stsLayout = [
        [sg.Column(menu, justification = "r", pad = 20)],
        [sg.Column(headlines, justification = "c", element_justification = "c")],
        [sg.Column([
            # Levý sloupec
            [sg.Column([
                [sg.Frame("Vstup", [
                    [sg.Column(leftCol, pad = (20, (10, 20)))]
                ], font = frameTitleFont, title_color = textColor, title_location = "n", size = (604, 526), pad = ((0, 6), 0))]
            ]),
            # Pravý sloupec
             sg.Column([
                # Horní
                [sg.Frame("Výstup", [
                    [sg.Column(rightUpCol, pad = (20, (10, 20)))]
                ], font = frameTitleFont, title_color = textColor, title_location = "n", size = (604, 256), pad = ((6, 0), (0, 15)))],
                # Dolní
                [sg.Frame("Generování", [
                    [sg.Column(rightDownCol, pad = (20, (0, 20)), justification = "c", element_justification = "c")]
                ], font = frameTitleFont, title_color = textColor, title_location = "n", size = (604, 256), pad = ((6, 0), 0))]
            ])]
        ], justification = "c", element_justification = "c", pad = (15, (10, 20)))]
    ]

    # Generování okna
    stsWin = sg.Window("REMBLEX - STS", stsLayout, element_justification = "c", resizable = True, finalize = True, )
    stsWin.Maximize()

    stsWin.set_min_size((1290, 735))        #!!!!!!!!!!!!!!!!!!!!!!!!

    # Smyčka
    while True:
        event, values = stsWin.read()

        # Zavření okna
        if event == sg.WIN_CLOSED:
            menuOpt = "finish"
            break

        # Stisknutí možností v menu
        elif event == "-optStt-":       # Přechod na STT
            menuOpt = "stt"
            break
        
        elif event == "-optTts-":       # Přechod na TTS
            menuOpt = "tts"
            break
        
        elif event == "-optSts-":       # Přechod na STS
            for element in updateList:
                if element != "-language-" and element != "-playAsap-":
                    stsWin[element].update("")
                elif element == "-language-":
                    stsWin[element].update(languageList[0])
                elif element == "-playAsap-":
                    stsWin[element].update(True)
    
        # Stisknutí "Diktafon"
        elif event == "-record-":
            stsWin["-voiceWav-"].update(dict(stsWin, elementList, textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize))

        # Vyplňování "-wavOutName-" - omezení možných znaků
        elif event == "-wavOutName-":
            signBlock(stsWin, elementList, values["-wavOutName-"], "-wavOutName-")

        # Stisknutí "Generovat"
        elif event == "-generate-":
            language = values["-language-"]
            refWav = values["-refWav-"]
            voiceWav = values["-voiceWav-"]
            wavOutName = values["-wavOutName-"]
            wavOutFolder = values["-wavOutFolder-"]

            # Kontrola vyplnění oken
            if refWav == "" or voiceWav == "" or wavOutName == "" or wavOutFolder == "":
                errorPopup(stsWin, elementList, "Aby bylo generování možné, musíte zadat referenční audio, audio\nhlasu, název výsledného wav souboru a jeho umístění.")

            # Vše ok => generování
            else:
                try:
                    # Soubor wav již se stejným názvem existuje - až funkční, přesunout dolů pod try
                    if wavOutName + ".wav" in listdir(wavOutFolder):
                        wavOutName = enumerateName(wavOutName, wavOutFolder)

                    wavOutPath = wavOutFolder + "/" + wavOutName + ".wav"

                    # Určení jazyku
                    if language == languageList[0]:
                        language = "en"

                    # Generování audia
                    'tts --model_name tts_models/multilingual/multi-dataset/your_tts  --speaker_wav testASMR.wav --reference_wav  testAudio.wav --language_idx "en"'
                    command = 'tts --model_name tts_models/multilingual/multi-dataset/your_tts --speaker_wav ' + voiceWav + ' --reference_wav ' + refWav + ' --language_idx \"' + language + '\" --out_path \"' + wavOutPath + '\"'
                    system(command)

                    stsWin["-wavOut-"].update(wavOutPath)

                    # Přehrát ihned po vygenerování
                    if values["-playAsap-"] == True:
                        try:
                            sleep(1)
                            soundIsPlaying = True
                            sound = mixer.Sound(wavOutPath)
                            soundChannel.play(sound)
                        except:
                            soundIsPlaying = False
                            errorPopup(stsWin, elementList, "Chyba při přehrávání.")                    
                    
                except:
                    errorPopup(stsWin, elementList, "Chyba při generování.")

                
        # Přehrávání audia          
        # Stisknutí "Přehrát" (jakéhokoliv)
        elif event == "-playWavOut-" or event == "-playRefWav-" or event == "-playVoiceWav-":
            if event == "-playWavOut-":
                wavPath = values["-wavOut-"]
            elif event == "-playRefWav-":
                wavPath = values["-refWav-"]
            else:
                wavPath = values["-voiceWav-"]
            
            if wavPath == "":
                errorPopup(stsWin, elementList, "Zadejte soubor, který chcete přehrát.")
            else:
                try:
                    soundIsPlaying = True
                    audioCorrection(wavPath)

                    sound = mixer.Sound(wavPath)
                    soundChannel.play(sound)
                except:
                    soundIsPlaying = False
                    errorPopup(stsWin, elementList, "Chyba při přehrávání.")
        
        # Stisknutí "Pause" (jakéhokoliv)
        elif event == "-pauseWavOut-" or event == "-pauseRefWav-" or event == "-pauseVoiceWav-":
            if not soundIsPlaying:
                soundIsPlaying = True
                soundChannel.unpause()
            else:
                soundIsPlaying = False
                soundChannel.pause()

        # Stisknutí "Stop" (jakéhokoliv)
        elif event == "-stopWavOut-" or event == "-stopRefWav-" or event == "-stopVoiceWav-":
            soundIsPlaying = False
            soundChannel.stop()

    stsWin.Close()
    return menuOpt
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

    mixer.init()

    #win = dict(neco, necolist, textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize)
    #win = mainMenu(textColor, basicFont)
    #win = stt(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize)
    #win = tts(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize)
    #win = sts(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize)

    #sg.popup("Error", background_color="midnight blue", button_color="midnight blue on white", font=("", 10, "bold"), non_blocking=False, text_color="white", keep_on_top=True, any_key_closes=True)
    #sleep(1)
    #choice = sg.Window('Continue?', [[sg.T('Do you want to continue?')], [sg.Yes(s=10), sg.No(s=10)]], disable_close=True).read(close=True)
    
    # Rozcestník
    win = mainMenu(textColor, basicFont)
    
    while win != "finish":
        if win == "stt":
            sleep(0.25)
            win = stt(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize)
        elif win == "tts":
            sleep(0.25)
            win = tts(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize)
        elif win == "sts":
            sleep(0.25)
            win = sts(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize)
# ------------------------------------------------------------------------------------