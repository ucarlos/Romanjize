# Romanjize

Romanjize is a small program that converts Japanese audio tags into English using google translator and uses translate-shell in order to Romanize Japanese text into a form that can be displayed in Latin characters. It also allows for audio conversion using ffmpeg.


## Dependencies

Romanjize requires ffmpeg and translate-shell to be installed on your system. You can do this in Ubuntu/Debian by doing

```sh
sudo apt install ffmpeg translate-shell
```

The process may be different for different package managers.

On Windows, you must place ffmpeg.exe into the bin folder in order to enable audio conversion. You may find ffmpeg builds [here.](https://ffmpeg.org/download.html) After extracting the ffmpeg build, move the ffmpeg.exe file from the unzipped directory into the bin folder in the Romanjize directory. Since translate-shell is unavailable for Windows, the option will not work.


## Usage

On Linux/UNIX, you can move Romanjize.py into your ~/bin in order to use the program anywhere. Using pip, you can install the module by doing

```sh
pip3 install .
```

in the Romanjize directory. You can then invoke the program using

```sh
python3 -m Romanjize
```

in the directory you want to convert music. Finally, you can simply place the music folder in the Romanjize directory and simply do

```
../Romanjize/Romanjize.py
```

Simply replace '/' with '\\' on Windows.
