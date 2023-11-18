import pystray
import PIL.Image
import PIL.ImageDraw


class MickeySystrayIcon:
    def __init__(self, gui_root, quit_function):
        self._gui_root = gui_root
        self._gui_destroy = quit_function
        self._image = self._get_icon_image()
        self._icon = None

        self._register_for_gui_closer()

    def _register_for_gui_closer(self):
        self._gui_root.protocol("WM_DELETE_WINDOW", self._hide_gui_and_start_icon)

    @staticmethod
    def _get_icon_image():
        image = PIL.Image.new('RGB', (64, 64), 'black')
        dc = PIL.ImageDraw.Draw(image)
        dc.rectangle(
            (64 // 2, 0, 64, 64 // 2),
            fill='white')
        dc.rectangle(
            (0, 64 // 2, 64 // 2, 64),
            fill='white')

        return image

    def _create_icon(self):
        menu = (
            pystray.MenuItem('Quit', self._quit_program),
            pystray.MenuItem('Options', self._hide_icon_and_show_gui, default=True)
        )

        return pystray.Icon('Mickey', icon=self._image, menu=menu)

    def _quit_program(self):
        self._gui_destroy()

        if self._icon:
            self._icon.stop()

    def _hide_icon_and_show_gui(self):
        if self._icon:
            self._icon.stop()
        self._gui_root.after(0, self._gui_root.deiconify)

    def _hide_gui_and_start_icon(self):
        self._gui_root.withdraw()
        self._icon = self._create_icon()
        self._icon.run()
