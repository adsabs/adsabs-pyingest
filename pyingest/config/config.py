# APS Journal dictionary: used by parsers/aps.py to get the bibstem

APS_PUBLISHER_IDS = {'PRL': 'PhRvL', 'PRX': 'PhRvX', 'RMP': 'RvMP',
                     'PRA': 'PhRvA', 'PRB': 'PhRvB', 'PRC': 'PhRvC',
                     'PRD': 'PhRvD', 'PRE': 'PhRvE', 'PRAB': 'PhRvS',
                     'PRSTAB': 'PhRvS', 'PRAPPLIED': 'PhRvP',
                     'PRFLUIDS': 'PhRvF', 'PRMATERIALS': 'PhRvM',
                     'PRPER': 'PRPER', 'PRSTPER': 'PRSTP', 'PR': 'PhRv',
                     'PRI': 'PhRvI','PHYSICS': 'PhyOJ'}

APS_ASTRO_KEYWORDS = [
            'Accretion disk & black-hole plasma',
            'Active & peculiar galaxies',
            'Alternative gravity theories',
            'Anthropic considerations',
            'Asteroids, meteors, & meteorites',
            'Astronomical black holes',
            'Astronomical masses & mass distributions',
            'Astrophysical & cosmological simulations',
            'Astrophysical electromagnetic fields',
            'Astrophysical fluid dynamics',
            'Astrophysical jets',
            'Astrophysical studies of gravity',
            'Baryogenesis & leptogenesis',
            'Big bang nucleosynthesis',
            'Binary stars',
            'Canonical quantum gravity',
            'Classical black holes',
            'Composition of astronomical objects',
            'Cosmic microwave background',
            'Cosmic ray & astroparticle detectors',
            'Cosmic ray acceleration',
            'Cosmic ray composition & spectra',
            'Cosmic ray propagation',
            'Cosmic ray sources',
            'Cosmic rays & astroparticles',
            'Cosmic strings & domain walls',
            'Cosmological constant',
            'Cosmological parameters',
            'Cosmology',
            'Dark energy',
            'Dark matter',
            'Dark matter detectors',
            'Distances, redshifts, & velocities',
            'Electromagnetic radiation astronomy',
            'Evolution of the Universe',
            'Experimental studies of gravity',
            'Explosive burning',
            'Extrasolar neutrino astronomy',
            'Extrasolar planets',
            'Fluid planets',
            'Fluids & classical fields in curved spacetime',
            'Formation & evolution of stars & galaxies',
            'Galactic disks',
            'Galactic halos',
            'Galactic nuclei & quasars',
            'Galaxies',
            'Galaxy clusters',
            'Gamma ray astronomy',
            'Gamma ray bursts',
            'General relativity',
            'General relativity equations & solutions',
            'General relativity formalism',
            'Gravitation',
            'Gravitational lenses',
            'Gravitational wave detection',
            'Gravitational wave detectors',
            'Gravitational wave sources',
            'Gravitational waves',
            'Gravity in dimensions other than four',
            'H & He burning',
            'Hydrostatic stellar nucleosynthesis',
            'Inflation',
            'Intergalactic medium',
            'Interplanetary magnetic field',
            'Interstellar medium',
            'Laboratory studies of gravity',
            'Laboratory studies of space & astrophysical plasmas',
            'Large scale structure of the Universe',
            'Loop quantum gravity',
            'Massive compact halo objects',
            'Milky Way',
            'Neutrino detectors',
            'Neutron stars & pulsars',
            'Normal galaxies',
            'Normal stars',
            'Novae & supernovae',
            'Nuclear astrophysics',
            'Nuclear physics of explosive environments',
            'Nucleosynthesis in explosive environments',
            'Numerical relativity',
            'Numerical simulations in gravitation & astrophysics',
            'Optical, UV, & IR astronomy',
            'Particle astrophysics',
            'Particle dark matter',
            'Planetary satellites & rings',
            'Planets & planetary systems',
            'Pre-main-sequence stars',
            'Primordial magnetic fields',
            'Quantum aspects of black holes',
            'Quantum cosmology',
            'Quantum fields in curved spacetime',
            'Quantum gravity',
            'Radio, microwave, & sub-mm astronomy',
            'Relativistic aspects of cosmology',
            'Singularities In general relativity',
            'Sky surveys',
            'Solar neutrinos',
            'Solar system & its planets',
            'Solid-surface planets',
            'Space & astrophysical plasma',
            'Space charge in beams',
            'Space science',
            'Space weather',
            'Spacetime symmetries',
            'Spacetime topology & causal structure',
            'Stars',
            'Stellar plasmas',
            'Sun',
            'Supergravity',
            'Supernova remnants',
            'Telescopes',
            'Transient & explosive astronomical phenomena',
            'Unruh effect',
            'Variable & peculiar stars',
            'X ray astronomy',
            'X ray bursts',
            'r process',
            's process'
]

JATS_TAGS_DANGER = ['php','script','css']

JATS_TAGS_MATH = ['inline-formula',
            'mml:math',
            'mml:semantics', 
            'mml:mrow', 
            'mml:munder', 
            'mml:mo', 
            'mml:mi', 
            'mml:msub', 
            'mml:mover', 
            'mml:mn', 
            'mml:annotation'
]

JATS_TAGS_HTML = ['sub','sup','a','astrobj']

JATS_TAGSET = {'title':JATS_TAGS_MATH + JATS_TAGS_HTML,
            'abstract':JATS_TAGS_MATH + JATS_TAGS_HTML + ['pre','br'],
            'comments':JATS_TAGS_MATH + JATS_TAGS_HTML + ['pre','br'],
            'affiliations':['email','orcid'],
            'keywords':['astrobj']
        }




# NAME-PARSING DEFAULTS: used by parsers/arxiv.py

from nameparser import HumanName
from nameparser.config import CONSTANTS
import os

# Name overrides from CLASSIC name parser

AUTH_CONFIG = '/proj/ads/abstracts/config/Authors'
if not os.path.isdir(AUTH_CONFIG):
    AUTH_CONFIG = 'test_data/config'
FIRST_NAMES = AUTH_CONFIG + '/first.dat'
LAST_NAMES = AUTH_CONFIG + '/last.dat'
PREFIX_NAMES = AUTH_CONFIG + '/prefixes.dat'
SUFFIX_NAMES = AUTH_CONFIG + '/suffixes.dat'

# Names/titles being added

# To remove *all* of the preset titles:
CONSTANTS.titles.remove(*CONSTANTS.titles)
CONSTANTS.suffix_acronyms.remove(*CONSTANTS.suffix_acronyms)
CONSTANTS.suffix_not_acronyms.remove(*CONSTANTS.suffix_not_acronyms)

# check for these strings to find collaborations
COLLAB_STRINGS = ['group', 'team', 'collaboration']
COLLAB_REMOVE_THE = False
COLLAB_SPLIT = True

AUTHOR_SEP = ';'
PRIORITY_LAST = True

CONSTANTS.string_format = u'{last}, {first} "{nickname}", {suffix}, {title}'
