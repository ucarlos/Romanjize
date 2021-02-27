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
# You may have to use another command on other package managers on other Linux
# or UNIX machines You may need to compile ffmpeg if your package manager
# does not provide ffmpeg.
#
# On Windows, you must have ffmpeg.exe in \bin in order to convert music.
# Since translate-shell relies on bash, it is currently disabled for Windows.
#
# Supported Formats:
# * Flac
# * MP3
# * m4a
# * OGG Vorbis
#
# -----------------------------------------------------------------------------

from sys import argv
from os import system
from sys import exit
from google_trans_new import google_translator
from mutagen import File
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4
from pathlib import Path
import subprocess
import platform
import re

accepted_formats = ['.flac', ".m4a", '.mp3', 'ogg']
file_format_list = ['mp3', 'm4a']
bin_path = Path.cwd().parent / "bin"


# ------------------------------------------------------------------------------
# Terminal Color class for debugging
class term_color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ------------------------------------------------------------------------------


DEBUG_MODE = False


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

    if DEBUG_MODE:
        print(f"{term_color.BOLD}{term_color.OKBLUE}Before Converting: {str(translated_tag_list)}{term_color.ENDC}")

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

    if DEBUG_MODE:
        print(f"{term_color.BOLD}{term_color.OKBLUE}After Converting: {str(translated_tag_list)}{term_color.ENDC}")

    return translated_tag_list


def google_translate_tags(tag_list):
    """
    Translate tags in tag_list to English using google-translate.
    These translations may be wrong.
    """
    translated_tag_list = tag_list

    if DEBUG_MODE:
        print(f"{term_color.BOLD}{term_color.OKBLUE}Before Converting: {str(translated_tag_list)}{term_color.ENDC}")
    g_translate = google_translator()
    for key in tag_list:
        # First, try to see if the tag can be displayed with latin characters only.
        # if so, just skip it
        can_skip = True
        try:
            string = str(tag_list[key])
            string.encode("latin1")
        except UnicodeEncodeError:
            can_skip = False

        # Next, detect the language.
        language = g_translate.detect(str(tag_list[key]))[0]
        # Skip any non-japanese tags if found.
        if not (language == 'ja' or language == "zh-CN") or can_skip:
            continue

        # result = g_translate.translate(str(tag_list[key]))
        # g_translate = google_translator()
        result = g_translate.translate(str(tag_list[key]))

        if not result:
            print("WARNING: I couldn't translate the tag. Skipping.")
        else:
            # translated_tag_list.update({key: str(result.text)})
            translated_tag_list.update({key: str(result)})

    if DEBUG_MODE:
        print(f"{term_color.BOLD}{term_color.OKBLUE}After Converting: {str(translated_tag_list)}{term_color.ENDC}")
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

    if (platform.system() == "Windows"):
        ffmpeg = str(bin_path / "ffmpeg.exe")
        command = f"{ffmpeg} -i \"{file_path}\" "
    else:
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
    Remove any parenthesis, brackets, or any strange
    characters that surround a tag.

    """

    # The regex pattern should extract any tag enclosed in '"[]() or any weird
    # punctuation. However, if the tag contains punctuation as a result of its
    # name, then that will be cut off from the tag.
    regex_pattern = r"[\w](\w|\s|([!\`\~\"\#$%&\'()*+,\-\.\/:;<=>\?@\[\\\]^_‘\{\|\}\~]))*([^ \"\#$%&\'\(\)*+,\-\.\/:;<=>@\[\\\]^_‘\{\|\}\~])"

    # print(f"full tag list: {str(tag_list)}")
    for key in tag_list:
        result = str(tag_list[key])

        # First remove the brackets surrounding the key.
        # first_pass = re.sub(r"\[[\'\"]+", "", result)
        # second_pass = re.sub(r"[\'\"]+\](\s+)?$", "", first_pass)
        first_pass = re.sub(r"(^\[[\'\"]+)?([\'\"]+\](\s+)?$)?", "", result)

        # Otherwise use the large pattern
        if DEBUG_MODE:
            # result = result[1:len(result) - 1]
            print(f"Checking \"{first_pass}\"")
        check = re.search(regex_pattern, first_pass)
        if check:
            if DEBUG_MODE:
                print(f"{first_pass} matches the full regex and is now \"{check[0]}\"")

            # Simply retrieve the matched string:
            # result = check[0]
            # Now update key:
            tag_list.update({key: check[0]})
        else:
            print(f"Warning: \"{result}\" did not match the regular expression."
                  " Skipping.")
            # Still update the result if the first_pass is different
            if first_pass != result:
                tag_list.update({key: first_pass})


def directory_translate(translator):
    if (translator == "shell" and platform.system() == "Windows"):
        raise Exception("This option is currently unavailable on "
                        "Windows. Please use the \"-g\" option "
                        " instead.")

    current_path = Path.cwd()
    pathlist = current_path.glob("*")
    for file in pathlist:
        filename = file.as_posix()

        if file.suffix in accepted_formats:
            tag_list = retrive_tags(filename)
            if translator == "google":
                if DEBUG_MODE:
                    print("-" * 80)
                print(f"Translating {file.name} to English.\n")

                translated_tags = google_translate_tags(tag_list)
            else:
                print(f"Converting {file.name} into Romanji.\n")
                translated_tags = shell_translate_tags(tag_list)

            fix_tags(translated_tags)
            if DEBUG_MODE:
                print(f"{term_color.BOLD}{term_color.OKGREEN}Final Tags: {str(translated_tags)}{term_color.ENDC}")
            else:
                apply_tags(filename, translated_tags)
        else:
            print(f"{file.name} is not a accepted format. Skipping.")
            continue


def directory_convert(format, bitrate):
    current_path = Path.cwd()

    pathlist = current_path.glob("*")
    for file in pathlist:
        filename = file.as_posix()

        if file.suffix in accepted_formats:
            convert_file(filename, format, bitrate)
        else:
            print(f"{file.name} is not a accepted format. Skipping.")
            continue


def main():
    global DEBUG_MODE
    if len(argv) == 1:
        directory_translate("shell")
    elif len(argv) == 2:
        if argv[1] == "-d":
            # Enable Debug Mode
            DEBUG_MODE = True

        if argv[1] == "-g":
            directory_translate("google")
        elif argv[1] == "-s":
            directory_translate("shell")
        else:
            help()
    else:
        # Iterate through the argv:
        for i in range(1, len(argv)):
            if argv[i] == '-d':
                DEBUG_MODE = True
            elif argv[i] == "-h":
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
