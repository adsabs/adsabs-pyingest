import json
import urllib


def find(key,dictionary):
    for k,v in dictionary.iteritems():
        if k == key:
            yield v
        elif isinstance(v,dict):
            for result in find(key,v):
                yield result
        elif isinstance(v,list):
            for d in v:
                for result in find(key,d):
                    yield result


MONTH_TO_NUMBER = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6,
                   'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12}
# APS Journal dictionary: used by parsers/aps.py to get the bibstem

APS_PUBLISHER_IDS = {'PRL': 'PhRvL', 'PRX': 'PhRvX', 'RMP': 'RvMP',
                     'PRA': 'PhRvA', 'PRB': 'PhRvB', 'PRC': 'PhRvC',
                     'PRD': 'PhRvD', 'PRE': 'PhRvE', 'PRAB': 'PhRvS',
                     'PRSTAB': 'PhRvS', 'PRAPPLIED': 'PhRvP',
                     'PRFLUIDS': 'PhRvF', 'PRMATERIALS': 'PhRvM',
                     'PRPER': 'PRPER', 'PRSTPER': 'PRSTP', 'PR': 'PhRv',
                     'PRI': 'PhRvI','PHYSICS': 'PhyOJ'}


IOP_PUBLISHER_IDS = {'rnaas': u'RNAAS', 'apj': u'ApJ', 'apjs': u'ApJS', 'apjl': u'ApJL', 'aj': 'AJ', 'jcap': u'JCAP', 'pasp': u'PASP'}
IOP_JOURNAL_NAMES = {'rnaas': u'Research Notes of the American Astronomical Society'}

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

# KEYWORDS

# Unified Astronomy Thesaurus
# retrieve current UAT from github
UAT_URL = 'https://raw.githubusercontent.com/astrothesaurus/UAT/master/UAT.json'
remote = urllib.urlopen(UAT_URL)
UAT_json = json.loads(remote.read())
UAT_ASTRO_KEYWORDS =  list(find('name', UAT_json))

# American Astronomical Society (superseded June 2019 by UAT)
AAS_ASTRO_KEYWORDS = [
            'General',
            'editorials, notices',
            'errata, addenda',
            'extraterrestrial intelligence',
            'history and philosophy of astronomy',
            'miscellaneous',
            'obituaries, biographies',
            'publications, bibliography',
            'sociology of astronomy',
            'standards',
            'Physical Data and Processes',
            'acceleration of particles',
            'accretion, accretion disks',
            'asteroseismology',
            'astrobiology',
            'astrochemistry',
            'astroparticle physics',
            'atomic data',
            'atomic processes',
            'black hole physics',
            'chaos',
            'conduction',
            'convection',
            'dense matter',
            'diffusion',
            'dynamo',
            'elementary particles',
            'equation of state',
            'gravitation',
            'gravitational lensing: strong',
            'gravitational lensing: weak',
            'gravitational lensing: micro',
            'gravitational waves',
            'hydrodynamics',
            'instabilities',
            'line: formation',
            'line: identification',
            'line: profiles',
            'magnetic fields',
            'magnetic reconnection',
            'magnetohydrodynamics (MHD)',
            'masers',
            'molecular data',
            'molecular processes',
            'neutrinos',
            'nuclear reactions, nucleosynthesis, abundances',
            'opacity',
            'plasmas',
            'polarization',
            'radiation: dynamics',
            'radiation mechanisms: general',
            'radiation mechanisms: non-thermal',
            'radiation mechanisms: thermal',
            'radiative transfer',
            'relativistic processes',
            'scattering',
            'shock waves',
            'solid state: refractory',
            'solid state: volatile',
            'turbulence',
            'waves',
            'Astronomical Instrumentation, Methods and Techniques',
            'atmospheric effects',
            'balloons',
            'instrumentation: adaptive optics',
            'instrumentation: detectors',
            'instrumentation: high angular resolution',
            'instrumentation: interferometers',
            'instrumentation: miscellaneous',
            'instrumentation: photometers',
            'instrumentation: polarimeters',
            'instrumentation: spectrographs',
            'light pollution',
            'methods: analytical',
            'methods: data analysis',
            'methods: laboratory: atomic',
            'methods: laboratory: molecular',
            'methods: laboratory: solid state',
            'methods: miscellaneous',
            'methods: numerical',
            'methods: observational',
            'methods: statistical',
            'site testing',
            'space vehicles',
            'space vehicles: instruments',
            'techniques: high angular resolution',
            'techniques: image processing',
            'techniques: imaging spectroscopy',
            'techniques: interferometric',
            'techniques: miscellaneous',
            'techniques: photometric',
            'techniques: polarimetric',
            'techniques: radar astronomy',
            'techniques: radial velocities',
            'techniques: spectroscopic',
            'telescopes',
            'Astronomical Databases',
            'astronomical databases: miscellaneous',
            'atlases',
            'catalogs',
            'surveys',
            'virtual observatory tools',
            'Astrometry and Celestial Mechanics',
            'astrometry',
            'celestial mechanics',
            'eclipses',
            'ephemerides',
            'occultations',
            'parallaxes',
            'proper motions',
            'reference systems',
            'time',
            'The Sun',
            'Sun: abundances',
            'Sun: activity',
            'Sun: atmosphere',
            'Sun: chromosphere',
            'Sun: corona',
            'Sun: coronal mass ejections (CMEs)',
            'Sun: evolution',
            'Sun: faculae, plages',
            'Sun: filaments, prominences',
            'Sun: flares',
            'Sun: fundamental parameters',
            'Sun: general',
            'Sun: granulation',
            'Sun: helioseismology',
            'Sun: heliosphere',
            'Sun: infrared',
            'Sun: interior',
            'Sun: magnetic fields',
            'Sun: oscillations',
            'Sun: particle emission',
            'Sun: photosphere',
            'Sun: radio radiation',
            'Sun: rotation',
            '(Sun:) solar-terrestrial relations',
            '(Sun:) solar wind',
            '(Sun:) sunspots',
            'Sun: transition region',
            'Sun: UV radiation',
            'Sun: X-rays, gamma rays',
            'Planetary Systems',
            'comets: general',
            'comets: individual (_, _)',
            'Earth',
            'interplanetary medium',
            'Kuiper belt: general',
            'Kuiper belt objects: individual (_, _)',
            'meteorites, meteors, meteoroids',
            'minor planets, asteroids: general',
            'minor planets, asteroids: individual (_, _)',
            'Moon',
            'Oort Cloud',
            'planets and satellites: atmospheres',
            'planets and satellites: aurorae',
            'planets and satellites: composition',
            'planets and satellites: detection',
            'planets and satellites: dynamical evolution and stability',
            'planets and satellites: formation',
            'planets and satellites: fundamental parameters',
            'planets and satellites: gaseous planets',
            'planets and satellites: general',
            'planets and satellites: individual (_, _)',
            'planets and satellites: interiors',
            'planets and satellites: magnetic fields',
            'planets and satellites: oceans',
            'planets and satellites: physical evolution',
            'planets and satellites: rings',
            'planets and satellites: surfaces',
            'planets and satellites: tectonics',
            'planets and satellites: terrestrial planets',
            'protoplanetary disks',
            'planet-disk interactions',
            'planet-star interactions',
            'zodiacal dust',
            'Stars',
            'stars: abundances',
            'stars: activity',
            'stars: AGB and post-AGB',
            'stars: atmospheres',
            '(stars:) binaries (including multiple): close',
            '(stars:) binaries: eclipsing',
            '(stars:) binaries: general',
            '(stars:) binaries: spectroscopic',
            '(stars:) binaries: symbiotic',
            '(stars:) binaries: visual',
            'stars: black holes',
            '(stars:) blue stragglers',
            '(stars:) brown dwarfs',
            'stars: carbon',
            'stars: chemically peculiar',
            'stars: chromospheres',
            '(stars:) circumstellar matter',
            'stars: coronae',
            'stars: distances',
            'stars: dwarf novae',
            'stars: early-type',
            'stars: emission-line, Be',
            'stars: evolution',
            'stars: flare',
            'stars: formation',
            'stars: fundamental parameters',
            'stars: general',
            '(stars:) gamma-ray burst: general',
            '(stars:) gamma-ray burst: individual (_, _)',
            '(stars:) Hertzsprung-Russell and C-M diagrams',
            'stars: horizontal-branch',
            'stars: imaging',
            'stars: individual (_, _)',
            'stars: interiors',
            'stars: jets',
            'stars: kinematics and dynamics',
            'stars: late-type',
            'stars: low-mass',
            'stars: luminosity function, mass function',
            'stars: magnetars',
            'stars: magnetic field',
            'stars: massive',
            'stars: mass-loss',
            'stars: neutron',
            '(stars:) novae, cataclysmic variables',
            'stars: oscillations (including pulsations)',
            'stars: peculiar (except chemically peculiar)',
            '(stars:) planetary systems',
            'stars: Population II',
            'stars: Population III',
            'stars: pre-main sequence',
            'stars: protostars',
            '(stars:) pulsars: general',
            '(stars:) pulsars: individual (_, _)',
            'stars: rotation',
            'stars: solar-type',
            '(stars:) starspots',
            'stars: statistics',
            '(stars:) subdwarfs',
            '(stars:) supergiants',
            '(stars:) supernovae: general',
            '(stars:) supernovae: individual (_, _)',
            'stars: variables: Cepheids',
            'stars: variables: delta Scuti',
            'stars: variables: general',
            'stars: variables: RR Lyrae',
            'stars: variables: S Doradus',
            'stars: variables: T Tauri, Herbig Ae/Be',
            '(stars:) white dwarfs',
            'stars: winds, outflows',
            'stars: Wolf-Rayet',
            'Interstellar Medium (ISM), Nebulae',
            'ISM: abundances',
            'ISM: atoms',
            'ISM: bubbles',
            'ISM: clouds',
            '(ISM:) cosmic rays',
            '(ISM:) dust, extinction',
            '(ISM:) evolution',
            'ISM: general',
            '(ISM:) HII regions',
            '(ISM:) Herbig-Haro objects',
            'ISM: individual objects (_, _) (except',
            'planetary nebulae)',
            'ISM: jets and outflows',
            'ISM: kinematics and dynamics',
            'ISM: lines and bands',
            'ISM: magnetic fields',
            'ISM: molecules',
            '(ISM:) planetary nebulae: general',
            '(ISM:) planetary nebulae: individual (_, _)',
            '(ISM:) photon-dominated region (PDR)',
            'ISM: structure',
            'ISM: supernova remnants',
            'The Galaxy',
            'Galaxy: abundances',
            'Galaxy: bulge',
            'Galaxy: center',
            'Galaxy: disk',
            'Galaxy: evolution',
            'Galaxy: formation',
            'Galaxy: fundamental parameters',
            'Galaxy: general',
            '(Galaxy:) globular clusters: general',
            '(Galaxy:) globular clusters: individual (_, _)',
            'Galaxy: halo',
            '(Galaxy:) local interstellar matter',
            'Galaxy: kinematics and dynamics',
            'Galaxy: nucleus',
            '(Galaxy:) open clusters and associations: general',
            '(Galaxy:) open clusters and associations: individual (_, _)',
            '(Galaxy:) solar neighborhood',
            'Galaxy: stellar content',
            'Galaxy: structure',
            'Galaxies',
            'galaxies: abundances',
            'galaxies: active',
            '(galaxies:) BL Lacertae objects: general',
            '(galaxies:) BL Lacertae objects: individual (_, _)',
            'galaxies: bulges',
            'galaxies: clusters: general',
            'galaxies: clusters: individual (_, _)',
            'galaxies: clusters: intracluster medium',
            'galaxies: distances and redshifts',
            'galaxies: dwarf',
            'galaxies: elliptical and lenticular, cD',
            'galaxies: evolution',
            'galaxies: formation',
            'galaxies: fundamental parameters',
            'galaxies: general',
            'galaxies: groups: general',
            'galaxies: groups: individual (_, _)',
            'galaxies: halos',
            'galaxies: high-redshift',
            'galaxies: individual (_, _)',
            'galaxies: interactions',
            '(galaxies:) intergalactic medium',
            'galaxies: irregular',
            'galaxies: ISM',
            'galaxies: jets',
            'galaxies: kinematics and dynamics',
            '(galaxies:) Local Group',
            'galaxies: luminosity function, mass function',
            '(galaxies:) Magellanic Clouds',
            'galaxies: magnetic fields',
            'galaxies: nuclei',
            'galaxies: peculiar',
            'galaxies: photometry',
            '(galaxies:) quasars: absorption lines',
            '(galaxies:) quasars: emission lines',
            '(galaxies:) quasars: general',
            '(galaxies:) quasars: individual (_, _)',
            '(galaxies:) quasars: supermassive black holes',
            'galaxies: Seyfert',
            'galaxies: spiral',
            'galaxies: starburst',
            'galaxies: star clusters: general',
            'galaxies: star clusters: individual (_, _)',
            'galaxies: star formation',
            'galaxies: statistics',
            'galaxies: stellar content',
            'galaxies: structure',
            'Cosmology',
            '(cosmology:) cosmic background radiation',
            '(cosmology:) cosmological parameters',
            'cosmology: miscellaneous',
            'cosmology: observations',
            'cosmology: theory',
            '(cosmology:) dark ages, reionization, first stars',
            '(cosmology:) dark matter',
            '(cosmology:) dark energy',
            '(cosmology:) diffuse radiation',
            '(cosmology:) distance scale',
            '(cosmology:) early universe',
            '(cosmology:) inflation',
            '(cosmology:) large-scale structure of universe',
            '(cosmology:) primordial nucleosynthesis',
            'Resolved and Unresolved Sources as a Function of Wavelength',
            'gamma rays: diffuse background',
            'gamma rays: galaxies',
            'gamma rays: galaxies: clusters',
            'gamma rays: general',
            'gamma rays: ISM',
            'gamma rays: stars',
            'infrared: diffuse background',
            'infrared: galaxies',
            'infrared: general',
            'infrared: ISM',
            'infrared: planetary systems',
            'infrared: stars',
            'radio continuum: galaxies',
            'radio continuum: general',
            'radio continuum: ISM',
            'radio continuum: planetary systems',
            'radio continuum: stars',
            'radio lines: galaxies',
            'radio lines: general',
            'radio lines: ISM',
            'radio lines: planetary systems',
            'radio lines: stars',
            'submillimeter: diffuse background',
            'submillimeter: galaxies',
            'submillimeter: general',
            'submillimeter: ISM',
            'submillimeter: planetary systems',
            'submillimeter: stars',
            'ultraviolet: galaxies',
            'ultraviolet: general',
            'ultraviolet: ISM',
            'ultraviolet: planetary systems',
            'ultraviolet: stars',
            'X-rays: binaries',
            'X-rays: bursts',
            'X-rays: diffuse background',
            'X-rays: galaxies',
            'X-rays: galaxies: clusters',
            'X-rays: general',
            'X-rays: individual (_, _)',
            'X-rays: ISM',
            'X-rays: stars'
]

# American Physical Society
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
