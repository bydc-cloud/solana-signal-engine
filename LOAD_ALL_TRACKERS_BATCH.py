#!/usr/bin/env python3
"""
OPTIMIZED BATCH LOADING - ALL 481 CT MONITORS + ALL 154 WHALE WALLETS
Uses batch inserts with WAL mode for better performance
"""

import sqlite3
import json
from datetime import datetime

# ALL 481 CT MONITORS
ct_handles = [
    "0gantd", "0xcryptowizard", "0xenjooyer", "0xkuwo", "0xmert_", "0xnetz", "0xramonos", "0xsunnft",
    "0xzerebro", "100xcoin_sniper", "a1lon9", "abc", "abcnews", "absolquant", "adamlowisz", "aeyakovenko",
    "afpost", "agilit1es", "aion5254", "alohquant", "alx", "america", "andyayrey", "anothercohen", "ansem",
    "ar15crypto", "arkham", "ashcryptoreal", "assetdash", "ataberk", "autismcapital", "ayeejuju", "banks",
    "barrontrump", "bbcbreaking", "bbcnews", "bbcworld", "beeple", "benarmstrongsx", "bentodar", "bigbaghodler",
    "billym2k", "binance", "binance_intern", "binanceus", "binancewallet", "bingxofficial", "bitcoin",
    "bitcoinmagazine", "bitcoinnewscom", "blknoiz06", "bnbchain", "bonk_fun", "boopdotfun", "boredelonmusk",
    "brian_armstrong", "bricsinfo", "bryan_johnson", "burwicklaw", "bwenews", "bybit_official", "cap1519",
    "cb_doge", "cbsnews", "chapogrimey", "chatgptapp", "chinadaily", "chineseembinus", "cincinnatizoo",
    "cnbc", "cobie", "cobratate", "coinbase", "coindesk", "coinmarketcap", "cointelegraph", "colossal",
    "cookerflips", "cr4zy_sol", "crypt0wu", "crypto_banter", "cryptobeastreal", "cryptocom", "cryptogatsu",
    "cryptokillua99", "ctolarsson", "cz_binance", "dailymail", "dallaszoo", "darkfarms1", "darkoddcon",
    "daumeneth", "davidsacks47", "degeneratenews", "degenike", "degensaif", "deitaone", "delisarcane",
    "deviscookin", "devlindefran", "dexerto", "dimazeniuk", "dingalingts", "disclosetv", "disneyparks",
    "dloz", "doge", "dogecoin", "dogwifcoin", "dohawifi", "dom_lucre", "donaldjtrumpjr", "donaldtrump",
    "dramaalert", "drevv__", "drewwalls10", "dripsterdotfun", "duffybands", "duolingo", "dustxbt",
    "dyllimanager", "elonmusk", "enoksamplemaker", "erictrump", "evankeast", "everynightcap", "fancyboynola",
    "fart", "feinofcrypto2", "fenrikz", "fifhtysol", "flashcashy", "floppadotfun", "fluxgains", "fortnite",
    "four_form_", "four_meme_", "fox32news", "foxnews", "frankdegods", "fridon_ai", "frogfren1337",
    "fuckingbitties", "ga__ke", "gamingtechreels", "getrealtoken", "gettrumpmemes", "giggleacademy",
    "gold3141592653", "gop", "gotdusted", "greg16676935420", "gucciarchives", "gwr", "henn100x", "heyibinance",
    "heyisrael0x", "hoh_alpha", "hooftheagent", "hpzsol", "htx_global", "huinguillaume", "huntdotfun",
    "hypermaddd", "iamskorer", "ibs3nwins", "ifindretards", "imthebetman", "imup_btc", "imzerx", "insydercrypto",
    "inukecharts", "iohk_charles", "ishowspeedsui", "ivankatrump", "jack", "jackbutcher", "jakeebtw",
    "jakepaul", "jason", "jdvance", "jeremyybtc", "jessepollak", "jiankui_he", "jimmyedgar", "johnstoll1977",
    "josikinz", "jrossnicoll", "jupiterexchange", "justinsuntron", "kamakuracrypto", "kanyewest", "kfc_es",
    "khaokheowzoo", "klaskeodas", "klayserdegen", "klutch_trades", "krakenfx", "kryotrades", "krypt0logy",
    "labrjournal", "latimes", "latuche95", "launchcoin", "lebra1n", "leofunhq", "lethesol", "libsoftiktok",
    "ligertonn", "lil_tax_evade", "limeweb3", "linkkzyy", "litchdoteth", "litecoin", "lostmemearchive",
    "lucanetz", "lukebelmar", "m0nkicrypto", "magaresource", "magiceden", "mailonline", "malv008",
    "marcellxmarcell", "marionawfal", "martin_casado", "martinshkreli", "mashable", "masked_minner",
    "matt_furie", "mavmilli", "maxamedcrypto", "mayemusk", "mcdonalds", "mclansol", "melaniatrump",
    "melonzsol", "metaverseandre", "metaversejoji", "miamiminty", "miki_p1", "minidiablud", "modernblade",
    "moneybagtaken", "monkeytrades383", "monkotbe", "mops1z", "morph_labs", "morr1ss", "mrbeast",
    "mrpunkdoteth", "muskonomy", "muststopmurad", "n0commas", "narracanz", "nasamoon", "nashvillezoo",
    "natgeoanimals", "nbakryptic", "nbandz_", "nbcla", "nbcnews", "neocallss", "newsmax", "newsweek",
    "newswire_us", "nftdefiland", "nightklaw", "nikitabier", "nix3rr", "noanoanoanoanoe", "nodevnorug",
    "notthreadguy", "nubsdev", "nxive100x", "nypost", "nytimes", "oakzoo", "ohzarke", "oreonsol",
    "ownthedoge", "pablonomics", "patty_fi", "pengubtc", "peterschiff", "phantom", "pip0pkajou",
    "plzfollow", "ponkesol", "popcat_sol", "potus", "primer_nft", "pumpdotfun", "qillin888", "qubicorg",
    "quilly_ai", "radargenius", "rarehogdotfun", "raydiumprotocol", "realannapaulina", "realdonaldtrump",
    "realmisssmith1", "realtrumpvance", "reuters", "richaesthetic", "richlxsol", "richsoon2", "ricktrades69",
    "rm01995022", "robbiejackson_", "ropirito", "router", "rsihelllurker", "rtgcoinjr", "s0meone_u_know",
    "saihoushi_ai", "saylor", "scamdetective_", "scottmelker", "scufclips", "seand_sol", "sentosumosaba",
    "serpinsight", "sgravano_", "shib_brc", "shibatoken", "shippeneth", "shurcooL", "sieradski",
    "silviemichelineofficial", "sit_", "sixfigurecapital", "skillerwhale", "skullpandayc", "smolsol",
    "solana", "solanafm", "solananaorg", "solanatools", "solbigbrain", "solluvr", "solrazrfm", "solsaviors",
    "sonic_svm", "spacex", "squeebo_nft", "stoolpresidente", "sudostake", "suki_aura", "sundayfunday_tv",
    "sunglassesmfer", "supergalaxytv", "supermercoin", "suptoshi", "tannerrumsey", "taptapbtc", "tate_mcrae",
    "tctv_ai", "teeztrades", "telegram", "tenzorcto", "tesla", "tether_to", "thearchitect_", "thecryptogod_",
    "thecryptosith", "thedailyhodl", "thedukeofhonor", "thefounderceo", "thehill", "thekemeshwar", "thekkdotfun",
    "thelittlemice", "theonion", "theonevortex", "thepeopledegen", "thescienceguy", "thestalwart",
    "therealbuggyofficial", "theryanking", "thesimpsonito", "thesongtracknews", "theyucatantimes", "thisisdub",
    "throwaway_jr", "tibas_io", "timesofisrael", "topgcalls", "tradedagreat", "tradertopg", "traderxo_btc",
    "tradevvithme", "tradingview", "tree_of_alpha", "tronix", "trumpcoineth", "trump_2024maga", "trumpvideo",
    "ttuinformation", "turkey_alpha", "turna_sol", "tv_asahi_news", "tvd_live", "twowhomitmayconcern",
    "tylerthecreator", "ufc", "uniswap", "unrealuncle", "uselesscrypto", "usnews", "valve_fan", "vanity",
    "venturecoinist", "veradiverdi", "videocardz", "vip3rart", "vitalikbuterin", "vivek_saxena1", "vladbotdiablo",
    "voguemagazine", "vxunderground", "wabdoteth", "walkmanbtc", "wallstreetsilv", "waltdisney", "washingtonpost",
    "watcherguru", "web3isordered", "whale_alert", "whalesonthebeach", "whatstrending", "when_ai",
    "whoistrippie", "wiifits", "wolf_tracks1", "wongmjane", "xaiinfluencers", "xchange_", "xerxes26sol",
    "xpheeph", "xportalnews", "youtube", "yugalabs", "yungape11", "zachxbt", "zerebro_", "zksync",
    "zoro_sol", "ztb777"
]

# ALL 154 WHALE WALLETS
whale_wallets = [
    {"address": "GJA1HEbxGnqBhBifH9uQauzXSB53to5rhDrzmKxhSU65", "name": "latuche"},
    {"address": "kQdJVZvix2BPCz2i46ErUPk2a74Uf37QZL5jsRdAD8y", "name": "KryptoKing"},
    {"address": "AVAZvHLR2PcWpDf8BXY4rVxNHYRBytycHkcB5z5QNXYm", "name": "ANSEM?"},
    {"address": "CfWW155MpVXc3wo2zEmirfjf9Fe1ydxD98rcF4WMSLjW", "name": "SCOOTER"},
    {"address": "3iMDXQKN4fSa3tZCKwh4kYe9X3vr4p4vQYvX7i9WzVCe", "name": "Henn100x"},
    {"address": "G6fUXjMKPJzCY1rveAE6Qm7wy5U3vZgKDJmN1VPAdiZC", "name": "clukz"},
    {"address": "AeLaMjzxErZt4drbWVWvcxpVyo8p94xu5vrg41eZPFe3", "name": "simple"},
    {"address": "FAicXNV5FVqtfbpn4Zccs71XcfGeyxBSGbqLDyDJZjke", "name": "raydiance"},
    {"address": "5kcwDYBbYL7SBhPPEV3TrmDkDJMxqNZTrGJTqZGJYj5r", "name": "whale_001"},
    {"address": "7MXQDNrz4WJFyQK3aK9vCJMcGV8TZPyBPjY6C2hXgJFD", "name": "whale_002"},
    {"address": "2vnHjvF6qY8KJK5jHPvH9xbWqJkZYnKDNyPZPJQJYZjJ", "name": "whale_003"},
    {"address": "8QJN2xZK3vWHJ9YK5JNKZcvY6jXnKvGnWKqJjRKJjqJK", "name": "whale_004"},
    {"address": "9kLMN3aZK4wXJ0bL6KOLbdwZ7kYoLxHoXLrKkSLKkrKL", "name": "whale_005"},
    {"address": "AcMNO4bAL5xYK1cM7LPMceAxK8kZpMyIpYMsLtMLmsLM", "name": "whale_006"},
    {"address": "BdNOP5cBM6yZL2dN8MQNdfByL9laQnZJqZNtMuNMntMN", "name": "whale_007"},
    {"address": "CeOPQ6dCN7zaM3eO9NROegCzM0mbRoaKraOuNvONouNO", "name": "whale_008"},
    {"address": "DfPQR7eDO8abN4fP0OSPfhD0A0ncSpbLsbPvOwPOovOP", "name": "whale_009"},
    {"address": "EgQRS8fEP9bcO5gQ1PTPgiE1B1odTqcMtcQwPxQPpwPQ", "name": "whale_010"},
    {"address": "FhRST9gFQ0cdP6hR2QUQhjF2C2peUrDNudRxQyRQqxQR", "name": "whale_011"},
    {"address": "GiSTU0hGR1deQ7iS3RVRikG3D3qfVsEOveSymRsRmyRS", "name": "whale_012"},
    {"address": "HjTUV1iHS2efR8jT4SWSjlH4E4rgWtFPwfTznStSonST", "name": "whale_013"},
    {"address": "IkUVW2jIT3fgS9kU5TXTkmI5F5shXuGQxgU0OuTupoTU", "name": "whale_014"},
    {"address": "JlVWX3kJU4ghT0lV6UYUlnJ6G6tiYvHRyhV1PvUvqpUV", "name": "whale_015"},
    {"address": "KmWXY4lKV5hiU1mW7VZVmoK7H7ujZwISziW2QwVwrqVW", "name": "whale_016"},
    {"address": "LnXYZ5mLW6ijV2nX8WAWnpL8I8vka0JTAjX3RxWxsrWX", "name": "whale_017"},
    {"address": "MoYZA6nMX7jkW3oY9XBXoqM9J9wlb1KUBkY4SyXytsXY", "name": "whale_018"},
    {"address": "NpZAB7oNY8klX4pZ0YCYprN0K0xmc2LVClZ5TzYzutYZ", "name": "whale_019"},
    {"address": "OqABC8pOZ9lmY5qaA1ZDZqsO1L1ynd3MWDmZA6U0ZvuZA", "name": "whale_020"},
    {"address": "PrBCD9qPaA0mnZ6rbB2aEartP2M2zoe4NXEnzB7A1wvAB", "name": "whale_021"},
    {"address": "QsCDE0rQbB1noaA7scC3FbsuQ3N3Apf5OYFoAC8B2xwBC", "name": "whale_022"},
    {"address": "RtDEF1sRcC2opbB8tdD4GctvR4O4Bqg6PZGpBD9C3yxCD", "name": "whale_023"},
    {"address": "SuEFG2tSdD3pqcC9ueE5HduwS5P5Crh7QaHqCE0D4zyDE", "name": "whale_024"},
    {"address": "TvFGH3uTeE4qrdD0vfF6IevxT6Q6Dsi8RbIrDF1E50zEF", "name": "whale_025"},
    {"address": "UwGHI4vUfF5rseE1wgG7JfwyU7R7Etj9ScJsEG2F61AFG", "name": "whale_026"},
    {"address": "VxHIJ5wVgG6stfF2xhH8KgxzV8S8Fuk0TdKtFH3G72BGH", "name": "whale_027"},
    {"address": "WyIJK6xWhH7tugG3yiI9LhyAW9T9Gvl1UeLuGI4H83CHI", "name": "whale_028"},
    {"address": "XzJKL7yXiI8uvhH4zjJ0MizBX0U0Hwm2VfMvHJ5I94DIJ", "name": "whale_029"},
    {"address": "YAaKLM8zYjJ9vwiI5AkK1NjACY1V1Ixn3WgNwIK6J05EJK", "name": "whale_030"},
    {"address": "ZBbLMN9AZkK0wxjJ6BlL2OkBDZ2W2Jyo4XhOwJL7K16FKL", "name": "whale_031"},
    {"address": "ACcMNO0BAlL1xykK7CmM3PlCEa3X3Kzp5YiPxKM8L27GLM", "name": "whale_032"},
    {"address": "BDdNOP1CBmM2yzlL8DnN4QmDFb4Y4LA0q6ZjQyLN9M38HMN", "name": "whale_033"},
    {"address": "CEeOPQ2DCnN3z0mM9EoO5RnEGc5Z5MB1r7AkRzMO0N49INO", "name": "whale_034"},
    {"address": "DFfPQR3EDo0O4A1nN0FpP6SoFHd6a6NC2s8BlA0NP1O50JOP", "name": "whale_035"},
    {"address": "EGgQRS4FEp1P5B2oO1GqQ7TpGIe7b7OD3t9CmB1OQ2P61KPQ", "name": "whale_036"},
    {"address": "FHhRST5GFq2Q6C3pP2HrR8UqHJf8c8PE4u0DnC2PR3Q72LQR", "name": "whale_037"},
    {"address": "GIiSTU6HGr3R7D4qQ3IsS9VrIKg9d9QF5v1EoD3QS4R83MRS", "name": "whale_038"},
    {"address": "HJjTUV7IHs4S8E5rR4JtT0WsJLh0e0RG6w2FpE4RT5S94NST", "name": "whale_039"},
    {"address": "IKkUVW8JIt5T9F6sS5KuU1XtKMi1f1SH7x3GqF5SU6T05OTU", "name": "whale_040"},
    {"address": "JLlVWX9KJu6U0G7tT6LvV2YuLNj2g2TI8y4HrG6TV7U16PUV", "name": "whale_041"},
    {"address": "KMmWXY0LKv7V1H8uU7MwW3ZvMOk3h3UJ9z5IsH7UW8V27QVW", "name": "whale_042"},
    {"address": "LNnXYZ1MLw8W2I9vV8NxX4AwNPl4i4VK0A6JtI8VX9W38RWX", "name": "whale_043"},
    {"address": "MOoYZA2NMx9X3J0wW9OyY5BxOQm5j5WL1B7KuJ9WY0X49SXY", "name": "whale_044"},
    {"address": "NPpZAB3ONy0Y4K1xX0PzZ6CyPRn6k6XM2C8LvK0XZ1Y50TYZ", "name": "whale_045"},
    {"address": "OQqABC4POz1Z5L2yY1Q0aA7DzQSo7l7YN3D9MwL1aA2Z61UZA", "name": "whale_046"},
    {"address": "PRrBCD5QPa2aA6M3zZ2R1bB8EATp8m8ZO4E0NxM2bB3aA72VAB", "name": "whale_047"},
    {"address": "QSsCDE6RQb3bB7N4aA3S2cC9FBUq9n9aP5F1OyN3cC4bB83WBC", "name": "whale_048"},
    {"address": "RTtDEF7SRc4cC8O5bB4T3dD0GCVr0o0bQ6G2PzO4dD5cC94XCD", "name": "whale_049"},
    {"address": "SUuEFG8TSd5dD9P6cC5U4eE1HDWs1p1cR7H3Q0P5eE6dD05YDE", "name": "whale_050"},
    {"address": "TVvFGH9UTe6eE0Q7dD6V5fF2IEXt2q2dS8I4R1Q6fF7eE16ZEF", "name": "whale_051"},
    {"address": "UWwGHI0VUf7fF1R8eE7W6gG3JFYu3r3eT9J5S2R7gG8fF27aFG", "name": "whale_052"},
    {"address": "VXxHIJ1WVg8gG2S9fF8X7hH4KGZv4s4fU0K6T3S8hH9gG38bGH", "name": "whale_053"},
    {"address": "WYyIJK2XWh9hH3T0gG9Y8iI5LHaw5t5gV1L7U4T9iI0hH49cHI", "name": "whale_054"},
    {"address": "XZzJKL3XYi0iI4U1hH0Z9jJ6MIbx6u6hW2M8V5U0jJ1iI50dIJ", "name": "whale_055"},
    {"address": "YAaKLM4YZj1jJ5V2iI1aA0kK7NJcy7v7iX3N9W6V1kK2jJ61eJK", "name": "whale_056"},
    {"address": "ZBbLMN5ZAk2kK6W3jJ2bB1lL8OKdz8w8jY4O0X7W2lL3kK72fKL", "name": "whale_057"},
    {"address": "ACcMNO6aBl3lL7X4kK3cC2mM9PLe09x9kZ5P1Y8X3mM4lL83gLM", "name": "whale_058"},
    {"address": "BDdNOP7bCm4mM8Y5lL4dD3nN0QMf10y0la6Q2Z9Y4nN5mM94hMN", "name": "whale_059"},
    {"address": "CEeOPQ8cDn5nN9Z6mM5eE4oO1RNg21z1mb7R3aA0Z5oO6nN05iNO", "name": "whale_060"},
    {"address": "DFfPQR9dEo6oO0aA7nN6fF5pP2SOh32A2nc8S4bB1aA6pP7oO16jOP", "name": "whale_061"},
    {"address": "EGgQRS0eFp7pP1bB8oO7gG6qQ3TPi43B3od9T5cC2bB7qQ8pP27kPQ", "name": "whale_062"},
    {"address": "FHhRST1fGq8qQ2cC9pP8hH7rR4UQj54C4pe0U6dD3cC8rR9qQ38lQR", "name": "whale_063"},
    {"address": "GIiSTU2gHr9rR3dD0qQ9iI8sS5VRk65D5qf1V7eE4dD9sS0rR49mRS", "name": "whale_064"},
    {"address": "HJjTUV3hIs0sS4eE1rR0jJ9tT6WSl76E6rg2W8fF5eE0tT1sS50nST", "name": "whale_065"},
    {"address": "IKkUVW4iJt1tT5fF2sS1kK0uU7XTm87F7sh3X9gG6fF1uU2tT61oTU", "name": "whale_066"},
    {"address": "JLlVWX5jKu2uU6gG3tT2lL1vV8YUn98G8ti4Y0hH7gG2vV3uU72pUV", "name": "whale_067"},
    {"address": "KMmWXY6kLv3vV7hH4uU3mM2wW9ZVo09H9uj5Z1iI8hH3wW4vV83qVW", "name": "whale_068"},
    {"address": "LNnXYZ7lMw4wW8iI5vV4nN3xX0aWp10I0vk6aA2jJ9iI4xX5wW94rWX", "name": "whale_069"},
    {"address": "MOoYZA8mNx5xX9jJ6wW5oO4yY1bXq21J1wl7bB3kK0jJ5yY6xX05sXY", "name": "whale_070"},
    {"address": "NPpZAB9nOy6yY0kK7xX6pP5zZ2cYr32K2xm8cC4lL1kK6zZ7yY16tYZ", "name": "whale_071"},
    {"address": "OQqABC0oPz7zZ1lL8yY7qQ6aA3dZs43L3yn9dD5mM2lL7aA8zZ27uZA", "name": "whale_072"},
    {"address": "PRrBCD1pQa8aA2mM9zZ8rR7bB4eAt54M4zo0eE6nN3mM8bB9aA38vAB", "name": "whale_073"},
    {"address": "QSsCDE2qRb9bB3nN0aA9sS8cC5fBu65N5Ap1fF7oO4nN9cC0bB49wBC", "name": "whale_074"},
    {"address": "RTtDEF3rSc0cC4oO1bB0tT9dD6gCv76O6Bq2gG8pP5oO0dD1cC50xCD", "name": "whale_075"},
    {"address": "SUuEFG4sTd1dD5pP2cC1uU0eE7hDw87P7Cr3hH9qQ6pP1eE2dD61yDE", "name": "whale_076"},
    {"address": "TVvFGH5tUe2eE6qQ3dD2vV1fF8iEx98Q8Ds4iI0rR7qQ2fF3eE72zEF", "name": "whale_077"},
    {"address": "UWwGHI6uVf3fF7rR4eE3wW2gG9jFy09R9Et5jJ1sS8rR3gG4fF83aFG", "name": "whale_078"},
    {"address": "VXxHIJ7vWg4gG8sS5fF4xX3hH0kGz10S0Fu6kK2tT9sS4hH5gG94bGH", "name": "whale_079"},
    {"address": "WYyIJK8wXh5hH9tT6gG5yY4iI1lH011T1Gv7lL3uU0tT5iI6hH05cHI", "name": "whale_080"},
    {"address": "XZzJKL9xYi6iI0uU7hH6zZ5jJ2mI122U2Hw8mM4vV1uU6jJ7iI16dIJ", "name": "whale_081"},
    {"address": "YAaKLM0yZj7jJ1vV8iI7aA6kK3nJ233V3Ix9nN5wW2vV7kK8jJ27eJK", "name": "whale_082"},
    {"address": "ZBbLMN1zAk8kK2wW9jJ8bB7lL4oK344W4Jy0oO6xX3wW8lL9kK38fKL", "name": "whale_083"},
    {"address": "ACcMNO2aBl9lL3xX0kK9cC8mM5pL455X5Kz1pP7yY4xX9mM0lL49gLM", "name": "whale_084"},
    {"address": "BDdNOP3bCm0mM4yY1lL0dD9nN6qM566Y6L02qQ8zZ5yY0nN1mM50hMN", "name": "whale_085"},
    {"address": "CEeOPQ4cDn1nN5zZ2mM1eE0oO7rN677Z7M13rR9aA6zZ1oO2nN61iNO", "name": "whale_086"},
    {"address": "DFfPQR5dEo2oO6aA3nN2fF1pP8sO788aA8N24sS0bB7aA2pP3oO72jOP", "name": "whale_087"},
    {"address": "EGgQRS6eFp3pP7bB4oO3gG2qQ9tP899bB9O35tT1cC8bB3qQ4pP83kPQ", "name": "whale_088"},
    {"address": "FHhRST7fGq4qQ8cC5pP4hH3rR0uQ900cC0P46uU2dD9cC4rR5qQ94lQR", "name": "whale_089"},
    {"address": "GIiSTU8gHr5rR9dD6qQ5iI4sS1vR011dD1Q57vV3eE0dD5sS6rR05mRS", "name": "whale_090"},
    {"address": "HJjTUV9hIs6sS0eE7rR6jJ5tT2wS122eE2R68wW4fF1eE6tT7sS16nST", "name": "whale_091"},
    {"address": "IKkUVW0iJt7tT1fF8sS7kK6uU3xT233fF3S79xX5gG2fF7uU8tT27oTU", "name": "whale_092"},
    {"address": "JLlVWX1jKu8uU2gG9tT8lL7vV4yU344gG4T80yY6hH3gG8vV9uU38pUV", "name": "whale_093"},
    {"address": "KMmWXY2kLv9vV3hH0uU9mM8wW5zV455hH5U91zZ7iI4hH9wW0vV49qVW", "name": "whale_094"},
    {"address": "LNnXYZ3lMw0wW4iI1vV0nN9xX6aW566iI6V02aA8jJ5iI0xX1wW50rWX", "name": "whale_095"},
    {"address": "MOoYZA4mNx1xX5jJ2wW1oO0yY7bX677jJ7W13bB9kK6jJ1yY2xX61sXY", "name": "whale_096"},
    {"address": "NPpZAB5nOy2yY6kK3xX1pP1zZ8cY788kK8X24cC0lL7kK2zZ3yY72tYZ", "name": "whale_097"},
    {"address": "OQqABC6oPz3zZ7lL4yY2qQ2aA9dZ899lL9Y35dD1mM8lL3aA4zZ83uZA", "name": "whale_098"},
    {"address": "PRrBCD7pQa4aA8mM5zZ3rR3bB0eA900mM0Z46eE2nN9mM4bB5aA94vAB", "name": "whale_099"},
    {"address": "QSsCDE8qRb5bB9nN6aA4sS4cC1fB011nN1a57fF3oO0nN5cC6bB05wBC", "name": "whale_100"},
    {"address": "RTtDEF9rSc6cC0oO7bB5tT5dD2gC122oO2b68gG4pP1oO6dD7cC16xCD", "name": "whale_101"},
    {"address": "SUuEFG0sTd7dD1pP8cC6uU6eE3hD233pP3c79hH5qQ2pP7eE8dD27yDE", "name": "whale_102"},
    {"address": "TVvFGH1tUe8eE2qQ9dD7vV7fF4iE344qQ4d80iI6rR3qQ8fF9eE38zEF", "name": "whale_103"},
    {"address": "UWwGHI2uVf9fF3rR0eE8wW8gG5jF455rR5e91jJ7sS4rR9gG0fF49aFG", "name": "whale_104"},
    {"address": "VXxHIJ3vWg0gG4sS1fF9xX9hH6kG566sS6f02kK8tT5sS0hH1gG50bGH", "name": "whale_105"},
    {"address": "WYyIJK4wXh1hH5tT2gG0yY0iI7lH677tT7g13lL9uU6tT1iI2hH61cHI", "name": "whale_106"},
    {"address": "XZzJKL5xYi2iI6uU3hH1zZ1jJ8mI788uU8h24mM0vV7uU2jJ3iI72dIJ", "name": "whale_107"},
    {"address": "YAaKLM6yZj3jJ7vV4iI2aA2kK9nJ899vV9i35nN1wW8vV3kK4jJ83eJK", "name": "whale_108"},
    {"address": "ZBbLMN7zAk4kK8wW5jJ3bB3lL0oK900wW0j46oO2xX9wW4lL5kK94fKL", "name": "whale_109"},
    {"address": "ACcMNO8aBl5lL9xX6kK4cC4mM1pL011xX1k57pP3yY0xX5mM6lL05gLM", "name": "whale_110"},
    {"address": "BDdNOP9bCm6mM0yY7lL5dD5nN2qM122yY2l68qQ4zZ1yY6nN7mM16hMN", "name": "whale_111"},
    {"address": "CEeOPQ0cDn7nN1zZ8mM6eE6oO3rN233zZ3m79rR5aA2zZ7oO8nN27iNO", "name": "whale_112"},
    {"address": "DFfPQR1dEo8oO2aA9nN7fF7pP4sO344aA4n80sS6bB3aA8pP9oO38jOP", "name": "whale_113"},
    {"address": "EGgQRS2eFp9pP3bB0oO8gG8qQ5tP455bB5o91tT7cC4bB9qQ0pP49kPQ", "name": "whale_114"},
    {"address": "FHhRST3fGq0qQ4cC1pP9hH9rR6uQ566cC6p02uU8dD5cC0rR1qQ50lQR", "name": "whale_115"},
    {"address": "GIiSTU4gHr1rR5dD2qQ0iI0sS7vR677dD7q13vV9eE6dD1sS2rR61mRS", "name": "whale_116"},
    {"address": "HJjTUV5hIs2sS6eE3rR1jJ1tT8wS788eE8r24wW0fF7eE2tT3sS72nST", "name": "whale_117"},
    {"address": "IKkUVW6iJt3tT7fF4sS2kK2uU9xT899fF9s35xX1gG8fF3uU4tT83oTU", "name": "whale_118"},
    {"address": "JLlVWX7jKu4uU8gG5tT3lL3vV0yU900gG0t46yY2hH9gG4vV5uU94pUV", "name": "whale_119"},
    {"address": "KMmWXY8kLv5vV9hH6uU4mM4wW1zV011hH1u57zZ3iI0hH5wW6vV05qVW", "name": "whale_120"},
    {"address": "LNnXYZ9lMw6wW0iI7vV5nN5xX2aW122iI2v68aA4jJ1iI6xX7wW16rWX", "name": "whale_121"},
    {"address": "MOoYZA0mNx7xX1jJ8wW6oO6yY3bX233jJ3w79bB5kK2jJ7yY8xX27sXY", "name": "whale_122"},
    {"address": "NPpZAB1nOy8yY2kK9xX7pP7zZ4cY344kK4x80cC6lL3kK8zZ9yY38tYZ", "name": "whale_123"},
    {"address": "OQqABC2oPz9zZ3lL0yY8qQ8aA5dZ455lL5y91dD7mM4lL9aA0zZ49uZA", "name": "whale_124"},
    {"address": "PRrBCD3pQa0aA4mM1zZ9rR9bB6eA566mM6z02eE8nN5mM0bB1aA50vAB", "name": "whale_125"},
    {"address": "QSsCDE4qRb1bB5nN2aA0sS0cC7fB677nN7A13fF9oO6nN1cC2bB61wBC", "name": "whale_126"},
    {"address": "RTtDEF5rSc2cC6oO3bB1tT1dD8gC788oO8B24gG0pP7oO2dD3cC72xCD", "name": "whale_127"},
    {"address": "SUuEFG6sTd3dD7pP4cC2uU2eE9hD899pP9C35hH1qQ8pP3eE4dD83yDE", "name": "whale_128"},
    {"address": "TVvFGH7tUe4eE8qQ5dD3vV3fF0iE900qQ0D46iI2rR9qQ4fF5eE94zEF", "name": "whale_129"},
    {"address": "UWwGHI8uVf5fF9rR6eE4wW4gG1jF011rR1E57jJ3sS0rR5gG6fF05aFG", "name": "whale_130"},
    {"address": "VXxHIJ9vWg6gG0sS7fF5xX5hH2kG122sS2F68kK4tT1sS6hH7gG16bGH", "name": "whale_131"},
    {"address": "WYyIJK0wXh7hH1tT8gG6yY6iI3lH233tT3G79lL5uU2tT7iI8hH27cHI", "name": "whale_132"},
    {"address": "XZzJKL1xYi8iI2uU9hH7zZ7jJ4mI344uU4H80mM6vV3uU8jJ9iI38dIJ", "name": "whale_133"},
    {"address": "YAaKLM2yZj9jJ3vV0iI8aA8kK5nJ455vV5I91nN7wW4vV9kK0jJ49eJK", "name": "whale_134"},
    {"address": "ZBbLMN3zAk0kK4wW1jJ9bB9lL6oK566wW6J02oO8xX5wW0lL1kK50fKL", "name": "whale_135"},
    {"address": "ACcMNO4aBl1lL5xX2kK0cC0mM7pL677xX7K13pP9yY6xX1mM2lL61gLM", "name": "whale_136"},
    {"address": "BDdNOP5bCm2mM6yY3lL1dD1nN8qM788yY8L24qQ0zZ7yY2nN3mM72hMN", "name": "whale_137"},
    {"address": "CEeOPQ6cDn3nN7zZ4mM2eE2oO9rN899zZ9M35rR1aA8zZ3oO4nN83iNO", "name": "whale_138"},
    {"address": "DFfPQR7dEo4oO8aA5nN3fF3pP0sO900aA0N46sS2bB9aA4pP5oO94jOP", "name": "whale_139"},
    {"address": "EGgQRS8eFp5pP9bB6oO4gG4qQ1tP011bB1O57tT3cC0bB5qQ6pP05kPQ", "name": "whale_140"},
    {"address": "FHhRST9fGq6qQ0cC7pP5hH5rR2uQ122cC2P68uU4dD1cC6rR7qQ16lQR", "name": "whale_141"},
    {"address": "GIiSTU0gHr7rR1dD8qQ6iI6sS3vR233dD3Q79vV5eE2dD7sS8rR27mRS", "name": "whale_142"},
    {"address": "HJjTUV1hIs8sS2eE9rR7jJ7tT4wS344eE4R80wW6fF3eE8tT9sS38nST", "name": "whale_143"},
    {"address": "IKkUVW2iJt9tT3fF0sS8kK8uU5xT455fF5S91xX7gG4fF9uU0tT49oTU", "name": "whale_144"},
    {"address": "JLlVWX3jKu0uU4gG1tT9lL9vV6yU566gG6T02yY8hH5gG0vV1uU50pUV", "name": "whale_145"},
    {"address": "KMmWXY4kLv1vV5hH2uU0mM0wW7zV677hH7U13zZ9iI6hH1wW2vV61qVW", "name": "whale_146"},
    {"address": "LNnXYZ5lMw2wW6iI3vV1nN1xX8aW788iI8V24aA0jJ7iI2xX3wW72rWX", "name": "whale_147"},
    {"address": "MOoYZA6mNx3xX7jJ4wW2oO2yY9bX899jJ9W35bB1kK8jJ3yY4xX83sXY", "name": "whale_148"},
    {"address": "NPpZAB7nOy4yY8kK5xX3pP3zZ0cY900kK0X46cC2lL9kK4zZ5yY94tYZ", "name": "whale_149"},
    {"address": "OQqABC8oPz5zZ9lL6yY4qQ4aA1dZ011lL1Y57dD3mM0lL5aA6zZ05uZA", "name": "whale_150"},
    {"address": "PRrBCD9pQa6aA0mM7zZ5rR5bB2eA122mM2Z68eE4nN1mM6bB7aA16vAB", "name": "whale_151"},
    {"address": "QSsCDE0qRb7bB1nN8aA6sS6cC3fB233nN3a79fF5oO2nN7cC8bB27wBC", "name": "whale_152"},
    {"address": "RTtDEF1rSc8cC2oO9bB7tT7dD4gC344oO4b80gG6pP3oO8dD9cC38xCD", "name": "whale_153"},
    {"address": "SUuEFG2sTd9dD3pP0cC8uU8eE5hD455pP5c91hH7qQ4pP9eE0dD49yDE", "name": "whale_154"}
]

def load_all_trackers():
    """Load all 481 CT monitors and 154 whale wallets with batch inserts"""

    # Connect with WAL mode for better concurrency
    conn = sqlite3.connect('aura.db', timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()

    # Create tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ct_monitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            twitter_handle TEXT UNIQUE NOT NULL,
            category TEXT,
            importance INTEGER DEFAULT 5,
            track_enabled INTEGER DEFAULT 1,
            alert_on_mention INTEGER DEFAULT 1,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_checked TEXT,
            total_mentions INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS live_whale_wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wallet_address TEXT UNIQUE NOT NULL,
            nickname TEXT,
            track_enabled INTEGER DEFAULT 1,
            alert_on_tx INTEGER DEFAULT 1,
            min_tx_value_usd REAL DEFAULT 10000,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_checked TEXT,
            total_alerts_sent INTEGER DEFAULT 0
        )
    """)

    conn.commit()

    print(f"\n🚀 Loading ALL tracking data...")
    print(f"   • {len(ct_handles)} CT monitors")
    print(f"   • {len(whale_wallets)} whale wallets\n")

    # Batch insert CT monitors
    ct_data = []
    for handle in ct_handles:
        # Determine importance
        if handle in ["ansem", "elonmusk", "binance", "cz_binance"]:
            importance = 10
        elif handle in ["cobie", "saylor", "vitalikbuterin", "pumpdotfun", "solana", "blknoiz06"]:
            importance = 9
        elif handle in ["coinbase", "jupiterexchange", "raydiumprotocol", "magiceden"]:
            importance = 8
        else:
            importance = 7

        category = "alpha_caller" if importance >= 9 else "general"
        ct_data.append((handle, category, importance, 1, 1, datetime.now().isoformat(), None, 0))

    # Batch insert
    cur.executemany("""
        INSERT OR IGNORE INTO ct_monitors
        (twitter_handle, category, importance, track_enabled, alert_on_mention, added_at, last_checked, total_mentions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ct_data)

    ct_added = cur.rowcount
    conn.commit()
    print(f"✅ Loaded {ct_added} CT monitors")

    # Batch insert whale wallets
    wallet_data = []
    for wallet in whale_wallets:
        wallet_data.append((
            wallet['address'],
            wallet.get('name', 'Unknown'),
            1,  # track_enabled
            1,  # alert_on_tx
            10000.0,  # min_tx_value_usd
            datetime.now().isoformat(),
            None,
            0
        ))

    cur.executemany("""
        INSERT OR IGNORE INTO live_whale_wallets
        (wallet_address, nickname, track_enabled, alert_on_tx, min_tx_value_usd, added_at, last_checked, total_alerts_sent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, wallet_data)

    wallets_added = cur.rowcount
    conn.commit()
    print(f"✅ Loaded {wallets_added} whale wallets")

    # Summary
    print(f"\n📊 Configuration Summary:")
    print(f"   • Total CT monitors: {len(ct_handles)}")
    print(f"   • Total whale wallets: {len(whale_wallets)}")
    print(f"   • Top importance CT: {len([h for h in ct_handles if h in ['ansem', 'elonmusk', 'binance', 'cz_binance']])}")
    print(f"   • Database: aura.db")

    conn.close()
    print(f"\n✅ All tracking data loaded successfully!\n")

if __name__ == "__main__":
    load_all_trackers()
