# -*- mode: Python ; coding: utf-8 -*-
# Copyright © 2020 Jonathan Dayley, <jonathandayley@gmail.com>
# with acknowledgement to Wiktionary, Forvo, and mdbg.net PRUEBA

# %% Import packages
import sys
import os
from aqt import gui_hooks
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
import logging
import pprint
import tempfile
import pathlib
import requests
import re
from bs4 import BeautifulSoup
import shutil

# %% Set up logging
# logging.basicConfig(
#	filename = '/Users/Cadenza/Desktop/LOG.log', # Change to target log destination
#	filemode = 'w',
#	format = '%(message)s',
#	level = logging.DEBUG
# )


def log(target, pp=True, utf8=False, mbox=False):
    target = str(target)
    if pp:
        target = pprint.pformat(target)
    if utf8:
        target = target.encode('utf-8')
    logging.debug(target)
    if mbox:
        showInfo(target)


# %% Set up config file
config = mw.addonManager.getConfig(__name__)

# %% Set constants
t_type = config["Chinese vocab note type"]
f_char = config["Chinese characters field"]
f_pinyin = config["Chinese pinyin field"]
f_anim = config["Chinese animations field"]
f_sound = config["Chinese sound field"]
forvoKey = config["Forvo API key"]

# %% Set up temporary file
os.chdir(tempfile.gettempdir())
destination = "chinesedownloads"
destination = os.getcwd() + "/" + destination

# %% Get file download routine


def download(url):
    file_name = re.findall("[^\/]*$", url)[0]
    file_path = destination + "/" + file_name
    data = requests.get(url)
    with open(file_path, 'wb') as f:
        f.write(data.content)
    return file_path

# %% Get data pulling routine


def getFieldValue(fieldName, note):
    fnames = note._model["flds"]
    for f in range(len(fnames)):
        if fnames[f]["name"] == fieldName:
            fIndex = f
            break
    try:
        value = note.fields[fIndex]
        value = re.sub('<.*?>', '', value)
        return value
    except:
        return "String of non-empty length to make functions stop"

# %% Get empty field checking routine


def isEmpty(fieldName, note):
    testlen = len(getFieldValue(fieldName, note))
    if testlen:
        return False
    else:
        return True

# %% Get data insertion routine


def toNote(data, fieldName, note):
    names = mw.col.models.fieldNames(note.model())
    for i in range(len(names)):
        if names[i] == fieldName:
            note.fields[i] = data
            break
    return note

# %% Get character function


def insert_char(note):
    if isEmpty(f_char, note):
        wiktBase = "https://en.wiktionary.org"
        wiktStub = "/wiki/"
        try:
            pinyinURL = wiktBase + wiktStub + getFieldValue(f_pinyin, note)
            pinyinHTML = requests.get(pinyinURL).content
            pinyinHTML = BeautifulSoup(pinyinHTML, features="html.parser")
            charURL = wiktBase + \
                pinyinHTML.select("a[href*=\"#Chinese\"]")[0].get("href")
            charHTML = requests.get(charURL).content
            charHTML = BeautifulSoup(charHTML, features="html.parser")
        except:
            return note
        try:
            heading = charHTML.select("h1")[0].text
        except:
            heading = charHTML.select("h1 > span")[0].text
        return toNote(heading, f_char, note)
    else:
        return note

# %% Get pinyin function


def insert_pinyin(note):
    if isEmpty(f_pinyin, note):
        wiktBase = "https://en.wiktionary.org"
        wiktStub = "/wiki/"
        wiktURL = wiktBase + wiktStub + getFieldValue(f_char, note)
        wiktHTML = requests.get(wiktURL).content
        wiktHTML = BeautifulSoup(wiktHTML, features="html.parser")
        atags = wiktHTML.select("a")
        for i in range(len(atags)):
            try:
                found = len(re.findall("Pinyin", atags[i].get("href")))
            except:
                found = 0
            if found:
                final = atags[i+1].text
                break
        try:
            return toNote(final, f_pinyin, note)
        except:
            return note
    else:
        return note

# %% Get animated gif function


def insert_anim(note):
    if isEmpty(f_anim, note) and not isEmpty(f_char, note):
        anim_URL = "https://www.mdbg.net/chinese/rsc/img/stroke_anim/"
        anim_URL_post = ".gif"
        HTMLclass = "chinese_char"
        source = getFieldValue(f_char, note)
        chars = list(source)
        payload = ""
        for i in chars:
            if ord(i) > 19968:
                anim_name = str(ord(i)) + anim_URL_post
                anim_link = anim_URL + anim_name
                anim_file = download(anim_link)
                mw.col.media.addFile(anim_file)
                HTMLtag = "<img class=\"" + HTMLclass + "\" src=\"" + anim_name + "\" />"
                payload = payload + HTMLtag
        return toNote(payload, f_anim, note)
    else:
        return note

# %% Get sound function


def insert_sound(note):
    if isEmpty(f_sound, note) and not isEmpty(f_char, note) and len(forvoKey) > 0:
        chars = getFieldValue(f_char, note)
        forvoURL = "https://apifree.forvo.com/action/word-pronunciations/format/xml/word/" + \
            chars + "/language/zh/order/rate-desc/limit/1/key/" + forvoKey + "/"
        forvoHTML = requests.get(
            forvoURL,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Safari/605.1.15'}
        ).content
        forvoHTML = BeautifulSoup(forvoHTML, features="html.parser")
        try:
            mp3URL = forvoHTML.select("pathmp3")[0].text
        except:
            try:
                forvoHTML.select("error")[0].text
                message = "It looks like your Forvo key is either expired or invalid. To fix the issue, get a new key at https://api.forvo.com/, enter it into this add-on's configuration field, and restart Anki."
                showInfo(message)
                return note
            except:
                return note
        mp3URL = mp3URL + ".mp3"
        mp3file = download(mp3URL)
        mp3title = re.findall("(?<=\/)[^\/]*$", mp3URL)[0][-50:]
        mp3fileNew = re.findall("^.*\/", mp3file)[0] + mp3title
        os.rename(mp3file, mp3fileNew)
        mp3file = mp3fileNew
        final = "[sound:" + mp3title + "]"
        mw.col.media.addFile(mp3file)
        return toNote(final, f_sound, note)
    else:
        return note

# %% Get master function


def chineseGetter(changed, note, current_field_idx):
    if(note._model["name"] == t_type):
        pathlib.Path(destination).mkdir(parents=True, exist_ok=True)
        oldfields = str(note.fields)
        note = insert_char(note)
        note = insert_pinyin(note)
        note = insert_anim(note)
        note = insert_sound(note)
        newfields = str(note.fields)
        compare = oldfields != newfields
        if(compare):
            note.flush()
            mw.col.save()
            shutil.rmtree(destination, ignore_errors=True)
            try:
                mw.reset()
            except:
                pass


# %% Go to town
gui_hooks.editor_did_unfocus_field.append(chineseGetter)
