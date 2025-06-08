import asyncio
import pyodide_http
from pyodide import http
import struct
from typing import Optional
import json
from bisect import bisect_right

# The growth rate tables were retreived using PokeAPI, which uses different names for a few of them.
# medium              = Medium Fast
# slow-then-very-fast = Erractic
# fast-then-very-slow = Fluctuating

exp_tables = {
    'fast': [
        0,
        0,
        6,
        21,
        51,
        100,
        172,
        274,
        409,
        583,
        800,
        1064,
        1382,
        1757,
        2195,
        2700,
        3276,
        3930,
        4665,
        5487,
        6400,
        7408,
        8518,
        9733,
        11059,
        12500,
        14060,
        15746,
        17561,
        19511,
        21600,
        23832,
        26214,
        28749,
        31443,
        34300,
        37324,
        40522,
        43897,
        47455,
        51200,
        55136,
        59270,
        63605,
        68147,
        72900,
        77868,
        83058,
        88473,
        94119,
        100000,
        106120,
        112486,
        119101,
        125971,
        133100,
        140492,
        148154,
        156089,
        164303,
        172800,
        181584,
        190662,
        200037,
        209715,
        219700,
        229996,
        240610,
        251545,
        262807,
        274400,
        286328,
        298598,
        311213,
        324179,
        337500,
        351180,
        365226,
        379641,
        394431,
        409600,
        425152,
        441094,
        457429,
        474163,
        491300,
        508844,
        526802,
        545177,
        563975,
        583200,
        602856,
        622950,
        643485,
        664467,
        685900,
        707788,
        730138,
        752953,
        776239,
        800000
    ],
    'medium': [
        0,
        1,
        8,
        27,
        64,
        125,
        216,
        343,
        512,
        729,
        1000,
        1331,
        1728,
        2197,
        2744,
        3375,
        4096,
        4913,
        5832,
        6859,
        8000,
        9261,
        10648,
        12167,
        13824,
        15625,
        17576,
        19683,
        21952,
        24389,
        27000,
        29791,
        32768,
        35937,
        39304,
        42875,
        46656,
        50653,
        54872,
        59319,
        64000,
        68921,
        74088,
        79507,
        85184,
        91125,
        97336,
        103823,
        110592,
        117649,
        125000,
        132651,
        140608,
        148877,
        157464,
        166375,
        175616,
        185193,
        195112,
        205379,
        216000,
        226981,
        238328,
        250047,
        262144,
        274625,
        287496,
        300763,
        314432,
        328509,
        343000,
        357911,
        373248,
        389017,
        405224,
        421875,
        438976,
        456533,
        474552,
        493039,
        512000,
        531441,
        551368,
        571787,
        592704,
        614125,
        636056,
        658503,
        681472,
        704969,
        729000,
        753571,
        778688,
        804357,
        830584,
        857375,
        884736,
        912673,
        941192,
        970299,
        1000000
    ],
    'medium-slow': [
        0,
        -53,
        9,
        57,
        96,
        135,
        179,
        236,
        314,
        419,
        560,
        742,
        973,
        1261,
        1612,
        2035,
        2535,
        3120,
        3798,
        4575,
        5460,
        6458,
        7577,
        8825,
        10208,
        11735,
        13411,
        15244,
        17242,
        19411,
        21760,
        24294,
        27021,
        29949,
        33084,
        36435,
        40007,
        43808,
        47846,
        52127,
        56660,
        61450,
        66505,
        71833,
        77440,
        83335,
        89523,
        96012,
        102810,
        109923,
        117360,
        125126,
        133229,
        141677,
        150476,
        159635,
        169159,
        179056,
        189334,
        199999,
        211060,
        222522,
        234393,
        246681,
        259392,
        272535,
        286115,
        300140,
        314618,
        329555,
        344960,
        360838,
        377197,
        394045,
        411388,
        429235,
        447591,
        466464,
        485862,
        505791,
        526260,
        547274,
        568841,
        590969,
        613664,
        636935,
        660787,
        685228,
        710266,
        735907,
        762160,
        789030,
        816525,
        844653,
        873420,
        902835,
        932903,
        963632,
        995030,
        1027103,
        1059860
    ],
    'slow': [
        0,
        1,
        10,
        33,
        80,
        156,
        270,
        428,
        640,
        911,
        1250,
        1663,
        2160,
        2746,
        3430,
        4218,
        5120,
        6141,
        7290,
        8573,
        10000,
        11576,
        13310,
        15208,
        17280,
        19531,
        21970,
        24603,
        27440,
        30486,
        33750,
        37238,
        40960,
        44921,
        49130,
        53593,
        58320,
        63316,
        68590,
        74148,
        80000,
        86151,
        92610,
        99383,
        106480,
        113906,
        121670,
        129778,
        138240,
        147061,
        156250,
        165813,
        175760,
        186096,
        196830,
        207968,
        219520,
        231491,
        243890,
        256723,
        270000,
        283726,
        297910,
        312558,
        327680,
        343281,
        359370,
        375953,
        393040,
        410636,
        428750,
        447388,
        466560,
        486271,
        506530,
        527343,
        548720,
        570666,
        593190,
        616298,
        640000,
        664301,
        689210,
        714733,
        740880,
        767656,
        795070,
        823128,
        851840,
        881211,
        911250,
        941963,
        973360,
        1005446,
        1038230,
        1071718,
        1105920,
        1140841,
        1176490,
        1212873,
        1250000
    ],
    'slow-then-very-fast': [
        0,
        1,
        15,
        52,
        122,
        237,
        406,
        637,
        942,
        1326,
        1800,
        2369,
        3041,
        3822,
        4719,
        5737,
        6881,
        8155,
        9564,
        11111,
        12800,
        14632,
        16610,
        18737,
        21012,
        23437,
        26012,
        28737,
        31610,
        34632,
        37800,
        41111,
        44564,
        48155,
        51881,
        55737,
        59719,
        63822,
        68041,
        72369,
        76800,
        81326,
        85942,
        90637,
        95406,
        100237,
        105122,
        110052,
        115015,
        120001,
        125000,
        131324,
        137795,
        144410,
        151165,
        158056,
        165079,
        172229,
        179503,
        186894,
        194400,
        202013,
        209728,
        217540,
        225443,
        233431,
        241496,
        249633,
        257834,
        267406,
        276915,
        286567,
        296358,
        306286,
        316344,
        326531,
        336840,
        347269,
        357812,
        368464,
        379221,
        390077,
        401028,
        412067,
        423190,
        434391,
        445663,
        457001,
        468398,
        479848,
        491346,
        502883,
        514453,
        526049,
        537664,
        549291,
        560922,
        572550,
        584166,
        591882,
        600000
    ],
    'fast-then-very-slow': [
        0,
        0,
        4,
        13,
        32,
        65,
        113,
        182,
        276,
        398,
        553,
        745,
        979,
        1259,
        1591,
        1980,
        2457,
        3046,
        3732,
        4526,
        5440,
        6482,
        7666,
        9003,
        10506,
        12187,
        14060,
        16140,
        18439,
        20974,
        23760,
        26811,
        30146,
        33780,
        37731,
        42017,
        46656,
        50653,
        55969,
        60505,
        66560,
        71677,
        78533,
        84277,
        91998,
        98415,
        107069,
        114205,
        123863,
        131766,
        142500,
        151222,
        163105,
        172697,
        185807,
        196322,
        210739,
        222231,
        238036,
        250562,
        267840,
        281456,
        300293,
        315059,
        335544,
        351520,
        373744,
        390991,
        415050,
        433631,
        459620,
        479600,
        507617,
        529063,
        559209,
        582187,
        614566,
        639146,
        673863,
        700115,
        737280,
        765275,
        804997,
        834809,
        877201,
        908905,
        954084,
        987754,
        1035837,
        1071552,
        1122660,
        1160499,
        1214753,
        1254796,
        1312322,
        1354652,
        1415577,
        1460276,
        1524731,
        1571884,
        1640000
    ]
}

growth_rates = {
    "gossifleur": "medium",
    "combee": "medium-slow",
    "cherubi": "medium",
    "kricketot": "medium-slow",
    "ledyba": "fast",
    "sunkern": "medium-slow",
    "oddish": "medium-slow",
    "bellsprout": "medium-slow",
    "chikorita": "medium-slow",
    "hoppip": "medium-slow",
    "lotad": "medium-slow",
    "seedot": "medium-slow",
    "surskit": "medium",
    "sewaddle": "medium-slow",
    "cottonee": "medium",
    "petilil": "medium",
    "karrablast": "medium",
    "shelmet": "medium",
    "grubbin": "medium",
    "cutiefly": "medium",
    "smoliv": "medium-slow",
    "tarountula": "slow-then-very-fast",
    "nymble": "medium",
    "bounsweet": "medium-slow",
    "caterpie": "medium",
    "weedle": "medium",
    "wurmple": "medium",
    "scatterbug": "medium",
    "blipbug": "medium",
    "sizzlipede": "medium",
    "rattata": "medium",
    "meowth": "medium",
    "mankey": "medium",
    "machop": "medium-slow",
    "eevee": "medium",
    "sentret": "medium",
    "snubbull": "fast",
    "teddiursa": "medium",
    "poochyena": "medium",
    "zigzagoon": "medium",
    "ralts": "slow",
    "torchic": "medium-slow",
    "whismur": "medium-slow",
    "skitty": "fast",
    "vulpix": "medium",
    "cyndaquil": "medium-slow",
    "bidoof": "medium",
    "buizel": "medium",
    "glameow": "fast",
    "patrat": "medium",
    "lillipup": "medium-slow",
    "purrloin": "medium",
    "timburr": "medium-slow",
    "darumaka": "medium-slow",
    "scraggy": "medium",
    "minccino": "fast",
    "mienfoo": "medium-slow",
    "bunnelby": "medium",
    "pancham": "medium",
    "yungoos": "medium",
    "shroodle": "medium-slow",
    "maschiff": "medium-slow",
    "pawmi": "medium",
    "tandemaus": "fast",
    "lechonk": "medium",
    "zigzagoon-galar": "medium",
    "skwovet": "medium",
    "meowth-alola": "medium",
    "rattata-alola": "medium",
    "nickit": "fast",
    "wooloo": "medium",
    "wooper-paldea": "medium",
    "wooper": "medium",
    "mudkip": "medium-slow",
    "shellos": "medium",
    "skorupi": "slow",
    "croagunk": "medium",
    "tympole": "medium-slow",
    "goomy": "slow",
    "fuecoco": "medium-slow",
    "sobble": "medium-slow",
    "tadbulb": "medium",
    "wattrel": "medium-slow",
    "popplio": "medium-slow",
    "crabrawler": "medium",
    "wingull": "medium",
    "krabby": "medium",
    "wimpod": "medium",
    "sandygast": "medium",
    "dreepy": "slow",
    "mareanie": "medium",
    "wiglett": "medium",
    "tentacool": "slow",
    "frillish": "medium",
    "horsea": "medium",
    "staryu": "slow",
    "dratini": "slow",
    "remoraid": "medium",
    "carvanha": "slow",
    "wailmer": "fast-then-very-slow",
    "corphish": "fast-then-very-slow",
    "clamperl": "slow-then-very-fast",
    "inkay": "medium",
    "binacle": "medium",
    "skrelp": "medium",
    "clauncher": "slow",
    "finizen": "slow",
    "clobbopus": "medium-slow",
    "arrokuda": "slow",
    "spheal": "medium-slow",
    "seel": "medium",
    "shellder": "slow",
    "bergmite": "medium",
    "pidgey": "medium-slow",
    "spearow": "medium",
    "doduo": "medium",
    "hoothoot": "medium",
    "natu": "medium",
    "taillow": "medium-slow",
    "starly": "medium-slow",
    "pidove": "medium-slow",
    "rufflet": "slow",
    "vullaby": "slow",
    "fletchling": "medium-slow",
    "pikipek": "medium",
    "rookidee": "medium-slow",
    "ekans": "medium",
    "nidoran-f": "medium-slow",
    "nidoran-m": "medium-slow",
    "mareep": "medium-slow",
    "lickitung": "medium",
    "dunsparce": "medium",
    "growlithe": "slow",
    "ponyta": "medium",
    "electrike": "slow",
    "gulpin": "fast-then-very-slow",
    "shinx": "medium-slow",
    "stunky": "medium",
    "tepig": "medium-slow",
    "blitzle": "medium",
    "litleo": "medium-slow",
    "flabebe": "medium",
    "spritzee": "medium",
    "swirlix": "medium",
    "deerling": "medium",
    "scorbunny": "medium-slow",
    "ponyta-galar": "medium",
    "cufant": "medium",
    "sandshrew": "medium",
    "rhyhorn": "slow",
    "phanpy": "medium",
    "numel": "medium",
    "hippopotas": "slow",
    "skiddo": "medium",
    "rockruff": "medium",
    "nacli": "medium-slow",
    "mudbray": "medium",
    "jangmo-o": "slow",
    "growlithe-hisui": "slow",
    "rolycoly": "medium-slow",
    "trapinch": "medium-slow",
    "cacnea": "medium-slow",
    "sandile": "medium-slow",
    "dwebble": "medium",
    "helioptile": "medium",
    "rellor": "fast",
    "bramblin": "medium",
    "silicobra": "medium",
    "squirtle": "medium-slow",
    "psyduck": "medium",
    "poliwag": "medium-slow",
    "slowpoke": "medium",
    "slowpoke-galar": "medium",
    "goldeen": "medium",
    "magikarp": "slow",
    "totodile": "medium-slow",
    "barboach": "medium",
    "feebas": "slow-then-very-fast",
    "finneon": "slow-then-very-fast",
    "oshawott": "medium-slow",
    "ducklett": "medium",
    "tynamo": "slow",
    "froakie": "medium-slow",
    "quaxly": "medium-slow",
    "dewpider": "medium",
    "chewtle": "medium",
    "diglett": "medium",
    "charmander": "medium-slow",
    "houndour": "slow",
    "zubat": "medium",
    "geodude": "medium-slow",
    "onix": "medium",
    "cubone": "medium",
    "larvitar": "slow",
    "slugma": "medium",
    "makuhita": "fast-then-very-slow",
    "aron": "slow",
    "baltoy": "medium",
    "bagon": "slow",
    "bronzor": "medium",
    "gible": "slow",
    "roggenrola": "medium-slow",
    "woobat": "medium",
    "drilbur": "medium",
    "axew": "slow",
    "deino": "slow",
    "noibat": "medium",
    "salandit": "medium",
    "geodude-alola": "medium-slow",
    "diglett-alola": "medium",
    "swinub": "slow",
    "snorunt": "medium",
    "vanillite": "slow",
    "frigibax": "slow",
    "cetoddle": "medium-slow",
    "sandshrew-alola": "medium",
    "paras": "medium",
    "venonat": "medium",
    "spinarak": "fast",
    "pineco": "medium",
    "bulbasaur": "medium-slow",
    "treecko": "medium-slow",
    "shroomish": "fast-then-very-slow",
    "slakoth": "slow",
    "nincada": "slow-then-very-fast",
    "exeggcute": "slow",
    "turtwig": "medium-slow",
    "chimchar": "medium-slow",
    "burmy": "medium",
    "buneary": "medium",
    "poltchageist": "medium",
    "snivy": "medium-slow",
    "pansage": "medium",
    "pansear": "medium",
    "panpour": "medium",
    "venipede": "medium-slow",
    "foongus": "medium",
    "chespin": "medium-slow",
    "fennekin": "medium-slow",
    "zorua": "medium-slow",
    "phantump": "medium",
    "pumpkaboo": "medium",
    "rowlet": "medium-slow",
    "capsakid": "medium",
    "toedscool": "medium-slow",
    "fomantis": "medium",
    "morelull": "medium",
    "stufful": "medium",
    "grookey": "medium-slow",
    "applin": "slow-then-very-fast",
    "snover": "slow",
    "cubchoo": "medium",
    "zorua-hisui": "medium-slow",
    "darumaka-galar": "medium-slow",
    "vulpix-alola": "medium",
    "snom": "medium",
    "drifloon": "fast-then-very-slow",
    "spoink": "fast",
    "shuppet": "fast",
    "duskull": "fast",
    "yamask": "medium",
    "grimer": "medium",
    "grimer-alola": "medium",
    "gastly": "medium-slow",
    "drowzee": "medium",
    "koffing": "medium",
    "munna": "fast",
    "sinistea": "medium",
    "gothita": "medium-slow",
    "solosis": "medium-slow",
    "litwick": "medium-slow",
    "greavard": "medium-slow",
    "golett": "medium",
    "charcadet": "slow",
    "yamask-galar": "medium",
    "hatenna": "slow",
    "impidimp": "medium",
    "elgyem": "medium",
    "abra": "medium-slow",
    "meditite": "medium",
    "swablu": "slow-then-very-fast",
    "beldum": "slow",
    "larvesta": "slow",
    "espurr": "medium",
    "honedge": "medium",
    "glimmet": "medium-slow",
    "flittle": "medium-slow",
    "cosmog": "slow",
    "poipole": "slow",
    "meltan": "slow",
    "magnemite": "medium",
    "voltorb": "medium",
    "piplup": "medium-slow",
    "chinchou": "slow",
    "gimmighoul-chest": "slow",
    "gimmighoul-roaming": "slow",
    "trubbish": "medium",
    "joltik": "medium",
    "ferroseed": "medium",
    "klink": "medium-slow",
    "pawniard": "medium",
    "varoom": "medium",
    "tinkatink": "medium-slow",
    "litten": "medium-slow",
    "fidough": "medium-slow",
    "sprigatito": "medium-slow",
    "voltorb-hisui": "medium",
    "meowth-galar": "medium",
    "milcery": "medium",
    "yamper": "fast",
    "tangela": "medium",
    "scyther": "medium",
    "porygon": "medium",
    "aipom": "fast",
    "yanma": "medium",
    "murkrow": "medium-slow",
    "misdreavus": "fast",
    "girafarig": "medium",
    "gligar": "medium-slow",
    "sneasel": "medium-slow",
    "stantler": "slow",
    "nosepass": "medium",
    "basculin-white-striped": "medium",
    "type-null": "slow",
    "qwilfish-hisui": "medium",
    "sneasel-hisui": "medium-slow",
    "farfetchd-galar": "medium",
    "corsola-galar": "fast",
    "kubfu": "slow",
    "duraludon": "medium",
    "omanyte": "medium",
    "kabuto": "medium",
    "lileep": "slow-then-very-fast",
    "anorith": "slow-then-very-fast",
    "cranidos": "slow-then-very-fast",
    "shieldon": "slow-then-very-fast",
    "tirtouga": "medium",
    "archen": "medium",
    "tyrunt": "medium",
    "amaura": "medium",
    "pichu": "medium",
    "cleffa": "fast",
    "igglybuff": "fast",
    "togepi": "fast",
    "tyrogue": "medium",
    "smoochum": "medium",
    "elekid": "medium",
    "magby": "medium",
    "azurill": "fast",
    "wynaut": "medium",
    "budew": "medium-slow",
    "chingling": "fast",
    "bonsly": "medium",
    "mime-jr": "medium",
    "happiny": "fast",
    "munchlax": "slow",
    "riolu": "medium-slow",
    "mantyke": "slow",
    "toxel": "medium-slow",
    "deerling-autumn": "medium",
    "deerling-summer": "medium",
    "deerling-winter": "medium",
    "petilil-fighting": "medium",
    "eevee-fire": "medium",
    "eevee-water": "medium",
    "eevee-electric": "medium",
    "eevee-dark": "medium",
    "eevee-psychic": "medium",
    "eevee-grass": "medium",
    "eevee-ice": "medium",
    "eevee-fairy": "medium",
    "charcadet-psychic": "slow",
    "charcadet-ghost": "slow",
    "ralts-fighting": "slow",
    "snorunt-ghost": "medium",
    "wurmple-poison": "medium",
    "nincada-ghost": "slow-then-very-fast",
    "exeggcute-dragon": "slow",
    "koffing-fairy": "medium",
    "rufflet-psychic": "slow",
    "goomy-steel": "slow",
    "bergmite-rock": "medium",
    "froakie-special": "medium-slow",
    "rockruff-special": "medium",
    "feebas-fairy": "slow-then-very-fast"
}

all_moves = [
    'None',
    'Pound',
    'Karate Chop',
    'Double Slap',
    'Comet Punch',
    'Mega Punch',
    'Pay Day',
    'Fire Punch',
    'Ice Punch',
    'Thunder Punch',
    'Scratch',
    'Vise Grip',
    'Guillotine',
    'Razor Wind',
    'Swords Dance',
    'Cut',
    'Gust',
    'Wing Attack',
    'Whirlwind',
    'Fly',
    'Bind',
    'Slam',
    'Vine Whip',
    'Stomp',
    'Double Kick',
    'Mega Kick',
    'Jump Kick',
    'Rolling Kick',
    'Sand-Attack',
    'Headbutt',
    'Horn Attack',
    'Fury Attack',
    'Horn Drill',
    'Tackle',
    'Body Slam',
    'Wrap',
    'Take Down',
    'Thrash',
    'Double-Edge',
    'Tail Whip',
    'Poison Sting',
    'Twineedle',
    'Pin Missile',
    'Leer',
    'Bite',
    'Growl',
    'Roar',
    'Sing',
    'Supersonic',
    'Sonic Boom',
    'Disable',
    'Acid',
    'Ember',
    'Flamethrower',
    'Mist',
    'Water Gun',
    'Hydro Pump',
    'Surf',
    'Ice Beam',
    'Blizzard',
    'Psybeam',
    'Bubble Beam',
    'Aurora Beam',
    'Hyper Beam',
    'Peck',
    'Drill Peck',
    'Submission',
    'Low Kick',
    'Counter',
    'Seismic Toss',
    'Strength',
    'Absorb',
    'Mega Drain',
    'Leech Seed',
    'Growth',
    'Razor Leaf',
    'Solar Beam',
    'Poison Powder',
    'Stun Spore',
    'Sleep Powder',
    'Petal Dance',
    'String Shot',
    'Dragon Rage',
    'Fire Spin',
    'Thunder Shock',
    'Thunderbolt',
    'Thunder Wave',
    'Thunder',
    'Rock Throw',
    'Earthquake',
    'Fissure',
    'Dig',
    'Toxic',
    'Confusion',
    'Psychic',
    'Hypnosis',
    'Meditate',
    'Agility',
    'Quick Attack',
    'Rage',
    'Teleport',
    'Night Shade',
    'Mimic',
    'Screech',
    'Double Team',
    'Recover',
    'Harden',
    'Minimize',
    'Smokescreen',
    'Confuse Ray',
    'Withdraw',
    'Defense Curl',
    'Barrier',
    'Light Screen',
    'Haze',
    'Reflect',
    'Focus Energy',
    'Bide',
    'Metronome',
    'Mirror Move',
    'Self Destruct',
    'Egg Bomb',
    'Lick',
    'Smog',
    'Sludge',
    'Bone Club',
    'Fire Blast',
    'Waterfall',
    'Clamp',
    'Swift',
    'Skull Bash',
    'Spike Cannon',
    'Constrict',
    'Amnesia',
    'Kinesis',
    'Soft Boiled',
    'High Jump Kick',
    'Glare',
    'Dream Eater',
    'Poison Gas',
    'Barrage',
    'Leech Life',
    'Lovely Kiss',
    'Sky Attack',
    'Transform',
    'Bubble',
    'Dizzy Punch',
    'Spore',
    'Flash',
    'Psywave',
    'Splash',
    'Acid Armor',
    'Crabhammer',
    'Explosion',
    'Fury Swipes',
    'Bonemerang',
    'Rest',
    'Rock Slide',
    'Hyper Fang',
    'Sharpen',
    'Conversion',
    'Tri Attack',
    'Super Fang',
    'Slash',
    'Substitute',
    'Struggle',
    'Sketch',
    'Triple Kick',
    'Thief',
    'Spider Web',
    'Mind Reader',
    'Nightmare',
    'Flame Wheel',
    'Snore',
    'Curse',
    'Flail',
    'Conversion 2',
    'Aeroblast',
    'Cotton Spore',
    'Reversal',
    'Spite',
    'Powder Snow',
    'Protect',
    'Mach Punch',
    'Scary Face',
    'Feint Attack',
    'Sweet Kiss',
    'Belly Drum',
    'Sludge Bomb',
    'Mud-Slap',
    'Octazooka',
    'Spikes',
    'Zap Cannon',
    'Foresight',
    'Destiny Bond',
    'Perish Song',
    'Icy Wind',
    'Detect',
    'Bone Rush',
    'Lock On',
    'Outrage',
    'Sandstorm',
    'Giga Drain',
    'Endure',
    'Charm',
    'Rollout',
    'False Swipe',
    'Swagger',
    'Milk Drink',
    'Spark',
    'Fury Cutter',
    'Steel Wing',
    'Mean Look',
    'Attract',
    'Sleep Talk',
    'Heal Bell',
    'Return',
    'Present',
    'Frustration',
    'Safeguard',
    'Pain Split',
    'Sacred Fire',
    'Magnitude',
    'Dynamic Punch',
    'Megahorn',
    'Dragon Breath',
    'Baton Pass',
    'Encore',
    'Pursuit',
    'Rapid Spin',
    'Sweet Scent',
    'Iron Tail',
    'Metal Claw',
    'Vital Throw',
    'Morning Sun',
    'Synthesis',
    'Moonlight',
    'Hidden Power',
    'Cross Chop',
    'Twister',
    'Rain Dance',
    'Sunny Day',
    'Crunch',
    'Mirror Coat',
    'Psych Up',
    'Extreme Speed',
    'Ancient Power',
    'Shadow Ball',
    'Future Sight',
    'Rock Smash',
    'Whirlpool',
    'Beat Up',
    'Fake Out',
    'Uproar',
    'Stockpile',
    'Spit Up',
    'Swallow',
    'Heat Wave',
    'Hail',
    'Torment',
    'Flatter',
    'Will-O-Wisp',
    'Memento',
    'Facade',
    'Focus Punch',
    'Smelling Salts',
    'Follow Me',
    'Nature Power',
    'Charge',
    'Taunt',
    'Helping Hand',
    'Trick',
    'Role Play',
    'Wish',
    'Assist',
    'Ingrain',
    'Superpower',
    'Magic Coat',
    'Recycle',
    'Revenge',
    'Brick Break',
    'Yawn',
    'Knock Off',
    'Endeavor',
    'Eruption',
    'Skill Swap',
    'Imprison',
    'Refresh',
    'Grudge',
    'Snatch',
    'Secret Power',
    'Dive',
    'Arm Thrust',
    'Camouflage',
    'Tail Glow',
    'Luster Purge',
    'Mist Ball',
    'Feather Dance',
    'Teeter Dance',
    'Blaze Kick',
    'Mud Sport',
    'Ice Ball',
    'Needle Arm',
    'Slack Off',
    'Hyper Voice',
    'Poison Fang',
    'Crush Claw',
    'Blast Burn',
    'Hydro Cannon',
    'Meteor Mash',
    'Astonish',
    'Weather Ball',
    'Aromatherapy',
    'Fake Tears',
    'Air Cutter',
    'Overheat',
    'Odor Sleuth',
    'Rock Tomb',
    'Silver Wind',
    'Metal Sound',
    'Grass Whistle',
    'Tickle',
    'Cosmic Power',
    'Water Spout',
    'Signal Beam',
    'Shadow Punch',
    'Extrasensory',
    'Sky Uppercut',
    'Sand Tomb',
    'Sheer Cold',
    'Muddy Water',
    'Bullet Seed',
    'Aerial Ace',
    'Icicle Spear',
    'Iron Defense',
    'Block',
    'Howl',
    'Dragon Claw',
    'Frenzy Plant',
    'Bulk Up',
    'Bounce',
    'Mud Shot',
    'Poison Tail',
    'Covet',
    'Volt Tackle',
    'Magical Leaf',
    'Water Sport',
    'Calm Mind',
    'Leaf Blade',
    'Dragon Dance',
    'Rock Blast',
    'Shock Wave',
    'Water Pulse',
    'Doom Desire',
    'Psycho Boost',
    'Roost',
    'Gravity',
    'Miracle Eye',
    'Wake-Up Slap',
    'Hammer Arm',
    'Gyro Ball',
    'Healing Wish',
    'Brine',
    'Natural Gift',
    'Feint',
    'Pluck',
    'Tailwind',
    'Acupressure',
    'Metal Burst',
    'U-turn',
    'Close Combat',
    'Payback',
    'Assurance',
    'Embargo',
    'Fling',
    'Psycho Shift',
    'Trump Card',
    'Heal Block',
    'Wring Out',
    'Power Trick',
    'Gastro Acid',
    'Lucky Chant',
    'Me First',
    'Copycat',
    'Power Swap',
    'Guard Swap',
    'Punishment',
    'Last Resort',
    'Worry Seed',
    'Sucker Punch',
    'Toxic Spikes',
    'Heart Swap',
    'Aqua Ring',
    'Magnet Rise',
    'Flare Blitz',
    'Force Palm',
    'Aura Sphere',
    'Rock Polish',
    'Poison Jab',
    'Dark Pulse',
    'Night Slash',
    'Aqua Tail',
    'Seed Bomb',
    'Air Slash',
    'X-Scissor',
    'Bug Buzz',
    'Dragon Pulse',
    'Dragon Rush',
    'Power Gem',
    'Drain Punch',
    'Vacuum Wave',
    'Focus Blast',
    'Energy Ball',
    'Brave Bird',
    'Earth Power',
    'Switcheroo',
    'Giga Impact',
    'Nasty Plot',
    'Bullet Punch',
    'Avalanche',
    'Ice Shard',
    'Shadow Claw',
    'Thunder Fang',
    'Ice Fang',
    'Fire Fang',
    'Shadow Sneak',
    'Mud Bomb',
    'Psycho Cut',
    'Zen Headbutt',
    'Mirror Shot',
    'Flash Cannon',
    'Rock Climb',
    'Defog',
    'Trick Room',
    'Draco Meteor',
    'Discharge',
    'Lava Plume',
    'Leaf Storm',
    'Power Whip',
    'Rock Wrecker',
    'Cross Poison',
    'Gunk Shot',
    'Iron Head',
    'Magnet Bomb',
    'Stone Edge',
    'Captivate',
    'Stealth Rock',
    'Grass Knot',
    'Chatter',
    'Judgment',
    'Bug Bite',
    'Charge Beam',
    'Wood Hammer',
    'Aqua Jet',
    'Attack Order',
    'Defend Order',
    'Heal Order',
    'Head Smash',
    'Double Hit',
    'Roar Of Time',
    'Spacial Rend',
    'Lunar Dance',
    'Crush Grip',
    'Magma Storm',
    'Dark Void',
    'Seed Flare',
    'Ominous Wind',
    'Shadow Force',
    'Hone Claws',
    'Wide Guard',
    'Guard Split',
    'Power Split',
    'Wonder Room',
    'Psyshock',
    'Venoshock',
    'Autotomize',
    'Rage Powder',
    'Telekinesis',
    'Magic Room',
    'Smack Down',
    'Storm Throw',
    'Flame Burst',
    'Sludge Wave',
    'Quiver Dance',
    'Heavy Slam',
    'Synchronoise',
    'Electro Ball',
    'Soak',
    'Flame Charge',
    'Coil',
    'Low Sweep',
    'Acid Spray',
    'Foul Play',
    'Simple Beam',
    'Entrainment',
    'After You',
    'Round',
    'Echoed Voice',
    'Chip Away',
    'Clear Smog',
    'Stored Power',
    'Quick Guard',
    'Ally Switch',
    'Scald',
    'Shell Smash',
    'Heal Pulse',
    'Hex',
    'Sky Drop',
    'Shift Gear',
    'Circle Throw',
    'Incinerate',
    'Quash',
    'Acrobatics',
    'Reflect Type',
    'Retaliate',
    'Final Gambit',
    'Bestow',
    'Inferno',
    'Water Pledge',
    'Fire Pledge',
    'Grass Pledge',
    'Volt Switch',
    'Struggle Bug',
    'Bulldoze',
    'Frost Breath',
    'Dragon Tail',
    'Work Up',
    'Electroweb',
    'Wild Charge',
    'Drill Run',
    'Dual Chop',
    'Heart Stamp',
    'Horn Leech',
    'Sacred Sword',
    'Razor Shell',
    'Heat Crash',
    'Leaf Tornado',
    'Steamroller',
    'Cotton Guard',
    'Night Daze',
    'Psystrike',
    'Tail Slap',
    'Hurricane',
    'Head Charge',
    'Gear Grind',
    'Searing Shot',
    'Techno Blast',
    'Relic Song',
    'Secret Sword',
    'Glaciate',
    'Bolt Strike',
    'Blue Flare',
    'Fiery Dance',
    'Freeze Shock',
    'Ice Burn',
    'Snarl',
    'Icicle Crash',
    'V-create',
    'Fusion Flare',
    'Fusion Bolt',
    'Flying Press',
    'Mat Block',
    'Belch',
    'Rototiller',
    'Sticky Web',
    'Fell Stinger',
    'Phantom Force',
    'Trick-or-Treat',
    'Noble Roar',
    'Ion Deluge',
    'Parabolic Charge',
    'Forests Curse',
    'Petal Blizzard',
    'Freeze-Dry',
    'Disarming Voice',
    'Parting Shot',
    'Topsy-Turvy',
    'Draining Kiss',
    'Crafty Shield',
    'Flower Shield',
    'Grassy Terrain',
    'Misty Terrain',
    'Electrify',
    'Play Rough',
    'Fairy Wind',
    'Moonblast',
    'Boomburst',
    'Fairy Lock',
    'Kings Shield',
    'Play Nice',
    'Confide',
    'Diamond Storm',
    'Steam Eruption',
    'Hyperspace Hole',
    'Water Shuriken',
    'Mystical Fire',
    'Spiky Shield',
    'Aromatic Mist',
    'Eerie Impulse',
    'Venom Drench',
    'Powder',
    'Geomancy',
    'Magnetic Flux',
    'Happy Hour',
    'Electric Terrain',
    'Dazzling Gleam',
    'Celebrate',
    'Hold Hands',
    'Baby-Doll Eyes',
    'Nuzzle',
    'Hold Back',
    'Infestation',
    'Power-Up Punch',
    'Oblivion Wing',
    'Thousand Arrows',
    'Thousand Waves',
    'Lands Wrath',
    'Light Of Ruin',
    'Origin Pulse',
    'Precipice Blades',
    'Dragon Ascent',
    'Hyperspace Fury',
    'Shore Up',
    'First Impression',
    'Baneful Bunker',
    'Spirit Shackle',
    'Darkest Lariat',
    'Sparkling Aria',
    'Ice Hammer',
    'Floral Healing',
    'High Horsepower',
    'Strength Sap',
    'Solar Blade',
    'Leafage',
    'Spotlight',
    'Toxic Thread',
    'Laser Focus',
    'Gear Up',
    'Throat Chop',
    'Pollen Puff',
    'Anchor Shot',
    'Psychic Terrain',
    'Lunge',
    'Fire Lash',
    'Power Trip',
    'Burn Up',
    'Speed Swap',
    'Smart Strike',
    'Purify',
    'Revelation Dance',
    'Core Enforcer',
    'Trop Kick',
    'Instruct',
    'Beak Blast',
    'Clanging Scales',
    'Dragon Hammer',
    'Brutal Swing',
    'Aurora Veil',
    'Shell Trap',
    'Fleur Cannon',
    'Psychic Fangs',
    'Stomping Tantrum',
    'Shadow Bone',
    'Accelerock',
    'Liquidation',
    'Prismatic Laser',
    'Spectral Thief',
    'Sunsteel Strike',
    'Moongeist Beam',
    'Tearful Look',
    'Zing Zap',
    'Natures Madness',
    'Multi-Attack',
    'Mind Blown',
    'Plasma Fists',
    'Photon Geyser',
    'Zippy Zap',
    'Splishy Splash',
    'Floaty Fall',
    'Pika Papow',
    'Bouncy Bubble',
    'Buzzy Buzz',
    'Sizzly Slide',
    'Glitzy Glow',
    'Baddy Bad',
    'Sappy Seed',
    'Freezy Frost',
    'Sparkly Swirl',
    'Veevee Volley',
    'Double Iron Bash',
    'Dynamax Cannon',
    'Snipe Shot',
    'Jaw Lock',
    'Stuff Cheeks',
    'No Retreat',
    'Tar Shot',
    'Magic Powder',
    'Dragon Darts',
    'Teatime',
    'Octolock',
    'Bolt Beak',
    'Fishious Rend',
    'Court Change',
    'Clangorous Soul',
    'Body Press',
    'Decorate',
    'Drum Beating',
    'Snap Trap',
    'Pyro Ball',
    'Behemoth Blade',
    'Behemoth Bash',
    'Aura Wheel',
    'Breaking Swipe',
    'Branch Poke',
    'Overdrive',
    'Apple Acid',
    'Grav Apple',
    'Spirit Break',
    'Strange Steam',
    'Life Dew',
    'Obstruct',
    'False Surrender',
    'Meteor Assault',
    'Eternabeam',
    'Steel Beam',
    'Expanding Force',
    'Steel Roller',
    'Scale Shot',
    'Meteor Beam',
    'Shell Side Arm',
    'Misty Explosion',
    'Grassy Glide',
    'Rising Voltage',
    'Terrain Pulse',
    'Skitter Smack',
    'Burning Jealousy',
    'Lash Out',
    'Poltergeist',
    'Corrosive Gas',
    'Coaching',
    'Flip Turn',
    'Triple Axel',
    'Dual Wingbeat',
    'Scorching Sands',
    'Jungle Healing',
    'Wicked Blow',
    'Surging Strikes',
    'Thunder Cage',
    'Dragon Energy',
    'Freezing Glare',
    'Fiery Wrath',
    'Thunderous Kick',
    'Glacial Lance',
    'Astral Barrage',
    'Eerie Spell',
    'Dire Claw',
    'Psyshield Bash',
    'Power Shift',
    'Stone Axe',
    'Springtide Storm',
    'Mystical Power',
    'Raging Fury',
    'Wave Crash',
    'Chloroblast',
    'Mountain Gale',
    'Victory Dance',
    'Headlong Rush',
    'Barb Barrage',
    'Esper Wing',
    'Bitter Malice',
    'Shelter',
    'Triple Arrows',
    'Infernal Parade',
    'Ceaseless Edge',
    'Bleakwind Storm',
    'Wildbolt Storm',
    'Sandsear Storm',
    'Lunar Blessing',
    'Take Heart\t',
    'Tera Blast',
    'Silk Trap',
    'Axe Kick',
    'Last Respects',
    'Lumina Crash',
    'Order Up',
    'Jet Punch',
    'Spicy Extract',
    'Spin Out',
    'Population Bomb',
    'Ice Spinner',
    'Glaive Rush',
    'Revival Blessing',
    'Salt Cure',
    'Triple Dive',
    'Mortal Spin',
    'Doodle',
    'Fillet Away',
    'Kowtow Cleave',
    'Flower Trick',
    'Torch Song',
    'Aqua Step',
    'Raging Bull',
    'Make It Rain',
    'Ruination',
    'Collision Course',
    'Electro Drift',
    'Shed Tail',
    'Chilly Reception',
    'Tidy Up',
    'Snowscape',
    'Pounce',
    'Trailblaze',
    'Chilling Water',
    'Hyper Drill',
    'Twin Beam',
    'Rage Fist',
    'Armor Cannon',
    'Bitter Blade',
    'Double Shock',
    'Gigaton Hammer',
    'Comeuppance',
    'Aqua Cutter',
    'Blazing Torque',
    'Wicked Torque',
    'Noxious Torque',
    'Combat Torque',
    'Magical Torque',
    'Psyblade',
    'Hydro Steam',
    'Blood Moon',
    'Matcha Gotcha',
    'Syrup Bomb',
    'Ivy Cudgel',
    'Electro Shot',
    'Tera Starstorm',
    'Fickle Beam',
    'Burning Bulwark',
    'Thunderclap',
    'Mighty Cleave',
    'Tachyon Cutter',
    'Hard Press',
    'Dragon Cheer',
    'Alluring Voice',
    'Temper Flare',
    'Supercell Slam',
    'Psychic Noise',
    'Upper Hand',
    'Malignant Chain',
    'Aqua Fang',
    'Dark Hole',
]

all_mons = {
    "0": "None",
    "1": "Bulbasaur",
    "2": "Ivysaur",
    "3": "Venusaur",
    "4": "Charmander",
    "5": "Charmeleon",
    "6": "Charizard",
    "7": "Squirtle",
    "8": "Wartortle",
    "9": "Blastoise",
    "10": "Caterpie",
    "11": "Metapod",
    "12": "Butterfree",
    "13": "Weedle",
    "14": "Kakuna",
    "15": "Beedrill",
    "16": "Pidgey",
    "17": "Pidgeotto",
    "18": "Pidgeot",
    "19": "Rattata",
    "20": "Raticate",
    "21": "Spearow",
    "22": "Fearow",
    "23": "Ekans",
    "24": "Arbok",
    "25": "Pikachu",
    "26": "Raichu",
    "27": "Sandshrew",
    "28": "Sandslash",
    "29": "Nidoran-F",
    "30": "Nidorina",
    "31": "Nidoqueen",
    "32": "Nidoran-M",
    "33": "Nidorino",
    "34": "Nidoking",
    "35": "Clefairy",
    "36": "Clefable",
    "37": "Vulpix",
    "38": "Ninetales",
    "39": "Jigglypuff",
    "40": "Wigglytuff",
    "41": "Zubat",
    "42": "Golbat",
    "43": "Oddish",
    "44": "Gloom",
    "45": "Vileplume",
    "46": "Paras",
    "47": "Parasect",
    "48": "Venonat",
    "49": "Venomoth",
    "50": "Diglett",
    "51": "Dugtrio",
    "52": "Meowth",
    "53": "Persian",
    "54": "Psyduck",
    "55": "Golduck",
    "56": "Mankey",
    "57": "Primeape",
    "58": "Growlithe",
    "59": "Arcanine",
    "60": "Poliwag",
    "61": "Poliwhirl",
    "62": "Poliwrath",
    "63": "Abra",
    "64": "Kadabra",
    "65": "Alakazam",
    "66": "Machop",
    "67": "Machoke",
    "68": "Machamp",
    "69": "Bellsprout",
    "70": "Weepinbell",
    "71": "Victreebel",
    "72": "Tentacool",
    "73": "Tentacruel",
    "74": "Geodude",
    "75": "Graveler",
    "76": "Golem",
    "77": "Ponyta",
    "78": "Rapidash",
    "79": "Slowpoke",
    "80": "Slowbro",
    "81": "Magnemite",
    "82": "Magneton",
    "83": "Farfetchd",
    "84": "Doduo",
    "85": "Dodrio",
    "86": "Seel",
    "87": "Dewgong",
    "88": "Grimer",
    "89": "Muk",
    "90": "Shellder",
    "91": "Cloyster",
    "92": "Gastly",
    "93": "Haunter",
    "94": "Gengar",
    "95": "Onix",
    "96": "Drowzee",
    "97": "Hypno",
    "98": "Krabby",
    "99": "Kingler",
    "100": "Voltorb",
    "101": "Electrode",
    "102": "Exeggcute",
    "103": "Exeggutor",
    "104": "Cubone",
    "105": "Marowak",
    "106": "Hitmonlee",
    "107": "Hitmonchan",
    "108": "Lickitung",
    "109": "Koffing",
    "110": "Weezing",
    "111": "Rhyhorn",
    "112": "Rhydon",
    "113": "Chansey",
    "114": "Tangela",
    "115": "Kangaskhan",
    "116": "Horsea",
    "117": "Seadra",
    "118": "Goldeen",
    "119": "Seaking",
    "120": "Staryu",
    "121": "Starmie",
    "122": "Mr-Mime",
    "123": "Scyther",
    "124": "Jynx",
    "125": "Electabuzz",
    "126": "Magmar",
    "127": "Pinsir",
    "128": "Tauros",
    "129": "Magikarp",
    "130": "Gyarados",
    "131": "Lapras",
    "132": "Ditto",
    "133": "Eevee",
    "134": "Vaporeon",
    "135": "Jolteon",
    "136": "Flareon",
    "137": "Porygon",
    "138": "Omanyte",
    "139": "Omastar",
    "140": "Kabuto",
    "141": "Kabutops",
    "142": "Aerodactyl",
    "143": "Snorlax",
    "144": "Articuno",
    "145": "Zapdos",
    "146": "Moltres",
    "147": "Dratini",
    "148": "Dragonair",
    "149": "Dragonite",
    "150": "Mewtwo",
    "151": "Mew",
    "152": "Chikorita",
    "153": "Bayleef",
    "154": "Meganium",
    "155": "Cyndaquil",
    "156": "Quilava",
    "157": "Typhlosion",
    "158": "Totodile",
    "159": "Croconaw",
    "160": "Feraligatr",
    "161": "Sentret",
    "162": "Furret",
    "163": "Hoothoot",
    "164": "Noctowl",
    "165": "Ledyba",
    "166": "Ledian",
    "167": "Spinarak",
    "168": "Ariados",
    "169": "Crobat",
    "170": "Chinchou",
    "171": "Lanturn",
    "172": "Pichu",
    "173": "Cleffa",
    "174": "Igglybuff",
    "175": "Togepi",
    "176": "Togetic",
    "177": "Natu",
    "178": "Xatu",
    "179": "Mareep",
    "180": "Flaaffy",
    "181": "Ampharos",
    "182": "Bellossom",
    "183": "Marill",
    "184": "Azumarill",
    "185": "Sudowoodo",
    "186": "Politoed",
    "187": "Hoppip",
    "188": "Skiploom",
    "189": "Jumpluff",
    "190": "Aipom",
    "191": "Sunkern",
    "192": "Sunflora",
    "193": "Yanma",
    "194": "Wooper",
    "195": "Quagsire",
    "196": "Espeon",
    "197": "Umbreon",
    "198": "Murkrow",
    "199": "Slowking",
    "200": "Misdreavus",
    "201": "Unown",
    "202": "Wobbuffet",
    "203": "Girafarig",
    "204": "Pineco",
    "205": "Forretress",
    "206": "Dunsparce",
    "207": "Gligar",
    "208": "Steelix",
    "209": "Snubbull",
    "210": "Granbull",
    "211": "Qwilfish",
    "212": "Scizor",
    "213": "Shuckle",
    "214": "Heracross",
    "215": "Sneasel",
    "216": "Teddiursa",
    "217": "Ursaring",
    "218": "Slugma",
    "219": "Magcargo",
    "220": "Swinub",
    "221": "Piloswine",
    "222": "Corsola",
    "223": "Remoraid",
    "224": "Octillery",
    "225": "Delibird",
    "226": "Mantine",
    "227": "Skarmory",
    "228": "Houndour",
    "229": "Houndoom",
    "230": "Kingdra",
    "231": "Phanpy",
    "232": "Donphan",
    "233": "Porygon2",
    "234": "Stantler",
    "235": "Smeargle",
    "236": "Tyrogue",
    "237": "Hitmontop",
    "238": "Smoochum",
    "239": "Elekid",
    "240": "Magby",
    "241": "Miltank",
    "242": "Blissey",
    "243": "Raikou",
    "244": "Entei",
    "245": "Suicune",
    "246": "Larvitar",
    "247": "Pupitar",
    "248": "Tyranitar",
    "249": "Lugia",
    "250": "Ho-Oh",
    "251": "Celebi",
    "252": "Treecko",
    "253": "Grovyle",
    "254": "Sceptile",
    "255": "Torchic",
    "256": "Combusken",
    "257": "Blaziken",
    "258": "Mudkip",
    "259": "Marshtomp",
    "260": "Swampert",
    "261": "Poochyena",
    "262": "Mightyena",
    "263": "Zigzagoon",
    "264": "Linoone",
    "265": "Wurmple",
    "266": "Silcoon",
    "267": "Beautifly",
    "268": "Cascoon",
    "269": "Dustox",
    "270": "Lotad",
    "271": "Lombre",
    "272": "Ludicolo",
    "273": "Seedot",
    "274": "Nuzleaf",
    "275": "Shiftry",
    "276": "Taillow",
    "277": "Swellow",
    "278": "Wingull",
    "279": "Pelipper",
    "280": "Ralts",
    "281": "Kirlia",
    "282": "Gardevoir",
    "283": "Surskit",
    "284": "Masquerain",
    "285": "Shroomish",
    "286": "Breloom",
    "287": "Slakoth",
    "288": "Vigoroth",
    "289": "Slaking",
    "290": "Nincada",
    "291": "Ninjask",
    "292": "Shedinja",
    "293": "Whismur",
    "294": "Loudred",
    "295": "Exploud",
    "296": "Makuhita",
    "297": "Hariyama",
    "298": "Azurill",
    "299": "Nosepass",
    "300": "Skitty",
    "301": "Delcatty",
    "302": "Sableye",
    "303": "Mawile",
    "304": "Aron",
    "305": "Lairon",
    "306": "Aggron",
    "307": "Meditite",
    "308": "Medicham",
    "309": "Electrike",
    "310": "Manectric",
    "311": "Plusle",
    "312": "Minun",
    "313": "Volbeat",
    "314": "Illumise",
    "315": "Roselia",
    "316": "Gulpin",
    "317": "Swalot",
    "318": "Carvanha",
    "319": "Sharpedo",
    "320": "Wailmer",
    "321": "Wailord",
    "322": "Numel",
    "323": "Camerupt",
    "324": "Torkoal",
    "325": "Spoink",
    "326": "Grumpig",
    "327": "Spinda",
    "328": "Trapinch",
    "329": "Vibrava",
    "330": "Flygon",
    "331": "Cacnea",
    "332": "Cacturne",
    "333": "Swablu",
    "334": "Altaria",
    "335": "Zangoose",
    "336": "Seviper",
    "337": "Lunatone",
    "338": "Solrock",
    "339": "Barboach",
    "340": "Whiscash",
    "341": "Corphish",
    "342": "Crawdaunt",
    "343": "Baltoy",
    "344": "Claydol",
    "345": "Lileep",
    "346": "Cradily",
    "347": "Anorith",
    "348": "Armaldo",
    "349": "Feebas",
    "350": "Milotic",
    "351": "Castform-Normal",
    "352": "Kecleon",
    "353": "Shuppet",
    "354": "Banette",
    "355": "Duskull",
    "356": "Dusclops",
    "357": "Tropius",
    "358": "Chimecho",
    "359": "Absol",
    "360": "Wynaut",
    "361": "Snorunt",
    "362": "Glalie",
    "363": "Spheal",
    "364": "Sealeo",
    "365": "Walrein",
    "366": "Clamperl",
    "367": "Huntail",
    "368": "Gorebyss",
    "369": "Relicanth",
    "370": "Luvdisc",
    "371": "Bagon",
    "372": "Shelgon",
    "373": "Salamence",
    "374": "Beldum",
    "375": "Metang",
    "376": "Metagross",
    "377": "Regirock",
    "378": "Regice",
    "379": "Registeel",
    "380": "Latias",
    "381": "Latios",
    "382": "Kyogre",
    "383": "Groudon",
    "384": "Rayquaza",
    "385": "Jirachi",
    "386": "Deoxys-Normal",
    "387": "Turtwig",
    "388": "Grotle",
    "389": "Torterra",
    "390": "Chimchar",
    "391": "Monferno",
    "392": "Infernape",
    "393": "Piplup",
    "394": "Prinplup",
    "395": "Empoleon",
    "396": "Starly",
    "397": "Staravia",
    "398": "Staraptor",
    "399": "Bidoof",
    "400": "Bibarel",
    "401": "Kricketot",
    "402": "Kricketune",
    "403": "Shinx",
    "404": "Luxio",
    "405": "Luxray",
    "406": "Budew",
    "407": "Roserade",
    "408": "Cranidos",
    "409": "Rampardos",
    "410": "Shieldon",
    "411": "Bastiodon",
    "412": "Burmy-Plant",
    "413": "Wormadam-Plant",
    "414": "Mothim-Plant",
    "415": "Combee",
    "416": "Vespiquen",
    "417": "Pachirisu",
    "418": "Buizel",
    "419": "Floatzel",
    "420": "Cherubi",
    "421": "Cherrim-Overcast",
    "422": "Shellos-West",
    "423": "Gastrodon-West",
    "424": "Ambipom",
    "425": "Drifloon",
    "426": "Drifblim",
    "427": "Buneary",
    "428": "Lopunny",
    "429": "Mismagius",
    "430": "Honchkrow",
    "431": "Glameow",
    "432": "Purugly",
    "433": "Chingling",
    "434": "Stunky",
    "435": "Skuntank",
    "436": "Bronzor",
    "437": "Bronzong",
    "438": "Bonsly",
    "439": "Mime-Jr",
    "440": "Happiny",
    "441": "Chatot",
    "442": "Spiritomb",
    "443": "Gible",
    "444": "Gabite",
    "445": "Garchomp",
    "446": "Munchlax",
    "447": "Riolu",
    "448": "Lucario",
    "449": "Hippopotas",
    "450": "Hippowdon",
    "451": "Skorupi",
    "452": "Drapion",
    "453": "Croagunk",
    "454": "Toxicroak",
    "455": "Carnivine",
    "456": "Finneon",
    "457": "Lumineon",
    "458": "Mantyke",
    "459": "Snover",
    "460": "Abomasnow",
    "461": "Weavile",
    "462": "Magnezone",
    "463": "Lickilicky",
    "464": "Rhyperior",
    "465": "Tangrowth",
    "466": "Electivire",
    "467": "Magmortar",
    "468": "Togekiss",
    "469": "Yanmega",
    "470": "Leafeon",
    "471": "Glaceon",
    "472": "Gliscor",
    "473": "Mamoswine",
    "474": "Porygon-Z",
    "475": "Gallade",
    "476": "Probopass",
    "477": "Dusknoir",
    "478": "Froslass",
    "479": "Rotom",
    "480": "Uxie",
    "481": "Mesprit",
    "482": "Azelf",
    "483": "Dialga",
    "484": "Palkia",
    "485": "Heatran",
    "486": "Regigigas",
    "487": "Giratina-Altered",
    "488": "Cresselia",
    "489": "Phione",
    "490": "Manaphy",
    "491": "Darkrai",
    "492": "Shaymin-Land",
    "493": "Arceus-Normal",
    "494": "Victini",
    "495": "Snivy",
    "496": "Servine",
    "497": "Serperior",
    "498": "Tepig",
    "499": "Pignite",
    "500": "Emboar",
    "501": "Oshawott",
    "502": "Dewott",
    "503": "Samurott",
    "504": "Patrat",
    "505": "Watchog",
    "506": "Lillipup",
    "507": "Herdier",
    "508": "Stoutland",
    "509": "Purrloin",
    "510": "Liepard",
    "511": "Pansage",
    "512": "Simisage",
    "513": "Pansear",
    "514": "Simisear",
    "515": "Panpour",
    "516": "Simipour",
    "517": "Munna",
    "518": "Musharna",
    "519": "Pidove",
    "520": "Tranquill",
    "521": "Unfezant",
    "522": "Blitzle",
    "523": "Zebstrika",
    "524": "Roggenrola",
    "525": "Boldore",
    "526": "Gigalith",
    "527": "Woobat",
    "528": "Swoobat",
    "529": "Drilbur",
    "530": "Excadrill",
    "531": "Audino",
    "532": "Timburr",
    "533": "Gurdurr",
    "534": "Conkeldurr",
    "535": "Tympole",
    "536": "Palpitoad",
    "537": "Seismitoad",
    "538": "Throh",
    "539": "Sawk",
    "540": "Sewaddle",
    "541": "Swadloon",
    "542": "Leavanny",
    "543": "Venipede",
    "544": "Whirlipede",
    "545": "Scolipede",
    "546": "Cottonee",
    "547": "Whimsicott",
    "548": "Petilil",
    "549": "Lilligant",
    "550": "Basculin-Red-Striped",
    "551": "Sandile",
    "552": "Krokorok",
    "553": "Krookodile",
    "554": "Darumaka",
    "555": "Darmanitan-Standard",
    "556": "Maractus",
    "557": "Dwebble",
    "558": "Crustle",
    "559": "Scraggy",
    "560": "Scrafty",
    "561": "Sigilyph",
    "562": "Yamask",
    "563": "Cofagrigus",
    "564": "Tirtouga",
    "565": "Carracosta",
    "566": "Archen",
    "567": "Archeops",
    "568": "Trubbish",
    "569": "Garbodor",
    "570": "Zorua",
    "571": "Zoroark",
    "572": "Minccino",
    "573": "Cinccino",
    "574": "Gothita",
    "575": "Gothorita",
    "576": "Gothitelle",
    "577": "Solosis",
    "578": "Duosion",
    "579": "Reuniclus",
    "580": "Ducklett",
    "581": "Swanna",
    "582": "Vanillite",
    "583": "Vanillish",
    "584": "Vanilluxe",
    "585": "Deerling-Spring",
    "586": "Sawsbuck-Spring",
    "587": "Emolga",
    "588": "Karrablast",
    "589": "Escavalier",
    "590": "Foongus",
    "591": "Amoonguss",
    "592": "Frillish",
    "593": "Jellicent",
    "594": "Alomomola",
    "595": "Joltik",
    "596": "Galvantula",
    "597": "Ferroseed",
    "598": "Ferrothorn",
    "599": "Klink",
    "600": "Klang",
    "601": "Klinklang",
    "602": "Tynamo",
    "603": "Eelektrik",
    "604": "Eelektross",
    "605": "Elgyem",
    "606": "Beheeyem",
    "607": "Litwick",
    "608": "Lampent",
    "609": "Chandelure",
    "610": "Axew",
    "611": "Fraxure",
    "612": "Haxorus",
    "613": "Cubchoo",
    "614": "Beartic",
    "615": "Cryogonal",
    "616": "Shelmet",
    "617": "Accelgor",
    "618": "Stunfisk",
    "619": "Mienfoo",
    "620": "Mienshao",
    "621": "Druddigon",
    "622": "Golett",
    "623": "Golurk",
    "624": "Pawniard",
    "625": "Bisharp",
    "626": "Bouffalant",
    "627": "Rufflet",
    "628": "Braviary",
    "629": "Vullaby",
    "630": "Mandibuzz",
    "631": "Heatmor",
    "632": "Durant",
    "633": "Deino",
    "634": "Zweilous",
    "635": "Hydreigon",
    "636": "Larvesta",
    "637": "Volcarona",
    "638": "Cobalion",
    "639": "Terrakion",
    "640": "Virizion",
    "641": "Tornadus-Incarnate",
    "642": "Thundurus-Incarnate",
    "643": "Reshiram",
    "644": "Zekrom",
    "645": "Landorus-Incarnate",
    "646": "Kyurem",
    "647": "Keldeo-Ordinary",
    "648": "Meloetta-Aria",
    "649": "Genesect",
    "650": "Chespin",
    "651": "Quilladin",
    "652": "Chesnaught",
    "653": "Fennekin",
    "654": "Braixen",
    "655": "Delphox",
    "656": "Froakie",
    "657": "Frogadier",
    "658": "Greninja",
    "659": "Bunnelby",
    "660": "Diggersby",
    "661": "Fletchling",
    "662": "Fletchinder",
    "663": "Talonflame",
    "664": "Scatterbug-Icy-Snow",
    "665": "Spewpa-Icy-Snow",
    "666": "Vivillon-Icy-Snow",
    "667": "Litleo",
    "668": "Pyroar",
    "669": "Flabebe-Red",
    "670": "Floette-Red",
    "671": "Florges-Red",
    "672": "Skiddo",
    "673": "Gogoat",
    "674": "Pancham",
    "675": "Pangoro",
    "676": "Furfrou-Natural",
    "677": "Espurr",
    "678": "Meowstic-M",
    "679": "Honedge",
    "680": "Doublade",
    "681": "Aegislash-Shield",
    "682": "Spritzee",
    "683": "Aromatisse",
    "684": "Swirlix",
    "685": "Slurpuff",
    "686": "Inkay",
    "687": "Malamar",
    "688": "Binacle",
    "689": "Barbaracle",
    "690": "Skrelp",
    "691": "Dragalge",
    "692": "Clauncher",
    "693": "Clawitzer",
    "694": "Helioptile",
    "695": "Heliolisk",
    "696": "Tyrunt",
    "697": "Tyrantrum",
    "698": "Amaura",
    "699": "Aurorus",
    "700": "Sylveon",
    "701": "Hawlucha",
    "702": "Dedenne",
    "703": "Carbink",
    "704": "Goomy",
    "705": "Sliggoo",
    "706": "Goodra",
    "707": "Klefki",
    "708": "Phantump",
    "709": "Trevenant",
    "710": "Pumpkaboo-Average",
    "711": "Gourgeist-Average",
    "712": "Bergmite",
    "713": "Avalugg",
    "714": "Noibat",
    "715": "Noivern",
    "716": "Xerneas-Neutral",
    "717": "Yveltal",
    "718": "Zygarde-50",
    "719": "Diancie",
    "720": "Hoopa-Confined",
    "721": "Volcanion",
    "722": "Rowlet",
    "723": "Dartrix",
    "724": "Decidueye",
    "725": "Litten",
    "726": "Torracat",
    "727": "Incineroar",
    "728": "Popplio",
    "729": "Brionne",
    "730": "Primarina",
    "731": "Pikipek",
    "732": "Trumbeak",
    "733": "Toucannon",
    "734": "Yungoos",
    "735": "Gumshoos",
    "736": "Grubbin",
    "737": "Charjabug",
    "738": "Vikavolt",
    "739": "Crabrawler",
    "740": "Crabominable",
    "741": "Oricorio-Baile",
    "742": "Cutiefly",
    "743": "Ribombee",
    "744": "Rockruff",
    "745": "Lycanroc-Midday",
    "746": "Wishiwashi-Solo",
    "747": "Mareanie",
    "748": "Toxapex",
    "749": "Mudbray",
    "750": "Mudsdale",
    "751": "Dewpider",
    "752": "Araquanid",
    "753": "Fomantis",
    "754": "Lurantis",
    "755": "Morelull",
    "756": "Shiinotic",
    "757": "Salandit",
    "758": "Salazzle",
    "759": "Stufful",
    "760": "Bewear",
    "761": "Bounsweet",
    "762": "Steenee",
    "763": "Tsareena",
    "764": "Comfey",
    "765": "Oranguru",
    "766": "Passimian",
    "767": "Wimpod",
    "768": "Golisopod",
    "769": "Sandygast",
    "770": "Palossand",
    "771": "Pyukumuku",
    "772": "Type-Null",
    "773": "Silvally-Normal",
    "774": "Minior-Meteor-Red",
    "775": "Komala",
    "776": "Turtonator",
    "777": "Togedemaru",
    "778": "Mimikyu-Disguised",
    "779": "Bruxish",
    "780": "Drampa",
    "781": "Dhelmise",
    "782": "Jangmo-O",
    "783": "Hakamo-O",
    "784": "Kommo-O",
    "785": "Tapu-Koko",
    "786": "Tapu-Lele",
    "787": "Tapu-Bulu",
    "788": "Tapu-Fini",
    "789": "Cosmog",
    "790": "Cosmoem",
    "791": "Solgaleo",
    "792": "Lunala",
    "793": "Nihilego",
    "794": "Buzzwole",
    "795": "Pheromosa",
    "796": "Xurkitree",
    "797": "Celesteela",
    "798": "Kartana",
    "799": "Guzzlord",
    "800": "Necrozma",
    "801": "Magearna",
    "802": "Marshadow",
    "803": "Poipole",
    "804": "Naganadel",
    "805": "Stakataka",
    "806": "Blacephalon",
    "807": "Zeraora",
    "808": "Meltan",
    "809": "Melmetal",
    "810": "Grookey",
    "811": "Thwackey",
    "812": "Rillaboom",
    "813": "Scorbunny",
    "814": "Raboot",
    "815": "Cinderace",
    "816": "Sobble",
    "817": "Drizzile",
    "818": "Inteleon",
    "819": "Skwovet",
    "820": "Greedent",
    "821": "Rookidee",
    "822": "Corvisquire",
    "823": "Corviknight",
    "824": "Blipbug",
    "825": "Dottler",
    "826": "Orbeetle",
    "827": "Nickit",
    "828": "Thievul",
    "829": "Gossifleur",
    "830": "Eldegoss",
    "831": "Wooloo",
    "832": "Dubwool",
    "833": "Chewtle",
    "834": "Drednaw",
    "835": "Yamper",
    "836": "Boltund",
    "837": "Rolycoly",
    "838": "Carkol",
    "839": "Coalossal",
    "840": "Applin",
    "841": "Flapple",
    "842": "Appletun",
    "843": "Silicobra",
    "844": "Sandaconda",
    "845": "Cramorant",
    "846": "Arrokuda",
    "847": "Barraskewda",
    "848": "Toxel",
    "849": "Toxtricity-Amped",
    "850": "Sizzlipede",
    "851": "Centiskorch",
    "852": "Clobbopus",
    "853": "Grapploct",
    "854": "Sinistea-Phony",
    "855": "Polteageist-Phony",
    "856": "Hatenna",
    "857": "Hattrem",
    "858": "Hatterene",
    "859": "Impidimp",
    "860": "Morgrem",
    "861": "Grimmsnarl",
    "862": "Obstagoon",
    "863": "Perrserker",
    "864": "Cursola",
    "865": "Sirfetchd",
    "866": "Mr-Rime",
    "867": "Runerigus",
    "868": "Milcery",
    "869": "Alcremie-Strawberry-Vanilla-Cream",
    "870": "Falinks",
    "871": "Pincurchin",
    "872": "Snom",
    "873": "Frosmoth",
    "874": "Stonjourner",
    "875": "Eiscue-Ice",
    "876": "Indeedee-M",
    "877": "Morpeko-Full-Belly",
    "878": "Cufant",
    "879": "Copperajah",
    "880": "Dracozolt",
    "881": "Arctozolt",
    "882": "Dracovish",
    "883": "Arctovish",
    "884": "Duraludon",
    "885": "Dreepy",
    "886": "Drakloak",
    "887": "Dragapult",
    "888": "Zacian-Hero",
    "889": "Zamazenta-Hero",
    "890": "Eternatus",
    "891": "Kubfu",
    "892": "Urshifu-Single-Strike",
    "893": "Zarude",
    "894": "Regieleki",
    "895": "Regidrago",
    "896": "Glastrier",
    "897": "Spectrier",
    "898": "Calyrex",
    "899": "Wyrdeer",
    "900": "Kleavor",
    "901": "Ursaluna",
    "902": "Basculegion-M",
    "903": "Sneasler",
    "904": "Overqwil",
    "905": "Enamorus-Incarnate",
    "906": "Venusaur-Mega",
    "907": "Charizard-Mega-X",
    "908": "Charizard-Mega-Y",
    "909": "Blastoise-Mega",
    "910": "Beedrill-Mega",
    "911": "Pidgeot-Mega",
    "912": "Alakazam-Mega",
    "913": "Slowbro-Mega",
    "914": "Gengar-Mega",
    "915": "Kangaskhan-Mega",
    "916": "Pinsir-Mega",
    "917": "Gyarados-Mega",
    "918": "Aerodactyl-Mega",
    "919": "Mewtwo-Mega-X",
    "920": "Mewtwo-Mega-Y",
    "921": "Ampharos-Mega",
    "922": "Steelix-Mega",
    "923": "Scizor-Mega",
    "924": "Heracross-Mega",
    "925": "Houndoom-Mega",
    "926": "Tyranitar-Mega",
    "927": "Sceptile-Mega",
    "928": "Blaziken-Mega",
    "929": "Swampert-Mega",
    "930": "Gardevoir-Mega",
    "931": "Sableye-Mega",
    "932": "Mawile-Mega",
    "933": "Aggron-Mega",
    "934": "Medicham-Mega",
    "935": "Manectric-Mega",
    "936": "Sharpedo-Mega",
    "937": "Camerupt-Mega",
    "938": "Altaria-Mega",
    "939": "Banette-Mega",
    "940": "Absol-Mega",
    "941": "Glalie-Mega",
    "942": "Salamence-Mega",
    "943": "Metagross-Mega",
    "944": "Latias-Mega",
    "945": "Latios-Mega",
    "946": "Lopunny-Mega",
    "947": "Garchomp-Mega",
    "948": "Lucario-Mega",
    "949": "Abomasnow-Mega",
    "950": "Gallade-Mega",
    "951": "Audino-Mega",
    "952": "Diancie-Mega",
    "953": "Rayquaza-Mega",
    "954": "Kyogre-Primal",
    "955": "Groudon-Primal",
    "956": "Rattata-Alola",
    "957": "Raticate-Alola",
    "958": "Raichu-Alola",
    "959": "Sandshrew-Alola",
    "960": "Sandslash-Alola",
    "961": "Vulpix-Alola",
    "962": "Ninetales-Alola",
    "963": "Diglett-Alola",
    "964": "Dugtrio-Alola",
    "965": "Meowth-Alola",
    "966": "Persian-Alola",
    "967": "Geodude-Alola",
    "968": "Graveler-Alola",
    "969": "Golem-Alola",
    "970": "Grimer-Alola",
    "971": "Muk-Alola",
    "972": "Exeggutor-Alola",
    "973": "Marowak-Alola",
    "974": "Meowth-Galar",
    "975": "Ponyta-Galar",
    "976": "Rapidash-Galar",
    "977": "Slowpoke-Galar",
    "978": "Slowbro-Galar",
    "979": "Farfetchd-Galar",
    "980": "Weezing-Galar",
    "981": "Mr-Mime-Galar",
    "982": "Articuno-Galar",
    "983": "Zapdos-Galar",
    "984": "Moltres-Galar",
    "985": "Slowking-Galar",
    "986": "Corsola-Galar",
    "987": "Zigzagoon-Galar",
    "988": "Linoone-Galar",
    "989": "Darumaka-Galar",
    "990": "Darmanitan-Galar-Standard",
    "991": "Yamask-Galar",
    "992": "Stunfisk-Galar",
    "993": "Growlithe-Hisui",
    "994": "Arcanine-Hisui",
    "995": "Voltorb-Hisui",
    "996": "Electrode-Hisui",
    "997": "Typhlosion-Hisui",
    "998": "Qwilfish-Hisui",
    "999": "Sneasel-Hisui",
    "1000": "Samurott-Hisui",
    "1001": "Lilligant-Hisui",
    "1002": "Zorua-Hisui",
    "1003": "Zoroark-Hisui",
    "1004": "Braviary-Hisui",
    "1005": "Sliggoo-Hisui",
    "1006": "Goodra-Hisui",
    "1007": "Avalugg-Hisui",
    "1008": "Decidueye-Hisui",
    "1009": "Pikachu-Cosplay",
    "1010": "Pikachu-Rock-Star",
    "1011": "Pikachu-Belle",
    "1012": "Pikachu-Pop-Star",
    "1013": "Pikachu-Phd",
    "1014": "Pikachu-Libre",
    "1015": "Pikachu-Original",
    "1016": "Pikachu-Hoenn",
    "1017": "Pikachu-Sinnoh",
    "1018": "Pikachu-Unova",
    "1019": "Pikachu-Kalos",
    "1020": "Pikachu-Alola",
    "1021": "Pikachu-Partner",
    "1022": "Pikachu-World",
    "1023": "Pichu-Spiky-Eared",
    "1024": "Unown-B",
    "1025": "Unown-C",
    "1026": "Unown-D",
    "1027": "Unown-E",
    "1028": "Unown-F",
    "1029": "Unown-G",
    "1030": "Unown-H",
    "1031": "Unown-I",
    "1032": "Unown-J",
    "1033": "Unown-K",
    "1034": "Unown-L",
    "1035": "Unown-M",
    "1036": "Unown-N",
    "1037": "Unown-O",
    "1038": "Unown-P",
    "1039": "Unown-Q",
    "1040": "Unown-R",
    "1041": "Unown-S",
    "1042": "Unown-T",
    "1043": "Unown-U",
    "1044": "Unown-V",
    "1045": "Unown-W",
    "1046": "Unown-X",
    "1047": "Unown-Y",
    "1048": "Unown-Z",
    "1049": "Unown-Exclamation",
    "1050": "Unown-Question",
    "1051": "Castform-Sunny",
    "1052": "Castform-Rainy",
    "1053": "Castform-Snowy",
    "1054": "Deoxys-Attack",
    "1055": "Deoxys-Defense",
    "1056": "Deoxys-Speed",
    "1057": "Burmy-Sandy",
    "1058": "Burmy-Trash",
    "1059": "Wormadam-Sandy",
    "1060": "Wormadam-Trash",
    "1061": "Cherrim-Sunshine",
    "1062": "Shellos-East",
    "1063": "Gastrodon-East",
    "1064": "Rotom-Heat",
    "1065": "Rotom-Wash",
    "1066": "Rotom-Frost",
    "1067": "Rotom-Fan",
    "1068": "Rotom-Mow",
    "1069": "Dialga-Origin",
    "1070": "Palkia-Origin",
    "1071": "Giratina-Origin",
    "1072": "Shaymin-Sky",
    "1073": "Arceus-Fighting",
    "1074": "Arceus-Flying",
    "1075": "Arceus-Poison",
    "1076": "Arceus-Ground",
    "1077": "Arceus-Rock",
    "1078": "Arceus-Bug",
    "1079": "Arceus-Ghost",
    "1080": "Arceus-Steel",
    "1081": "Arceus-Fire",
    "1082": "Arceus-Water",
    "1083": "Arceus-Grass",
    "1084": "Arceus-Electric",
    "1085": "Arceus-Psychic",
    "1086": "Arceus-Ice",
    "1087": "Arceus-Dragon",
    "1088": "Arceus-Dark",
    "1089": "Arceus-Fairy",
    "1090": "Basculin-Blue-Striped",
    "1091": "Basculin-White-Striped",
    "1092": "Darmanitan-Zen",
    "1093": "Darmanitan-Galar-Zen",
    "1094": "Deerling-Summer",
    "1095": "Deerling-Autumn",
    "1096": "Deerling-Winter",
    "1097": "Sawsbuck-Summer",
    "1098": "Sawsbuck-Autumn",
    "1099": "Sawsbuck-Winter",
    "1100": "Tornadus-Therian",
    "1101": "Thundurus-Therian",
    "1102": "Landorus-Therian",
    "1103": "Enamorus-Therian",
    "1104": "Kyurem-White",
    "1105": "Kyurem-Black",
    "1106": "Keldeo-Resolute",
    "1107": "Meloetta-Pirouette",
    "1108": "Genesect-Douse",
    "1109": "Genesect-Shock",
    "1110": "Genesect-Burn",
    "1111": "Genesect-Chill",
    "1112": "Greninja-Bond",
    "1113": "Greninja-Ash",
    "1114": "Vivillon-Polar",
    "1115": "Vivillon-Tundra",
    "1116": "Vivillon-Continental",
    "1117": "Vivillon-Garden",
    "1118": "Vivillon-Elegant",
    "1119": "Vivillon-Meadow",
    "1120": "Vivillon-Modern",
    "1121": "Vivillon-Marine",
    "1122": "Vivillon-Archipelago",
    "1123": "Vivillon-High-Plains",
    "1124": "Vivillon-Sandstorm",
    "1125": "Vivillon-River",
    "1126": "Vivillon-Monsoon",
    "1127": "Vivillon-Savanna",
    "1128": "Vivillon-Sun",
    "1129": "Vivillon-Ocean",
    "1130": "Vivillon-Jungle",
    "1131": "Vivillon-Fancy",
    "1132": "Vivillon-Pokeball",
    "1133": "Flabebe-Yellow",
    "1134": "Flabebe-Orange",
    "1135": "Flabebe-Blue",
    "1136": "Flabebe-White",
    "1137": "Floette-Yellow",
    "1138": "Floette-Orange",
    "1139": "Floette-Blue",
    "1140": "Floette-White",
    "1141": "Floette-Eternal",
    "1142": "Florges-Yellow",
    "1143": "Florges-Orange",
    "1144": "Florges-Blue",
    "1145": "Florges-White",
    "1146": "Furfrou-Heart-Trim",
    "1147": "Furfrou-Star-Trim",
    "1148": "Furfrou-Diamond-Trim",
    "1149": "Furfrou-Debutante-Trim",
    "1150": "Furfrou-Matron-Trim",
    "1151": "Furfrou-Dandy-Trim",
    "1152": "Furfrou-La-Reine-Trim",
    "1153": "Furfrou-Kabuki-Trim",
    "1154": "Furfrou-Pharaoh-Trim",
    "1155": "Meowstic-F",
    "1156": "Aegislash-Blade",
    "1157": "Pumpkaboo-Small",
    "1158": "Pumpkaboo-Large",
    "1159": "Pumpkaboo-Super",
    "1160": "Gourgeist-Small",
    "1161": "Gourgeist-Large",
    "1162": "Gourgeist-Super",
    "1163": "Xerneas-Active",
    "1164": "Zygarde-10-Aura-Break",
    "1165": "Zygarde-10-Power-Construct",
    "1166": "Zygarde-50-Power-Construct",
    "1167": "Zygarde-Complete",
    "1168": "Hoopa-Unbound",
    "1169": "Oricorio-Pom-Pom",
    "1170": "Oricorio-Pau",
    "1171": "Oricorio-Sensu",
    "1172": "Rockruff-Own-Tempo",
    "1173": "Lycanroc-Midnight",
    "1174": "Lycanroc-Dusk",
    "1175": "Wishiwashi-School",
    "1176": "Silvally-Fighting",
    "1177": "Silvally-Flying",
    "1178": "Silvally-Poison",
    "1179": "Silvally-Ground",
    "1180": "Silvally-Rock",
    "1181": "Silvally-Bug",
    "1182": "Silvally-Ghost",
    "1183": "Silvally-Steel",
    "1184": "Silvally-Fire",
    "1185": "Silvally-Water",
    "1186": "Silvally-Grass",
    "1187": "Silvally-Electric",
    "1188": "Silvally-Psychic",
    "1189": "Silvally-Ice",
    "1190": "Silvally-Dragon",
    "1191": "Silvally-Dark",
    "1192": "Silvally-Fairy",
    "1193": "Minior-Meteor-Orange",
    "1194": "Minior-Meteor-Yellow",
    "1195": "Minior-Meteor-Green",
    "1196": "Minior-Meteor-Blue",
    "1197": "Minior-Meteor-Indigo",
    "1198": "Minior-Meteor-Violet",
    "1199": "Minior-Core-Red",
    "1200": "Minior-Core-Orange",
    "1201": "Minior-Core-Yellow",
    "1202": "Minior-Core-Green",
    "1203": "Minior-Core-Blue",
    "1204": "Minior-Core-Indigo",
    "1205": "Minior-Core-Violet",
    "1206": "Mimikyu-Busted",
    "1207": "Necrozma-Dusk-Mane",
    "1208": "Necrozma-Dawn-Wings",
    "1209": "Necrozma-Ultra",
    "1210": "Magearna-Original",
    "1211": "Cramorant-Gulping",
    "1212": "Cramorant-Gorging",
    "1213": "Toxtricity-Low-Key",
    "1214": "Sinistea-Antique",
    "1215": "Polteageist-Antique",
    "1216": "Alcremie-Strawberry-Ruby-Cream",
    "1217": "Alcremie-Strawberry-Matcha-Cream",
    "1218": "Alcremie-Strawberry-Mint-Cream",
    "1219": "Alcremie-Strawberry-Lemon-Cream",
    "1220": "Alcremie-Strawberry-Salted-Cream",
    "1221": "Alcremie-Strawberry-Ruby-Swirl",
    "1222": "Alcremie-Strawberry-Caramel-Swirl",
    "1223": "Alcremie-Strawberry-Rainbow-Swirl",
    "1224": "Eiscue-Noice",
    "1225": "Indeedee-F",
    "1226": "Morpeko-Hangry",
    "1227": "Zacian-Crowned",
    "1228": "Zamazenta-Crowned",
    "1229": "Eternatus-Eternamax",
    "1230": "Urshifu-Rapid-Strike",
    "1231": "Zarude-Dada",
    "1232": "Calyrex-Ice",
    "1233": "Calyrex-Shadow",
    "1234": "Basculegion-F",
    "1235": "Alcremie-Berry-Vanilla-Cream",
    "1236": "Alcremie-Berry-Ruby-Cream",
    "1237": "Alcremie-Berry-Matcha-Cream",
    "1238": "Alcremie-Berry-Mint-Cream",
    "1239": "Alcremie-Berry-Lemon-Cream",
    "1240": "Alcremie-Berry-Salted-Cream",
    "1241": "Alcremie-Berry-Ruby-Swirl",
    "1242": "Alcremie-Berry-Caramel-Swirl",
    "1243": "Alcremie-Berry-Rainbow-Swirl",
    "1244": "Alcremie-Love-Vanilla-Cream",
    "1245": "Alcremie-Love-Ruby-Cream",
    "1246": "Alcremie-Love-Matcha-Cream",
    "1247": "Alcremie-Love-Mint-Cream",
    "1248": "Alcremie-Love-Lemon-Cream",
    "1249": "Alcremie-Love-Salted-Cream",
    "1250": "Alcremie-Love-Ruby-Swirl",
    "1251": "Alcremie-Love-Caramel-Swirl",
    "1252": "Alcremie-Love-Rainbow-Swirl",
    "1253": "Alcremie-Star-Vanilla-Cream",
    "1254": "Alcremie-Star-Ruby-Cream",
    "1255": "Alcremie-Star-Matcha-Cream",
    "1256": "Alcremie-Star-Mint-Cream",
    "1257": "Alcremie-Star-Lemon-Cream",
    "1258": "Alcremie-Star-Salted-Cream",
    "1259": "Alcremie-Star-Ruby-Swirl",
    "1260": "Alcremie-Star-Caramel-Swirl",
    "1261": "Alcremie-Star-Rainbow-Swirl",
    "1262": "Alcremie-Clover-Vanilla-Cream",
    "1263": "Alcremie-Clover-Ruby-Cream",
    "1264": "Alcremie-Clover-Matcha-Cream",
    "1265": "Alcremie-Clover-Mint-Cream",
    "1266": "Alcremie-Clover-Lemon-Cream",
    "1267": "Alcremie-Clover-Salted-Cream",
    "1268": "Alcremie-Clover-Ruby-Swirl",
    "1269": "Alcremie-Clover-Caramel-Swirl",
    "1270": "Alcremie-Clover-Rainbow-Swirl",
    "1271": "Alcremie-Flower-Vanilla-Cream",
    "1272": "Alcremie-Flower-Ruby-Cream",
    "1273": "Alcremie-Flower-Matcha-Cream",
    "1274": "Alcremie-Flower-Mint-Cream",
    "1275": "Alcremie-Flower-Lemon-Cream",
    "1276": "Alcremie-Flower-Salted-Cream",
    "1277": "Alcremie-Flower-Ruby-Swirl",
    "1278": "Alcremie-Flower-Caramel-Swirl",
    "1279": "Alcremie-Flower-Rainbow-Swirl",
    "1280": "Alcremie-Ribbon-Vanilla-Cream",
    "1281": "Alcremie-Ribbon-Ruby-Cream",
    "1282": "Alcremie-Ribbon-Matcha-Cream",
    "1283": "Alcremie-Ribbon-Mint-Cream",
    "1284": "Alcremie-Ribbon-Lemon-Cream",
    "1285": "Alcremie-Ribbon-Salted-Cream",
    "1286": "Alcremie-Ribbon-Ruby-Swirl",
    "1287": "Alcremie-Ribbon-Caramel-Swirl",
    "1288": "Alcremie-Ribbon-Rainbow-Swirl",
    "1289": "Sprigatito",
    "1290": "Floragato",
    "1291": "Meowscarada",
    "1292": "Fuecoco",
    "1293": "Crocalor",
    "1294": "Skeledirge",
    "1295": "Quaxly",
    "1296": "Quaxwell",
    "1297": "Quaquaval",
    "1298": "Lechonk",
    "1299": "Oinkologne-M",
    "1300": "Oinkologne-F",
    "1301": "Tarountula",
    "1302": "Spidops",
    "1303": "Nymble",
    "1304": "Lokix",
    "1305": "Pawmi",
    "1306": "Pawmo",
    "1307": "Pawmot",
    "1308": "Tandemaus",
    "1309": "Maushold-Three",
    "1310": "Maushold-Four",
    "1311": "Fidough",
    "1312": "Dachsbun",
    "1313": "Smoliv",
    "1314": "Dolliv",
    "1315": "Arboliva",
    "1316": "Squawkabilly-Green",
    "1317": "Squawkabilly-Blue",
    "1318": "Squawkabilly-Yellow",
    "1319": "Squawkabilly-White",
    "1320": "Nacli",
    "1321": "Naclstack",
    "1322": "Garganacl",
    "1323": "Charcadet",
    "1324": "Armarouge",
    "1325": "Ceruledge",
    "1326": "Tadbulb",
    "1327": "Bellibolt",
    "1328": "Wattrel",
    "1329": "Kilowattrel",
    "1330": "Maschiff",
    "1331": "Mabosstiff",
    "1332": "Shroodle",
    "1333": "Grafaiai",
    "1334": "Bramblin",
    "1335": "Brambleghast",
    "1336": "Toedscool",
    "1337": "Toedscruel",
    "1338": "Klawf",
    "1339": "Capsakid",
    "1340": "Scovillain",
    "1341": "Rellor",
    "1342": "Rabsca",
    "1343": "Flittle",
    "1344": "Espathra",
    "1345": "Tinkatink",
    "1346": "Tinkatuff",
    "1347": "Tinkaton",
    "1348": "Wiglett",
    "1349": "Wugtrio",
    "1350": "Bombirdier",
    "1351": "Finizen",
    "1352": "Palafin-Zero",
    "1353": "Palafin-Hero",
    "1354": "Varoom",
    "1355": "Revavroom",
    "1356": "Cyclizar",
    "1357": "Orthworm",
    "1358": "Glimmet",
    "1359": "Glimmora",
    "1360": "Greavard",
    "1361": "Houndstone",
    "1362": "Flamigo",
    "1363": "Cetoddle",
    "1364": "Cetitan",
    "1365": "Veluza",
    "1366": "Dondozo",
    "1367": "Tatsugiri-Curly",
    "1368": "Tatsugiri-Droopy",
    "1369": "Tatsugiri-Stretchy",
    "1370": "Annihilape",
    "1371": "Clodsire",
    "1372": "Farigiraf",
    "1373": "Dudunsparce-Two-Segment",
    "1374": "Dudunsparce-Three-Segment",
    "1375": "Kingambit",
    "1376": "Great-Tusk",
    "1377": "Scream-Tail",
    "1378": "Brute-Bonnet",
    "1379": "Flutter-Mane",
    "1380": "Slither-Wing",
    "1381": "Sandy-Shocks",
    "1382": "Iron-Treads",
    "1383": "Iron-Bundle",
    "1384": "Iron-Hands",
    "1385": "Iron-Jugulis",
    "1386": "Iron-Moth",
    "1387": "Iron-Thorns",
    "1388": "Frigibax",
    "1389": "Arctibax",
    "1390": "Baxcalibur",
    "1391": "Gimmighoul-Chest",
    "1392": "Gimmighoul-Roaming",
    "1393": "Gholdengo",
    "1394": "Wo-Chien",
    "1395": "Chien-Pao",
    "1396": "Ting-Lu",
    "1397": "Chi-Yu",
    "1398": "Roaring-Moon",
    "1399": "Iron-Valiant",
    "1400": "Koraidon",
    "1401": "Miraidon",
    "1402": "Tauros-Paldea-Combat",
    "1403": "Tauros-Paldea-Blaze",
    "1404": "Tauros-Paldea-Aqua",
    "1405": "Wooper-Paldea",
    "1406": "Walking-Wake",
    "1407": "Iron-Leaves",
    "1408": "Dipplin",
    "1409": "Poltchageist-Counterfeit",
    "1410": "Poltchageist-Artisan",
    "1411": "Sinistcha-Unremarkable",
    "1412": "Sinistcha-Masterpiece",
    "1413": "Okidogi",
    "1414": "Munkidori",
    "1415": "Fezandipiti",
    "1416": "Ogerpon-Teal",
    "1417": "Ogerpon-Wellspring",
    "1418": "Ogerpon-Hearthflame",
    "1419": "Ogerpon-Cornerstone",
    "1420": "Ogerpon-Teal-Tera",
    "1421": "Ogerpon-Wellspring-Tera",
    "1422": "Ogerpon-Hearthflame-Tera",
    "1423": "Ogerpon-Cornerstone-Tera",
    "1424": "Ursaluna-Bloodmoon",
    "1425": "Archaludon",
    "1426": "Hydrapple",
    "1427": "Gouging-Fire",
    "1428": "Raging-Bolt",
    "1429": "Iron-Boulder",
    "1430": "Iron-Crown",
    "1431": "Terapagos-Normal",
    "1432": "Terapagos-Terastal",
    "1433": "Terapagos-Stellar",
    "1434": "Pecharunt",
    "1435": "Lugia-Shadow",
    "1436": "Mothim-Sandy",
    "1437": "Mothim-Trash",
    "1438": "Scatterbug-Polar",
    "1439": "Scatterbug-Tundra",
    "1440": "Scatterbug-Continental",
    "1441": "Scatterbug-Garden",
    "1442": "Scatterbug-Elegant",
    "1443": "Scatterbug-Meadow",
    "1444": "Scatterbug-Modern",
    "1445": "Scatterbug-Marine",
    "1446": "Scatterbug-Archipelago",
    "1447": "Scatterbug-High-Plains",
    "1448": "Scatterbug-Sandstorm",
    "1449": "Scatterbug-River",
    "1450": "Scatterbug-Monsoon",
    "1451": "Scatterbug-Savanna",
    "1452": "Scatterbug-Sun",
    "1453": "Scatterbug-Ocean",
    "1454": "Scatterbug-Jungle",
    "1455": "Scatterbug-Fancy",
    "1456": "Scatterbug-Pokeball",
    "1457": "Spewpa-Polar",
    "1458": "Spewpa-Tundra",
    "1459": "Spewpa-Continental",
    "1460": "Spewpa-Garden",
    "1461": "Spewpa-Elegant",
    "1462": "Spewpa-Meadow",
    "1463": "Spewpa-Modern",
    "1464": "Spewpa-Marine",
    "1465": "Spewpa-Archipelago",
    "1466": "Spewpa-High-Plains",
    "1467": "Spewpa-Sandstorm",
    "1468": "Spewpa-River",
    "1469": "Spewpa-Monsoon",
    "1470": "Spewpa-Savanna",
    "1471": "Spewpa-Sun",
    "1472": "Spewpa-Ocean",
    "1473": "Spewpa-Jungle",
    "1474": "Spewpa-Fancy",
    "1475": "Spewpa-Pokeball",
    "1476": "Raticate-Alola-Totem",
    "1477": "Gumshoos-Totem",
    "1478": "Vikavolt-Totem",
    "1479": "Lurantis-Totem",
    "1480": "Salazzle-Totem",
    "1481": "Mimikyu-Totem-Disguised",
    "1482": "Kommo-O-Totem",
    "1483": "Marowak-Alola-Totem",
    "1484": "Ribombee-Totem",
    "1485": "Araquanid-Totem",
    "1486": "Togedemaru-Totem",
    "1487": "Pikachu-Starter",
    "1488": "Eevee-Starter",
    "1489": "Venusaur-Gmax",
    "1490": "Blastoise-Gmax",
    "1491": "Charizard-Gmax",
    "1492": "Butterfree-Gmax",
    "1493": "Pikachu-Gmax",
    "1494": "Meowth-Gmax",
    "1495": "Machamp-Gmax",
    "1496": "Gengar-Gmax",
    "1497": "Kingler-Gmax",
    "1498": "Lapras-Gmax",
    "1499": "Eevee-Gmax",
    "1500": "Snorlax-Gmax",
    "1501": "Garbodor-Gmax",
    "1502": "Melmetal-Gmax",
    "1503": "Rillaboom-Gmax",
    "1504": "Cinderace-Gmax",
    "1505": "Inteleon-Gmax",
    "1506": "Corviknight-Gmax",
    "1507": "Orbeetle-Gmax",
    "1508": "Drednaw-Gmax",
    "1509": "Coalossal-Gmax",
    "1510": "Flapple-Gmax",
    "1511": "Appletun-Gmax",
    "1512": "Sandaconda-Gmax",
    "1513": "Toxtricity-Amped-Gmax",
    "1514": "Toxtricity-Low-Key-Gmax",
    "1515": "Centiskorch-Gmax",
    "1516": "Hatterene-Gmax",
    "1517": "Grimmsnarl-Gmax",
    "1518": "Alcremie-Gmax",
    "1519": "Copperajah-Gmax",
    "1520": "Duraludon-Gmax",
    "1521": "Urshifu-Single-Strike-Gmax",
    "1522": "Urshifu-Rapid-Strike-Gmax",
    "1523": "Mimikyu-Busted-Totem",
    "1524": "Pichu-Mega",
    "1525": "Cleffa-Mega",
    "1526": "Igglybuff-Mega",
    "1527": "Togepi-Mega",
    "1528": "Tyrogue-Mega-L",
    "1529": "Tyrogue-Mega-C",
    "1530": "Tyrogue-Mega-T",
    "1531": "Smoochum-Mega",
    "1532": "Elekid-Mega",
    "1533": "Magby-Mega",
    "1534": "Azurill-Mega",
    "1535": "Wynaut-Mega",
    "1536": "Budew-Mega",
    "1537": "Chingling-Mega",
    "1538": "Bonsly-Mega",
    "1539": "Mime-Jr-Mega-K",
    "1540": "Happiny-Mega",
    "1541": "Munchlax-Mega",
    "1542": "Riolu-Mega",
    "1543": "Mantyke-Mega",
    "1544": "Toxel-Mega-A",
    "1545": "Toxel-Mega-L",
    "1546": "Eevee-Fire",
    "1547": "Eevee-Water",
    "1548": "Eevee-Electric",
    "1549": "Eevee-Dark",
    "1550": "Eevee-Psychic",
    "1551": "Eevee-Grass",
    "1552": "Eevee-Ice",
    "1553": "Eevee-Fairy",
    "1554": "Charcadet-Psychic",
    "1555": "Charcadet-Ghost",
    "1556": "Eevee-Starter-Fire",
    "1557": "Eevee-Starter-Water",
    "1558": "Eevee-Starter-Electric",
    "1559": "Eevee-Starter-Dark",
    "1560": "Eevee-Starter-Psychic",
    "1561": "Eevee-Starter-Grass",
    "1562": "Eevee-Starter-Ice",
    "1563": "Eevee-Starter-Fairy",
    "1564": "Ralts-Fighting",
    "1565": "Snorunt-Ghost",
    "1566": "Wurmple-Poison",
    "1567": "Nincada-Ghost",
    "1568": "Exeggcute-Dragon",
    "1569": "Koffing-Fairy",
    "1570": "Petilil-Fighting",
    "1571": "Rufflet-Psychic",
    "1572": "Goomy-Steel",
    "1573": "Bergmite-Rock",
    "1574": "Cosmog-Ghost",
    "1575": "Mime-Jr-Mega-G",
    "1576": "Magikarp-Monster",
    "1577": "Froakie-Special",
    "1578": "Rockruff-Special",
    "1579": "Feebas-Fairy"
}

all_abilities = [
    None,
    'stench',
    'drizzle',
    'speed-boost',
    'battle-armor',
    'sturdy',
    'damp',
    'limber',
    'sand-veil',
    'static',
    'volt-absorb',
    'water-absorb',
    'oblivious',
    'cloud-nine',
    'compound-eyes',
    'insomnia',
    'color-change',
    'immunity',
    'flash-fire',
    'shield-dust',
    'own-tempo',
    'suction-cups',
    'intimidate',
    'shadow-tag',
    'rough-skin',
    'wonder-guard',
    'levitate',
    'effect-spore',
    'synchronize',
    'clear-body',
    'natural-cure',
    'lightning-rod',
    'serene-grace',
    'swift-swim',
    'chlorophyll',
    'illuminate',
    'trace',
    'huge-power',
    'poison-point',
    'inner-focus',
    'magma-armor',
    'water-veil',
    'magnet-pull',
    'soundproof',
    'rain-dish',
    'sand-stream',
    'pressure',
    'thick-fat',
    'early-bird',
    'flame-body',
    'run-away',
    'keen-eye',
    'hyper-cutter',
    'pickup',
    'truant',
    'hustle',
    'cute-charm',
    'plus',
    'minus',
    'forecast',
    'sticky-hold',
    'shed-skin',
    'guts',
    'marvel-scale',
    'liquid-ooze',
    'overgrow',
    'blaze',
    'torrent',
    'swarm',
    'rock-head',
    'drought',
    'arena-trap',
    'vital-spirit',
    'white-smoke',
    'pure-power',
    'shell-armor',
    'air-lock',
    'tangled-feet',
    'motor-drive',
    'rivalry',
    'steadfast',
    'snow-cloak',
    'gluttony',
    'anger-point',
    'unburden',
    'heatproof',
    'simple',
    'dry-skin',
    'download',
    'iron-fist',
    'poison-heal',
    'adaptability',
    'skill-link',
    'hydration',
    'solar-power',
    'quick-feet',
    'normalize',
    'sniper',
    'magic-guard',
    'no-guard',
    'stall',
    'technician',
    'leaf-guard',
    'klutz',
    'mold-breaker',
    'super-luck',
    'aftermath',
    'anticipation',
    'forewarn',
    'unaware',
    'tinted-lens',
    'filter',
    'slow-start',
    'scrappy',
    'storm-drain',
    'ice-body',
    'solid-rock',
    'snow-warning',
    'honey-gather',
    'frisk',
    'reckless',
    'multitype',
    'flower-gift',
    'bad-dreams',
    'pickpocket',
    'sheer-force',
    'contrary',
    'unnerve',
    'defiant',
    'defeatist',
    'cursed-body',
    'healer',
    'friend-guard',
    'weak-armor',
    'heavy-metal',
    'light-metal',
    'multiscale',
    'toxic-boost',
    'flare-boost',
    'harvest',
    'telepathy',
    'moody',
    'overcoat',
    'poison-touch',
    'regenerator',
    'big-pecks',
    'sand-rush',
    'wonder-skin',
    'analytic',
    'illusion',
    'imposter',
    'infiltrator',
    'mummy',
    'moxie',
    'justified',
    'rattled',
    'magic-bounce',
    'sap-sipper',
    'prankster',
    'sand-force',
    'iron-barbs',
    'zen-mode',
    'victory-star',
    'turboblaze',
    'teravolt',
    'aroma-veil',
    'flower-veil',
    'cheek-pouch',
    'protean',
    'fur-coat',
    'magician',
    'bulletproof',
    'competitive',
    'strong-jaw',
    'refrigerate',
    'sweet-veil',
    'stance-change',
    'gale-wings',
    'mega-launcher',
    'grass-pelt',
    'symbiosis',
    'tough-claws',
    'pixilate',
    'gooey',
    'aerilate',
    'parental-bond',
    'dark-aura',
    'fairy-aura',
    'aura-break',
    'primordial-sea',
    'desolate-land',
    'delta-stream',
    'stamina',
    'wimp-out',
    'emergency-exit',
    'water-compaction',
    'merciless',
    'shields-down',
    'stakeout',
    'water-bubble',
    'steelworker',
    'berserk',
    'slush-rush',
    'long-reach',
    'liquid-voice',
    'triage',
    'galvanize',
    'surge-surfer',
    'schooling',
    'disguise',
    'battle-bond',
    'power-construct',
    'corrosion',
    'comatose',
    'queenly-majesty',
    'innards-out',
    'dancer',
    'battery',
    'fluffy',
    'dazzling',
    'soul-heart',
    'tangling-hair',
    'receiver',
    'power-of-alchemy',
    'beast-boost',
    'rks-system',
    'electric-surge',
    'psychic-surge',
    'misty-surge',
    'grassy-surge',
    'full-metal-body',
    'shadow-shield',
    'prism-armor',
    'neuroforce',
    'intrepid-sword',
    'dauntless-shield',
    'libero',
    'ball-fetch',
    'cotton-down',
    'propeller-tail',
    'mirror-armor',
    'gulp-missile',
    'stalwart',
    'steam-engine',
    'punk-rock',
    'sand-spit',
    'ice-scales',
    'ripen',
    'ice-face',
    'power-spot',
    'mimicry',
    'screen-cleaner',
    'steely-spirit',
    'perish-body',
    'wandering-spirit',
    'gorilla-tactics',
    'neutralizing-gas',
    'pastel-veil',
    'hunger-switch',
    'quick-draw',
    'unseen-fist',
    'curious-medicine',
    'transistor',
    'dragons-maw',
    'chilling-neigh',
    'grim-neigh',
    'as-one-glastrier',
    'as-one-spectrier',
    'lingering-aroma',
    'seed-sower',
    'thermal-exchange',
    'anger-shell',
    'purifying-salt',
    'well-baked-body',
    'wind-rider',
    'guard-dog',
    'rocky-payload',
    'wind-power',
    'zero-to-hero',
    'commander',
    'electromorphosis',
    'protosynthesis',
    'quark-drive',
    'good-as-gold',
    'vessel-of-ruin',
    'sword-of-ruin',
    'tablets-of-ruin',
    'beads-of-ruin',
    'orichalcum-pulse',
    'hadron-engine',
    'opportunist',
    'cud-chew',
    'sharpness',
    'supreme-overlord',
    'costar',
    'toxic-debris',
    'armor-tail',
    'earth-eater',
    'mycelium-might',
    'minds-eye',
    'supersweet-syrup',
    'hospitality',
    'toxic-chain',
    'embody-aspect',
    'tera-shift',
    'tera-shell',
    'teraform-zero',
    'poison-puppeteer',
]

pokemon_abilities = {
  "bulbasaur": [
    65,
    34,
    47
  ],
  "ivysaur": [
    65,
    None,
    34
  ],
  "venusaur": [
    65,
    None,
    34
  ],
  "charmander": [
    66,
    94,
    70
  ],
  "charmeleon": [
    66,
    None,
    94
  ],
  "charizard": [
    66,
    None,
    94
  ],
  "squirtle": [
    67,
    44,
    177
  ],
  "wartortle": [
    67,
    None,
    44
  ],
  "blastoise": [
    67,
    None,
    44
  ],
  "caterpie": [
    19,
    None,
    50
  ],
  "metapod": [
    61
  ],
  "butterfree": [
    14,
    None,
    110
  ],
  "weedle": [
    19,
    None,
    50
  ],
  "kakuna": [
    61
  ],
  "beedrill": [
    68,
    None,
    97
  ],
  "pidgey": [
    51,
    77,
    145
  ],
  "pidgeotto": [
    51,
    77,
    145
  ],
  "pidgeot": [
    51,
    77,
    145
  ],
  "rattata": [
    50,
    62,
    55
  ],
  "raticate": [
    50,
    62,
    55
  ],
  "spearow": [
    51,
    None,
    97
  ],
  "fearow": [
    51,
    None,
    97
  ],
  "ekans": [
    22,
    61,
    127
  ],
  "arbok": [
    22,
    61,
    127
  ],
  "pikachu": [
    9,
    None,
    31
  ],
  "raichu": [
    9,
    None,
    31
  ],
  "sandshrew": [
    8,
    None,
    146
  ],
  "sandslash": [
    8,
    None,
    146
  ],
  "nidoran-f": [
    38,
    79,
    55
  ],
  "nidorina": [
    38,
    79,
    55
  ],
  "nidoqueen": [
    38,
    79,
    125
  ],
  "nidoran-m": [
    38,
    79,
    55
  ],
  "nidorino": [
    38,
    79,
    55
  ],
  "nidoking": [
    38,
    79,
    125
  ],
  "clefairy": [
    56,
    98,
    132
  ],
  "clefable": [
    56,
    98,
    109
  ],
  "vulpix": [
    18,
    None,
    70
  ],
  "ninetales": [
    18,
    None,
    70
  ],
  "jigglypuff": [
    56,
    172,
    132
  ],
  "wigglytuff": [
    56,
    172,
    119
  ],
  "zubat": [
    39,
    None,
    151
  ],
  "golbat": [
    39,
    None,
    151
  ],
  "oddish": [
    34,
    None,
    50
  ],
  "gloom": [
    34,
    None,
    1
  ],
  "vileplume": [
    34,
    None,
    27
  ],
  "paras": [
    27,
    87,
    6
  ],
  "parasect": [
    27,
    87,
    6
  ],
  "venonat": [
    14,
    110,
    50
  ],
  "venomoth": [
    19,
    110,
    147
  ],
  "diglett": [
    8,
    71,
    159
  ],
  "dugtrio": [
    8,
    71,
    159
  ],
  "meowth": [
    53,
    101,
    127
  ],
  "persian": [
    7,
    101,
    127
  ],
  "psyduck": [
    6,
    13,
    33
  ],
  "golduck": [
    6,
    13,
    33
  ],
  "mankey": [
    72,
    83,
    128
  ],
  "primeape": [
    72,
    83,
    128
  ],
  "growlithe": [
    22,
    18,
    154
  ],
  "arcanine": [
    22,
    18,
    154
  ],
  "poliwag": [
    11,
    6,
    33
  ],
  "poliwhirl": [
    11,
    6,
    33
  ],
  "poliwrath": [
    11,
    6,
    33
  ],
  "abra": [
    28,
    39,
    98
  ],
  "kadabra": [
    28,
    39,
    98
  ],
  "alakazam": [
    28,
    39,
    98
  ],
  "machop": [
    62,
    99,
    80
  ],
  "machoke": [
    62,
    99,
    80
  ],
  "machamp": [
    62,
    99,
    80
  ],
  "bellsprout": [
    34,
    None,
    82
  ],
  "weepinbell": [
    34,
    None,
    82
  ],
  "victreebel": [
    34,
    None,
    82
  ],
  "tentacool": [
    29,
    64,
    44
  ],
  "tentacruel": [
    29,
    64,
    44
  ],
  "geodude": [
    69,
    5,
    8
  ],
  "graveler": [
    69,
    5,
    8
  ],
  "golem": [
    69,
    5,
    8
  ],
  "ponyta": [
    50,
    18,
    49
  ],
  "rapidash": [
    50,
    18,
    49
  ],
  "slowpoke": [
    12,
    20,
    144
  ],
  "slowbro": [
    12,
    20,
    144
  ],
  "magnemite": [
    42,
    5,
    148
  ],
  "magneton": [
    42,
    5,
    148
  ],
  "farfetchd": [
    51,
    39,
    128
  ],
  "doduo": [
    50,
    48,
    77
  ],
  "dodrio": [
    50,
    48,
    77
  ],
  "seel": [
    47,
    93,
    115
  ],
  "dewgong": [
    47,
    93,
    115
  ],
  "grimer": [
    1,
    60,
    143
  ],
  "muk": [
    1,
    60,
    143
  ],
  "shellder": [
    75,
    92,
    142
  ],
  "cloyster": [
    75,
    92,
    142
  ],
  "gastly": [
    26
  ],
  "haunter": [
    26
  ],
  "gengar": [
    130
  ],
  "onix": [
    69,
    5,
    133
  ],
  "drowzee": [
    15,
    108,
    39
  ],
  "hypno": [
    15,
    108,
    39
  ],
  "krabby": [
    52,
    75,
    125
  ],
  "kingler": [
    52,
    75,
    125
  ],
  "voltorb": [
    43,
    9,
    106
  ],
  "electrode": [
    43,
    9,
    106
  ],
  "exeggcute": [
    34,
    None,
    139
  ],
  "exeggutor": [
    34,
    None,
    139
  ],
  "cubone": [
    69,
    31,
    4
  ],
  "marowak": [
    69,
    31,
    4
  ],
  "hitmonlee": [
    7,
    120,
    84
  ],
  "hitmonchan": [
    51,
    89,
    39
  ],
  "lickitung": [
    20,
    12,
    13
  ],
  "koffing": [
    26,
    256,
    1
  ],
  "weezing": [
    26,
    256,
    1
  ],
  "rhyhorn": [
    31,
    69,
    120
  ],
  "rhydon": [
    31,
    69,
    120
  ],
  "chansey": [
    30,
    32,
    131
  ],
  "tangela": [
    34,
    102,
    144
  ],
  "kangaskhan": [
    48,
    113,
    39
  ],
  "horsea": [
    33,
    97,
    6
  ],
  "seadra": [
    38,
    97,
    6
  ],
  "goldeen": [
    33,
    41,
    31
  ],
  "seaking": [
    33,
    41,
    31
  ],
  "staryu": [
    35,
    30,
    148
  ],
  "starmie": [
    35,
    30,
    148
  ],
  "mr-mime": [
    43,
    111,
    101
  ],
  "scyther": [
    68,
    101,
    80
  ],
  "jynx": [
    12,
    108,
    87
  ],
  "electabuzz": [
    9,
    None,
    72
  ],
  "magmar": [
    49,
    None,
    72
  ],
  "pinsir": [
    52,
    104,
    153
  ],
  "tauros": [
    22,
    83,
    125
  ],
  "magikarp": [
    33,
    None,
    155
  ],
  "gyarados": [
    22,
    None,
    153
  ],
  "lapras": [
    11,
    75,
    93
  ],
  "ditto": [
    7,
    None,
    150
  ],
  "eevee": [
    50,
    91,
    107
  ],
  "vaporeon": [
    11,
    None,
    93
  ],
  "jolteon": [
    10,
    None,
    95
  ],
  "flareon": [
    18,
    None,
    62
  ],
  "porygon": [
    36,
    88,
    148
  ],
  "omanyte": [
    33,
    75,
    133
  ],
  "omastar": [
    33,
    75,
    133
  ],
  "kabuto": [
    33,
    4,
    133
  ],
  "kabutops": [
    33,
    4,
    133
  ],
  "aerodactyl": [
    69,
    46,
    127
  ],
  "snorlax": [
    17,
    47,
    82
  ],
  "articuno": [
    46,
    None,
    81
  ],
  "zapdos": [
    46,
    None,
    9
  ],
  "moltres": [
    46,
    None,
    49
  ],
  "dratini": [
    61,
    None,
    63
  ],
  "dragonair": [
    61,
    None,
    63
  ],
  "dragonite": [
    39,
    None,
    136
  ],
  "mewtwo": [
    46,
    None,
    127
  ],
  "mew": [
    28
  ],
  "chikorita": [
    65,
    None,
    102
  ],
  "bayleef": [
    65,
    None,
    102
  ],
  "meganium": [
    65,
    None,
    102
  ],
  "cyndaquil": [
    66,
    None,
    18
  ],
  "quilava": [
    66,
    None,
    18
  ],
  "typhlosion": [
    66,
    None,
    18
  ],
  "totodile": [
    67,
    None,
    125
  ],
  "croconaw": [
    67,
    None,
    125
  ],
  "feraligatr": [
    67,
    None,
    125
  ],
  "sentret": [
    50,
    51,
    119
  ],
  "furret": [
    50,
    51,
    119
  ],
  "hoothoot": [
    15,
    51,
    110
  ],
  "noctowl": [
    15,
    51,
    110
  ],
  "ledyba": [
    68,
    48,
    155
  ],
  "ledian": [
    68,
    48,
    89
  ],
  "spinarak": [
    68,
    15,
    97
  ],
  "ariados": [
    68,
    15,
    97
  ],
  "crobat": [
    39,
    None,
    151
  ],
  "chinchou": [
    10,
    35,
    11
  ],
  "lanturn": [
    10,
    35,
    11
  ],
  "pichu": [
    9,
    None,
    31
  ],
  "cleffa": [
    56,
    98,
    132
  ],
  "igglybuff": [
    56,
    172,
    132
  ],
  "togepi": [
    55,
    32,
    105
  ],
  "togetic": [
    55,
    32,
    105
  ],
  "natu": [
    28,
    48,
    156
  ],
  "xatu": [
    28,
    48,
    156
  ],
  "mareep": [
    9,
    None,
    57
  ],
  "flaaffy": [
    9,
    None,
    57
  ],
  "ampharos": [
    9,
    None,
    57
  ],
  "bellossom": [
    34,
    None,
    131
  ],
  "marill": [
    47,
    37,
    157
  ],
  "azumarill": [
    47,
    37,
    157
  ],
  "sudowoodo": [
    5,
    69,
    155
  ],
  "politoed": [
    11,
    6,
    2
  ],
  "hoppip": [
    34,
    102,
    151
  ],
  "skiploom": [
    34,
    102,
    151
  ],
  "jumpluff": [
    34,
    102,
    151
  ],
  "aipom": [
    50,
    53,
    92
  ],
  "sunkern": [
    34,
    94,
    48
  ],
  "sunflora": [
    34,
    94,
    48
  ],
  "yanma": [
    3,
    14,
    119
  ],
  "wooper": [
    6,
    11,
    109
  ],
  "quagsire": [
    6,
    11,
    109
  ],
  "espeon": [
    28,
    None,
    156
  ],
  "umbreon": [
    28,
    None,
    39
  ],
  "murkrow": [
    15,
    105,
    158
  ],
  "slowking": [
    12,
    20,
    144
  ],
  "misdreavus": [
    26
  ],
  "unown": [
    26
  ],
  "wobbuffet": [
    23,
    None,
    140
  ],
  "girafarig": [
    39,
    48,
    157
  ],
  "pineco": [
    5,
    None,
    142
  ],
  "forretress": [
    5,
    None,
    142
  ],
  "dunsparce": [
    32,
    50,
    155
  ],
  "gligar": [
    52,
    8,
    17
  ],
  "steelix": [
    69,
    5,
    125
  ],
  "snubbull": [
    22,
    50,
    155
  ],
  "granbull": [
    22,
    95,
    155
  ],
  "qwilfish": [
    38,
    33,
    22
  ],
  "scizor": [
    68,
    101,
    135
  ],
  "shuckle": [
    5,
    82,
    126
  ],
  "heracross": [
    68,
    62,
    153
  ],
  "sneasel": [
    39,
    51,
    124
  ],
  "teddiursa": [
    53,
    95,
    118
  ],
  "ursaring": [
    62,
    95,
    127
  ],
  "slugma": [
    40,
    49,
    133
  ],
  "magcargo": [
    40,
    49,
    133
  ],
  "swinub": [
    12,
    81,
    47
  ],
  "piloswine": [
    12,
    81,
    47
  ],
  "corsola": [
    55,
    30,
    144
  ],
  "remoraid": [
    55,
    97,
    141
  ],
  "octillery": [
    21,
    97,
    141
  ],
  "delibird": [
    72,
    55,
    15
  ],
  "mantine": [
    33,
    11,
    41
  ],
  "skarmory": [
    51,
    5,
    133
  ],
  "houndour": [
    48,
    18,
    127
  ],
  "houndoom": [
    48,
    18,
    127
  ],
  "kingdra": [
    33,
    97,
    6
  ],
  "phanpy": [
    53,
    None,
    8
  ],
  "donphan": [
    5,
    None,
    8
  ],
  "porygon2": [
    36,
    88,
    148
  ],
  "stantler": [
    22,
    119,
    157
  ],
  "smeargle": [
    20,
    101,
    141
  ],
  "tyrogue": [
    62,
    80,
    72
  ],
  "hitmontop": [
    22,
    101,
    80
  ],
  "smoochum": [
    12,
    108,
    93
  ],
  "elekid": [
    9,
    None,
    72
  ],
  "magby": [
    49,
    None,
    72
  ],
  "miltank": [
    47,
    113,
    157
  ],
  "blissey": [
    30,
    32,
    131
  ],
  "raikou": [
    46,
    None,
    39
  ],
  "entei": [
    46,
    None,
    39
  ],
  "suicune": [
    46,
    None,
    39
  ],
  "larvitar": [
    62,
    None,
    8
  ],
  "pupitar": [
    61
  ],
  "tyranitar": [
    45,
    None,
    127
  ],
  "lugia": [
    46,
    None,
    136
  ],
  "ho-oh": [
    46,
    None,
    144
  ],
  "celebi": [
    30
  ],
  "treecko": [
    65,
    None,
    84
  ],
  "grovyle": [
    65,
    None,
    84
  ],
  "sceptile": [
    65,
    None,
    84
  ],
  "torchic": [
    66,
    None,
    3
  ],
  "combusken": [
    66,
    None,
    3
  ],
  "blaziken": [
    66,
    None,
    3
  ],
  "mudkip": [
    67,
    None,
    6
  ],
  "marshtomp": [
    67,
    None,
    6
  ],
  "swampert": [
    67,
    None,
    6
  ],
  "poochyena": [
    50,
    95,
    155
  ],
  "mightyena": [
    22,
    95,
    153
  ],
  "zigzagoon": [
    53,
    82,
    95
  ],
  "linoone": [
    53,
    82,
    95
  ],
  "wurmple": [
    19,
    None,
    50
  ],
  "silcoon": [
    61
  ],
  "beautifly": [
    68,
    None,
    79
  ],
  "cascoon": [
    61
  ],
  "dustox": [
    19,
    None,
    14
  ],
  "lotad": [
    33,
    44,
    20
  ],
  "lombre": [
    33,
    44,
    20
  ],
  "ludicolo": [
    33,
    44,
    20
  ],
  "seedot": [
    34,
    48,
    124
  ],
  "nuzleaf": [
    34,
    48,
    124
  ],
  "shiftry": [
    34,
    274,
    124
  ],
  "taillow": [
    62,
    None,
    113
  ],
  "swellow": [
    62,
    None,
    113
  ],
  "wingull": [
    51,
    93,
    44
  ],
  "pelipper": [
    51,
    2,
    44
  ],
  "ralts": [
    28,
    36,
    140
  ],
  "kirlia": [
    28,
    36,
    140
  ],
  "gardevoir": [
    28,
    36,
    140
  ],
  "surskit": [
    33,
    None,
    44
  ],
  "masquerain": [
    22,
    None,
    127
  ],
  "shroomish": [
    27,
    90,
    95
  ],
  "breloom": [
    27,
    90,
    101
  ],
  "slakoth": [
    54
  ],
  "vigoroth": [
    72
  ],
  "slaking": [
    54
  ],
  "nincada": [
    14,
    None,
    50
  ],
  "ninjask": [
    3,
    None,
    151
  ],
  "shedinja": [
    25
  ],
  "whismur": [
    43,
    None,
    155
  ],
  "loudred": [
    43,
    None,
    113
  ],
  "exploud": [
    43,
    None,
    113
  ],
  "makuhita": [
    47,
    62,
    125
  ],
  "hariyama": [
    47,
    62,
    125
  ],
  "azurill": [
    47,
    37,
    157
  ],
  "nosepass": [
    5,
    42,
    159
  ],
  "skitty": [
    56,
    96,
    147
  ],
  "delcatty": [
    56,
    96,
    147
  ],
  "sableye": [
    51,
    100,
    158
  ],
  "mawile": [
    52,
    22,
    125
  ],
  "aron": [
    5,
    69,
    134
  ],
  "lairon": [
    5,
    69,
    134
  ],
  "aggron": [
    5,
    69,
    134
  ],
  "meditite": [
    74,
    None,
    140
  ],
  "medicham": [
    74,
    None,
    140
  ],
  "electrike": [
    9,
    31,
    58
  ],
  "manectric": [
    9,
    31,
    58
  ],
  "plusle": [
    57,
    None,
    31
  ],
  "minun": [
    58,
    None,
    10
  ],
  "volbeat": [
    35,
    68,
    158
  ],
  "illumise": [
    12,
    110,
    158
  ],
  "roselia": [
    30,
    38,
    102
  ],
  "gulpin": [
    64,
    60,
    82
  ],
  "swalot": [
    64,
    60,
    82
  ],
  "carvanha": [
    24,
    None,
    3
  ],
  "sharpedo": [
    24,
    None,
    3
  ],
  "wailmer": [
    41,
    12,
    46
  ],
  "wailord": [
    41,
    12,
    46
  ],
  "numel": [
    12,
    86,
    20
  ],
  "camerupt": [
    40,
    116,
    83
  ],
  "torkoal": [
    73,
    70,
    75
  ],
  "spoink": [
    47,
    20,
    82
  ],
  "grumpig": [
    47,
    20,
    82
  ],
  "spinda": [
    20,
    77,
    126
  ],
  "trapinch": [
    52,
    71,
    125
  ],
  "vibrava": [
    26
  ],
  "flygon": [
    26
  ],
  "cacnea": [
    8,
    None,
    11
  ],
  "cacturne": [
    8,
    None,
    11
  ],
  "swablu": [
    30,
    None,
    13
  ],
  "altaria": [
    30,
    None,
    13
  ],
  "zangoose": [
    17,
    None,
    137
  ],
  "seviper": [
    61,
    None,
    151
  ],
  "lunatone": [
    26
  ],
  "solrock": [
    26
  ],
  "barboach": [
    12,
    107,
    93
  ],
  "whiscash": [
    12,
    107,
    93
  ],
  "corphish": [
    52,
    75,
    91
  ],
  "crawdaunt": [
    52,
    75,
    91
  ],
  "baltoy": [
    26
  ],
  "claydol": [
    26
  ],
  "lileep": [
    21,
    None,
    114
  ],
  "cradily": [
    21,
    None,
    114
  ],
  "anorith": [
    4,
    None,
    33
  ],
  "armaldo": [
    4,
    None,
    33
  ],
  "feebas": [
    33,
    12,
    91
  ],
  "milotic": [
    63,
    172,
    56
  ],
  "castform": [
    59
  ],
  "kecleon": [
    16,
    None,
    168
  ],
  "shuppet": [
    15,
    119,
    130
  ],
  "banette": [
    15,
    119,
    130
  ],
  "duskull": [
    26,
    None,
    119
  ],
  "dusclops": [
    46,
    None,
    119
  ],
  "tropius": [
    34,
    94,
    139
  ],
  "chimecho": [
    26
  ],
  "absol": [
    46,
    105,
    154
  ],
  "wynaut": [
    23,
    None,
    140
  ],
  "snorunt": [
    39,
    115,
    141
  ],
  "glalie": [
    39,
    115,
    141
  ],
  "spheal": [
    47,
    115,
    12
  ],
  "sealeo": [
    47,
    115,
    12
  ],
  "walrein": [
    47,
    115,
    12
  ],
  "clamperl": [
    75,
    None,
    155
  ],
  "huntail": [
    33,
    None,
    41
  ],
  "gorebyss": [
    33,
    None,
    93
  ],
  "relicanth": [
    33,
    69,
    5
  ],
  "luvdisc": [
    33,
    None,
    93
  ],
  "bagon": [
    69,
    None,
    125
  ],
  "shelgon": [
    69,
    None,
    142
  ],
  "salamence": [
    22,
    None,
    153
  ],
  "beldum": [
    29,
    None,
    135
  ],
  "metang": [
    29,
    None,
    135
  ],
  "metagross": [
    29,
    None,
    135
  ],
  "regirock": [
    29,
    None,
    5
  ],
  "regice": [
    29,
    None,
    115
  ],
  "registeel": [
    29,
    None,
    135
  ],
  "latias": [
    26
  ],
  "latios": [
    26
  ],
  "kyogre": [
    2
  ],
  "groudon": [
    70
  ],
  "rayquaza": [
    76
  ],
  "jirachi": [
    32
  ],
  "deoxys": [
    46
  ],
  "turtwig": [
    65,
    None,
    75
  ],
  "grotle": [
    65,
    None,
    75
  ],
  "torterra": [
    65,
    None,
    75
  ],
  "chimchar": [
    66,
    None,
    89
  ],
  "monferno": [
    66,
    None,
    89
  ],
  "infernape": [
    66,
    None,
    89
  ],
  "piplup": [
    67,
    None,
    172
  ],
  "prinplup": [
    67,
    None,
    172
  ],
  "empoleon": [
    67,
    None,
    172
  ],
  "starly": [
    51,
    None,
    120
  ],
  "staravia": [
    22,
    None,
    120
  ],
  "staraptor": [
    22,
    None,
    120
  ],
  "bidoof": [
    86,
    109,
    141
  ],
  "bibarel": [
    86,
    109,
    141
  ],
  "kricketot": [
    61,
    None,
    50
  ],
  "kricketune": [
    68,
    None,
    101
  ],
  "shinx": [
    79,
    22,
    62
  ],
  "luxio": [
    79,
    22,
    62
  ],
  "luxray": [
    79,
    22,
    62
  ],
  "budew": [
    30,
    38,
    102
  ],
  "roserade": [
    30,
    38,
    101
  ],
  "cranidos": [
    104,
    None,
    125
  ],
  "rampardos": [
    104,
    None,
    125
  ],
  "shieldon": [
    5,
    None,
    43
  ],
  "bastiodon": [
    5,
    None,
    43
  ],
  "burmy": [
    61,
    None,
    142
  ],
  "wormadam": [
    107,
    None,
    142
  ],
  "mothim": [
    68,
    None,
    110
  ],
  "combee": [
    118,
    None,
    55
  ],
  "vespiquen": [
    46,
    None,
    127
  ],
  "pachirisu": [
    50,
    53,
    10
  ],
  "buizel": [
    33,
    None,
    41
  ],
  "floatzel": [
    33,
    None,
    41
  ],
  "cherubi": [
    34
  ],
  "cherrim": [
    122
  ],
  "shellos": [
    60,
    114,
    159
  ],
  "gastrodon": [
    60,
    114,
    159
  ],
  "ambipom": [
    101,
    53,
    92
  ],
  "drifloon": [
    106,
    84,
    138
  ],
  "drifblim": [
    106,
    84,
    138
  ],
  "buneary": [
    50,
    103,
    7
  ],
  "lopunny": [
    56,
    103,
    7
  ],
  "mismagius": [
    26
  ],
  "honchkrow": [
    15,
    105,
    153
  ],
  "glameow": [
    7,
    20,
    51
  ],
  "purugly": [
    47,
    20,
    128
  ],
  "chingling": [
    26
  ],
  "stunky": [
    1,
    106,
    51
  ],
  "skuntank": [
    1,
    106,
    51
  ],
  "bronzor": [
    26,
    85,
    134
  ],
  "bronzong": [
    26,
    85,
    134
  ],
  "bonsly": [
    5,
    69,
    155
  ],
  "mime-jr": [
    43,
    111,
    101
  ],
  "happiny": [
    30,
    32,
    132
  ],
  "chatot": [
    51,
    77,
    145
  ],
  "spiritomb": [
    46,
    None,
    151
  ],
  "gible": [
    8,
    None,
    24
  ],
  "gabite": [
    8,
    None,
    24
  ],
  "garchomp": [
    8,
    None,
    24
  ],
  "munchlax": [
    53,
    47,
    82
  ],
  "riolu": [
    80,
    39,
    158
  ],
  "lucario": [
    80,
    39,
    154
  ],
  "hippopotas": [
    45,
    None,
    159
  ],
  "hippowdon": [
    45,
    None,
    159
  ],
  "skorupi": [
    4,
    97,
    51
  ],
  "drapion": [
    4,
    97,
    51
  ],
  "croagunk": [
    107,
    87,
    143
  ],
  "toxicroak": [
    107,
    87,
    143
  ],
  "carnivine": [
    26
  ],
  "finneon": [
    33,
    114,
    41
  ],
  "lumineon": [
    33,
    114,
    41
  ],
  "mantyke": [
    33,
    11,
    41
  ],
  "snover": [
    117,
    None,
    43
  ],
  "abomasnow": [
    117,
    None,
    43
  ],
  "weavile": [
    46,
    None,
    124
  ],
  "magnezone": [
    42,
    5,
    148
  ],
  "lickilicky": [
    20,
    12,
    13
  ],
  "rhyperior": [
    31,
    116,
    120
  ],
  "tangrowth": [
    34,
    102,
    144
  ],
  "electivire": [
    78,
    None,
    72
  ],
  "magmortar": [
    49,
    None,
    72
  ],
  "togekiss": [
    55,
    32,
    105
  ],
  "yanmega": [
    3,
    110,
    119
  ],
  "leafeon": [
    102,
    None,
    34
  ],
  "glaceon": [
    81,
    None,
    115
  ],
  "gliscor": [
    52,
    8,
    90
  ],
  "mamoswine": [
    12,
    81,
    47
  ],
  "porygon-z": [
    91,
    88,
    148
  ],
  "gallade": [
    80,
    292,
    154
  ],
  "probopass": [
    5,
    42,
    159
  ],
  "dusknoir": [
    46,
    None,
    119
  ],
  "froslass": [
    81,
    None,
    130
  ],
  "rotom": [
    26
  ],
  "uxie": [
    26
  ],
  "mesprit": [
    26
  ],
  "azelf": [
    26
  ],
  "dialga": [
    46,
    None,
    140
  ],
  "palkia": [
    46,
    None,
    140
  ],
  "heatran": [
    18,
    None,
    49
  ],
  "regigigas": [
    112
  ],
  "giratina": [
    46,
    None,
    140
  ],
  "cresselia": [
    26
  ],
  "phione": [
    93
  ],
  "manaphy": [
    93
  ],
  "darkrai": [
    123
  ],
  "shaymin": [
    30
  ],
  "arceus": [
    121
  ],
  "victini": [
    162
  ],
  "snivy": [
    65,
    None,
    126
  ],
  "servine": [
    65,
    None,
    126
  ],
  "serperior": [
    65,
    None,
    126
  ],
  "tepig": [
    66,
    None,
    47
  ],
  "pignite": [
    66,
    None,
    47
  ],
  "emboar": [
    66,
    None,
    120
  ],
  "oshawott": [
    67,
    None,
    75
  ],
  "dewott": [
    67,
    None,
    75
  ],
  "samurott": [
    67,
    None,
    75
  ],
  "patrat": [
    50,
    51,
    148
  ],
  "watchog": [
    35,
    51,
    148
  ],
  "lillipup": [
    72,
    53,
    50
  ],
  "herdier": [
    22,
    146,
    113
  ],
  "stoutland": [
    22,
    146,
    113
  ],
  "purrloin": [
    7,
    84,
    158
  ],
  "liepard": [
    7,
    84,
    158
  ],
  "pansage": [
    82,
    None,
    65
  ],
  "simisage": [
    82,
    None,
    65
  ],
  "pansear": [
    82,
    None,
    66
  ],
  "simisear": [
    82,
    None,
    66
  ],
  "panpour": [
    82,
    None,
    67
  ],
  "simipour": [
    82,
    None,
    67
  ],
  "munna": [
    108,
    28,
    140
  ],
  "musharna": [
    108,
    28,
    140
  ],
  "pidove": [
    145,
    105,
    79
  ],
  "tranquill": [
    145,
    105,
    79
  ],
  "unfezant": [
    145,
    105,
    79
  ],
  "blitzle": [
    31,
    78,
    157
  ],
  "zebstrika": [
    31,
    78,
    157
  ],
  "roggenrola": [
    5,
    133,
    159
  ],
  "boldore": [
    5,
    133,
    159
  ],
  "gigalith": [
    5,
    45,
    159
  ],
  "woobat": [
    109,
    103,
    86
  ],
  "swoobat": [
    109,
    103,
    86
  ],
  "drilbur": [
    146,
    159,
    104
  ],
  "excadrill": [
    146,
    159,
    104
  ],
  "audino": [
    131,
    144,
    103
  ],
  "timburr": [
    62,
    125,
    89
  ],
  "gurdurr": [
    62,
    125,
    89
  ],
  "conkeldurr": [
    62,
    125,
    89
  ],
  "tympole": [
    33,
    93,
    11
  ],
  "palpitoad": [
    33,
    93,
    11
  ],
  "seismitoad": [
    33,
    143,
    11
  ],
  "throh": [
    62,
    39,
    104
  ],
  "sawk": [
    5,
    39,
    104
  ],
  "sewaddle": [
    68,
    34,
    142
  ],
  "swadloon": [
    102,
    34,
    142
  ],
  "leavanny": [
    68,
    34,
    142
  ],
  "venipede": [
    38,
    68,
    3
  ],
  "whirlipede": [
    38,
    68,
    3
  ],
  "scolipede": [
    38,
    68,
    3
  ],
  "cottonee": [
    158,
    151,
    34
  ],
  "whimsicott": [
    158,
    151,
    34
  ],
  "petilil": [
    34,
    20,
    102
  ],
  "lilligant": [
    34,
    20,
    102
  ],
  "basculin": [
    120,
    91,
    104
  ],
  "sandile": [
    22,
    153,
    83
  ],
  "krokorok": [
    22,
    153,
    83
  ],
  "krookodile": [
    22,
    153,
    83
  ],
  "darumaka": [
    55,
    None,
    39
  ],
  "darmanitan": [
    125,
    None,
    161
  ],
  "maractus": [
    11,
    34,
    114
  ],
  "dwebble": [
    5,
    75,
    133
  ],
  "crustle": [
    5,
    75,
    133
  ],
  "scraggy": [
    61,
    153,
    22
  ],
  "scrafty": [
    61,
    153,
    22
  ],
  "sigilyph": [
    147,
    98,
    110
  ],
  "yamask": [
    152
  ],
  "cofagrigus": [
    152
  ],
  "tirtouga": [
    116,
    5,
    33
  ],
  "carracosta": [
    116,
    5,
    33
  ],
  "archen": [
    129
  ],
  "archeops": [
    129
  ],
  "trubbish": [
    1,
    60,
    106
  ],
  "garbodor": [
    1,
    133,
    106
  ],
  "zorua": [
    149
  ],
  "zoroark": [
    149
  ],
  "minccino": [
    56,
    101,
    92
  ],
  "cinccino": [
    56,
    101,
    92
  ],
  "gothita": [
    119,
    172,
    23
  ],
  "gothorita": [
    119,
    172,
    23
  ],
  "gothitelle": [
    119,
    172,
    23
  ],
  "solosis": [
    142,
    98,
    144
  ],
  "duosion": [
    142,
    98,
    144
  ],
  "reuniclus": [
    142,
    98,
    144
  ],
  "ducklett": [
    51,
    145,
    93
  ],
  "swanna": [
    51,
    145,
    93
  ],
  "vanillite": [
    115,
    81,
    133
  ],
  "vanillish": [
    115,
    81,
    133
  ],
  "vanilluxe": [
    115,
    117,
    133
  ],
  "deerling": [
    34,
    157,
    32
  ],
  "sawsbuck": [
    34,
    157,
    32
  ],
  "emolga": [
    9,
    None,
    78
  ],
  "karrablast": [
    68,
    61,
    99
  ],
  "escavalier": [
    68,
    75,
    142
  ],
  "foongus": [
    27,
    None,
    144
  ],
  "amoonguss": [
    27,
    None,
    144
  ],
  "frillish": [
    11,
    130,
    6
  ],
  "jellicent": [
    11,
    130,
    6
  ],
  "alomomola": [
    131,
    93,
    144
  ],
  "joltik": [
    14,
    127,
    68
  ],
  "galvantula": [
    14,
    127,
    68
  ],
  "ferroseed": [
    160
  ],
  "ferrothorn": [
    160,
    None,
    107
  ],
  "klink": [
    57,
    58,
    29
  ],
  "klang": [
    57,
    58,
    29
  ],
  "klinklang": [
    57,
    58,
    29
  ],
  "tynamo": [
    26
  ],
  "eelektrik": [
    26
  ],
  "eelektross": [
    26
  ],
  "elgyem": [
    140,
    28,
    148
  ],
  "beheeyem": [
    140,
    28,
    148
  ],
  "litwick": [
    18,
    49,
    151
  ],
  "lampent": [
    18,
    49,
    151
  ],
  "chandelure": [
    18,
    49,
    151
  ],
  "axew": [
    79,
    104,
    127
  ],
  "fraxure": [
    79,
    104,
    127
  ],
  "haxorus": [
    79,
    104,
    127
  ],
  "cubchoo": [
    81,
    202,
    155
  ],
  "beartic": [
    81,
    202,
    33
  ],
  "cryogonal": [
    26
  ],
  "shelmet": [
    93,
    75,
    142
  ],
  "accelgor": [
    93,
    60,
    84
  ],
  "stunfisk": [
    9,
    7,
    8
  ],
  "mienfoo": [
    39,
    144,
    120
  ],
  "mienshao": [
    39,
    144,
    120
  ],
  "druddigon": [
    24,
    125,
    104
  ],
  "golett": [
    89,
    103,
    99
  ],
  "golurk": [
    89,
    103,
    99
  ],
  "pawniard": [
    128,
    39,
    46
  ],
  "bisharp": [
    128,
    39,
    46
  ],
  "bouffalant": [
    120,
    157,
    43
  ],
  "rufflet": [
    51,
    125,
    55
  ],
  "braviary": [
    51,
    125,
    128
  ],
  "vullaby": [
    145,
    142,
    133
  ],
  "mandibuzz": [
    145,
    142,
    133
  ],
  "heatmor": [
    82,
    18,
    73
  ],
  "durant": [
    68,
    55,
    54
  ],
  "deino": [
    55
  ],
  "zweilous": [
    55
  ],
  "hydreigon": [
    26
  ],
  "larvesta": [
    49,
    None,
    68
  ],
  "volcarona": [
    49,
    None,
    68
  ],
  "cobalion": [
    154
  ],
  "terrakion": [
    154
  ],
  "virizion": [
    154
  ],
  "tornadus": [
    158,
    None,
    128
  ],
  "thundurus": [
    158,
    None,
    128
  ],
  "reshiram": [
    163
  ],
  "zekrom": [
    164
  ],
  "landorus": [
    159,
    None,
    125
  ],
  "kyurem": [
    46
  ],
  "keldeo": [
    154
  ],
  "meloetta": [
    32
  ],
  "genesect": [
    88
  ],
  "chespin": [
    65,
    None,
    171
  ],
  "quilladin": [
    65,
    None,
    171
  ],
  "chesnaught": [
    65,
    None,
    171
  ],
  "fennekin": [
    66,
    None,
    170
  ],
  "braixen": [
    66,
    None,
    170
  ],
  "delphox": [
    66,
    None,
    170
  ],
  "froakie": [
    67,
    None,
    168
  ],
  "frogadier": [
    67,
    None,
    168
  ],
  "greninja": [
    67,
    None,
    168
  ],
  "bunnelby": [
    53,
    167,
    37
  ],
  "diggersby": [
    53,
    167,
    37
  ],
  "fletchling": [
    145,
    None,
    177
  ],
  "fletchinder": [
    49,
    None,
    177
  ],
  "talonflame": [
    49,
    None,
    177
  ],
  "scatterbug": [
    19,
    14,
    132
  ],
  "spewpa": [
    61,
    None,
    132
  ],
  "vivillon": [
    19,
    14,
    132
  ],
  "litleo": [
    79,
    127,
    153
  ],
  "pyroar": [
    79,
    127,
    153
  ],
  "flabebe": [
    166,
    None,
    180
  ],
  "floette": [
    166,
    None,
    180
  ],
  "florges": [
    166,
    None,
    180
  ],
  "skiddo": [
    157,
    None,
    179
  ],
  "gogoat": [
    157,
    None,
    179
  ],
  "pancham": [
    89,
    104,
    113
  ],
  "pangoro": [
    89,
    104,
    113
  ],
  "furfrou": [
    169
  ],
  "espurr": [
    51,
    151,
    20
  ],
  "meowstic": [
    51,
    151,
    158
  ],
  "honedge": [
    99
  ],
  "doublade": [
    99
  ],
  "aegislash": [
    176
  ],
  "spritzee": [
    131,
    None,
    165
  ],
  "aromatisse": [
    131,
    None,
    165
  ],
  "swirlix": [
    175,
    None,
    84
  ],
  "slurpuff": [
    175,
    None,
    84
  ],
  "inkay": [
    126,
    21,
    151
  ],
  "malamar": [
    126,
    21,
    151
  ],
  "binacle": [
    181,
    97,
    124
  ],
  "barbaracle": [
    181,
    97,
    124
  ],
  "skrelp": [
    38,
    143,
    91
  ],
  "dragalge": [
    38,
    143,
    91
  ],
  "clauncher": [
    178
  ],
  "clawitzer": [
    178
  ],
  "helioptile": [
    87,
    8,
    94
  ],
  "heliolisk": [
    87,
    8,
    94
  ],
  "tyrunt": [
    173,
    None,
    5
  ],
  "tyrantrum": [
    173,
    None,
    69
  ],
  "amaura": [
    174,
    None,
    117
  ],
  "aurorus": [
    174,
    None,
    117
  ],
  "sylveon": [
    56,
    None,
    182
  ],
  "hawlucha": [
    7,
    84,
    104
  ],
  "dedenne": [
    167,
    53,
    57
  ],
  "carbink": [
    29,
    None,
    5
  ],
  "goomy": [
    157,
    93,
    183
  ],
  "sliggoo": [
    157,
    93,
    183
  ],
  "goodra": [
    157,
    93,
    183
  ],
  "klefki": [
    158,
    None,
    170
  ],
  "phantump": [
    30,
    119,
    139
  ],
  "trevenant": [
    30,
    119,
    139
  ],
  "pumpkaboo": [
    53,
    119,
    15
  ],
  "gourgeist": [
    53,
    119,
    15
  ],
  "bergmite": [
    20,
    115,
    5
  ],
  "avalugg": [
    20,
    115,
    5
  ],
  "noibat": [
    119,
    151,
    140
  ],
  "noivern": [
    119,
    151,
    140
  ],
  "xerneas": [
    187
  ],
  "yveltal": [
    186
  ],
  "zygarde": [
    188
  ],
  "diancie": [
    29
  ],
  "hoopa": [
    170
  ],
  "volcanion": [
    11
  ],
  "rowlet": [
    65,
    None,
    203
  ],
  "dartrix": [
    65,
    None,
    203
  ],
  "decidueye": [
    65,
    None,
    203
  ],
  "litten": [
    66,
    None,
    22
  ],
  "torracat": [
    66,
    None,
    22
  ],
  "incineroar": [
    66,
    None,
    22
  ],
  "popplio": [
    67,
    None,
    204
  ],
  "brionne": [
    67,
    None,
    204
  ],
  "primarina": [
    67,
    None,
    204
  ],
  "pikipek": [
    51,
    92,
    53
  ],
  "trumbeak": [
    51,
    92,
    53
  ],
  "toucannon": [
    51,
    92,
    125
  ],
  "yungoos": [
    198,
    173,
    91
  ],
  "gumshoos": [
    198,
    173,
    91
  ],
  "grubbin": [
    68
  ],
  "charjabug": [
    217
  ],
  "vikavolt": [
    26
  ],
  "crabrawler": [
    52,
    89,
    83
  ],
  "crabominable": [
    52,
    89,
    83
  ],
  "oricorio": [
    216
  ],
  "cutiefly": [
    118,
    19,
    175
  ],
  "ribombee": [
    118,
    19,
    175
  ],
  "rockruff": [
    51,
    72,
    80
  ],
  "lycanroc": [
    51,
    146,
    80
  ],
  "wishiwashi": [
    208
  ],
  "mareanie": [
    196,
    7,
    144
  ],
  "toxapex": [
    196,
    7,
    144
  ],
  "mudbray": [
    20,
    192,
    39
  ],
  "mudsdale": [
    20,
    192,
    39
  ],
  "dewpider": [
    199,
    None,
    11
  ],
  "araquanid": [
    199,
    None,
    11
  ],
  "fomantis": [
    102,
    None,
    126
  ],
  "lurantis": [
    102,
    None,
    126
  ],
  "morelull": [
    35,
    27,
    44
  ],
  "shiinotic": [
    35,
    27,
    44
  ],
  "salandit": [
    212,
    None,
    12
  ],
  "salazzle": [
    212,
    None,
    12
  ],
  "stufful": [
    218,
    103,
    56
  ],
  "bewear": [
    218,
    103,
    127
  ],
  "bounsweet": [
    102,
    12,
    175
  ],
  "steenee": [
    102,
    12,
    175
  ],
  "tsareena": [
    102,
    214,
    175
  ],
  "comfey": [
    166,
    205,
    30
  ],
  "oranguru": [
    39,
    140,
    180
  ],
  "passimian": [
    222,
    None,
    128
  ],
  "wimpod": [
    193
  ],
  "golisopod": [
    194
  ],
  "sandygast": [
    195,
    None,
    8
  ],
  "palossand": [
    195,
    None,
    8
  ],
  "pyukumuku": [
    215,
    None,
    109
  ],
  "type-None": [
    4
  ],
  "silvally": [
    225
  ],
  "minior": [
    197
  ],
  "komala": [
    213
  ],
  "turtonator": [
    75
  ],
  "togedemaru": [
    160,
    31,
    5
  ],
  "mimikyu": [
    209
  ],
  "bruxish": [
    219,
    173,
    147
  ],
  "drampa": [
    201,
    157,
    13
  ],
  "dhelmise": [
    200
  ],
  "jangmo-o": [
    171,
    43,
    142
  ],
  "hakamo-o": [
    171,
    43,
    142
  ],
  "kommo-o": [
    171,
    43,
    142
  ],
  "tapu-koko": [
    226,
    None,
    140
  ],
  "tapu-lele": [
    227,
    None,
    140
  ],
  "tapu-bulu": [
    229,
    None,
    140
  ],
  "tapu-fini": [
    228,
    None,
    140
  ],
  "cosmog": [
    109
  ],
  "cosmoem": [
    5
  ],
  "solgaleo": [
    230
  ],
  "lunala": [
    231
  ],
  "nihilego": [
    224
  ],
  "buzzwole": [
    224
  ],
  "pheromosa": [
    224
  ],
  "xurkitree": [
    224
  ],
  "celesteela": [
    224
  ],
  "kartana": [
    224
  ],
  "guzzlord": [
    224
  ],
  "necrozma": [
    232
  ],
  "magearna": [
    220
  ],
  "marshadow": [
    101
  ],
  "poipole": [
    224
  ],
  "naganadel": [
    224
  ],
  "stakataka": [
    224
  ],
  "blacephalon": [
    224
  ],
  "zeraora": [
    10
  ],
  "meltan": [
    42
  ],
  "melmetal": [
    89
  ],
  "grookey": [
    65,
    None,
    229
  ],
  "thwackey": [
    65,
    None,
    229
  ],
  "rillaboom": [
    65,
    None,
    229
  ],
  "scorbunny": [
    66,
    None,
    236
  ],
  "raboot": [
    66,
    None,
    236
  ],
  "cinderace": [
    66,
    None,
    236
  ],
  "sobble": [
    67,
    None,
    97
  ],
  "drizzile": [
    67,
    None,
    97
  ],
  "inteleon": [
    67,
    None,
    97
  ],
  "skwovet": [
    167,
    None,
    82
  ],
  "greedent": [
    167,
    None,
    82
  ],
  "rookidee": [
    51,
    127,
    145
  ],
  "corvisquire": [
    51,
    127,
    145
  ],
  "corviknight": [
    46,
    127,
    240
  ],
  "blipbug": [
    68,
    14,
    140
  ],
  "dottler": [
    68,
    14,
    140
  ],
  "orbeetle": [
    68,
    119,
    140
  ],
  "nickit": [
    50,
    84,
    198
  ],
  "thievul": [
    50,
    84,
    198
  ],
  "gossifleur": [
    238,
    144,
    27
  ],
  "eldegoss": [
    238,
    144,
    27
  ],
  "wooloo": [
    218,
    50,
    171
  ],
  "dubwool": [
    218,
    80,
    171
  ],
  "chewtle": [
    173,
    75,
    33
  ],
  "drednaw": [
    173,
    75,
    33
  ],
  "yamper": [
    237,
    None,
    155
  ],
  "boltund": [
    173,
    None,
    172
  ],
  "rolycoly": [
    243,
    85,
    18
  ],
  "carkol": [
    243,
    49,
    18
  ],
  "coalossal": [
    243,
    49,
    18
  ],
  "applin": [
    247,
    82,
    171
  ],
  "flapple": [
    247,
    82,
    55
  ],
  "appletun": [
    247,
    82,
    47
  ],
  "silicobra": [
    245,
    61,
    8
  ],
  "sandaconda": [
    245,
    61,
    8
  ],
  "cramorant": [
    241
  ],
  "arrokuda": [
    33,
    None,
    239
  ],
  "barraskewda": [
    33,
    None,
    239
  ],
  "toxel": [
    155,
    9,
    103
  ],
  "toxtricity": [
    244,
    57,
    101
  ],
  "sizzlipede": [
    18,
    73,
    49
  ],
  "centiskorch": [
    18,
    73,
    49
  ],
  "clobbopus": [
    7,
    None,
    101
  ],
  "grapploct": [
    7,
    None,
    101
  ],
  "sinistea": [
    133,
    None,
    130
  ],
  "polteageist": [
    133,
    None,
    130
  ],
  "hatenna": [
    131,
    107,
    156
  ],
  "hattrem": [
    131,
    107,
    156
  ],
  "hatterene": [
    131,
    107,
    156
  ],
  "impidimp": [
    158,
    119,
    124
  ],
  "morgrem": [
    158,
    119,
    124
  ],
  "grimmsnarl": [
    158,
    119,
    124
  ],
  "obstagoon": [
    120,
    62,
    128
  ],
  "perrserker": [
    4,
    181,
    252
  ],
  "cursola": [
    133,
    None,
    253
  ],
  "sirfetchd": [
    80,
    None,
    113
  ],
  "mr-rime": [
    77,
    251,
    115
  ],
  "runerigus": [
    254
  ],
  "milcery": [
    175,
    None,
    165
  ],
  "alcremie": [
    175,
    None,
    165
  ],
  "falinks": [
    4,
    None,
    128
  ],
  "pincurchin": [
    31,
    None,
    226
  ],
  "snom": [
    19,
    None,
    246
  ],
  "frosmoth": [
    19,
    None,
    246
  ],
  "stonjourner": [
    249
  ],
  "eiscue": [
    248
  ],
  "indeedee": [
    39,
    28,
    227
  ],
  "morpeko": [
    258
  ],
  "cufant": [
    125,
    None,
    134
  ],
  "copperajah": [
    125,
    None,
    134
  ],
  "dracozolt": [
    10,
    55,
    146
  ],
  "arctozolt": [
    10,
    9,
    202
  ],
  "dracovish": [
    11,
    173,
    146
  ],
  "arctovish": [
    11,
    115,
    202
  ],
  "duraludon": [
    135,
    134,
    242
  ],
  "dreepy": [
    29,
    151,
    130
  ],
  "drakloak": [
    29,
    151,
    130
  ],
  "dragapult": [
    29,
    151,
    130
  ],
  "zacian": [
    234
  ],
  "zamazenta": [
    235
  ],
  "eternatus": [
    46
  ],
  "kubfu": [
    39
  ],
  "urshifu": [
    260
  ],
  "zarude": [
    102
  ],
  "regieleki": [
    262
  ],
  "regidrago": [
    263
  ],
  "glastrier": [
    264
  ],
  "spectrier": [
    265
  ],
  "calyrex": [
    127
  ],
  "wyrdeer": [
    22,
    119,
    157
  ],
  "kleavor": [
    68,
    125,
    292
  ],
  "ursaluna": [
    62,
    171,
    127
  ],
  "basculegion": [
    33,
    91,
    104
  ],
  "sneasler": [
    46,
    84,
    143
  ],
  "overqwil": [
    38,
    33,
    22
  ],
  "enamorus": [
    56,
    None,
    126
  ],
  "sprigatito": [
    65,
    None,
    168
  ],
  "floragato": [
    65,
    None,
    168
  ],
  "meowscarada": [
    65,
    None,
    168
  ],
  "fuecoco": [
    66,
    None,
    109
  ],
  "crocalor": [
    66,
    None,
    109
  ],
  "skeledirge": [
    66,
    None,
    109
  ],
  "quaxly": [
    67,
    None,
    153
  ],
  "quaxwell": [
    67,
    None,
    153
  ],
  "quaquaval": [
    67,
    None,
    153
  ],
  "lechonk": [
    165,
    82,
    47
  ],
  "oinkologne": [
    268,
    82,
    47
  ],
  "tarountula": [
    15,
    None,
    198
  ],
  "spidops": [
    15,
    None,
    198
  ],
  "nymble": [
    68,
    None,
    110
  ],
  "lokix": [
    68,
    None,
    110
  ],
  "pawmi": [
    9,
    30,
    89
  ],
  "pawmo": [
    10,
    30,
    89
  ],
  "pawmot": [
    10,
    30,
    89
  ],
  "tandemaus": [
    50,
    53,
    20
  ],
  "maushold": [
    132,
    167,
    101
  ],
  "fidough": [
    20,
    None,
    103
  ],
  "dachsbun": [
    273,
    None,
    165
  ],
  "smoliv": [
    48,
    None,
    139
  ],
  "dolliv": [
    48,
    None,
    139
  ],
  "arboliva": [
    269,
    None,
    139
  ],
  "squawkabilly": [
    22,
    55,
    62
  ],
  "nacli": [
    272,
    5,
    29
  ],
  "naclstack": [
    272,
    5,
    29
  ],
  "garganacl": [
    272,
    5,
    29
  ],
  "charcadet": [
    18,
    None,
    49
  ],
  "armarouge": [
    18,
    None,
    133
  ],
  "ceruledge": [
    18,
    None,
    133
  ],
  "tadbulb": [
    20,
    9,
    6
  ],
  "bellibolt": [
    280,
    9,
    6
  ],
  "wattrel": [
    277,
    10,
    172
  ],
  "kilowattrel": [
    277,
    10,
    172
  ],
  "maschiff": [
    22,
    50,
    198
  ],
  "mabosstiff": [
    22,
    275,
    198
  ],
  "shroodle": [
    84,
    124,
    158
  ],
  "grafaiai": [
    84,
    143,
    158
  ],
  "bramblin": [
    274,
    None,
    151
  ],
  "brambleghast": [
    274,
    None,
    151
  ],
  "toedscool": [
    298,
    None,
    298
  ],
  "toedscruel": [
    298,
    None,
    298
  ],
  "klawf": [
    271,
    75,
    144
  ],
  "capsakid": [
    34,
    15,
    103
  ],
  "scovillain": [
    34,
    15,
    141
  ],
  "rellor": [
    14,
    None,
    61
  ],
  "rabsca": [
    28,
    None,
    140
  ],
  "flittle": [
    107,
    119,
    3
  ],
  "espathra": [
    290,
    119,
    3
  ],
  "tinkatink": [
    104,
    20,
    124
  ],
  "tinkatuff": [
    104,
    20,
    124
  ],
  "tinkaton": [
    104,
    20,
    124
  ],
  "wiglett": [
    183,
    155,
    8
  ],
  "wugtrio": [
    183,
    155,
    8
  ],
  "bombirdier": [
    145,
    51,
    276
  ],
  "finizen": [
    41,
    None,
    41
  ],
  "palafin": [
    278,
    None,
    278
  ],
  "varoom": [
    142,
    None,
    112
  ],
  "revavroom": [
    142,
    None,
    111
  ],
  "cyclizar": [
    61,
    None,
    144
  ],
  "orthworm": [
    297,
    None,
    8
  ],
  "glimmet": [
    295,
    None,
    212
  ],
  "glimmora": [
    295,
    None,
    212
  ],
  "greavard": [
    53,
    None,
    218
  ],
  "houndstone": [
    146,
    None,
    218
  ],
  "flamigo": [
    113,
    77,
    294
  ],
  "cetoddle": [
    47,
    81,
    125
  ],
  "cetitan": [
    47,
    202,
    125
  ],
  "veluza": [
    104,
    None,
    292
  ],
  "dondozo": [
    109,
    12,
    41
  ],
  "tatsugiri": [
    279,
    None,
    114
  ],
  "annihilape": [
    72,
    39,
    128
  ],
  "clodsire": [
    38,
    11,
    109
  ],
  "farigiraf": [
    291,
    296,
    157
  ],
  "dudunsparce": [
    32,
    50,
    155
  ],
  "kingambit": [
    128,
    293,
    46
  ],
  "great-tusk": [
    281
  ],
  "scream-tail": [
    281
  ],
  "brute-bonnet": [
    281
  ],
  "flutter-mane": [
    281
  ],
  "slither-wing": [
    281
  ],
  "sandy-shocks": [
    281
  ],
  "iron-treads": [
    282
  ],
  "iron-bundle": [
    282
  ],
  "iron-hands": [
    282
  ],
  "iron-jugulis": [
    282
  ],
  "iron-moth": [
    282
  ],
  "iron-thorns": [
    282
  ],
  "frigibax": [
    270,
    None,
    115
  ],
  "arctibax": [
    270,
    None,
    115
  ],
  "baxcalibur": [
    270,
    None,
    115
  ],
  "gimmighoul": [
    155
  ],
  "gholdengo": [
    283
  ],
  "wo-chien": [
    286
  ],
  "chien-pao": [
    285
  ],
  "ting-lu": [
    284
  ],
  "chi-yu": [
    287
  ],
  "roaring-moon": [
    281
  ],
  "iron-valiant": [
    282
  ],
  "koraidon": [
    288
  ],
  "miraidon": [
    289
  ],
  "walking-wake": [
    281
  ],
  "iron-leaves": [
    282
  ],
  "dipplin": [
    300,
    82,
    60
  ],
  "poltchageist": [
    301,
    None,
    85
  ],
  "sinistcha": [
    301,
    None,
    85
  ],
  "okidogi": [
    302,
    None,
    275
  ],
  "munkidori": [
    302,
    None,
    119
  ],
  "fezandipiti": [
    302,
    None,
    101
  ],
  "ogerpon": [
    128
  ],
  "archaludon": [
    192,
    5,
    242
  ],
  "hydrapple": [
    300,
    144,
    60
  ],
  "gouging-fire": [
    281
  ],
  "raging-bolt": [
    281
  ],
  "iron-boulder": [
    282
  ],
  "iron-crown": [
    282
  ],
  "terapagos": [
    304
  ],
  "pecharunt": [
    307
  ]
}

natures = [
    "Hardy", "Lonely", "Brave", "Adamant", "Naughty",
    "Bold", "Docile", "Relaxed", "Impish", "Lax",
    "Timid", "Hasty", "Serious", "Jolly", "Naive",
    "Modest", "Mild", "Quiet", "Bashful", "Rash",
    "Calm", "Gentle", "Sassy", "Careful", "Quirky"
]

new_forms = {
    # the new forms have the same growth rate as their base species
    'deerling-autumn' : 'deerling',
    'deerling-summer' : 'deerling',
    'deerling-winter' : 'deerling',
    'petilil-fighting' : 'petilil',
    'eevee-fire' : 'eevee',
    'eevee-water' : 'eevee',
    'eevee-electric' : 'eevee',
    'eevee-dark' : 'eevee',
    'eevee-psychic' : 'eevee',
    'eevee-grass' : 'eevee',
    'eevee-ice' : 'eevee',
    'eevee-fairy' : 'eevee',
    'charcadet-psychic' : 'charcadet',
    'charcadet-ghost' : 'charcadet',
    'ralts-fighting' : 'ralts',
    'snorunt-ghost' : 'snorunt',
    'wurmple-poison' : 'wurmple',
    'nincada-ghost' : 'nincada',
    'exeggcute-dragon' : 'exeggcute',
    'koffing-fairy' : 'koffing',
    'rufflet-psychic' : 'rufflet',
    'goomy-steel' : 'goomy',
    'bergmite-rock' : 'bergmite',
    'froakie-special' : 'froakie',
    'rockruff-special' : 'rockruff',
    'feebas-fairy' : 'feebas',

    # regional forms (same growth rate as base species)
    'zigzagoon-galar': 'zigzagoon',
    'meowth-alola': 'meowth',
    'rattata-alola': 'rattata',
    'wooper-paldea': 'wooper',
    'ponyta-galar': 'ponyta',
    'growlithe-hisui': 'growlithe',
    'slowpoke-galar': 'slowpoke',
    'geodude-alola': 'geodude',
    'diglett-alola': 'diglett',
    'sandshrew-alola': 'sandshrew',
    'zorua-hisui': 'zorua',
    'darumaka-galar': 'darumaka',
    'vulpix-alola': 'vulpix',
    'grimer-alola': 'grimer',
    'yamask-galar': 'yamask',
    'gimmighoul-chest': 'gimmighoul',
    'gimmighoul-roaming': 'gimmighoul',
    'voltorb-hisui': 'voltorb',
    'meowth-galar': 'meowth',
    'basculin-white-striped': 'basculin',
    'qwilfish-hisui': 'qwilfish',
    'sneasel-hisui': 'sneasel',
    'farfetchd-galar': 'farfetchd',
    'corsola-galar': 'corsola',
}

def format_ability(name: Optional[str]) -> str:
    if name is None:
        return '0'
    # Replace dashes and underscores with spaces
    name = name.replace('-', ' ').replace('_', ' ')
    # Capitalize each word
    return ' '.join(word.capitalize() for word in name.split())

def get_level_from_exp(exp: int, growth_rate: Optional[str]) -> Optional[int]:
    if growth_rate is None:
        return

    table = exp_tables.get(growth_rate)
    if table is None:
        return

    exp = min(exp, 1000000)
    level = bisect_right(table, exp) - 1
    return max(1, min(level, 100))
    
def middle_bits_from_index(number, m, n):
    # Create a mask to extract 'n' bits
    mask = (1 << n) - 1
    # Shift the mask to align it with the desired starting bit and extract those bits
    return (number >> m) & mask

order_formats = [
    [1,2,3,4],            
    [1,2,4,3],            
    [1,3,2,4],            
    [1,3,4,2],            
    [1,4,2,3],            
    [1,4,3,2],            
    [2,1,3,4],
    [2,1,4,3],
    [2,3,1,4],
    [2,3,4,1],
    [2,4,1,3],
    [2,4,3,1],
    [3,1,2,4],
    [3,1,4,2],
    [3,2,1,4],
    [3,2,4,1],
    [3,4,1,2],
    [3,4,2,1],
    [4,1,2,3],
    [4,1,3,2],
    [4,2,1,3],
    [4,2,3,1],
    [4,3,1,2],
    [4,3,2,1],
]

def extract_hyper_trained_bits(data: bytes) -> dict:
    if len(data) != 12:
        raise ValueError("Expected exactly 12 bytes for PokemonSubstruct1")

    # Read 12 bytes as a little-endian 96-bit integer
    value = int.from_bytes(data, 'little')

    return {
        'HP'  : (value >> 62) & 1,
        'Atk' : (value >> 63) & 1,
        'Def' : (value >> 71) & 1,
        'Spe' : (value >> 79) & 1,
        'SpA' : (value >> 87) & 1,
        'SpD' : (value >> 95) & 1,
    }
    
async def get_import_data(mon_data: bytes, evs: bool, debug: bool) -> tuple[str, str]:
    if debug:
        print(f'EVs: {evs}')
        
    # Key Extraction
    try:
        pid, tid = struct.unpack('<II', mon_data[:8])
    except Exception as e:
        return print(f'Error: {e}'), None
    key = tid ^ pid

    # General Data
    iv_stats = ['HP', 'Atk', 'Def', 'Spe', 'SpA', 'SpD']
    sub_order = order_formats[pid % 24]
    showdown_data = mon_data[32:]
    decrypted = [
        struct.unpack('<I', showdown_data[i:i+4])[0] ^ key
        for i in range(0, 48, 4)
    ]                          
    growth_index = sub_order.index(1)
    moves_index = sub_order.index(2)
    evs_index = sub_order.index(3)
    misc_index = sub_order.index(4)
    
    # Species Name
    start = growth_index * 3
    block_bytes = b''.join(struct.pack('<I', decrypted[i]) for i in range(start, start + 3))
    species_id_bytes = block_bytes[0:2]  # or the correct offset if known
    species_id = struct.unpack('<H', species_id_bytes)[0] & 0x07FF
    try:
        species_name = all_mons[str(species_id)].strip()
    except KeyError:
        species_name = 'Unknown'
    base_name = species_name.lower()
    if debug:
        print(f'Species: {species_name}')

    # EXP and Level
    u32_0, u32_1, u32_2 = struct.unpack('<III', block_bytes)
    exp = u32_1 & 0x1FFFFF # mask lower 21 bits
    if debug:
        print(f'EXP: {exp}')
    if base_name in new_forms:
        base_name = new_forms[base_name]
    growth_rate = growth_rates.get(base_name, 'fast')
    if debug:
        print(f'Growth Rate: {growth_rate}')
    lvl = get_level_from_exp(exp, growth_rate)
    if lvl is None:
        lvl = 100

    # Nature
    personality = struct.unpack('<I', mon_data[:4])[0]
    # hiddenNatureModifier is stores in the upper 5 bits of the 18th byte
    hiddenNatureModifier = (mon_data[18] >> 3) & 0x1F
    # personality % 25 is the original nature
    nature = natures[(personality % 25) ^ hiddenNatureModifier]

    # EVs
    int1 = decrypted[evs_index * 3].to_bytes(4, 'little')
    int2 = decrypted[evs_index * 3 + 1].to_bytes(4, 'little') # Only first 2 bytes are used
    ev_bytes = int1 + int2[:2] # total 6 bytes
    ev_spread = {stat: ev_bytes[i] for i, stat in enumerate(iv_stats)}
    
    # IVs
    ivs = decrypted[misc_index * 3 + 1]
    start = moves_index * 3
    block_bytes = b''.join(struct.pack('<I', decrypted[i]) for i in range(start, start + 3))
    hyper_trained_stats = extract_hyper_trained_bits(block_bytes)
    spread = {}
    for i, stat in enumerate(iv_stats):
        spread[stat] = middle_bits_from_index(ivs, i * 5, 5)
        
    # Ability
    start = misc_index * 3
    substruct3_bytes = b''.join(struct.pack('<I', decrypted[i]) for i in range(start, start + 3))
    bitfield = struct.unpack_from("<I", substruct3_bytes, offset = 8)[0]
    ability_slot = (bitfield >> 30) & 0x3 # 2 bits
    if debug:
        print(f'Ability Slot: {ability_slot}')
    if ability_slot == 3:
        ability_id = (bitfield >> 21) & 0x1FF # 9 bits
    else:
        try:
            try:
                ability_id = pokemon_abilities[base_name][ability_slot]
                if ability_id is None:
                    ability_id = pokemon_abilities[base_name][0]
            except IndexError:
                ability_id = pokemon_abilities[base_name][0]
        except KeyError:
            ability_id = 0
            if debug:
                print('Error mapping ability ID, defaulting to 0')
    ability_name = format_ability(all_abilities[ability_id])
    if debug:
        print(f'Ability: {ability_name}')
    
    # Moves
    try:
        move1 = all_moves[decrypted[moves_index * 3] & 0x07FF]
    except IndexError:
        move1 = 'Unknown'
    try:
        move2 = all_moves[(decrypted[moves_index * 3] >> 16) & 0x07FF]
    except IndexError:
        move2 = 'Unknown'
    try:
        move3 = all_moves[decrypted[moves_index * 3 + 1] & 0x07FF]
    except IndexError:
        move3 = 'Unknown'
    try:
        move4 = all_moves[(decrypted[moves_index * 3 + 1] >> 16) & 0x07FF]
    except IndexError:
        move4 = 'Unknown'
    moves = [move1, move2, move3, move4]
    
    # Adding the data to the string
    import_data = f'{species_name}\n'
    import_data += f'Level: {lvl}\n'
    import_data += f'{nature} Nature\n'
    
    if evs:
        import_data += 'EVs: '
        for stat in iv_stats:
            import_data += f'{ev_spread[stat]} {stat} / '
        import_data = import_data[0:-4]
        import_data += '\n'

    import_data += 'IVs: '
    for stat in iv_stats:
        iv = 31 if hyper_trained_stats[stat] else spread[stat]
        import_data += f'{iv} {stat} / '
    import_data = f'{import_data[0:-4]}\n'
    
    import_data += f'Ability: {ability_name}\n'
    
    for move in moves:
        import_data += f'- {move}\n'
    import_data += '\n'
    
    return import_data, base_name.replace('_', '-')
    
async def read(save_data, evs: bool = False, debug: bool = False) -> tuple[str, list[str,]]:
    save = save_data
    
    save_index_a_offset = 0xffc
    save_block_b_offset = 0x00E000
    save_index_b_offset = save_block_b_offset + save_index_a_offset
    save_index_a = struct.unpack('<H', save[save_index_a_offset:save_index_a_offset + 2])[0]
    save_index_b = struct.unpack('<H', save[save_index_b_offset:save_index_b_offset + 2])[0]

    block_offset = 0
    if save_index_b > save_index_a or save_index_a == 65535:
        block_offset = save_block_b_offset
    save = save[block_offset:block_offset + 57344]

    if save_index_a == 65535:
        save_index = save_index_b
    elif save_index_b == 65535:
        save_index = save_index_a
    else:
        save_index = max(save_index_a, save_index_b)


    rotation = (save_index % 14) 
    total_offset = rotation * 4096

    box_offset = (20480 + 4 + total_offset) % 57344
    party_offset = (total_offset + 4096 + 0x238) % 57344

    import_data = ''
    species_names = []
    
    # read the party
    party_data = save[party_offset:party_offset + 600] # 600 bytes
    for n in range(6):
        # party pokemon are 100 bytes
        start = n * 100
        end = start + 100
        mon_data = party_data[start:end]
        if mon_data[0] != 0 or mon_data[1] != 0:
            if debug:
                print(f'Slot {n}: Non-zero personality, likely valid Pokémon')
            new_data, species_name = await get_import_data(mon_data, evs, debug)
            if new_data is not None:
                import_data += new_data
                species_names.append(species_name)

    for n in range(1):
        box_start = n * 2400 + box_offset
        pc_box = save[box_start:box_start + 4096]
        for m in range(30):
            # box pokemon are 80 bytes
            start = m * 80
            end = start + 80
            mon_data = pc_box[start:end]
            if mon_data[0] != 0 or mon_data[1] != 0:
                if debug:
                    print(f'Box {n}, Slot {m}: Non-zero personality, likely valid Pokémon')
                new_data, species_name = await get_import_data(mon_data, evs, debug)
                if new_data is not None:
                    import_data += new_data
                    species_names.append(species_name)

    return import_data, species_names
