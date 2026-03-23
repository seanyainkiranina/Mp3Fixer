""" this module is the entry point for the application.
 It initializes the Mp3Runner class and starts the GUI. """
from mp3runner import Mp3Runner


if __name__ == "__main__":
    mp3mover = Mp3Runner()
    folder_path = mp3mover.browse_folder()
    if folder_path:
        mp3mover.read_directory(folder_path)
