import os
import glob
from time import time
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pydub import AudioSegment
import ffmpeg as ffmpeg_lib

def return_dir():
    dir = filedialog.askdirectory()
    a.set(dir)
    diffbox.pack()
    exec_btn.pack()

    global mp3, song
    mp3 = glob.glob("*.mp3")
    song = AudioSegment.from_mp3(mp3[0])

def set_rate(e):
    b.set(f'{rate.get()}')

def export():
    if diffbox.get() != "":

        start = time()

        with open(diffbox.get(), mode="r", encoding="utf8") as ksh:
            metadata = ksh.readlines()
            print(ksh.name)
        # for element in metadata[0:20]:
        #     print(*element.split("=", 1), end="") #"*" unpacks a list

        title = metadata[0][7:].rstrip("\n")
        bpm = float(metadata[7][2:])
        offset = int(metadata[10][2:])
        preview_point = int(metadata[13][3:])
        preview_length = int(metadata[14][8:])
        print(title, bpm, offset, preview_point, preview_length)

        metadata[0] = "title=" + title + " x" + str(b.get()) + "\n"
        metadata[7] = "bpm=" + str(round((bpm * float(b.get())), 3)) + "\n"
        metadata[10] = "o=" + str(round((offset / float(b.get())))) + "\n"
        metadata[13] = "po=" + str(round(preview_point / float(b.get()))) + "\n"
        metadata[14] = "plength=" + str(round(preview_length / float(b.get()))) + "\n"

        if not os.path.isdir("testOutput"):
            os.mkdir("testOutput")

        with open(f"testOutput/{diffbox.get()}", mode = "w") as output:
            output.writelines(metadata)

        change_speed_and_pitch(mp3[0],
                               f"testOutput/{mp3[0]}",
                               speed_factor=float(b.get()),
                               pitch_factor=float(b.get()) if c.get() == 1 else 1.0,
                               sample_rate=song.frame_rate)
        
        os.remove("temp_speed.wav")

        end = time() - start

        messagebox.showinfo("", f"Export Finished in {end}")

def change_speed_and_pitch(input_file, output_file, speed_factor=1.0, pitch_factor=1.0, sample_rate=44100):
    # Change speed
    speed_command = (
        ffmpeg_lib
        .input(input_file)
        .filter('atempo', speed_factor)
        .output('temp_speed.wav')
    )
    speed_command.run(overwrite_output=True)
    
    # Change pitch with the specified sample rate
    pitch_command = (
        ffmpeg_lib
        .input('temp_speed.wav')
        .filter('asetrate', sample_rate * pitch_factor)
        .output(output_file)
    )
    pitch_command.run(overwrite_output=True)

# window name and size
root = tk.Tk()
root.title("RateChangerKSM")
root.geometry(f'{600}x{400}')
root.resizable(False, False)

#variables
a = tk.StringVar()
a.set("")
b = tk.StringVar()
b.set("")
c = tk.IntVar()
kshs = glob.glob("*.ksh")

#input directory elements
input_text = tk.Label(root, text=".ksh file(s) directory to open:")
input_text.place(x=20, y=20)
input_text.pack()
input_dir = tk.Entry(root, textvariable=a).pack()
input_btn = tk.Button(root, text="Open", command=return_dir).pack()

pitch = tk.Checkbutton(root, text="Pitch Shifting", variable=c)
pitch.pack()

diffbox = ttk.Combobox(root, values=[ksh for ksh in kshs])

rate = tk.Scale(root, from_=0.05, to=3, length=295, orient="horizontal", resolution=0.01, command=set_rate)
rate.pack()

exec_btn = tk.Button(root, text="Export", command=export)

root.mainloop()