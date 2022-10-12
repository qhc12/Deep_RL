import sys

from controller.tree_simulator import TreeSimulator
from utils import except_hook

if __name__ == "__main__":
    # install exception hook: without this, uncaught exception would cause application to exit
    sys.excepthook = except_hook

    from run_configurations.default.settings import settings
    from run_configurations.paths import add_path
    settings = add_path(settings, "default")

    if settings.render and settings.no_threads > 1:
        sys.stderr.write('WARNING: When rendering is enabled, multithreaded running is unavailable.\n')

    TreeSimulator(settings).run()
