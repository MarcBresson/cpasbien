import subprocess
import shutil
from git import Repo
from pathlib import Path
import logging
logger = logging.getLogger()

QBITTORRENT_URL = "https://github.com/qbittorrent/qBittorrent"
SEARCH_ENGINE_PATH = Path("src/searchengine/nova3")
QBITTORRENT_FOLDER = Path(__file__).parent / Path("./.search_engine_test")

CPASBIEN_ENGINE_PATH = Path("src/cpasbien.py")


def test_engine():
    clone_search_engine()
    copy_cpasbien_engine()
    cpasbien_engine_test()


def clone_search_engine():
    if not QBITTORRENT_FOLDER.exists():
        logger.info("Cloning qbittorrent repo ...")

        repo = Repo.clone_from(
            QBITTORRENT_URL,
            QBITTORRENT_FOLDER,
            multi_options=[
                "-n",               # No checkout of HEAD is performed
                "--depth=1",        # history truncated to 1 commit
                "--filter=tree:0"   # prevent objects from being downlaoded
            ]
        )

        git = repo.git
        git.execute(("git", "sparse-checkout", "set", "--no-cone", SEARCH_ENGINE_PATH.as_posix()))

        repo.active_branch.checkout()
    else:
        logger.info("qbittorrent repo already exists")


def create_recurrent_module(base_path: Path):
    init_file = base_path / "__init__.py"

    # we stop if the folder already has an __init__ file
    if init_file.exists():
        return

    init_file.write_text("")

    for file_folder in base_path.iterdir():
        # we can only have an __init__ file in folders
        if file_folder.is_file():
            return

        create_recurrent_module(file_folder)


def copy_cpasbien_engine():
    custom_engines_path = QBITTORRENT_FOLDER / SEARCH_ENGINE_PATH / "engines"
    custom_engines_path.mkdir(exist_ok=True)

    shutil.copy2(CPASBIEN_ENGINE_PATH, custom_engines_path)


def cpasbien_engine_test():
    search_script = QBITTORRENT_FOLDER / SEARCH_ENGINE_PATH / "nova2.py"
    download_script = QBITTORRENT_FOLDER / SEARCH_ENGINE_PATH / "nova2dl.py"

    run = subprocess.run(
        ["python", str(search_script), "cpasbien", "all", "la reine des neiges"],
        capture_output=True,
        check=False
    )
    logger.info("STDOUT: %s", run.stdout)
    logger.info("STDERR: %s", run.stderr)

    torrent_url = str(run.stdout).split("|")[6].split(r"\r")[0]
    logger.info("Attempting to download torrent file at %s", torrent_url)

    run = subprocess.run(
        ["python", str(download_script), "http://www.cpasbien.fr", torrent_url],
        capture_output=True,
        check=False
    )
    logger.info("STDOUT: %s", run.stdout)
    logger.info("STDERR: %s", run.stderr)
