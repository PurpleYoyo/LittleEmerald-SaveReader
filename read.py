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

all_mons = [
    '-----',
    'Bulbasaur',
    'Ivysaur',
    'Venusaur',
    'Charmander',
    'Charmeleon',
    'Charizard',
    'Squirtle',
    'Wartortle',
    'Blastoise',
    'Caterpie',
    'Metapod',
    'Butterfree',
    'Weedle',
    'Kakuna',
    'Beedrill',
    'Pidgey',
    'Pidgeotto',
    'Pidgeot',
    'Rattata',
    'Raticate',
    'Spearow',
    'Fearow',
    'Ekans',
    'Arbok',
    'Pikachu',
    'Raichu',
    'Sandshrew',
    'Sandslash',
    'Nidoran-F',
    'Nidorina',
    'Nidoqueen',
    'Nidoran-M',
    'Nidorino',
    'Nidoking',
    'Clefairy',
    'Clefable',
    'Vulpix',
    'Ninetales',
    'Jigglypuff',
    'Wigglytuff',
    'Zubat',
    'Golbat',
    'Oddish',
    'Gloom',
    'Vileplume',
    'Paras',
    'Parasect',
    'Venonat',
    'Venomoth',
    'Diglett',
    'Dugtrio',
    'Meowth',
    'Persian',
    'Psyduck',
    'Golduck',
    'Mankey',
    'Primeape',
    'Growlithe',
    'Arcanine',
    'Poliwag',
    'Poliwhirl',
    'Poliwrath',
    'Abra',
    'Kadabra',
    'Alakazam',
    'Machop',
    'Machoke',
    'Machamp',
    'Bellsprout',
    'Weepinbell',
    'Victreebel',
    'Tentacool',
    'Tentacruel',
    'Geodude',
    'Graveler',
    'Golem',
    'Ponyta',
    'Rapidash',
    'Slowpoke',
    'Slowbro',
    'Magnemite',
    'Magneton',
    'Farfetch’d',
    'Doduo',
    'Dodrio',
    'Seel',
    'Dewgong',
    'Grimer',
    'Muk',
    'Shellder',
    'Cloyster',
    'Gastly',
    'Haunter',
    'Gengar',
    'Onix',
    'Drowzee',
    'Hypno',
    'Krabby',
    'Kingler',
    'Voltorb',
    'Electrode',
    'Exeggcute',
    'Exeggutor',
    'Cubone',
    'Marowak',
    'Hitmonlee',
    'Hitmonchan',
    'Lickitung',
    'Koffing',
    'Weezing',
    'Rhyhorn',
    'Rhydon',
    'Chansey',
    'Tangela',
    'Kangaskhan',
    'Horsea',
    'Seadra',
    'Goldeen',
    'Seaking',
    'Staryu',
    'Starmie',
    'Mr-Mime',
    'Scyther',
    'Jynx',
    'Electabuzz',
    'Magmar',
    'Pinsir',
    'Tauros',
    'Magikarp',
    'Gyarados',
    'Lapras',
    'Ditto',
    'Eevee',
    'Vaporeon',
    'Jolteon',
    'Flareon',
    'Porygon',
    'Omanyte',
    'Omastar',
    'Kabuto',
    'Kabutops',
    'Aerodactyl',
    'Snorlax',
    'Articuno',
    'Zapdos',
    'Moltres',
    'Dratini',
    'Dragonair',
    'Dragonite',
    'Mewtwo',
    'Mew',
    'Chikorita',
    'Bayleef',
    'Meganium',
    'Cyndaquil',
    'Quilava',
    'Typhlosion',
    'Totodile',
    'Croconaw',
    'Feraligatr',
    'Sentret',
    'Furret',
    'Hoothoot',
    'Noctowl',
    'Ledyba',
    'Ledian',
    'Spinarak',
    'Ariados',
    'Crobat',
    'Chinchou',
    'Lanturn',
    'Pichu',
    'Cleffa',
    'Igglybuff',
    'Togepi',
    'Togetic',
    'Natu',
    'Xatu',
    'Mareep',
    'Flaaffy',
    'Ampharos',
    'Bellossom',
    'Marill',
    'Azumarill',
    'Sudowoodo',
    'Politoed',
    'Hoppip',
    'Skiploom',
    'Jumpluff',
    'Aipom',
    'Sunkern',
    'Sunflora',
    'Yanma',
    'Wooper',
    'Quagsire',
    'Espeon',
    'Umbreon',
    'Murkrow',
    'Slowking',
    'Misdreavus',
    'Unown',
    'Wobbuffet',
    'Girafarig',
    'Pineco',
    'Forretress',
    'Dunsparce',
    'Gligar',
    'Steelix',
    'Snubbull',
    'Granbull',
    'Qwilfish',
    'Scizor',
    'Shuckle',
    'Heracross',
    'Sneasel',
    'Teddiursa',
    'Ursaring',
    'Slugma',
    'Magcargo',
    'Swinub',
    'Piloswine',
    'Corsola',
    'Remoraid',
    'Octillery',
    'Delibird',
    'Mantine',
    'Skarmory',
    'Houndour',
    'Houndoom',
    'Kingdra',
    'Phanpy',
    'Donphan',
    'Porygon2',
    'Stantler',
    'Smeargle',
    'Tyrogue',
    'Hitmontop',
    'Smoochum',
    'Elekid',
    'Magby',
    'Miltank',
    'Blissey',
    'Raikou',
    'Entei',
    'Suicune',
    'Larvitar',
    'Pupitar',
    'Tyranitar',
    'Lugia',
    'Ho-Oh',
    'Celebi',
    'Treecko',
    'Grovyle',
    'Sceptile',
    'Torchic',
    'Combusken',
    'Blaziken',
    'Mudkip',
    'Marshtomp',
    'Swampert',
    'Poochyena',
    'Mightyena',
    'Zigzagoon',
    'Linoone',
    'Wurmple',
    'Silcoon',
    'Beautifly',
    'Cascoon',
    'Dustox',
    'Lotad',
    'Lombre',
    'Ludicolo',
    'Seedot',
    'Nuzleaf',
    'Shiftry',
    'Taillow',
    'Swellow',
    'Wingull',
    'Pelipper',
    'Ralts',
    'Kirlia',
    'Gardevoir',
    'Surskit',
    'Masquerain',
    'Shroomish',
    'Breloom',
    'Slakoth',
    'Vigoroth',
    'Slaking',
    'Nincada',
    'Ninjask',
    'Shedinja',
    'Whismur',
    'Loudred',
    'Exploud',
    'Makuhita',
    'Hariyama',
    'Azurill',
    'Nosepass',
    'Skitty',
    'Delcatty',
    'Sableye',
    'Mawile',
    'Aron',
    'Lairon',
    'Aggron',
    'Meditite',
    'Medicham',
    'Electrike',
    'Manectric',
    'Plusle',
    'Minun',
    'Volbeat',
    'Illumise',
    'Roselia',
    'Gulpin',
    'Swalot',
    'Carvanha',
    'Sharpedo',
    'Wailmer',
    'Wailord',
    'Numel',
    'Camerupt',
    'Torkoal',
    'Spoink',
    'Grumpig',
    'Spinda',
    'Trapinch',
    'Vibrava',
    'Flygon',
    'Cacnea',
    'Cacturne',
    'Swablu',
    'Altaria',
    'Zangoose',
    'Seviper',
    'Lunatone',
    'Solrock',
    'Barboach',
    'Whiscash',
    'Corphish',
    'Crawdaunt',
    'Baltoy',
    'Claydol',
    'Lileep',
    'Cradily',
    'Anorith',
    'Armaldo',
    'Feebas',
    'Milotic',
    'Castform',
    'Kecleon',
    'Shuppet',
    'Banette',
    'Duskull',
    'Dusclops',
    'Tropius',
    'Chimecho',
    'Absol',
    'Wynaut',
    'Snorunt',
    'Glalie',
    'Spheal',
    'Sealeo',
    'Walrein',
    'Clamperl',
    'Huntail',
    'Gorebyss',
    'Relicanth',
    'Luvdisc',
    'Bagon',
    'Shelgon',
    'Salamence',
    'Beldum',
    'Metang',
    'Metagross',
    'Regirock',
    'Regice',
    'Registeel',
    'Latias',
    'Latios',
    'Kyogre',
    'Groudon',
    'Rayquaza',
    'Jirachi',
    'Deoxys',
    'Turtwig',
    'Grotle',
    'Torterra',
    'Chimchar',
    'Monferno',
    'Infernape',
    'Piplup',
    'Prinplup',
    'Empoleon',
    'Starly',
    'Staravia',
    'Staraptor',
    'Bidoof',
    'Bibarel',
    'Kricketot',
    'Kricketune',
    'Shinx',
    'Luxio',
    'Luxray',
    'Budew',
    'Roserade',
    'Cranidos',
    'Rampardos',
    'Shieldon',
    'Bastiodon',
    'Burmy',
    'Wormadam',
    'Mothim',
    'Combee',
    'Vespiquen',
    'Pachirisu',
    'Buizel',
    'Floatzel',
    'Cherubi',
    'Cherrim',
    'Shellos',
    'Gastrodon',
    'Ambipom',
    'Drifloon',
    'Drifblim',
    'Buneary',
    'Lopunny',
    'Mismagius',
    'Honchkrow',
    'Glameow',
    'Purugly',
    'Chingling',
    'Stunky',
    'Skuntank',
    'Bronzor',
    'Bronzong',
    'Bonsly',
    'Mime-Jr',
    'Happiny',
    'Chatot',
    'Spiritomb',
    'Gible',
    'Gabite',
    'Garchomp',
    'Munchlax',
    'Riolu',
    'Lucario',
    'Hippopotas',
    'Hippowdon',
    'Skorupi',
    'Drapion',
    'Croagunk',
    'Toxicroak',
    'Carnivine',
    'Finneon',
    'Lumineon',
    'Mantyke',
    'Snover',
    'Abomasnow',
    'Weavile',
    'Magnezone',
    'Lickilicky',
    'Rhyperior',
    'Tangrowth',
    'Electivire',
    'Magmortar',
    'Togekiss',
    'Yanmega',
    'Leafeon',
    'Glaceon',
    'Gliscor',
    'Mamoswine',
    'Porygon-Z',
    'Gallade',
    'Probopass',
    'Dusknoir',
    'Froslass',
    'Rotom',
    'Uxie',
    'Mesprit',
    'Azelf',
    'Dialga',
    'Palkia',
    'Heatran',
    'Regigigas',
    'Giratina',
    'Cresselia',
    'Phione',
    'Manaphy',
    'Darkrai',
    'Shaymin',
    'Arceus',
    'Victini',
    'Snivy',
    'Servine',
    'Serperior',
    'Tepig',
    'Pignite',
    'Emboar',
    'Oshawott',
    'Dewott',
    'Samurott',
    'Patrat',
    'Watchog',
    'Lillipup',
    'Herdier',
    'Stoutland',
    'Purrloin',
    'Liepard',
    'Pansage',
    'Simisage',
    'Pansear',
    'Simisear',
    'Panpour',
    'Simipour',
    'Munna',
    'Musharna',
    'Pidove',
    'Tranquill',
    'Unfezant',
    'Blitzle',
    'Zebstrika',
    'Roggenrola',
    'Boldore',
    'Gigalith',
    'Woobat',
    'Swoobat',
    'Drilbur',
    'Excadrill',
    'Audino',
    'Timburr',
    'Gurdurr',
    'Conkeldurr',
    'Tympole',
    'Palpitoad',
    'Seismitoad',
    'Throh',
    'Sawk',
    'Sewaddle',
    'Swadloon',
    'Leavanny',
    'Venipede',
    'Whirlipede',
    'Scolipede',
    'Cottonee',
    'Whimsicott',
    'Petilil',
    'Lilligant',
    'Basculin',
    'Sandile',
    'Krokorok',
    'Krookodile',
    'Darumaka',
    'Darmanitan',
    'Maractus',
    'Dwebble',
    'Crustle',
    'Scraggy',
    'Scrafty',
    'Sigilyph',
    'Yamask',
    'Cofagrigus',
    'Tirtouga',
    'Carracosta',
    'Archen',
    'Archeops',
    'Trubbish',
    'Garbodor',
    'Zorua',
    'Zoroark',
    'Minccino',
    'Cinccino',
    'Gothita',
    'Gothorita',
    'Gothitelle',
    'Solosis',
    'Duosion',
    'Reuniclus',
    'Ducklett',
    'Swanna',
    'Vanillite',
    'Vanillish',
    'Vanilluxe',
    'Deerling',
    'Sawsbuck',
    'Emolga',
    'Karrablast',
    'Escavalier',
    'Foongus',
    'Amoonguss',
    'Frillish',
    'Jellicent',
    'Alomomola',
    'Joltik',
    'Galvantula',
    'Ferroseed',
    'Ferrothorn',
    'Klink',
    'Klang',
    'Klinklang',
    'Tynamo',
    'Eelektrik',
    'Eelektross',
    'Elgyem',
    'Beheeyem',
    'Litwick',
    'Lampent',
    'Chandelure',
    'Axew',
    'Fraxure',
    'Haxorus',
    'Cubchoo',
    'Beartic',
    'Cryogonal',
    'Shelmet',
    'Accelgor',
    'Stunfisk',
    'Mienfoo',
    'Mienshao',
    'Druddigon',
    'Golett',
    'Golurk',
    'Pawniard',
    'Bisharp',
    'Bouffalant',
    'Rufflet',
    'Braviary',
    'Vullaby',
    'Mandibuzz',
    'Heatmor',
    'Durant',
    'Deino',
    'Zweilous',
    'Hydreigon',
    'Larvesta',
    'Volcarona',
    'Cobalion',
    'Terrakion',
    'Virizion',
    'Tornadus',
    'Thundurus',
    'Reshiram',
    'Zekrom',
    'Landorus',
    'Kyurem',
    'Keldeo',
    'Meloetta',
    'Genesect',
    'Chespin',
    'Quilladin',
    'Chesnaught',
    'Fennekin',
    'Braixen',
    'Delphox',
    'Froakie',
    'Frogadier',
    'Greninja',
    'Bunnelby',
    'Diggersby',
    'Fletchling',
    'Fletchinder',
    'Talonflame',
    'Scatterbug',
    'Spewpa',
    'Vivillon',
    'Litleo',
    'Pyroar',
    'Flabebe',
    'Floette',
    'Florges',
    'Skiddo',
    'Gogoat',
    'Pancham',
    'Pangoro',
    'Furfrou',
    'Espurr',
    'Meowstic',
    'Honedge',
    'Doublade',
    'Aegislash',
    'Spritzee',
    'Aromatisse',
    'Swirlix',
    'Slurpuff',
    'Inkay',
    'Malamar',
    'Binacle',
    'Barbaracle',
    'Skrelp',
    'Dragalge',
    'Clauncher',
    'Clawitzer',
    'Helioptile',
    'Heliolisk',
    'Tyrunt',
    'Tyrantrum',
    'Amaura',
    'Aurorus',
    'Sylveon',
    'Hawlucha',
    'Dedenne',
    'Carbink',
    'Goomy',
    'Sliggoo',
    'Goodra',
    'Klefki',
    'Phantump',
    'Trevenant',
    'Pumpkaboo',
    'Gourgeist',
    'Bergmite',
    'Avalugg',
    'Noibat',
    'Noivern',
    'Xerneas',
    'Yveltal',
    'Zygarde',
    'Diancie',
    'Hoopa',
    'Volcanion',
    'Rowlet',
    'Dartrix',
    'Decidueye',
    'Litten',
    'Torracat',
    'Incineroar',
    'Popplio',
    'Brionne',
    'Primarina',
    'Pikipek',
    'Trumbeak',
    'Toucannon',
    'Yungoos',
    'Gumshoos',
    'Grubbin',
    'Charjabug',
    'Vikavolt',
    'Crabrawler',
    'Crabominable',
    'Oricorio',
    'Cutiefly',
    'Ribombee',
    'Rockruff',
    'Lycanroc',
    'Wishiwashi',
    'Mareanie',
    'Toxapex',
    'Mudbray',
    'Mudsdale',
    'Dewpider',
    'Araquanid',
    'Fomantis',
    'Lurantis',
    'Morelull',
    'Shiinotic',
    'Salandit',
    'Salazzle',
    'Stufful',
    'Bewear',
    'Bounsweet',
    'Steenee',
    'Tsareena',
    'Comfey',
    'Oranguru',
    'Passimian',
    'Wimpod',
    'Golisopod',
    'Sandygast',
    'Palossand',
    'Pyukumuku',
    'Type-Null',
    'Silvally',
    'Minior',
    'Komala',
    'Turtonator',
    'Togedemaru',
    'Mimikyu',
    'Bruxish',
    'Drampa',
    'Dhelmise',
    'Jangmo-o',
    'Hakamo-o',
    'Kommo-o',
    'Tapu Koko',
    'Tapu Lele',
    'Tapu-Bulu',
    'Tapu-Fini',
    'Cosmog',
    'Cosmoem',
    'Solgaleo',
    'Lunala',
    'Nihilego',
    'Buzzwole',
    'Pheromosa',
    'Xurkitree',
    'Celesteela',
    'Kartana',
    'Guzzlord',
    'Necrozma',
    'Magearna',
    'Marshadow',
    'Poipole',
    'Naganadel',
    'Stakataka',
    'Blacephalon',
    'Zeraora',
    'Meltan',
    'Melmetal',
    'Grookey',
    'Thwackey',
    'Rillaboom',
    'Scorbunny',
    'Raboot',
    'Cinderace',
    'Sobble',
    'Drizzile',
    'Inteleon',
    'Skwovet',
    'Greedent',
    'Rookidee',
    'Corvisquire',
    'Corviknight',
    'Blipbug',
    'Dottler',
    'Orbeetle',
    'Nickit',
    'Thievul',
    'Gossifleur',
    'Eldegoss',
    'Wooloo',
    'Dubwool',
    'Chewtle',
    'Drednaw',
    'Yamper',
    'Boltund',
    'Rolycoly',
    'Carkol',
    'Coalossal',
    'Applin',
    'Flapple',
    'Appletun',
    'Silicobra',
    'Sandaconda',
    'Cramorant',
    'Arrokuda',
    'Barraskewda',
    'Toxel',
    'Toxtricity',
    'Sizzlipede',
    'Centiskorch',
    'Clobbopus',
    'Grapploct',
    'Sinistea',
    'Polteageist',
    'Hatenna',
    'Hattrem',
    'Hatterene',
    'Impidimp',
    'Morgrem',
    'Grimmsnarl',
    'Obstagoon',
    'Perrserker',
    'Cursola',
    'Sirfetch’d',
    'Mr-Rime',
    'Runerigus',
    'Milcery',
    'Alcremie',
    'Falinks',
    'Pincurchin',
    'Snom',
    'Frosmoth',
    'Stonjourner',
    'Eiscue',
    'Indeedee',
    'Morpeko',
    'Cufant',
    'Copperajah',
    'Dracozolt',
    'Arctozolt',
    'Dracovish',
    'Arctovish',
    'Duraludon',
    'Dreepy',
    'Drakloak',
    'Dragapult',
    'Zacian',
    'Zamazenta',
    'Eternatus',
    'Kubfu',
    'Urshifu',
    'Zarude',
    'Regieleki',
    'Regidrago',
    'Glastrier',
    'Spectrier',
    'Calyrex',
    'Venusaur-Mega',
    'Charizard-Mega-X',
    'Charizard-Mega-Y',
    'Blastoise-Mega',
    'Beedrill-Mega',
    'Pidgeot-Mega',
    'Alakazam-Mega',
    'Slowbro-Mega',
    'Gengar-Mega',
    'Kangaskhan-Mega',
    'Pinsir-Mega',
    'Gyarados-Mega',
    'Aerodactyl-Mega',
    'Mewtwo-Mega-X',
    'Mewtwo-Mega-Y',
    'Ampharos-Mega',
    'Steelix-Mega',
    'Scizor-Mega',
    'Heracross-Mega',
    'Houndoom-Mega',
    'Tyranitar-Mega',
    'Sceptile-Mega',
    'Blaziken-Mega',
    'Swampert-Mega',
    'Gardevoir-Mega',
    'Sableye-Mega',
    'Mawile-Mega',
    'Aggron-Mega',
    'Medicham-Mega',
    'Manectric-Mega',
    'Sharpedo-Mega',
    'Camerupt-Mega',
    'Altaria-Mega',
    'Banette-Mega',
    'Absol-Mega',
    'Glalie-Mega',
    'Salamence-Mega',
    'Metagross-Mega',
    'Latias-Mega',
    'Latios-Mega',
    'Lopunny-Mega',
    'Garchomp-Mega',
    'Lucario-Mega',
    'Abomasnow-Mega',
    'Gallade-Mega',
    'Audino-Mega',
    'Diancie-Mega',
    'Milotic-Mega',
    'Butterfree-Mega',
    'Machamp-Mega',
    'Kingler-Mega',
    'Lapras-Mega',
    'Flygon-Mega',
    'Kingdra-Mega',
    'Rayquaza-Mega',
    'Kyogre-Primal',
    'Groudon-Primal',
    'Rattata-Alola',
    'Raticate-Alola',
    'Raichu-Alola',
    'Sandshrew-Alola',
    'Sandslash-Alola',
    'Vulpix-Alola',
    'Ninetales-Alola',
    'Diglett-Alola',
    'Dugtrio-Alola',
    'Meowth-Alola',
    'Persian-Alola',
    'Geodude-Alola',
    'Graveler-Alola',
    'Golem-Alola',
    'Grimer-Alola',
    'Muk-Alola',
    'Exeggutor-Alola',
    'Marowak-Alola',
    'Meowth-Galarian',
    'Ponyta-Galarian',
    'Rapidash-Galarian',
    'Slowpoke-Galarian',
    'Slowbro-Galarian',
    'Farfetch’d-Galarian',
    'Weezing-Galarian',
    'Mr-Mime-Galarian',
    'Articuno-Galarian',
    'Zapdos-Galarian',
    'Moltres-Galarian',
    'Slowking-Galarian',
    'Corsola-Galarian',
    'Zigzagoon-Galarian',
    'Linoone-Galarian',
    'Darumaka-Galarian',
    'Darmanitan-Galarian',
    'Yamask-Galarian',
    'Stunfisk-Galarian',
    'Pikachu-Cosplay',
    'Pikachu-Rock-Star',
    'Pikachu-Belle',
    'Pikachu-Pop-Star',
    'Pikachu-Ph-D',
    'Pikachu-Libre',
    'Pikachu-Original-Cap',
    'Pikachu-Hoenn-Cap',
    'Pikachu-Sinnoh-Cap',
    'Pikachu-Unova-Cap',
    'Pikachu-Kalos-Cap',
    'Pikachu-Alola-Cap',
    'Pikachu-Partner-Cap',
    'Pikachu-World-Cap',
    'Pichu-Spiky-Eared',
    'Unown-B',
    'Unown-C',
    'Unown-D',
    'Unown-E',
    'Unown-F',
    'Unown-G',
    'Unown-H',
    'Unown-I',
    'Unown-J',
    'Unown-K',
    'Unown-L',
    'Unown-M',
    'Unown-N',
    'Unown-O',
    'Unown-P',
    'Unown-Q',
    'Unown-R',
    'Unown-S',
    'Unown-T',
    'Unown-U',
    'Unown-V',
    'Unown-W',
    'Unown-X',
    'Unown-Y',
    'Unown-Z',
    'Unown-Emark',
    'Unown-Qmark',
    'Castform-Sunny',
    'Castform-Rainy',
    'Castform-Snowy',
    'Deoxys-Attack',
    'Deoxys-Defense',
    'Deoxys-Speed',
    'Burmy-Sandy-Cloak',
    'Burmy-Trash-Cloak',
    'Wormadam-Sandy',
    'Wormadam-Trash',
    'Cherrim-Sunshine',
    'Shellos-East-Sea',
    'Gastrodon',
    'Rotom-Heat',
    'Rotom-Wash',
    'Rotom-Frost',
    'Rotom-Fan',
    'Rotom-Mow',
    'Giratina-Origin',
    'Shaymin-Sky',
    'Arceus-Fighting',
    'Arceus-Flying',
    'Arceus-Poison',
    'Arceus-Ground',
    'Arceus-Rock',
    'Arceus-Bug',
    'Arceus-Ghost',
    'Arceus-Steel',
    'Arceus-Fire',
    'Arceus-Water',
    'Arceus-Grass',
    'Arceus-Electric',
    'Arceus-Psychic',
    'Arceus-Ice',
    'Arceus-Dragon',
    'Arceus-Dark',
    'Arceus-Fairy',
    'Basculin-Blue-Striped',
    'Darmanitan-Zen-Mode',
    'Darmanitan-Zen-Mode-Galarian',
    'Deerling-Summer',
    'Deerling-Autumn',
    'Deerling-Winter',
    'Sawsbuck-Summer',
    'Sawsbuck-Autumn',
    'Sawsbuck-Winter',
    'Tornadus-Therian',
    'Thundurus-Therian',
    'Landorus-Therian',
    'Kyurem-White',
    'Kyurem-Black',
    'Keldeo-Resolute',
    'Meloetta-Pirouette',
    'Genesect-Douse-Drive',
    'Genesect-Shock-Drive',
    'Genesect-Burn-Drive',
    'Genesect-Chill-Drive',
    'Greninja-Battle-Bond',
    'Greninja-Ash',
    'Deerling-Summer',
    'Deerling-Autumn',
    'Deerling-Winter',
    'Vivillon-Garden',
    'Vivillon-Elegant',
    'Vivillon-Meadow',
    'Vivillon-Modern',
    'Vivillon-Marine',
    'Vivillon-Archipelago',
    'Vivillon-High-Plains',
    'Vivillon-Sandstorm',
    'Vivillon-River',
    'Vivillon-Monsoon',
    'Vivillon-Savanna',
    'Vivillon-Sun',
    'Vivillon-Ocean',
    'Vivillon-Jungle',
    'Vivillon-Fancy',
    'Vivillon-Poke-Ball',
    'Flabebe-Yellow-Flower',
    'Flabebe-Orange-Flower',
    'Flabebe-Blue-Flower',
    'Flabebe-White-Flower',
    'Floette-Yellow-Flower',
    'Floette-Orange-Flower',
    'Floette-Blue-Flower',
    'Floette-White-Flower',
    'Floette-Eternal-Flower',
    'Florges-Yellow-Flower',
    'Florges-Orange-Flower',
    'Florges-Blue-Flower',
    'Florges-White-Flower',
    'Furfrou-Heart-Trim',
    'Furfrou-Star-Trim',
    'Furfrou-Diamond-Trim',
    'Furfrou-Debutante-Trim',
    'Furfrou-Matron-Trim',
    'Furfrou-Dandy-Trim',
    'Furfrou-La-Reine-Trim',
    'Furfrou-Kabuki-Trim',
    'Furfrou-Pharaoh-Trim',
    'Meowstic-F',
    'Aegislash-Blade',
    'Pumpkaboo-Small',
    'Pumpkaboo-Large',
    'Pumpkaboo-Super',
    'Gourgeist-Small',
    'Gourgeist-Large',
    'Gourgeist-Super',
    'Xerneas-Active',
    'Zygarde-10',
    'Zygarde-10-Power-Construct',
    'Zygarde-50-Power-Construct',
    'Zygarde-Complete',
    'Hoopa-Unbound',
    'Oricorio-Pom-Pom',
    'Oricorio-Pau',
    'Oricorio-Sensu',
    'Rockruff-Own-Tempo',
    'Lycanroc-Midnight',
    'Lycanroc-Dusk',
    'Wishiwashi-School',
    'Silvally-Fighting',
    'Silvally-Flying',
    'Silvally-Poison',
    'Silvally-Ground',
    'Silvally-Rock',
    'Silvally-Bug',
    'Silvally-Ghost',
    'Silvally-Steel',
    'Silvally-Fire',
    'Silvally-Water',
    'Silvally-Grass',
    'Silvally-Electric',
    'Silvally-Psychic',
    'Silvally-Ice',
    'Silvally-Dragon',
    'Silvally-Dark',
    'Silvally-Fairy',
    'Minior-Meteor-Orange',
    'Minior-Meteor-Yellow',
    'Minior-Meteor-Green',
    'Minior-Meteor-Blue',
    'Minior-Meteor-Indigo',
    'Minior-Meteor-Violet',
    'Minior-Core-Red',
    'Minior-Core-Orange',
    'Minior-Core-Yellow',
    'Minior-Core-Green',
    'Minior-Core-Blue',
    'Minior-Core-Indigo',
    'Minior-Core-Violet',
    'Mimikyu-Busted',
    'Necrozma-Dusk-Mane',
    'Necrozma-Dawn-Wings',
    'Necrozma-Ultra',
    'Magearna-Original-Color',
    'Cramorant-Gulping',
    'Cramorant-Gorging',
    'Toxtricity-Low-Key',
    'Sinistea-Antique',
    'Polteageist-Antique',
    'Alcremie-Ruby-Cream',
    'Alcremie-Matcha-Cream',
    'Alcremie-Mint-Cream',
    'Alcremie-Lemon-Cream',
    'Alcremie-Salted-Cream',
    'Alcremie-Ruby-Swirl',
    'Alcremie-Caramel-Swirl',
    'Alcremie-Rainbow-Swirl',
    'Eiscue-Noice-Face',
    'Indeedee-Female',
    'Morpeko-Hangry',
    'Zacian-Crowned-Sword',
    'Zamazenta-Crowned-Shield',
    'Eternatus-Eternamax',
    'Urshifu-Rapid-Strike-Style',
    'Zarude-Dada',
    'Calyrex-Ice',
    'Calyrex-Shadow',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    'Sprigatito',
    '',
    '',
    'Fuecoco',
    '',
    '',
    'Quaxly                  ',
    '',
    '',
    'Lechonk',
    '',
    '',
    'Tarountula',
    '',
    'Nymble               ',
    '',
    'Pawmi                   ',
    '',
    '',
    'Tandemaus',
    '',
    '',
    'Fidough                ',
    '',
    'Smoliv                 ',
    '',
    '',
    '',
    '',
    '',
    '',
    'Nacli',
    '',
    '',
    'Charcadet',
    '',
    '',
    'Tadbulb',
    '',
    'Wattrel',
    '',
    'Maschiff',
    '',
    'Shroodle',
    '',
    'Bramblin',
    '',
    'Toedscool',
    '',
    '',
    'Capsakid',
    '',
    'Rellor',
    '',
    'Flittle',
    '',
    'Tinkatink',
    '',
    '',
    'Wiglett',
    '',
    '',
    'Finizen',
    '',
    '',
    'Varoom',
    '',
    '',
    '',
    'Glimmet',
    '',
    'Greavard',
    '',
    '',
    'Cetoddle',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    'Frigibax',
    '',
    '',
    'Gimmighoul-Chest',
    'Gimmighoul-Roaming',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    'Wooper-Paldea',
    '',
    '',
    '',
    'Poltchageist',
    'Poltchageist',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    'Scatterbug',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    'Pichu-Mega',
    'Cleffa-Mega',
    'Igglybuff-Mega',
    'Togepi-Mega',
    'Tyrogue-Mega-L',
    'Tyrogue-Mega-C',
    'Tyrogue-Mega-T',
    'Smoochum-Mega',
    'Elekid-Mega',
    'Magby-Mega',
    'Azurill-Mega',
    'Wynaut-Mega',
    'Budew-Mega',
    'Chingling-Mega',
    'Bonsly-Mega',
    'Mime Jr.-Mega-K',
    'Happiny-Mega',
    'Munchlax-Mega',
    'Riolu-Mega',
    'Mantyke-Mega',
    'Toxel-Mega-A',
    'Toxel-Mega-L',
    'Eevee-Fire',
    'Eevee-Water',
    'Eevee-Electric',
    'Eevee-Dark',
    'Eevee-Psychic',
    'Eevee-Grass',
    'Eevee-Ice',
    'Eevee-Fairy',
    'Charcadet-Psychic',
    'Charcadet-Ghost',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    'Ralts-Fighting',
    'Snorunt-Ghost',
    'Wurmple-Poison',
    'Nincada-Ghost',
    'Exeggcute-Dragon',
    'Koffing-Fairy',
    'Petilil-Fighting',
    'Rufflet-Psychic',
    'Goomy-Steel',
    'Bergmite-Rock',
    '',
    'Mime Jr.-Mega-G',
    '',
    'Froakie-Special',
    'Rockruff-Special',
    'Feebas-Fairy',
]

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
    None,
    34
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
    None,
    94
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
    None,
    44
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

def format_ability(name: str) -> str:
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
        species_name = all_mons[species_id].strip()
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
            ability_id = pokemon_abilities[base_name][ability_slot]
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
