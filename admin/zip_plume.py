"""Crée une archive du plugin QGIS Plume.

En supposant que le dossier parent correspond à la
racine du Git, on exécutera simplement:

    >>> zip_plume()

Cette commande crée un fichier ``plume.zip`` à la
racine du Git contenant le code du plugin Plume, allegé
de tout ce dont les utilisateurs n'ont pas besoin, en
particulier les scripts de tests et les données associées.

Pour créer l'archive dans un autre répertoire:

    >>> zip_plume('C:\\Users\\Me\\Documents\\Destination')

"""

from pathlib import Path
from zipfile import ZipFile, PyZipFile

from plume.rdf.utils import abspath


def zip_plume(dest=None):
    """Crée un ZIP contenant le code source du plugin QGIS Plume.

    Parameters
    ----------
    dest : str or pathlib.Path, optional
        Le chemin du répertoire où le ZIP doit être
        créé. Si non spécifié, il est créé dans le dossier parent,
        qui correspond en principe à la racine du Git metadata-postgresql.

    Notes
    -----
    Si un fichier ``plume.zip`` existait déjà dans le répertoire
    de destination, il sera silencieusement remplacé.

    """
    plume = abspath('')

    if not plume.exists() or not plume.is_dir:
        raise FileNotFoundError(
            "Le répertoire 'plume' est introuvable."
            )
    
    dest = dest or plume.parents[0]
  
    if not Path(dest).exists() or not Path(dest).is_dir:
        raise FileNotFoundError(
            "Le répertoire de destination n'existe pas " \
            "ou n'est pas un dossier ({}).".format(dest)
            )

    plumezip = dest / 'plume.zip'

    if Path(plumezip).exists():
        Path(plumezip).unlink()

    with ZipFile(plumezip, mode="a") as zhpy:
        p = [plume]
        
        while p:
            d = p.pop()
            
            for e in d.iterdir():
                
                if e.is_file():
                    zhpy.write(e, arcname=e.relative_to(plume))
                        
                elif e.is_dir() and include(e):
                    zhpy.write(e, arcname=e.relative_to(plume))
                    p.append(e)


def include(anypath):
    """L'élément doit-il être inclus dans le ZIP ?

    Parameters
    ----------
    anypath : str or pathlib.Path
        Une chaîne de caractères correspondant à un chemin.

    Returns
    -------
    bool
        ``True`` si le fichier ou répertoire doit être inclus
        dans la sauvegarde, ``False`` sinon.
    
    """
    p = Path(anypath)
    return not p.name in ("__archives__", "__save__", "__pycache__",
        "tests")


if __name__ == "__main__":
    zip_plume()
