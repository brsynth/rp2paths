# tar.py
# tested with python 2.6 and 3.1
# See also the standard modules tarfile and gzip

import tarfile

def tar_cz(*path, relative=False):
    """tar_cz(*path) -> bytes
    Compress a sequence of files or directories in memory.
    The resulting string could be stored as a .tgz file."""
    file_out = io.BytesIO()
    tar = tarfile.open(mode = "w:gz", fileobj = file_out)
    for p in path:
        if(relative): tar.add(p, arcname='./')
        else: tar.add(p)
    tar.close()
    return file_out.getvalue()

def tar_xz(stringz, folder = "."):
    """tar_xz(stringz, folder = ".") -> None
    Uncompress a string created by tar_cz in a given directory."""
    file_in = BIO(stringz)
    tar = tarfile.open(mode= "r:gz", fileobj = file_in)
    tar.extractall(folder)
