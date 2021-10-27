"""
Crée une archive du plugin QGIS Plume.
"""

from pathlib import Path
from zipfile import ZipFile, PyZipFile


def zip_plume(dest=None):
    """Crée un ZIP contenant le code source du plugin QGIS Plume.

    ARGUMENTS
    ---------
    - [optionnel] dest (str) : le chemin du répertoire où le ZIP doit être
    créé. Si non spécifié, il est créé dans le dossier courant.

    RESULTAT
    --------
    Pas de valeur renvoyée.
    """
    plume = Path("plume")
    if not plume.exists() or not plume.is_dir:
        raise FileNotFoundError(
            "Could'nt find sub-directory 'plume' in current directory."
            )
    if dest and (not Path(dest).exists() or not Path(dest).is_dir):
        raise FileNotFoundError(
            "Destination doesn't exist or is not a directory ({}).".format(dest)
            )

    mDest = (dest + r"\plume.zip") if dest else "plume.zip"

    if Path(mDest).exists():
        Path(mDest).unlink()

    with ZipFile(mDest, mode="a") as zhpy:
        p = [plume]
        
        while p:
            d = p.pop()
            
            for e in d.iterdir():
                
                if e.is_file():
                    zhpy.write(e)
                        
                elif e.is_dir() and include(e):
                    zhpy.write(e)
                    p.append(e)


def include(strPath):
    """L'élément doit-il inclus dans le ZIP ?

    ARGUMENTS
    ---------
    - strPath (str) : une chaîne de caractères correspondant à un chemin.
    Admet aussi le type Path de pathlib.

    RESULTAT
    --------
    Un booléen (bool). True si le fichier ou répertoire doit être inclus
    dans la sauvegarde, False sinon.
    """
    p = Path(strPath)
    return not p.name in ("__archives__", "__save__", "__pycache__",
        "tests", "exemples", "admin")


if __name__ == "__main__":
    zip_plume()
