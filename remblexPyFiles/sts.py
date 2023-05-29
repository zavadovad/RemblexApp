# IMPORT
# Import - knihovny
import PySimpleGUI as sg

from pygame import mixer
from time import sleep
from os import listdir, system

# Import - funkce
from .other import *

# STS  -------------------------------------------------------------------------------
def sts(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize, savesDir):
    # Lokální proměnné
    languageList = [
        "Anglický - vlastní hlas"
    ]
    elementList = [
        "-optStt-", "-optTts-", "-optSts-",
        "-language-", "-refWav-", "-refWavBrowse-", "-playRefWav-", "-pauseRefWav-", "-stopRefWav-",
        "-recordRefWav-", "-recordVoiceWav-", "-voiceWav-", "-voiceWavBrowse-", "-playVoiceWav-", "-pauseVoiceWav-", "-stopVoiceWav-",
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
             sg.FileBrowse("Vyhledat", key = "-refWavBrowse-", file_types = (("Audio Files", "*.wav"),),),
             sg.Button("Diktafon", key = "-recordRefWav-")],
            [sg.Button("Přehrát", key = "-playRefWav-"),
             sg.Button("Pauza", key = "-pauseRefWav-", pad = (40, 4)),
             sg.Button("Stop", key = "-stopRefWav-")],
        ], pad = (0, (15, 0)))],

        [sg.Column([
            [sg.Text("Vyberte wav soubor s hlasem, který chcete na výstupu nebo svůj hlas nahrajte:")],
            [sg.Input("", key = "-voiceWav-", font = inputFont, size = inputWinSize, disabled_readonly_background_color = "#F1F4FC"),
             sg.FileBrowse("Vyhledat", key = "-voiceWavBrowse-", file_types = (("Audio Files", "*.wav"),),),
             sg.Button("Diktafon", key = "-recordVoiceWav-")],
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

    stsWin.set_min_size((1290, 735))    # Nastavení minimální velikosti okna

    # Smyčka
    while True:
        event, values = stsWin.read()

        # Zavření okna
        if event == sg.WIN_CLOSED:
            menuOpt = "finish"
            break

        # Stisknutí možností v menu
        # Přechod na STT
        elif event == "-optStt-":
            menuOpt = "stt"
            break
        
        # Přechod na TTS
        elif event == "-optTts-":
            menuOpt = "tts"
            break
        
        # Obnovení STS
        elif event == "-optSts-":
            for element in updateList:
                if element != "-language-" and element != "-playAsap-":
                    stsWin[element].update("")
                elif element == "-language-":
                    stsWin[element].update(languageList[0])
                elif element == "-playAsap-":
                    stsWin[element].update(True)
    
        # Stisknutí "Diktafon" u referenčního audia
        elif event == "-recordRefWav-":
            stsWin["-refWav-"].update(dict(stsWin, elementList, textColor, basicFont, inputFont, subTitleFont, frameTitleFont, buttSize, inputWinSize, savesDir))

        # Stisknutí "Diktafon" u audia hlasu
        elif event == "-recordVoiceWav-":
            stsWin["-voiceWav-"].update(dict(stsWin, elementList, textColor, basicFont, inputFont, subTitleFont, frameTitleFont, buttSize, inputWinSize, savesDir))

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
                    # Soubor wav již se stejným názvem existuje
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