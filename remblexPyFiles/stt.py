# IMPORT
# Import
import PySimpleGUI as sg
import whisper as w

from pygame import mixer
from os import listdir

# Import - funkce
from .other import *

# STT  -------------------------------------------------------------------------------
def stt(textColor, basicFont, inputFont, titleFont, subTitleFont, frameTitleFont, buttSize, inputWinSize, savesDir):
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

    # Nahraje model "base" knihovny whisper
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
             sg.Input(savesDir + "transcriptions", key = "-txtOutFolder-", font = inputFont, size = inputWinSize, disabled_readonly_background_color = "#F1F4FC"),
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

    sttWin.set_min_size((1290, 735))    # Nastavení minimální velikosti okna

    # Smyčka
    while True:
        event, values = sttWin.read()

        # Zavření okna
        if event == sg.WIN_CLOSED:
            menuOpt = "finish"
            break

        # Stisknutí možností v menu
        # Obnovení STT
        elif event == "-optStt-":
            for element in updateList:
                sttWin[element].update("")
        
        # Přechod na TTS
        elif event == "-optTts-":
            menuOpt = "tts"
            break

        # Přechod na STS
        elif event == "-optSts-":
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
            wavIn = dict(sttWin, elementList, textColor, basicFont, inputFont, subTitleFont, frameTitleFont, buttSize, inputWinSize, savesDir)

            if wavIn != "":
                sttWin["-wavIn-"].update(wavIn)
                sttWin.write_event_value("-wavIn-", wavIn)

        # Vyplňování "-txtOutName-" - omezení možných znaků
        elif event == "-txtOutName-":
            signBlock(sttWin, elementList, values["-txtOutName-"], "-txtOutName-")

        # Stisknutí "Přepsat audio"
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