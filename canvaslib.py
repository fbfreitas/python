"""CanvasLib educativa para Python, para VS Code e aplicações tkinter.

Utilização:
    from canvaslib import *
    arena = Canvas(600, 400, WHITE)
    arena.drawCircle(100, 100, 20, RED)
    arena.run()

Apenas uma janela Canvas de cada vez é recomendada.
"""

import math
import os
import subprocess
import sys
import time
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path

BLACK = 0x000000
WHITE = 0xFFFFFF
RED = 0xFF0000
GREEN = 0x00FF00
BLUE = 0x0000FF
YELLOW = 0xFFFF00
CYAN = 0x00FFFF
MAGENTA = 0xFF00FF


def _color(value):
    return f"#{value & 0xFFFFFF:06x}"


@dataclass(frozen=True)
class MouseEvent:
    x: int
    y: int
    down: bool


@dataclass(frozen=True)
class KeyEvent:
    char: str
    code: int
    text: str


class TimerCtrl:
    """Controla uma tarefa periódica; stop() impede futuras execuções."""

    def __init__(self, canvas):
        self._canvas = canvas
        self._job = None
        self.active = True

    def stop(self):
        self.active = False
        if self._job is not None:
            try:
                self._canvas._root.after_cancel(self._job)
            except tk.TclError:
                pass
            self._job = None


class Canvas:
    def __init__(self, width, height, background=WHITE):
        self.width = int(width)
        self.height = int(height)
        self.background = background
        self._root = tk.Tk()
        self._root.title("CanvasLib Python")
        self._canvas = tk.Canvas(
            self._root, width=self.width, height=self.height,
            bg=_color(background), highlightthickness=0
        )
        self._canvas.pack()
        self._font_size = 32
        self._images = []
        self.mouse = MouseEvent(0, 0, False)
        self._mouse_down = None
        self._mouse_move = None
        self._key_pressed = None
        self._key_released = None
        self._pressed_keys = set()
        self._pending_releases = {}
        self._closed = False
        self._canvas.bind("<ButtonPress-1>", self._press)
        self._canvas.bind("<ButtonRelease-1>", self._release_mouse)
        self._canvas.bind("<Motion>", self._move)
        self._root.bind("<KeyPress>", self._key_press)
        self._root.bind("<KeyRelease>", self._key_release)
        self._root.bind("<FocusOut>", self._focus_out)
        self._root.protocol("WM_DELETE_WINDOW", self.close)
        self._root.after_idle(self._canvas.focus_set)

    def _press(self, event):
        self._canvas.focus_set()
        self.mouse = MouseEvent(event.x, event.y, True)
        if self._mouse_down:
            self._mouse_down(self.mouse)

    def _release_mouse(self, event):
        self.mouse = MouseEvent(event.x, event.y, False)

    def _move(self, event):
        self.mouse = MouseEvent(event.x, event.y, self.mouse.down)
        if self._mouse_move:
            self._mouse_move(self.mouse)

    @staticmethod
    def _key_event(event):
        return KeyEvent(event.char, event.keycode, event.keysym)

    def _key_press(self, event):
        key = event.keysym
        pending = self._pending_releases.pop(key, None)
        if pending is not None:
            self._root.after_cancel(pending)
        # Ignorar KeyPress repetidos enquanto a tecla estiver premida.
        if key not in self._pressed_keys:
            self._pressed_keys.add(key)
            if self._key_pressed:
                self._key_pressed(self._key_event(event))

    def _key_release(self, event):
        key = event.keysym
        pending = self._pending_releases.pop(key, None)
        if pending is not None:
            self._root.after_cancel(pending)
        info = self._key_event(event)

        def confirm_release():
            self._pending_releases.pop(key, None)
            if key in self._pressed_keys:
                self._pressed_keys.remove(key)
                if self._key_released:
                    self._key_released(info)

        # macOS pode enviar KeyRelease + KeyPress durante auto-repeat.
        # Pequeno atraso permite cancelar essas falsas libertações.
        self._pending_releases[key] = self._root.after(35, confirm_release)

    def _focus_out(self, event):
        if event.widget is not self._root:
            return
        for job in self._pending_releases.values():
            self._root.after_cancel(job)
        self._pending_releases.clear()
        keys = list(self._pressed_keys)
        self._pressed_keys.clear()
        if self._key_released:
            for key in keys:
                self._key_released(KeyEvent("", 0, key))
        self.mouse = MouseEvent(self.mouse.x, self.mouse.y, False)

    def erase(self):
        self._canvas.delete("all")
        self._images.clear()

    def drawLine(self, xFrom, yFrom, xTo, yTo, color=BLACK, thickness=3):
        self._canvas.create_line(xFrom, yFrom, xTo, yTo,
                                 fill=_color(color), width=thickness)

    def drawRect(self, x, y, width, height, color=BLACK, thickness=0):
        self._canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=_color(color) if thickness == 0 else "",
            outline=_color(color), width=max(1, thickness)
        )

    def drawCircle(self, xCenter, yCenter, radius, color=BLACK, thickness=0):
        self._canvas.create_oval(
            xCenter-radius, yCenter-radius,
            xCenter+radius, yCenter+radius,
            fill=_color(color) if thickness == 0 else "",
            outline=_color(color), width=max(1, thickness)
        )

    def drawArc(self, xCenter, yCenter, radius, startAng, endAng=360,
                color=BLACK, thickness=0):
        self._canvas.create_arc(
            xCenter-radius, yCenter-radius,
            xCenter+radius, yCenter+radius,
            start=startAng, extent=endAng-startAng,
            style=tk.ARC if thickness else tk.PIESLICE,
            fill="" if thickness else _color(color),
            outline=_color(color), width=max(1, thickness)
        )

    def drawText(self, x, y, txt, color=BLACK, fontSize=None):
        if fontSize is not None:
            self._font_size = fontSize
        self._canvas.create_text(
            x, y, text=str(txt), fill=_color(color),
            font=("Arial", self._font_size), anchor="sw"
        )

    def drawImage(self, filename, x, y, width=0, height=0):
        try:
            from PIL import Image, ImageTk
        except ImportError as exc:
            raise ImportError("Instala Pillow: python3 -m pip install pillow") from exc
        name, *crop = filename.split("|", 1)
        if not Path(name).suffix:
            name += ".png"
        image = Image.open(name).convert("RGBA")
        if crop:
            left, top, w, h = map(int, crop[0].split(","))
            image = image.crop((left, top, left+w, top+h))
        if width or height:
            image = image.resize((int(width or image.width), int(height or image.height)))
        photo = ImageTk.PhotoImage(image)
        self._images.append(photo)
        self._canvas.create_image(x, y, anchor="nw", image=photo)

    def onTime(self, delay, handler):
        return self._root.after(max(0, int(delay)), handler)

    def onTimeProgress(self, period, handler):
        period = max(1, int(period))
        ctrl = TimerCtrl(self)
        start = time.monotonic()
        frame = 1

        def tick():
            nonlocal frame
            if not ctrl.active or self._closed:
                return
            elapsed_ms = int((time.monotonic() - start) * 1000)
            handler(elapsed_ms)
            if ctrl.active and not self._closed:
                frame += 1
                target = start + frame * period / 1000
                wait = max(1, round((target - time.monotonic()) * 1000))
                ctrl._job = self._root.after(wait, tick)

        ctrl._job = self._root.after(period, tick)
        return ctrl

    def onMouseDown(self, handler):
        self._mouse_down = handler

    def onMouseMove(self, handler):
        self._mouse_move = handler

    def onKeyPressed(self, handler):
        self._key_pressed = handler

    def onKeyReleased(self, handler):
        self._key_released = handler

    def close(self):
        if not self._closed:
            self._closed = True
            self._root.destroy()

    def run(self):
        self._root.mainloop()


def _sound_path(sound):
    if not Path(sound).suffix:
        sound += ".wav"
    return str(Path(sound).resolve())


def playSound(sound):
    """Reproduz WAV no macOS (afplay) ou Windows (winsound)."""
    path = _sound_path(sound)
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    if sys.platform == "darwin":
        subprocess.Popen(["afplay", path], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    elif sys.platform == "win32":
        import winsound
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    else:
        raise NotImplementedError("playSound: suporte integrado apenas em macOS e Windows")


def loadSounds(*names):
    """Verifica a existência dos sons (sem cache de áudio nesta versão)."""
    for name in names:
        path = _sound_path(name)
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
