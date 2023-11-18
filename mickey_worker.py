import random
import logging
import threading
import pyttsx3
from datetime import datetime, timedelta

from mickey_configuration import MickeyConfiguration


class MickeyWorker:
    def __init__(self, logger: logging.Logger, configuration: MickeyConfiguration):
        self._logger = logger
        self._config = configuration

        self._running_thread = None  # type: threading.Thread
        self._stop_event = threading.Event()

        self._next_iteration_time = None
        self._engine = None

    def _create_tts_engine(self):
        engine = pyttsx3.init()
        engine.setProperty('rate', self._config.engine_rate)
        engine.setProperty('volume', self._config.volume)
        engine.connect('started-word', self._on_word)
        return engine

    def _on_word(self, name, location, length):
        if self._stop_event.is_set():
            self._logger.info("stopping engine mid-sentence due to stop event")
            self._engine.stop()

    def _mickey(self, amount_of_mickeys: int):
        self._logger.info(f"starting to mickey {amount_of_mickeys} times")

        self._engine = self._create_tts_engine()
        self._engine.say("Get ready to hydrate! Mickey begins in a couple of seconds. 3. 2. 1.")
        self._engine.runAndWait()

        if not self._stop_event.is_set():
            self._engine.say("mickey " * amount_of_mickeys + "mouse")
            self._engine.runAndWait()

        self._engine = None

    def _start_thread(self):
        self._logger.info("worker thread started")

        while not self._stop_event.wait(0):
            self._logger.info("starting iteration")
            amount_of_mickeys = random.randint(self._config.min_mickeys, self._config.max_mickeys + 1)
            seconds_to_wait = random.randint(
                self._config.min_time_between_iterations, self._config.max_time_between_iterations + 1)

            self._logger.info(f"waiting for {seconds_to_wait} seconds")
            self._next_iteration_time = datetime.now() + timedelta(seconds=seconds_to_wait)
            event_signaled = self._stop_event.wait(seconds_to_wait)
            if event_signaled:
                self._logger.info("stopping due to stop event")
                return

            self._mickey(amount_of_mickeys)
            self._logger.info("iteration finished")

    def start(self):
        self._logger.info("starting worker thread")
        self._running_thread = threading.Thread(target=self._start_thread)
        self._running_thread.start()

    def stop(self):
        if not self._running_thread:
            return

        self._logger.info("stopping worker thread")
        self._stop_event.set()
        self._running_thread.join()
        self._running_thread = None
        self._stop_event.clear()
        self._next_iteration_time = None
        self._logger.info("working thread stopped")

    def restart(self):
        self.stop()
        self.start()

    def get_volatile_configuration(self):
        return self._config

    def get_next_iteration_time(self) -> datetime:
        return self._next_iteration_time
