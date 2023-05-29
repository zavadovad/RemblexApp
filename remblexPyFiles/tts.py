# IMPORT
# Import - knihovny
import PySimpleGUI as sg

from TTS.api import TTS
from pygame import mixer
from time import sleep
from os import listdir, system

# Import - funkce
from .other import *

# TTS  -------------------------------------------------------------------------------
def tts(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize, savesDir):
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
             sg.Input(savesDir + "audios", key = "-wavOutFolder-", font = inputFont, size = inputWinSize, disabled_readonly_background_color = "#F1F4FC"),
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

    ttsWin.set_min_size((1290, 735))    # Nastavení minimální velikosti okna

    # Smyčka
    while True:
        event, values = ttsWin.read()

        # Zavření okna
        if event == sg.WIN_CLOSED:
            menuOpt = "finish"
            break

        # Stisknutí možností v menu
        # Přechod na STT
        elif event == "-optStt-":
            menuOpt = "stt"
            break

        # Obnovení TTS
        elif event == "-optTts-":
            for element in updateList:
                if element != "-language-" and element != "-playAsap-":
                    ttsWin[element].update("")
                elif element == "-language-":
                    ttsWin[element].update(languageList[0])
                elif element == "-playAsap-":
                    ttsWin[element].update(True)

        # Přechod na STS
        elif event == "-optSts-":
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
            ttsWin["-wavIn-"].update(dict(ttsWin, elementList, textColor, basicFont, inputFont, subTitleFont, frameTitleFont, buttSize, inputWinSize, savesDir))
            
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
                        # Soubor wav již se stejným názvem existuje - až funkční, přesunout dolů pod try
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