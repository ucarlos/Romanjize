#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Created by Ulysses Carlos on 07/23/2020 at 03:43 PM
#
# Romanjize.py
# This program takes music tags with Japanese Characters and converts
# them to Romanji or English, allowing the tags to be displayed on audio
# devices that can only render ASCII or Latin characters only.
#
# Requires:
#     * ffmpeg to convert to different audio formats
#     * translate-shell to convert to romaji
# In Ubuntu, you can install them by doing
#     sudo apt-get install ffmpeg translate-shell
# You may have to use another command on other package managers.
#
# Supported Formats:
# * Flac
# * MP3
# * m4a
# * OGG vorbis
#
# -----------------------------------------------------------------------------

from sys import argv
from os import system
from sys import exit
from googletrans import Translator
from mutagen import File
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4
from pathlib import Path
import subprocess

accepted_formats = ['.flac', ".m4a", '.mp3', 'ogg']
file_format_list = ['mp3', 'm4a']


def help():
    print("USAGE: ./Romanjize.py [OPTION] [OPTION PARAMETERS]")
    print("")
    print("OPTION LIST")
    print("\t-c: Convert the entire directory to a given format and bitrate.")
    print("\t-g: Use Google Translate to translate the tags into English.")
    print("\t-h: Display this message.")
    print("\t-s: Use translate-shell to translate tags into Romanji.")


def retrive_tags(file_path):
    """
    Retrieve the Title, Album, and Artist Name from a file.
    """

    tag_list = {"title": "",
                "album": "",
                "artist": ""}

    if file_path.endswith(".mp3"):
        muta = EasyID3(file_path)
    elif file_path.endswith(".m4a"):
        muta = EasyMP4(file_path)
    else:
        muta = File(file_path)

    for key in tag_list:
        tag_list.update({key: muta[key]})

    return tag_list


def shell_translate_tags(tag_list):
    """
    Translate tags in tag_list into Romanji using translate-shell.
    """
    # Given the key, value, convert
    translated_tag_list = tag_list

    for key in tag_list:
        lang_command = f"trans -identify -no-ansi {str(tag_list[key])} | head -n 1"

        language = subprocess.getoutput(lang_command)

        error_message = """[ERROR] Language not found: auto
        Run '-reference / -R' to see a list of available languages."""
        # Skip any tags that are not japanese or chinese
        if (language == error_message):
            print("The Translator is messing up again.")
            print(f"It's spitting out this:\n{error_message}.\n")
            print("This sometimes happens with translate-shell, so "
                  + "I'll revert the tags.")
            print("Try the -g option if you want to translate "
                  + "the tags in english instead.")
            exit(1)
        elif not (language == "日本語" or language == "简体中文"):
            print("Skipping non-japanese tag...")
            continue

        command = f"trans {str(tag_list[key])} | head -2 | tail -1"

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

    return translated_tag_list


def google_translate_tags(tag_list):
    """
    Translate tags in tag_list to English using google-translate.
    These translations may be wrong.
    """
    translated_tag_list = tag_list

    g_translate = Translator()
    for key in tag_list:
        language = g_translate.detect(str(tag_list[key]))

        # Skip any non-japanese tags if found.
        if language.lang != 'ja':
            continue

        result = g_translate.translate(str(tag_list[key]))
        if not result:
            print("WARNING: I couldn't translate the tag. Skipping.")
        else:
            translated_tag_list.update({key: str(result.text)})

    print(translated_tag_list)
    return translated_tag_list


def apply_tags(file_path, tag_list):
    """
    Using mutagen, apply the tags to the file.
    """

    if file_path.endswith(".mp3"):
        muta = EasyID3(file_path)
    elif file_path.endswith(".m4a"):
        muta = EasyMP4(file_path)
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

    # print(command)
    system(command)


def fix_tags(tag_list):
    """
    Remove any parenthesis or brackets that surround a tag.

    """
    filter_list = ["['", "[\"", "([\'", "([", "('", "(\""]

    # Usually, it is either ([' or [', but if it isn'
    for key in tag_list:
        result = str(tag_list[key])
        length = len(result)

        for i in filter_list:
            check = result.find(i)
            if check != -1:
                result = result[len(i): (length - len(i))]
                tag_list.update({key: result})
                break


def directory_translate(translator):
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

            tag_list = retrive_tags(filename)
            if translator == "google":
                print(f"Translating {file.name} to English.\n")
                translated_tags = google_translate_tags(tag_list)
            else:
                print(f"Translating {file.name} to Romanji.\n")
                translated_tags = shell_translate_tags(tag_list)

            fix_tags(translated_tags)
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

    # Yeah, it's pretty awful
    if len(argv) == 1:
        directory_translate("shell")
    elif len(argv) == 2:
        if argv[1] == "-g":
            directory_translate("google")
        elif argv[1] == "-s":
            directory_translate("shell")
        else:
            help()
    else:
        # Iterate through the argv:
        for i in range(1, len(argv)):
            if argv[i] == "-h":
                help()
                exit(0)
            elif argv[i] == "-g":
                directory_translate("google")
            elif argv[i] == "-s":
                directory_translate("shell")
            elif argv[i] == "-c":
                file_format = argv[i + 1].lower()

                if file_format in file_format_list:
                    bit_rate = int(argv[i + 2])
                    if bit_rate < 0:
                        raise Exception("Cannot have a negative bit rate.")
                    directory_convert(file_format, bit_rate)
                    exit(0)
                else:
                    raise Exception(f"Cannot convert to {file_format}.")
            else:
                raise Exception(f"Invalid Command {argv[i]}")


# Run the Program.
if __name__ == "__main__":
    main()
