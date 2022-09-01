"""Utilitaires pour la gestion des images.

"""

import subprocess
from pathlib import Path

from plume import __path__ as plume_path

def export_svg_as_png(
    svg_file, target_dir=None, inkscape=None, dpi=None,
    width=None, height=None
    ):
    """Convertit en PNG une image SVG.

    Parameters
    ----------
    svg_file : str or pathlib.Path
        Le chemin d'un fichier SVG à convertir.
    png : str or pathlib.Path, optional
        Le chemin du répertoire dans lequel sera placé le
        fichier PNG. Si non spécifié, le fichier est placé dans
        un répertoire ``pictures`` à la racine. Le nom du PNG est
        identique à celui du SVG et tout fichier pré-existant
        sera silencieusement écrasé.
    inkscape : str or pathlib.Path, optional
        Le chemin d'accès au logiciel Inskape. Il est
        possible de ne pas fournir cet argument si 
        Inskape est déclaré dans la variable d'environnement
        Path.
    dpi : int, optional
        Résolution d'export. Si non spécifié, la valeur par
        défaut d'Inkscape est utilisée (96dpi).
    width : int, optional
        Force la largeur d'export à valeur fournie (en pixels).
    height : int, optional
        Force la hauteur d'export à valeur fournie (en pixels).

    """
    svg = Path(svg_file)
    if not svg.exists() or not svg.is_file() or not svg.suffix.lower() == '.svg':
        raise ValueError(f"'{svg}' n'est pas le chemin d'un fichier SVG.")
    
    if target_dir:
        png = Path(target_dir)
        if not png.exists() or not png.is_dir():
            raise FileNotFoundError(f"'{target_dir}' n'est pas un répertoire.")
    else:
        png = Path(plume_path[0]).parent / 'pictures'
        if not png.exists() or not png.is_dir():
            png.mkdir()
        png = png / f'{svg.stem}.png'
    
    if inkscape:
        inkscape = Path(inkscape)
        if not inkscape.exists() or not inkscape.is_file() or not inkscape.name == 'inkscape.exe':
            raise ValueError(f"'{inkscape}' n'est pas le chemin de l'exécutable Inkscape.")
    else:
        inkscape = Path('inkscape')
    
    args = [inkscape.as_posix(), '--export-filename', png.as_posix(), '--export-type', 'png']
    if dpi:
        args += ['--export-dpi', dpi]
    if width:
        args += ['--export-width', width]
    if height:
        args += ['--export-height', height]
    args.append(svg.as_posix())

    subprocess.run(args)



