"""Pixel-sized, monitor-directed Qt window for SLMPy Browser.

Runs in its own process because a Qt event loop belongs to the GUI thread.
This is a practical preview/output prototype, NOT verified timing or a calibrated
scientific SLM driver. Operating-system scaling and color management must be
validated experimentally.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout


def screens_info(app):
    return [
        {
            "index": i,
            "name": s.name(),
            "width": s.geometry().width(),
            "height": s.geometry().height(),
            "x": s.geometry().x(),
            "y": s.geometry().y(),
            "device_pixel_ratio": s.devicePixelRatio(),
        }
        for i, s in enumerate(app.screens())
    ]


class ScreenOutput(QWidget):
    def __init__(self, screen_index: int, image_path: Path, app: QApplication):
        super().__init__()
        screens = app.screens()
        if screen_index >= len(screens):
            raise ValueError("Screen %d not found" % screen_index)
        self.screen = screens[screen_index]
        self.image_path = image_path
        self.last_mtime = None
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")
        self.label = QLabel(self)
        self.label.setStyleSheet("background-color: black;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.label)
        # Qt top-level windows are explicitly associated with target QScreen.
        self.winId()
        self.windowHandle().setScreen(self.screen)
        self.setGeometry(self.screen.geometry())
        self.showFullScreen()
        self.check_image()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_image)
        self.timer.start(30)

    def check_image(self):
        try:
            mtime = self.image_path.stat().st_mtime_ns
            if mtime == self.last_mtime:
                return
            frame = QImage(str(self.image_path))
            if frame.isNull():
                return
            logical_w, logical_h = self.screen.geometry().width(), self.screen.geometry().height()
            if (frame.width(), frame.height()) != (logical_w, logical_h):
                # Never silently resample a hologram.
                print("Refusing mismatched hologram size", file=sys.stderr)
                return
            self.label.setPixmap(QPixmap.fromImage(frame))
            self.last_mtime = mtime
        except OSError:
            pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--screen", type=int)
    parser.add_argument("--image", type=Path)
    args = parser.parse_args()
    app = QApplication(sys.argv)
    if args.list:
        print(json.dumps(screens_info(app)))
        return 0
    if args.screen is None or args.image is None:
        parser.error("--screen and --image are required unless --list is specified")
    output = ScreenOutput(args.screen, args.image, app)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
