"""Utilitaires pour la gestion des images.

"""

import subprocess
from pathlib import Path

from plume import __path__ as plume_path

def export_svg_as_png(
    svg_file, png_dir=None, inkscape=None, dpi=None,
    width=None, height=None
    ):
    """Convertit en PNG une image SVG.

    Parameters
    ----------
    svg_file : str or pathlib.Path
        Le chemin d'un fichier SVG à convertir.
    png_dir : str or pathlib.Path, optional
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
    
    if png_dir:
        png_dir = Path(png_dir)
        if not png_dir.exists() or not png_dir.is_dir():
            raise FileNotFoundError(f"'{png_dir}' n'est pas un répertoire.")
    else:
        png_dir = Path(plume_path[0]).parent / 'pictures'
        if not png_dir.exists() or not png_dir.is_dir():
            png_dir.mkdir()
    png = png_dir / f'{svg.stem}.png'
    
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

def all_svg_as_png(
    svg_dir=None, png_dir=None, inkscape=None, recursive=True,
    verbose=True
    ):
    """Exporte tous les SVG d'un répertoire au format PNG.

    Avec les paramètres par défaut, cette fonction exporte
    les icônes de Plume dans un répertoire ``pictures`` à
    la racine.

    Parameters
    ----------
    svg_dir : str or pahtlib.Path, optional
        Le chemin du dossier contenant les fichiers
        SVG à convertir. Si non spécifié, la fonction cible
        les icônes du répertoire ``plume/icons``.
    png_dir : str or pathlib.Path, optional
        Le chemin du répertoire dans lequel seront placés les
        fichiers PNG. Si non spécifié, les fichiers sont placés
        dans un répertoire ``pictures`` à la racine.
    inkscape : str or pathlib.Path, optional
        Le chemin d'accès au logiciel Inskape. Il est
        possible de ne pas fournir cet argument si 
        Inskape est déclaré dans la variable d'environnement
        Path.
    recursive : bool, default True
        Si ``True``, la fonction ira chercher les fichiers
        SVG des sous-répertoires du répertoire source (ainsi
        que leurs sous-répertoires, etc.). Les répertoires
        dont le nom commence par ``'.'`` ou ``'__'`` sont
        systématiquement exclus.
    verbose : bool, default True
        Si ``True``, la fonction liste les fichiers traités
        dans la console.

    """
    if png_dir:
        png_dir = Path(png_dir)
        if not png_dir.exists() or not png_dir.is_dir():
            raise FileNotFoundError(f"'{png_dir}' n'est pas un répertoire.")
    else:
        png_dir = Path(plume_path[0]).parent / 'pictures'
        if not png_dir.exists() or not png_dir.is_dir():
            png_dir.mkdir()

    if svg_dir:
        svg_dir = Path(svg_dir)
        if not svg_dir.exists() or not svg_dir.is_dir():
            raise FileNotFoundError(f"'{svg_dir}' n'est pas un répertoire.")
    else:
        svg_dir = Path(plume_path[0]) / 'icons'
        if not svg_dir.exists() or not svg_dir.is_dir():
            raise FileNotFoundError(
                'Le répertoire "plume/icons" est introuvable.'
            )
    
    for obj in svg_dir.iterdir():
        if obj.is_file() and obj.suffix.lower() == '.svg':
            export_svg_as_png(obj, png_dir=png_dir, inkscape=inkscape)
            if verbose:
                print(obj.name)
        elif obj.is_dir() and recursive and not obj.name.startswith(('__', '.')):
            if verbose:
                print(f'> {obj}')
            all_svg_as_png(
                svg_dir=obj, png_dir=png_dir, inkscape=inkscape,
                recursive=recursive
            )




