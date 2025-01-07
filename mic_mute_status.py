#!/usr/bin/env python3
import subprocess
import threading
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango, GLib, GdkPixbuf
import os

class MicOverlay(Gtk.Window):
    def __init__(self, x=50, y=50):
        super().__init__(title="Mic Status Overlay")

        # Set basic window properties:
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_accept_focus(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)

        # Set transparency if desired:
        self.set_app_paintable(True)
        screen = Gdk.Screen.get_default()
        visual = screen.get_rgba_visual()
        if visual is not None and self.is_composited():
            self.set_visual(visual)

        # Set fixed position:
        self.move(x, y)

        # Add drag functionality
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
        self.connect("button-press-event", self.on_button_press)
        self.connect("button-release-event", self.on_button_release)
        self.connect("motion-notify-event", self.on_motion_notify)

        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Create an Image widget
        self.image = Gtk.Image()
        self.add(self.image)

        self.show_all()

        # Initial update
        self.update_mute_status()

        # Start a background thread to listen for changes via pactl subscribe
        self.listener_thread = threading.Thread(target=self.listen_for_changes, daemon=True)
        self.listener_thread.start()

    def on_button_press(self, widget, event):
        if event.button == 1:  # Left mouse button
            self.dragging = True
            self.drag_offset_x = event.x
            self.drag_offset_y = event.y
            return True

    def on_button_release(self, widget, event):
        if event.button == 1:
            self.dragging = False
            return True

    def on_motion_notify(self, widget, event):
        if self.dragging:
            x, y = event.window.get_position()
            new_x = x + event.x - self.drag_offset_x
            new_y = y + event.y - self.drag_offset_y
            self.move(new_x, new_y)
            return True

    def update_mute_status(self):
        is_muted = self.get_mute_status()
        if is_muted:
            self.set_icon("mic-muted.png")
        else:
            self.set_icon("mic-unmuted.png")

    def set_icon(self, icon_filename):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, icon_filename)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 96, 96) # Adjust size as needed
            self.image.set_from_pixbuf(pixbuf)
        except Exception as e:
            print(f"Error loading icon: {e}")
            if "No such file or directory" in str(e):
                print("Make sure the icon files are in the same directory as the script.")
            self.image.set_from_icon_name("dialog-error", Gtk.IconSize.DIALOG)

    def get_mute_status(self):
        try:
            output = subprocess.check_output(["pactl", "get-source-mute", "@DEFAULT_SOURCE@"], text=True).strip()
            if "yes" in output.lower():
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            return False

    def listen_for_changes(self):
        process = subprocess.Popen(["pactl", "subscribe"], stdout=subprocess.PIPE, text=True)
        for line in process.stdout:
            if "source" in line.lower():
                GLib.idle_add(self.update_mute_status)

def main():
    win = MicOverlay(x=1310, y=105)
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()

if __name__ == "__main__":
    main()