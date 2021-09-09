#Aplicacion de alarma en python
#Funciones

from datetime import datetime as dt
from pytube import YouTube as YT
from pathlib import Path as p
import win32com.client as win
import scipy.io.wavfile as wav
import moviepy.editor as edit
import sounddevice as sd
import pandas as pd
import shutil as sh 
import stat
import sys
import os
import re

class checker():

    def __init__(self):

        self.current = p.cwd()
        self.today = dt.now()
        self.leap = self.leap_year()
        self.sound_file, self.alarm_file, self.preferences_file = self.check()
        self.check_alarm_csv()
        self.check_sound()
        
    def check(self):

            need = [p("Alarms_sounds"), p("Alarms.csv"), p("Alarm_preferences.txt")]
            exist = []

            for dirs in need:
                
                paths = self.current.joinpath(dirs.name)

                if paths.exists():

                    exist.append(paths)
                    continue

                state = self.finder_os(dirs.name)

                if state != []:

                    exist.append(state)
                    continue

                if dirs is need[0]:

                    paths.mkdir(parents=True, exist_ok=True)
                    
                else:

                    paths.touch(exist_ok=True)
                    os.chmod(paths, stat.S_IRWXU)

                exist.append(paths)
            
            return str(exist[0]), str(exist[1]), str(exist[2])

    def finder_os(self, path):

            paths = []

            for root, dirs, files in os.walk(rf"C:\Users\{os.environ.get('USERNAME')}"):

                    for docs in files:

                        if path.lower() in docs.lower():

                            paths.append(rf"{root}\{docs}")
            
            return paths if len(paths) != 1 else paths[0]

    def check_alarm_csv(self):

        line_0 = "Date, Sound, Name\n"

        with open(self.alarm_file, "r", encoding= "utf-8") as doc:

            lines = doc.readlines()

        if len(lines) > 0 and lines[0] == line_0:

            return True
        
        else:
            
            lines.insert(0, line_0)

            with open(self.alarm_file, "w", encoding = "utf-8") as doc:

                doc.writelines(lines)

    def check_sound(self):

        with open(self.preferences_file, "r", encoding = "utf-8") as doc:

            lenght = doc.readlines()

        path = p(self.sound_file)

        if len(lenght) == 1:

            path_pre = path.joinpath(lenght[0])
            
            if path_pre.exists():

                return True

        yt = YT("https://www.youtube.com/watch?v=DdHZUsSxUco")
        audio = yt.streams.get_audio_only()
        audio.download(output_path = self.sound_file, filename = f"{audio.default_filename}", timeout = 30)
        sound = sounds(self.sound_file)
        sound.convert(f"{self.sound_file}\{audio.default_filename}")
        print("im here")
                    
        with open(self.preferences_file, "w", encoding = "utf-8") as doc:

            doc.write(f"{audio.default_filename[:-4]}.wav")
            print("Here too")

        return True
    
    def leap_year(self):

        year = int(self.today.strftime("%Y"))

        for years in range(4):

            if year%4 == 0:

                return years
            
            else:

                year += 1

class enter():

    def __init__(self, alarm, today, sound, preferences):

        self.alarm = alarm
        self.today = today
        self.sound = sound
        self.preferences = preferences

    def enter_name(self):

        name = input("Introduzca el nombre de la alarma, si no introduce uno"\
                    "\nel nombre por defecto sera la cantidad de alarmas que tenga en lista"\
                    "\n\nNombre: ")

        return name

    def enter_sound(self, pre = False):
        
        if pre == False:

            set_sound = input("Introduzca el nombre de la cancion que desea reproducir\n"\
                        "Si no introduce uno, se utilizara el sonido predeterminado\n\n"
                        "Cancion: ")

            sound = self.pure_sound(set_sound)

            return sound
        
        else:

            set_sound = input("Introduzca el nombre del nuevo sonido\n"\
                                "Cancion: ")
            
            sound = self.pure_sound(set_sound, True)

            return sound

    def enter_dates(self):

        set_date = input("Introduzca la fecha (DD/MM/YY)"\
                        "\n\nFecha: ")
        
        date = self.pure_date(set_date)

        return date

    def enter_hours(self, date):

        set_hour = input("Introduzca la hora (HH/MM/SS)"\
                        "\nLos segundos son opcionales y la hora va desde las '00h' hasta las '23h'"\
                        "\n\nHora: ")

        hour = self.pure_hour(set_hour, date)
            
        return hour
    
    def pure_sound(self, file_name, pre = False):

        file_val = "".join([char if char.isalnum() else "" for char in file_name])

        validate = [file_val.isalnum(), file_val != "", file_val.isspace() != True]

        if all(validate):

            ext = [".mp4", ".mp3", ".wav"]
            path = p(f"{self.sound}\{file_name}.wav") if file_name[-4:] not in ext else p(f"{self.sound}\{file_name}")

            if path.exists():

                return path.name
            
            else:
                
                line_3 = "3. Usar el predeterminado\n" if pre == False else ""
                choice = input("Ha ocurrido un error al encontrar el sonido escogido\n\n"\
                                "1. Volver a buscarlo\n"\
                                "2. Descargarlo\n"+\
                                line_3 +\
                                "Opcion Nro.: ")
                
                if choice == "1":

                    self.enter_sound()
                
                elif choice == "2":

                    sound = sounds(self.sound)
                    sound.download_sound()
                    self.enter_sound()

                elif choice == "3" and line_3 != "":

                    with open(self.preferences, "r") as doc:

                        line = doc.read()
                    
                    return line
                
                else:

                    print("Parametros incorrectos")
                    app().exec()
                    
        else:

            if pre == False:

                with open(self.preferences) as doc:

                    line = doc.read()
                
                return line
            
            else:

                print("No ha introducido un nombre de archivo valido")
                self.enter_sound()

    def pure_date(self, date):

        letter, sym = self.finder(date)
        validate = [letter == False, len(date) <= 10, sym != None]

        if all(validate):
            
            try:

                date_new = self.replacer(" |/|,|:", "-", date, "d")
                today = self.today
                delta = dt.strptime(date_new, "%d-%m-%Y") - today if today.strftime("%d-%m-%Y") != date_new else 1
                difference = delta if type(delta) == type(0) else delta.days

                print(difference, delta)
                if difference >= 0:

                    return date_new
                    
                else:
                        
                    print("Parametros incorrectos, introduzcalos como se le indica")
                    self.enter_dates()
            
            except:

                print("Ha ocurrido un error, por favor ingrese datos reales y siga los parametros")
                self.enter_dates()

        else:

            print("Parametros incorrectos, introduzcalos como se le indica")
            self.enter_dates()

    def pure_hour(self, hr, date):

        letter, sym = self.finder(hr)       
        validate = [letter == False, len(hr) <= 8, sym != None]

        if all(validate):

            try:
                
                hour_new = self.replacer(" |/|,|-", ":", hr, "h")
                delta_date = dt.strptime(date, "%d-%m-%Y") - self.today

                if int(delta_date.days) > 0:

                    return hour_new
                    
                else:
                    
                    delta_hour = dt.strptime(hour_new, "%H:%M:%S") - self.today
                    current_hour = list(map(lambda x: int(x), self.today.strftime("%H:%M:%S").split(":")))
                    val_hour = list(map(lambda x: int(x), hour_new.split(":")))
                    validate = [86400 > delta_hour.seconds > 0,
                                current_hour[0] <= val_hour[0],
                                current_hour[1] < val_hour[1] if current_hour[0] == val_hour[0] else True,
                                current_hour[2] < val_hour[2] if current_hour[1] == val_hour[1] else True]

                    if all(validate):

                        return hour_new

                    else:

                        print("Parametros incorrectos, introduzcalos como se le indica")
                        self.enter_hours(date)
            
            except:

                print("Ha ocurrido un error, por favor ingrese datos reales y siga los parametros")
                self.enter_hours(date)

        else:

            print("Parametros incorrectos, introduzcalos como se le indica")
            self.enter_hours(date)

    def finder(self, parameter):

        find_letter = re.search("[a-zA-z]", parameter)
        letter = False if find_letter == None else True
        find_sym = re.search(" |/|,|:|-", parameter)

        return letter, find_sym
    
    def replacer(self, to_replace, replace, string, type_time):

        subs = re.sub(to_replace, replace, string) if (len(re.findall(replace, string)) != 2) else string
        ind = re.split(replace, subs)
        ind = self.fill(ind, type_time)
        string_new = "-".join(ind) if type_time == "d" else ":".join(ind)

        return string_new
    
    def fill(self, lis, typ):

        end = []

        if typ == "d":

            for chars in lis:

                if chars != lis[2]:

                    end.append("0" + chars if len(chars) == 1 else chars)
                
                else:

                    end.append("20" + chars[-2:] if len(chars) > 2 else "20" + chars)
        
        else:

            end = ["0" + chars if len(chars)<2 else chars for chars in lis]
            
            if len(end) < 3:

                end.append("00")
            
        return end

class handle():

    def __init__(self, alarm, sound, preferences):
  
        self.alarm = alarm
        self.sound = sound
        self.preferences = preferences
    
    def show(self):

        with open(self.alarm, "r") as doc:

            file_lines = doc.readlines()
        
        print("Tus alarmas configuradas son:\n")
        
        for lines in file_lines:

            line = lines.split(",")
            print(f"{file_lines.index(lines) + 1}.{line[3]} a las {line[0]} {line[1]} con {line[2]}\n")

    def add_alarm(self, name, date, hour, sound):

        the_date = dt.strptime(f"{date} {hour}", "%d-%m-%Y %H:%M:%S")
        new_str = f"{the_date}, {sound}, {name}\n"
        to_del = p(self.alarm)

        with open(self.alarm, "a") as doc:

            doc.write(new_str)

        file_sorted= pd.read_csv(self.alarm)
        file_sorted.sort_values(by = ["Date"], ignore_index =  True, inplace = True)
        to_del.unlink()
        file_sorted.to_csv(self.alarm)
        
        with open(self.alarm, "r", encoding = "utf-8") as doc:

            file_lines = doc.readlines()
        
        with open(self.alarm, "w", encoding = "utf-8") as doc:

            file_org = [",".join(line.split(",")[1:]) for line in file_lines]
            doc.writelines(file_org)

    def erase_alarm(self, change = 1):

        lines = change - 1 if change > 1 else 1

        with open(self.alarm, "r") as docs:

            files = docs.readlines()

        with open(self.alarm, "w") as docs:

            files.pop(lines)
            docs.writelines(files)
    
    def change_preferences(self, new_sound):

        with open(self.preferences, "w") as doc:

            doc.write(new_sound)

    def move_sound(self, path_out):

        ext = [".mp4", ".mp3", ".wav"]
        path_in = self.sound
        paths = checker.finder_os(path_out)

        if len(paths) < 1:

            print("Lo lamentamos, no tiene un archivo con el nombre que nos dio")

            return False

        else:

            ex_files = []

            for files in paths:

                if any([suffix in files for suffix in ext]):
                    
                    print(f"{len(ex_files)+1 if len(ex_files) > 0 else 1}. {files}")
                    ex_files.append(files)
                
                else:

                    continue
            
            if len(ex_files) > 0:

                file_index = input("Introduzca el numero del archivo correcto: ") if len(ex_files) > 1 else "0"
                sh.move(paths[paths.index(ex_files[int(file_index)])], path_in)
                print("Se ha guardado correctamente")

                return True

            else:

                print("Lo lamentamos, no tiene un archivo con el nombre que nos dio")
                
                return False

class sounds():

    def __init__(self, sound):
        
        self.sound = sound

    def play_sound(self, song):

        path = f"{self.sound}\{song}"
        sr, fr = wav.read(path)
        sd.play(fr, sr)
        sd.sleep(30000)
        sd.stop()

    def download_sound(self):

        link = input("Ingrese el URL (Unicamente se puede descargar de youtube)\n\n"\
                    "URL: ")

        if "youtube.com" in link or "youtu.be" in link:
            
            yt = YT(link)
            audio = yt.streams.get_audio_only()
            print(f"\nTitulo: {yt.title}\n"\
                    f"Duracion: {yt.length} (Tenga en cuenta que solo se guardaran los primeros 30s)\n"\
                    f"Autor: {yt.author}\n")
            action = input("\n¿Desea guardar el archivo con el nombre del Titulo?\n\n"\
                            "[y/n]: ")
            
            if action == "y":

                print(f"\nNombre de archivo: {audio.default_filename[:-4]}.wav\n"\
                        f"Tamaño: {audio.filesize}\n")
                
                action = input("Confirma la descarga [y/n]: ")

                if action == "y":

                    audio.download(output_path = self.sound, filename = f"{audio.default_filename}", timeout = 30)
                    self.convert(f"{self.sound}\{audio.default_filename}")
                    print("\nDescarga realizada con exito")

                else:

                    print("\n\nDescarga abortada, no se realizara")

            elif action == "n":

                new_name = input("\nNuevo nombre: ")
                print(f"\nNombre de archivo: {new_name}.wav\n"\
                        f"Tamaño: {audio.filesize}")
                
                action = input("\nConfirma la descarga [y/n]: ")

                if action == "y":

                    audio.download(output_path = self.sound, filename = f"{new_name}.mp4", timeout = 30)
                    self.convert(f"{self.sound}\{new_name}.mp4")
                    print(f"\nArchivo descargado con exito")

                else:

                    print("\n\nDescarga abortada, no se realizara")

            else:

                print("\n\nParametros incorrectos, ingreselos como se le pide")
                self.download_sound()

        else:

            print("\n\nParametros incorrectos, ingreselos como se le pide")
            self.download_sound()

    def convert(self, path):
        
        path_mp4 = p(path)
        video = edit.AudioFileClip(path)
        video.write_audiofile(f"{path[:-4]}.wav")
        path_mp4.unlink()

class Alarm():

    def __init__(self, current, today, alarm, sound, preferences):

        self.current = current
        self.today = today
        self.alarm = alarm
        self.sound = sound
        self.preferences  = preferences

    def alarm_now(self):

        with open(self.alarm_file, "r") as doc:

            first_line = doc.readline(0)
            first_line.split(",")
        
        first_alarm = " ".join([first_line[0], first_line[1][:-3]]) if len(first_line) > 1 else ""
        
        if self.today.strftime("%d-%m-%Y %H:%M") == first_alarm:

            sound = sounds(self.sound)
            sound.play_sound(first_line[3])
            hand = handle(self.alarm, self.sound, self.preferences)
            hand.erase_alarm()

            sys.exit()

    def set_alarm(self, date, hour, name):

        try:

            task = win.Dispatch("Schedule.Service")
            task.Connect()
            root = task.GetFolder("\\")
            newtask = task.NewTask(0)
            time = dt.strptime(f"{date} {hour}", "%d-%m-%Y %H:%M:%S")
            task_trigger = 1
            trigger = newtask.Triggers.Create(task_trigger)
            trigger.StartBoundary = time.isoformat()
            task_action = 0
            action = newtask.Actions.Create(task_action)
            action.ID = "DO NOTHING"
            action.Path = rf"{self.current}\Alarm.py"
            action.Arguments = rf"{self.current}\alarm_func.py"
            newtask.RegistrationInfo.Description = f"Alarm at {date} {hour}"
            task_creat = 6
            task_log = 0
            root.RegisterTaskDefinition(name, newtask, task_creat, "", "", task_log)

        except:

            print("Ha ocurrido un error al registrar la alarma,\n"\
                "asegurese de estar trabajando en un sistema Windows")
            app.exec()

class app():

    def __init__(self):
        
        actual = checker()
        self.sounds = sounds(actual.sound_file)
        self.enter = enter(actual.alarm_file, actual.today, actual.sound_file, actual.preferences_file)
        self.alarm = Alarm(actual.current, actual.today, actual.alarm_file, actual.sound_file, actual.preferences_file)
        self.hand = handle(actual.alarm_file, actual.sound_file, actual.preferences_file)
        self.today = actual.today
        self.leap = actual.leap
        self.now()

    def now(self):

        self.alarm.alarm_now()
    
    def exec(self, route = "0"):

        leap_line = f"Next Leap Year: {self.leap}" if self.today.strftime("%Y") != self.leap else f"Current Leap Year: {self.leap}"
        print(f"\nToday: {self.today.strftime('%d-%m-%Y %H:%M:S')}\n"\
                f"{leap_line}\n\n")
        choice = input("Bienvenido a tu alarma personalizada, ¿Que deseas hacer?\n\n"\
                        "1. Ver tus alarmas\n"\
                        "2. Manejar tus alarmas\n"\
                        "3. Cambiar el sonido predeterminado\n"
                        "4. Agregar un nuevo sonido para tus alarmas\n"\
                        "5. Salir\n\n"\
                        "Opcion Nro.: ") if route == "0" else route

        if choice == "1":

            self.hand.show()
            self.exec()

        elif choice == "2":

            action = input("\nQue desea hacer con sus alarmas?\n\n"\
                            "1. Agregar una nueva\n"
                            "2. Eliminar una alarma\n"\
                            "3. Volver\n\n"\
                            "Opcion: ")
            
            if action == "1":

                date = self.enter.enter_dates()
                hour = self.enter.enter_hours(date)
                sound = self.enter.enter_sound()
                name = self.enter.enter_name()
                self.alarm.set_alarm(date, hour, name)
                self.hand.add_alarm(name, date, hour, sound)
                print("\nAlarma configurada correctamente\n\n")
                self.exec()
            
            elif action == "2":
                
                self.hand.show()
                line = input("Seleccione la alarma que desea eliminar\n"\
                            "Alarma Nro.: ")
                self.hand.erase_alarm(line)
                print("\nAlarma eliminada\n\n")
                self.exec()
            
            elif action == "3":

                self.exec()
            
            else:

                print("Parametros incorrectos, introduzcalos correctamente")
                self.exec(2)
        
        elif choice == "3":

            sound = self.enter.enter_sound(True)
            self.hand.change_preferences(sound)
            print("Se ha cambiado correctamente las preferencias")
            self.exec()
        
        elif choice == "4":

            action = input("\nQue desea hacer?\n"\
                            "1. Agregar a la aplicacion una cancion de mis archivos\n"\
                            "2. Descargar una de Youtube\n"
                            "3. Volver\n\n"\
                            "Opcion: ")
            
            if action == "1":

                sound = self.enter.enter_sound()
                self.hand.move_sound(sound)
                print("Sonido agregado a la carpeta correctamente")
                self.exec()
            
            elif action == "2":

                self.sounds.download_sound()
                self.exec()
            
            elif action == "3":

                self.exec()
    
        elif choice == "5":

            sys.exit()