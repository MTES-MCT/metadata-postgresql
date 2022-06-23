# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021   

def classFactory(iface):
  from .plume import MainPlugin
  return MainPlugin(iface)