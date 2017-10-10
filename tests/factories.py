import factory
from api import models
import pytz
import random

meeting_groups = ('OSF', 'Labs', 'COS')
meeting_suffixes = ('Con', 'Convention')
meetings_location = ('West', 'East', 'North', 'South', 'England', 'Ontario', 'Spain', 'Berlin', 'Cape Horn',
                     'Cancun', 'Southwest', 'Greece', 'Central America', 'Netherlands', 'Midwest', 'New England',
                     'Underground')

# list taken from https://github.com/csheldonhess/FakeConsumer/blob/master/faker/providers/science.py. Thank you!!
word_list = ('abiosis', 'abrade', 'absorption', 'acceleration', 'accumulation',
             'acid', 'acidic', 'activist', 'adaptation', 'agonistic', 'agrarian', 'airborne',
             'alchemist', 'alignment', 'allele', 'alluvial', 'alveoli', 'ambiparous',
             'amphibian', 'amplitude', 'analysis', 'ancestor', 'anodize', 'anomaly',
             'anther', 'antigen', 'apiary', 'apparatus', 'application', 'approximation',
             'aquatic', 'aquifer', 'arboreal', 'archaeology', 'artery', 'assessment',
             'asteroid', 'atmosphere', 'atomic', 'atrophy', 'attenuate', 'aven', 'aviary',
             'axis', 'bacteria', 'balance', 'bases', 'biome', 'biosphere', 'black hole',
             'blight', 'buoyancy', 'calcium', 'canopy', 'capacity', 'capillary', 'carapace',
             'carcinogen', 'catalyst', 'cauldron', 'celestial', 'cells', 'centigrade',
             'centimeter', 'centrifugal', 'chemical reaction', 'chemicals', 'chemistry',
             'chlorophyll', 'choked', 'chromosome', 'chronic', 'churn', 'classification',
             'climate', 'cloud', 'comet', 'composition', 'compound', 'compression',
             'condensation', 'conditions', 'conduction', 'conductivity', 'conservation',
             'constant', 'constellation', 'continental', 'convection', 'convention', 'cool',
             'core', 'cosmic', 'crater', 'creature', 'crepuscular', 'crystals', 'cycle', 'cytoplasm',
             'dampness', 'data', 'decay', 'decibel', 'deciduous', 'defoliate', 'density',
             'denude', 'dependency', 'deposits', 'depth', 'desiccant', 'detritus',
             'development', 'digestible', 'diluted', 'direction', 'disappearance', 'discovery',
             'dislodge', 'displace', 'dissection', 'dissolution', 'dissolve', 'distance',
             'diurnal', 'diverse', 'doldrums', 'dynamics', 'earthquake', 'eclipse', 'ecology',
             'ecosystem', 'electricity', 'elements', 'elevation', 'embryo', 'endangered',
             'endocrine', 'energy', 'entropy', 'environment', 'enzyme', 'epidermis', 'epoch',
             'equilibrium', 'equine', 'erosion', 'essential', 'estuary', 'ethical', 'evaporation',
             'event', 'evidence', 'evolution', 'examination', 'existence', 'expansion',
             'experiment', 'exploration ', 'extinction', 'extreme', 'facet', 'fault', 'fauna',
             'feldspar', 'fermenting', 'fission', 'fissure', 'flora', 'flourish', 'flowstone',
             'foliage', 'food chain', 'forage', 'force', 'forecast', 'forensics', 'formations',
             'fossil fuel', 'frequency', 'friction', 'fungi', 'fusion', 'galaxy', 'gastric',
             'geo-science', 'geothermal', 'germination', 'gestation', 'global', 'gravitation',
             'green', 'greenhouse effect', 'grotto', 'groundwater', 'habitat', 'heat', 'heavens',
             'hemisphere', 'hemoglobin', 'herpetologist', 'hormones', 'host', 'humidity', 'hyaline',
             'hydrogen', 'hydrology', 'hypothesis', 'ichthyology', 'illumination', 'imagination',
             'impact of', 'impulse', 'incandescent', 'indigenous', 'inertia', 'inevitable', 'inherit',
             'inquiry', 'insoluble', 'instinct', 'instruments', 'integrity', 'intelligence',
             'interacts with', 'interdependence', 'interplanetary', 'invertebrate', 'investigation',
             'invisible', 'ions', 'irradiate', 'isobar', 'isotope', 'joule', 'jungle', 'jurassic',
             'jutting', 'kilometer', 'kinetics', 'kingdom', 'knot', 'laser', 'latitude', 'lava',
             'lethal', 'life', 'lift', 'light', 'limestone', 'lipid', 'lithosphere', 'load',
             'lodestone', 'luminous', 'luster', 'magma', 'magnet', 'magnetism', 'mangrove', 'mantle',
             'marine', 'marsh', 'mass', 'matter', 'measurements', 'mechanical', 'meiosis', 'meridian',
             'metamorphosis', 'meteor', 'microbes', 'microcosm', 'migration', 'millennia', 'minerals',
             'modulate', 'moisture', 'molecule', 'molten', 'monograph', 'monolith', 'motion',
             'movement', 'mutant', 'mutation', 'mysterious', 'natural', 'navigable', 'navigation',
             'negligence', 'nervous system', 'nesting', 'neutrons', 'niche', 'nocturnal',
             'nuclear energy', 'numerous', 'nurture', 'obsidian', 'ocean', 'oceanography', 'omnivorous',
             'oolites (cave pearls)', 'opaque', 'orbit', 'organ', 'organism', 'ornithology',
             'osmosis', 'oxygen', 'paleontology', 'parallax', 'particle', 'penumbra',
             'percolate', 'permafrost', 'permutation', 'petrify', 'petrograph', 'phenomena',
             'physical property', 'planetary', 'plasma', 'polar', 'pole', 'pollination',
             'polymer', 'population', 'precipitation', 'predator', 'prehensile', 'preservation',
             'preserve', 'pressure', 'primate', 'pristine', 'probe', 'process', 'propagation',
             'properties', 'protected', 'proton', 'pulley', 'qualitative data', 'quantum', 'quark',
             'quarry', 'radiation', 'radioactivity', 'rain forest', 'ratio', 'reaction', 'reagent',
             'realm', 'redwoods', 'reeds', 'reflection', 'refraction', 'relationships between', 'reptile',
             'research', 'resistance', 'resonate', 'rookery', 'rubble', 'runoff', 'salinity', 'sandbar',
             'satellite', 'saturation', 'scientific investigation', 'scientist\'s', 'sea floor', 'season',
             'sedentary', 'sediment', 'sedimentary', 'seepage', 'seismic', 'sensors', 'shard',
             'similarity', 'solar', 'soluble', 'solvent', 'sonic', 'sound', 'source', 'species',
             'spectacular', 'spectrum', 'speed', 'sphere', 'spring', 'stage', 'stalactite',
             'stalagmites', 'stimulus', 'substance', 'subterranean', 'sulfuric acid', 'surface',
             'survival', 'swamp', 'sylvan', 'symbiosis', 'symbol', 'synergy', 'synthesis', 'taiga',
             'taxidermy', 'technology', 'tectonics', 'temperate', 'temperature', 'terrestrial',
             'thermals', 'thermometer', 'thrust', 'torque', 'toxin', 'trade winds', 'pterodactyl',
             'transformation tremors', 'tropical', 'umbra', 'unbelievable', 'underwater', 'unearth',
             'unique', 'unite', 'unity', 'universal', 'unpredictable', 'unusual', 'ursine', 'vacuole',
             'valuable', 'vapor', 'variable', 'variety', 'vast', 'velocity', 'ventifact', 'verdant',
             'vespiary', 'viable', 'vibration', 'virus', 'viscosity', 'visible', 'vista', 'vital',
             'vitreous', 'volt', 'volume', 'vulpine', 'wave', 'wax', 'weather', 'westerlies', 'wetlands',
             'whitewater', 'xeriscape', 'xylem', 'yield', 'zero-impact', 'zone', 'zygote', 'achieving',
             'acquisition of', 'an alternative', 'analysis of', 'approach toward', 'area', 'aspects of',
             'assessment of', 'assuming', 'authority', 'available', 'benefit of', 'circumstancial',
             'commentary', 'components', 'concept of', 'consistent', 'corresponding', 'criteria',
             'data', 'deduction', 'demonstrating', 'derived', 'distribution', 'dominant', 'elements',
             'equation', 'estimate', 'evaluation', 'factors', 'features', 'final', 'function',
             'initial', 'instance ', 'interpretation of', 'maintaining ', 'method', 'perceived',
             'percent', 'period', 'positive', 'potential', 'previous', 'primary', 'principle',
             'procedure', 'process', 'range', 'region', 'relevant', 'required', 'research',
             'resources', 'response', 'role', 'section', 'select', 'significant ', 'similar',
             'source', 'specific', 'strategies', 'structure', 'theory', 'transfer', 'variables',
             'corvidae', 'passerine', 'Pica pica', 'Chinchilla lanigera', 'Nymphicus hollandicus',
             'Melopsittacus undulatus',)


def meeting_title():
    return random.choice(word_list).title() + ' ' \
           + random.choice(meetings_location) + ' ' \
           + str(random.randint(2005, 2020))


def science_word():
    return random.choice(word_list)


def science_words(words=6):
    return [science_word() for _ in range(0, words)]


def science_sentence(words=6):
    _words = science_words(words=words)
    _words[0] = _words[0].title()
    return ' '.join(_words) + '.'


def science_tags(tags=5):
    return ', '.join(science_words(words=tags))


def science_sentences(sentences=5):
    return [science_sentence() for _ in range(0, sentences)]


def science_paragraph(sentences=5):
    return ' '.join(science_sentences(sentences=sentences))


def science_description(paragraphs=3):
    return '\n\n'.join([science_paragraph() for _ in range(0, paragraphs)])


class UserFactory(factory.Factory):
    class Meta:
        model = models.User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.LazyAttribute(
        lambda u: (str(u.first_name)[0] + str(u.last_name)).lower()
    )
    password = factory.PostGenerationMethodCall('set_password', 'password123')


class ItemFactory(factory.Factory):
    class Meta:
        model = models.Item

    title = factory.LazyFunction(science_sentence)
    description = factory.LazyFunction(science_description)
    status = 'approved'
    source_id = 'xrfye'


class CollectionFactory(factory.Factory):
    class Meta:
        model = models.Collection

    title = factory.LazyFunction(meeting_title)
    description = factory.LazyFunction(science_paragraph)
    tags = factory.LazyFunction(science_tags)
    settings = {}
    submission_settings = {}
    collection_type = "meeting"


class MeetingFactory(CollectionFactory):
    collection_type = "meeting"
    address = factory.Faker('address')
    location = factory.Faker('city')
    start_datetime = factory.Faker('date_time_between', start_date="-1w", end_date="-1d",
                                   tzinfo=pytz.timezone('US/Eastern'))
    end_datetime = factory.Faker('date_time_between', start_date="+1d", end_date="+1w",
                                 tzinfo=pytz.timezone('US/Eastern'))
