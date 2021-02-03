# requires: pydub numpy requests
"""
Зависимости

.terminal pip3 install pydub numpy requests; apt-get install ffmpeg -y

!Не работает на Heroku! 
Оригинал: @dekftgmodules
"""
from pydub import AudioSegment
from pydub import effects
from telethon import types
from .. import loader, utils
import io
import os
import requests
import numpy as np
import math
@loader.tds
class AudioEditorMod(loader.Module):
    "Переиздание легендарного модуля"
    strings = {"name": "AudioEditor"}
    @loader.owner
    async def basscmd(self, m):
        """.bass [уровень bass'а 2-100 (Default 2)] <reply to audio>
        BassBoost"""
        pref = "BassBoost"
        reply = await m.get_reply_message()
        audio = await get_audio(m, reply, pref)
        if not audio: return
        args = utils.get_args_raw(m)
        if not args: lvl = 2
        else:
            if args.isdigit() and (1<int(args)<101): lvl = int(args)
            else:
                await m.edit(f"[{pref}] Укажи уровень от 2 до 100...")
                return
        await m.edit(f"[{pref}] Работаю...")
        sample_track = list(audio[0].get_array_of_samples())
        est_mean = np.mean(sample_track)
        est_std = 3 * np.std(sample_track) / (math.sqrt(2))
        bass_factor = int(round((est_std - est_mean) * 0.005))
        attenuate_db = 0
        filtered = audio[0].low_pass_filter(bass_factor)
        out = (audio[0] - attenuate_db).overlay(filtered + lvl)
        await go_out(m, reply, audio, out, pref, f"{pref} {lvl}lvl")
    async def echoscmd(self, m):
        """.echos <reply to audio>
            Эхо эффект"""
        pref = "Эхо эффект"
        reply = await m.get_reply_message()
        audio = await get_audio(m, reply, pref)
        if not audio: return
        await m.edit(f"[{pref}] Работаю...")
        out = AudioSegment.empty()
        n = 200
        none = io.BytesIO(requests.get("https://raw.githubusercontent.com/Daniel3k00/files-for-modules/master/none.mp3").content)
        out += audio[0] + AudioSegment.from_file(none)
        for i in range(5):
        	echo = audio[0] - 10
        	out = out.overlay(audio[0], n)
        	n += 200
        await go_out(m, reply, audio, out, pref, pref)
    async def volupcmd(self, m):
        """.volup <reply to audio>
            Увеличить громкость на 10dB"""
        pref = "+10dB"
        reply = await m.get_reply_message()
        audio = await get_audio(m, reply, pref)
        if not audio: return
        await m.edit(f"[{pref}] Работаю...")
        out = audio[0] + 10
        await go_out(m, reply, audio, out, pref, pref)
    async def voldwcmd(self, m):
        """.voldw <reply to audio>
            Уменьшить громкость на 10dB"""
        pref = "-10dB"
        reply = await m.get_reply_message()
        audio = await get_audio(m, reply, pref)
        if not audio: return
        await m.edit(f"[{pref}] Работаю...")
        out = audio[0] - 10
        await go_out(m, reply, audio, out, pref, pref)
    async def revscmd(self, m):
        """.revs <reply to audio>
            Развернуть аудио"""
        pref = "Reverse"
        reply = await m.get_reply_message()
        audio = await get_audio(m, reply, pref)
        if not audio: return
        await m.edit(f"[{pref}] Работаю...")
        out = audio[0].reverse()
        await go_out(m, reply, audio, out, pref, pref)
    async def repscmd(self, m):
        """.reps <reply to audio>
            Повторить аудио 2 раза подряд"""
        pref = "Повтор"
        reply = await m.get_reply_message()
        audio = await get_audio(m, reply, pref)
        if not audio: return
        await m.edit(f"[{pref}] Работаю...")
        out = audio[0]*2
        await go_out(m, reply, audio, out, pref, pref)
    async def slowscmd(self, m):
        """.slows <reply to audio>
            Замедлить аудио 0.5x"""
        pref = "Замедление"
        reply = await m.get_reply_message()
        audio = await get_audio(m, reply, pref)
        if not audio: return
        await m.edit(f"[{pref}] Работаю...")
        s2 = audio[0]._spawn(audio[0].raw_data, overrides={
        "frame_rate": int(audio[0].frame_rate * 0.5)
    	})
        out = s2.set_frame_rate(audio[0].frame_rate)
        await go_out(m, reply, audio, out, pref, pref, round(audio[2]/2))
    async def fastscmd(self, m):
        """.fasts <reply to audio>
        Ускорить аудио 1.5x"""
        pref = "Ускорение"
        reply = await m.get_reply_message()
        audio = await get_audio(m, reply, pref)
        if not audio: return
        await m.edit(f"[{pref}] Работаю...")
        s2 = audio[0]._spawn(audio[0].raw_data, overrides={
        "frame_rate": int(audio[0].frame_rate * 1.5)
    	})
        out = s2.set_frame_rate(audio[0].frame_rate)
        await go_out(m, reply, audio, out, pref, pref, audio[2]*2)
    async def rightscmd(self, m):
        """.rights <reply to audio>
            Весь звук в правый канал"""
        pref = "Правый канал"
        reply = await m.get_reply_message()
        audio = await get_audio(m, reply, pref)
        if not audio: return
        await m.edit(f"[{pref}] Работаю...")
        out = effects.pan(audio[0], +1.0)
        await go_out(m, reply, audio, out, pref, pref)
    async def leftscmd(self, m):
        """.lefts <reply to audio>
            Весь звук в левый канал"""
        pref = "Левый канал"
        reply = await m.get_reply_message()
        audio = await get_audio(m, reply, pref)
        if not audio: return
        await m.edit(f"[{pref}] Работаю...")
        out = effects.pan(audio[0], -1.0)
        await go_out(m, reply, audio, out, pref, pref)
    async def normscmd(self, m):
        """.norms <reply to audio>
            Нормализовать звук (Из тихого - нормальный)"""
        pref = "Нормализация"
        reply = await m.get_reply_message()
        audio = await get_audio(m, reply, pref)
        if not audio: return
        await m.edit(f"[{pref}] Работаю...")
        out = effects.normalize(audio[0])
        await go_out(m, reply, audio, out, pref, pref)
    async def byrobertscmd(self, m):
        '''.byroberts <reply to audio>
            Добавить в конец аудио "Directed by Robert B Weide"'''
        pref = "Directed by..."
        reply = await m.get_reply_message()
        audio = await get_audio(m, reply, pref)
        if not audio: return
        await m.edit(f"[{pref}] Работаю...")
        out = audio[0] + AudioSegment.from_file(io.BytesIO(requests.get("https://raw.githubusercontent.com/Daniel3k00/files-for-modules/master/directed.mp3").content)).apply_gain(+8)
        await go_out(m, reply, audio, out, pref, pref)
async def get_audio(m, reply, pref):
    if reply:
        if reply.file:
            if reply.file.mime_type.split("/")[0] == "audio":
                try: voice = reply.document.attributes[0].voice
                except: voice = False
                try: duration = reply.document.attributes[0].duration
                except: duration = 260
                await m.edit(f"[{pref}] Скачиваю...")
                audio = AudioSegment.from_file(io.BytesIO(await reply.download_media(bytes)))
                return (audio, voice, duration)
            else:
                await m.edit(f"[{pref}] reply to audio...")
                return None
        else:
            await m.edit(f"[{pref}] reply to audio...")
            return None
    else:
        await m.edit(f"[{pref}] reply to audio...")
        return None

async def go_out(m, reply, audio, out, pref, title, fs=None):
    o = io.BytesIO()
    o.name = "audio." + ("ogg" if audio[1] else "mp3")
    if audio[1]: out.split_to_mono()
    await m.edit(f"[{pref}] Экспортирую...")
    out.export(o, format="ogg" if audio[1] else "mp3", bitrate="64k" if audio[1] else None, codec="libopus" if audio[1] else None)
    await m.edit(f"[{pref}] Отправляю...")
    await m.client.send_file(m.to_id, o, reply_to=reply.id, voice_note=audio[1], attributes=[types.DocumentAttributeAudio(duration = fs if fs else audio[2], title=title, performer="AudioEditor")] if not audio[1] else None)
    await m.delete()
