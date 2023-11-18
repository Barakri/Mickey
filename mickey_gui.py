import threading
from tkinter import *
from tkinter import ttk

from mickey_worker import MickeyWorker
from mickey_configuration import MickeyConfiguration
from mickey_systray_icon import MickeySystrayIcon


class MickeyGui:
    def __init__(self, worker: MickeyWorker):
        self._root = Tk()
        self._root.title("MICKEY!")
        self._mainframe = self._set_mainframe()
        self._worker = worker
        self._config = self._worker.get_volatile_configuration()
        self._updated_config = MickeyConfiguration.from_other_config(self._config)

        self._heading_label = None
        self._heading_button = None

        self._stop_event = threading.Event()

        self._header_frame = self._create_header_frame()
        self._header_frame.grid(column=0, row=0)

        self._config_frame = self._create_configuration_frame()
        self._config_frame.grid(column=0, row=1)

        self._footer_frame = self._create_footer_frame()
        self._footer_frame.grid(column=0, row=2)

        self._icon = MickeySystrayIcon(self._root, self.quit)

    def _set_mainframe(self):
        mainframe = ttk.Frame(self._root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0)
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)
        return mainframe

    def _create_footer_frame(self):
        footer_frame = ttk.Frame(self._mainframe, padding="3 3 12 12")
        ttk.Button(footer_frame, text="Quit (no more mickeys)", command=self.quit)\
            .grid(columnspan=4, row=0, sticky="news")

        return footer_frame

    def _create_header_frame(self):
        header_frame = ttk.Frame(self._mainframe, padding="3 3 12 12")
        ttk.Label(header_frame, text="Mickey!", font=("TkHeadingFont", 40)).grid(column=0, row=0, columnspan=4)
        self._heading_label = ttk.Label(header_frame,
                                        text="No Mickey scheduled :( Start now by pressing the Start button!")
        self._heading_label.grid(column=0, row=1, columnspan=2, sticky="w")
        self._heading_button = ttk.Button(header_frame, text="Start!", command=self._submit)
        self._heading_button.grid(column=3, row=1, rowspan=3)

        return header_frame

    @staticmethod
    def _create_spinbox_config_line(frame, text, row_num, var, spin_range, reset_func):
        ttk.Label(frame, text=text).grid(column=0, row=row_num)
        ttk.Spinbox(frame, textvariable=var, from_=spin_range[0], to=spin_range[1]).grid(column=1, row=row_num)
        ttk.Button(frame, text="Reset", command=reset_func).grid(column=2, row=row_num)

    @staticmethod
    def _create_scale_config_line(frame, text, row_num, var, scale_range, reset_func):
        ttk.Label(frame, text=text).grid(column=0, row=row_num)
        ttk.Scale(frame,
                  orient=HORIZONTAL, variable=var, from_=scale_range[0], to=scale_range[1]).grid(column=1, row=row_num)
        ttk.Button(frame, text="Reset", command=reset_func).grid(column=2, row=row_num)

    def _create_configuration_frame(self):
        configuration_frame = ttk.Frame(self._mainframe, padding="3 3 12 12")

        # making sure there are no leftovers from last gui session
        self._updated_config = MickeyConfiguration.from_other_config(self._config)

        min_mickeys = IntVar(value=self._config.min_mickeys)
        self._create_spinbox_config_line(configuration_frame,
                                         "Minimum mickeys:",
                                         0,
                                         min_mickeys,
                                         (0, 200),
                                         lambda: min_mickeys.set(self._config.min_mickeys))
        min_mickeys.trace_add("write",
                              lambda a, b, c: self._updated_config.set_min_mickeys(min_mickeys.get()))

        max_mickeys = IntVar(value=self._config.max_mickeys)
        self._create_spinbox_config_line(configuration_frame,
                                         "Maximum mickeys:",
                                         1,
                                         max_mickeys,
                                         (0, 500),
                                         lambda: max_mickeys.set(self._config.max_mickeys))
        max_mickeys.trace_add("write",
                              lambda a, b, c: self._updated_config.set_max_mickeys(max_mickeys.get()))

        min_minutes = IntVar(value=self._config.min_time_between_iterations / 60)
        self._create_spinbox_config_line(configuration_frame,
                                         "Minimum minutes between iterations:",
                                         2,
                                         min_minutes,
                                         (0, 200),
                                         lambda: min_minutes.set(self._config.min_time_between_iterations / 60))
        min_minutes.trace_add("write",
                              lambda a, b, c:
                              self._updated_config.set_min_time_between_iterations(min_minutes.get() * 60))

        max_minutes = IntVar(value=self._config.max_time_between_iterations / 60)
        self._create_spinbox_config_line(configuration_frame,
                                         "Maximum minutes between iterations:",
                                         3,
                                         max_minutes,
                                         (0, 200),
                                         lambda: max_minutes.set(self._config.max_time_between_iterations / 60))
        max_minutes.trace_add("write",
                              lambda a, b, c:
                              self._updated_config.set_max_time_between_iterations(max_minutes.get() * 60))

        engine_rate = IntVar(value=self._config.engine_rate)
        self._create_spinbox_config_line(configuration_frame,
                                         "Speaker speed (wpm):",
                                         4,
                                         engine_rate,
                                         (0, 500),
                                         lambda: engine_rate.set(self._config.engine_rate))
        engine_rate.trace_add("write", lambda a, b, c: self._updated_config.set_engine_rate(engine_rate.get()))

        volume = DoubleVar(value=self._config.volume)
        self._create_scale_config_line(configuration_frame,
                                       "Volume (1-100):",
                                       5,
                                       volume,
                                       (0, 100),
                                       lambda: volume.set(self._config.volume))
        volume.trace_add("write", lambda a, b, c: self._updated_config.set_volume(int(volume.get())))

        ttk.Button(configuration_frame, text="Update!", command=self._submit).grid(column=0, columnspan=4, row=6)

        return configuration_frame

    def _submit(self):
        self._config.update_configuration(self._updated_config)
        self._worker.restart()

    def _update_gui(self):
        if next_iter := self._worker.get_next_iteration_time():
            self._heading_label['text'] = f"Next iteration at {next_iter.strftime('%d/%m %H:%M:%S')}!"
            self._heading_button['command'] = self._worker.stop
            self._heading_button['text'] = "Cancel"
        else:
            self._heading_label['text'] = "No Mickey scheduled :( Start now by pressing the button!"
            self._heading_button['command'] = self._submit
            self._heading_button['text'] = "Start!"

        self._root.after(1000, self._update_gui)

    def quit(self):
        self._root.destroy()
        self._worker.stop()

    def run(self):
        for frame in [self._mainframe, self._config_frame, self._header_frame]:
            for child in frame.winfo_children():
                child.grid_configure(padx=5, pady=5)

        self._root.after(0, self._update_gui)
        self._root.mainloop()
