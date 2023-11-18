import logging

from mickey_configuration import MickeyConfiguration
from mickey_worker import MickeyWorker
from mickey_gui import MickeyGui


def main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.WARNING)

    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)
    logger.info("STARING")

    config = MickeyConfiguration(min_time_between_iterations=0, max_time_between_iterations=15)
    worker = MickeyWorker(logger, config)
    worker.start()

    gui = MickeyGui(worker)
    gui.run()


if __name__ == '__main__':
    main()
