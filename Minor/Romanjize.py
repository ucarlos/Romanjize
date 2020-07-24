#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Created by Ulysses Carlos on 07/23/2020 at 03:43 PM
#
# Romanjize.py
# This program takes flac or mp3 tags with Japanese Characters and converts
# them to Romanji, allowing the tags to be displayed in Latin Characters.
# It's better than to do so by hand in most cases.
#
# Requires:
#     * ffmpeg to convert to different formats
#     * translate-shell to convert to romaji
# In Ubuntu, you can install them by doing
#     sudo apt-get install ffmpeg translate-shell
# You may have to use another command on other package managers.
#
# Supported Formats:
# * Flac
# * MP3
# * Vorbis
#
# TO-DO:
# * m4a support
# -----------------------------------------------------------------------------

from sys import argv
from os import system
from sys import exit
from mutagen import File
from mutagen.easyid3 import EasyID3
from mutagen.aac import AAC
from pathlib import Path
import subprocess

accepted_formats = ['.flac', '.mp3', 'ogg']
file_format_list = ['mp3', 'm4a', 'ogg']


def help():
    print("USAGE: ./Romanjize.py [OPTION] [OPTION PARAMETERS]")
    print("")
    print("OPTION LIST")
    print("\t-c: Convert the directory to a given format and bitrate.")
    print("\t-h: Display this message.")


def retrive_tags(file_path):
    """
    Retrieve the Title, Album, and Artist Name from a file.
    """
    # print(file_path)

    tag_list = {"title": "",
                "album": "",
                "artist": ""}

    if file_path.endswith(".mp3"):
        muta = EasyID3(file_path)
    elif file_path.endswith(".m4a"):
        muta = AAC(file_path)
    else:
        muta = File(file_path)

    for key in tag_list:
        tag_list.update({key: muta[key]})

    # Now print tag_list:
    # print(tag_list)
    return tag_list


def translate_tags(tag_list):
    """
    Translate tags in tag_list into Romanji.
    """
    # Given the key, value, convert
    translated_tag_list = tag_list

    for key in tag_list:
        command = "trans -show-dictionary n -show-languages n " \
            + "-show-translation n -show-alternatives n " \
            + "-show-prompt-message n -show-original-dictionary n \"" \
            + str(tag_list[key]) + "\""

        # print(command)
        result = subprocess.getoutput(command)
        # If result contains more than one sentence, set the tag
        # to the last sentence.
        check = result.rfind('\n')
        tag = result[check + 1:] if check != -1 else result
        if not tag:
            print("WARNING: I wasn't able to translate the tag for '"
                  + key + "' due to the translator not working at the moment."
                  + " I'll keep the old tag.")
            continue
        else:
            translated_tag_list.update({key: tag})

    # print(translated_tag_list)
    return translated_tag_list


def apply_tags(file_path, tag_list):
    """
    Using mutagen, apply the tags to the file.
    """

    if file_path.endswith(".mp3"):
        muta = EasyID3(file_path)
    elif file_path.endswith(".m4a"):
        muta = AAC(file_path)
    else:
        muta = File(file_path)

    for key in tag_list:
        muta.update({key: tag_list[key]})

    muta.save()


def convert_file(file_path, new_format, bitrate):
    """
    Convert an audio file into a new format with a specified format
    using ffmpeg.
    """

    command = f"ffmpeg -i \"{file_path}\" "

    if new_format == "mp3":
        command += f"-codec:a libmp3lame -b:a {bitrate}k "
    elif new_format == "m4a":
        command += f"-c:a aac -b:a {bitrate}k "
    elif new_format == "ogg":
        command += f"-c:a libvorbis -b:a {bitrate}k "
    else:
        raise Exception("Cannot convert to " + new_format + " format.")


    # Create the appropriate new file name:
    index = file_path.rfind(".")
    if index == -1:
        raise Exception("File path " + file_path + "is invalid.")

    new_name = file_path[:index + 1]
    new_name += new_format
    command = command + "\"" + new_name + "\""
    # Now make the system call.
    print(command)
    system(command)


def fix_tags(tag_list):
    """
    Remove any parenthesis or brackets that surround a tag.

    """

    # Usually, it is either ([' or [', but if it isn'
    for key in tag_list:
        result = tag_list[key]
        check_1 = result.find("(['")
        length = len(result)
        if check_1 != -1:
            result = result[3: length - 3]
            tag_list.update({key: result})

        check_2 = result.find("['")
        if check_2 != -1:
            result = result[2: length - 1]
            tag_list.update({key: result})


def directory_translate():
    current_path = Path.cwd()

    pathlist = current_path.glob("*")
    for file in pathlist:
        filename = file.as_posix()
        is_valid_file = False
        # Check if filename ends in an accepted format.
        for i in range(0, len(accepted_formats)):
            if filename.endswith(accepted_formats[i]):
                is_valid_file = True
                break
        
        if is_valid_file:
            print(f"Translating {file.name}\n")
            tag_list = retrive_tags(filename)
            translated_tags = translate_tags(tag_list)
            fix_tags(tag_list)
            # print(translated_tags)
            apply_tags(filename, translated_tags)
        else:
            print(f"{file.name} is not a accepted format. Skipping.")
            continue


def directory_convert(format, bitrate):
    current_path = Path.cwd()

    pathlist = current_path.glob("*")
    for file in pathlist:
        filename = file.as_posix()
        is_valid_file = False
        # Check if filename ends in an accepted format.
        for i in range(0, len(accepted_formats)):
            if filename.endswith(accepted_formats[i]):
                is_valid_file = True
                break

        if is_valid_file:
            convert_file(filename, format, bitrate)
        else:
            print(f"{file.name} is not a accepted format. Skipping.")
            continue


def main():
    # print(str(argv))
    if len(argv) == 1:
        directory_translate()
    elif argv[1] == "-c":

        file_format = argv[2].lower()

        if file_format in file_format_list:
            # Convert argv[3] into int and then pass the program
            bit_rate = int(argv[3])
            directory_translate()
            directory_convert(file_format, bit_rate)
        else:
            print(f"Error: Cannot convert to file format {file_format}.")
            exit(1)
    else:
        # Print out the help screen.
        help()


# Run the Program.
if __name__ == "__main__":
    main()
