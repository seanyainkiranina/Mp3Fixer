import os
from tinytag import TinyTag
import shutil

def create_directory(path):
    """
    Creates a directory if it does not exist.
    
    Args:
        path (str): The directory path to create.
    """
    try:
        # os.makedirs with exist_ok=True will not raise an error if the folder exists
        os.makedirs(path, exist_ok=True)
        print(f"Directory created or already exists: {path}")
    except OSError as e:
        print(f"Error creating directory '{path}': {e}")

# Example usage
if __name__ == "__main__":
    pathdir = "C:\\Users\\seany\\Music\\Hollies"
    #create_directory(folder_path)
    files = os.listdir(pathdir)
    newdir = pathdir
    ext = ""
    for file in files:
        ext = file[file.rfind('.') + 1:]
        if ext == "mp3":
            targetFile = pathdir + "\\" + file
            newdirArtist = newdir
            tag: TinyTag = TinyTag.get(targetFile)
            if tag.artist is not None:
                newdirArtist = newdir + "\\" + tag.artist
                create_directory(newdirArtist)
                if tag.album is not None:
                    newdirArtistAlbum = newdirArtist + "\\" + tag.album
                    create_directory(newdirArtistAlbum)
                    shutil.copy(targetFile, newdirArtistAlbum)

