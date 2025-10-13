#!/usr/bin/env python3
"""
FULL CONFIGURATION - ALL 481 CT MONITORS + ALL 154 WHALE WALLETS
Load complete live tracking data into AURA
"""

import json
from aura_live_config import AuraLiveConfig

# ALL 481 CT MONITORS (Twitter handles)
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
    "pluffin_", "pmarca", "poe_ether", "pokemon", "polymarket", "popbase", "poshzilla", "potus",
    "pr6spr", "prericher_x", "project02", "pumpdotfun", "pureunitycoin", "quantum1tx", "rainmaker1973",
    "rajgokal", "rapidresponse47", "rasmr_eth", "rayasianboy", "raydiumprotocol", "realdonaldtrump",
    "realdonaltrump", "realrossu", "reem_onchain", "regipumps", "reubenstill", "reversecapo", "rianix7",
    "rm8nv2", "rockstargames", "roundtablespace", "runitbackghost", "s1cksicks1ck", "s1mple_s1mple",
    "sama", "samlbnb", "samlessin", "sandiegozoo", "sasori1333", "saylor", "sbf_ftx", "scarfacepog",
    "scoot_sol", "sdcrypto_1", "sealonchain", "secgov", "secretservice", "senlummis", "_shadow36",
    "shadurx", "sharkssignals", "shawmakesmagic", "shfred0", "siren", "sizthetrencher", "sk_cryypto",
    "skxonsol", "skynews", "slyyguy_", "solana", "solana_dexpaid", "_solgoodman", "solidintel_x",
    "solnovacrypto", "solopperatoooor", "solporttom", "something", "spasovsol", "spidercrypto0x",
    "stoolpresidente", "suppressant_s", "surreaall", "swearsol", "sydix_", "sypherlit", "techcrunch",
    "tekkerrss", "telegram", "tempest1z", "tensor_hq", "tesla", "tesla_optimus", "teslaownerssv",
    "tethegamer", "thatboycrzy", "thebabylonbee", "theblock__", "theeconomist", "themfrayan",
    "thenotoriousmma", "theroaringkitty", "theunipcs", "tier10k", "time", "timsweeneyepic", "tmz",
    "toibimemeschoi", "tradeonnova", "tradewithrunner", "trenchdiver101", "trend_eth", "trumpdailyposts",
    "trump_repost", "trumpwarroom", "truth_terminal", "tsomisol", "twitch", "unload112", "unusual_whales",
    "veinvariance", "venturetwins", "vibed333", "vice", "viclaranja", "vitalikbuterin", "voidsolx",
    "vynsirr", "vzzzzczzzz", "washingtonpost", "watcherguru", "watchingmarkets", "weremeow", "wewuzbig",
    "whaleinsider", "whitehouse", "windows", "wirelyss", "wisemenmentors", "witloofsol", "x", "xmbonsol",
    "x_pally", "xshop", "yennii56", "youranoncentral", "youranonnews", "yxngsnipez", "yyomoessi",
    "zachboychuk", "zachxbt", "_zeta_crypto", "zghire_", "zguz", "zhusu", "zoomiami", "zssbecker", "ztb777"
]

# ALL 154 WHALE WALLETS (Solana addresses with names)
whale_wallets = [
    {"address": "GJA1HEbxGnqBhBifH9uQauzXSB53to5rhDrzmKxhSU65", "name": "latuche"},
    {"address": "HwRnKq7RPtKHvX9wyHsc1zvfHtGjPQa5tyZtGtbvfXE", "name": "Unnamed1"},
    {"address": "kQdJVZvix2BPCz2i46ErUPk2a74Uf37QZL5jsRdAD8y", "name": "KryptoKing"},
    {"address": "niggerd597QYedtvjQDVHZTCCGyJrwHNm2i49dkm5zS", "name": "Unnamed2"},
    {"address": "5jMW1hzAKZSYbLvpHf6UviQ8PoSMmdh8LY8ZYPyb94ve", "name": "SerpentsGame"},
    {"address": "5rkPDK4JnVAumgzeV2Zu8vjggMTtHdDtrsd5o9dhGZHD", "name": "DavePortnoy"},
    {"address": "6RoLbZJWJHpTk4sdPsWzocEHiRtzPS36WcBjnMXuQrfU", "name": "Jugg"},
    {"address": "Avc4fcAvrXRNnoEjwRVgM61EjwKX6smdPspGQjeRWLV1", "name": "goodtraderpnut"},
    {"address": "BZ6AhC75Xhhm5fpkuaU1pJq7jLfsPoJ9xHPCNQWh7xVJ", "name": "SuperWhale"},
    {"address": "G5nxEXuFMfV74DSnsrSatqCW32F34XUnBeq3PfDS7w5E", "name": "$$"},
    {"address": "5B52w1ZW9tuwUduueP5J7HXz5AcGfruGoX6YoAudvyxG", "name": "Yenni"},
    {"address": "5fWkLJfoDsRAaXhPJcJY19qNtDDQ5h6q1SPzsAPRrUNG", "name": "Unnamed3"},
    {"address": "5mtbmPwj2SMkxPP9c93s9oD9bmMdByTqepNarM9Y7u7e", "name": "-$Gm3"},
    {"address": "5YkZmuaLhrPjFv4vtYE2mcR6J4JEXG1EARGh8YYFo8s4", "name": "Unnamed4"},
    {"address": "62FZUSWPMX9pofoV1uWHMdzFJRjwMa1LHgh2zhdEB7Zj", "name": "Unnamed5"},
    {"address": "7CeeipDnoTVE343cfmNuaEPL1BWLBzFKL2jzHcqBXN9c", "name": "Unnamed6"},
    {"address": "ApRnQN2HkbCn7W2WWiT2FEKvuKJp9LugRyAE1a9Hdz1", "name": "Unnamed7"},
    {"address": "4t9bWuZsXXKGMgmd96nFD4KWxyPNTsPm4q9jEMH4jD2i", "name": "Unnamed8"},
    {"address": "7Dt5oUpxHWuKH8bCTXDLz2j3JyxA7jEmtzqCG6pnh96X", "name": "leens"},
    {"address": "7i7vHEv87bs135DuoJVKe9c7abentawA5ydfWcWc8iY2", "name": "ChartFu🐒"},
    {"address": "BuV9QKhkfu1pstvwzvWkLejfPTZiqiksWKd6yD33qCaj", "name": "Unnamed9"},
    {"address": "CCUcjek5p6DLoH2YNtjizxYhAnStXAQAGVxhp1cYJF7w", "name": "elchartox"},
    {"address": "ELwogpDn5xqQ9AHoKA7pnctrvUc2djMMVFfn3BCcgecP", "name": "VladislavUtushkin"},
    {"address": "HkFt55P3PhRWHXoTFeuvkKEE4ab26xZ1bk6UmXV88Pwz", "name": "terp"},
    {"address": "9K18MstUaXmSFSBoa9qDTqWTnYhTZqdgEhuKRTVRgh6g", "name": "Unnamed10"},
    {"address": "9ru9BSVFSUqSRQFwdjjnkzQGf9yUdpRTjpjXPKc4BvxX", "name": "Unnamed11"},
    {"address": "9UWZFoiCHeYRLmzmDJhdMrP7wgrTw7DMSpPiT2eHgJHe", "name": "Unnamed12"},
    {"address": "AVAZvHLR2PcWpDf8BXY4rVxNHYRBytycHkcB5z5QNXYm", "name": "ANSEM?"},
    {"address": "BeTvN1ucBnCj4Ef688i51KHn2oq35CWDvD2J5aLFp17t", "name": "Unnamed13"},
    {"address": "BpycpQ7STrD8d73kjui5nzJmp7EBAgSmFfV8zeqMMX5z", "name": "Unnamed14"},
    {"address": "D2wBctC1K2mEtA17i8ZfdEubkiksiAH2j8F7ri3ec71V", "name": "Dior"},
    {"address": "dVs7zZksjFuq73xbtUC62brFXYYuxCuPSG4wZeGiHck", "name": "Unnamed15"},
    {"address": "EdDCRfDDeiiDXdntrP59abH4DXHFNU48zpMPYisDMjA7", "name": "MEZOTERIC"},
    {"address": "FvTBarKFhrnhL9Q55bSJnMmAdXisayUb5u96eLejhMF9", "name": "SCOOTER"},
    {"address": "G1pRtSyKuWSjTqRDcazzKBDzqEF96i1xSURpiXj3yFcc", "name": "CryptoD|1000XGEM"},
    {"address": "Gf9XgdmvNHt8fUTFsWAccNbKeyDXsgJyZN8iFJKg5Pbd", "name": "0xuezhang|985.eth"},
    {"address": "Grx451o9TBJp9dfVbMgzictW2TUbMFmaNhTu62DnMCMC", "name": "Unnamed16"},
    {"address": "RFSqPtn1JfavGiUID4HJsZyYXvZsycxf31hnYfbyG6iB", "name": "Unnamed17"},
    {"address": "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK", "name": "cupsy"},
    {"address": "2Dk2je4iif7yttyGMLbjc8JrqUSMw2wqLPuHxVsJZ2Bg", "name": "Unnamed18"},
    {"address": "2huXTbjeBhtMZ1ugNwUGucYBRasRaaiypymUX6P1Kwjx", "name": "Unnamed19"},
    {"address": "2YrKxjg1WKPqd19ivu6fWkfCG7VFZPyCAGYefd9zAnC7", "name": "Unnamed20"},
    {"address": "3h65MmPZksoKKyEpEjnWU2Yk2iYT5oZDNitGy5cTaxoE", "name": "jidn"},
    {"address": "3tc4BVAdzjr1JpeZu6NAjLHyp4kK3iic7TexMBYGJ4Xk", "name": "Insentos"},
    {"address": "45yBcpnzFTqLYQJtjxsa1DdZkgrTYponCg6yLQ6LQPu6", "name": "Unnamed21"},
    {"address": "HXkaN7TAQYXsybY1UHLrn18cVa9jgM3mbReasbAoSjTv", "name": "Unnamed22"},
    {"address": "iWinRYGEWcaFFqWfgjh28jnqWL72XUMmUfhADpTQaRL", "name": "Scooter"},
    {"address": "m7Kaas3Kd8FHLnCioSjCoSuVDReZ6FDNBVM6HTNYuF7", "name": "Unnamed23"},
    {"address": "EAnB5151L8ejp3SM6haLgyv3snk6oqc8acKgWEg9T5J", "name": "Jordan"},
    {"address": "FRbUNvGxYNC1eFngpn7AD3f14aKKTJVC6zSMtvj2dyCS", "name": "Henn100x"},
    {"address": "BCnqsPEtA1TkgednYEebRpkmwFRJDCjMQcKZMMtEdArc", "name": "Kreo"},
    {"address": "BieeZkdnBAgNYknzo3RH2vku7FcPkFZMZmRJANh2TpW", "name": "Unnamed24"},
    {"address": "2PBRmZuPxeLAAmyHLCLQgikB5HGP1Y7mLzg6KpNNVJ16", "name": "Unnamed25"},
    {"address": "7A4x4kL8LZgKyNb8deE9xM5wH7jhLLFPJJatZqtfAjGr", "name": "Unnamed26"},
    {"address": "3kebnKw7cPdSkLRfiMEALyZJGZ4wdiSRvmoN4rD1yPzV", "name": "Bastille"},
    {"address": "4hSXPtxZgXFpo6Vxq9yqxNjcBoqWN3VoaPJWonUtupzD", "name": "MATL"},
    {"address": "mW4PZB45isHmnjGkLpJvjKBzVS5NXzTJ8UDyug4gTsM", "name": "Dex"},
    {"address": "AbcX4XBm7DJ3i9p29i6sU8WLmiW4FWY5tiwB9D6UBbcE", "name": "404flipped"},
    {"address": "BoYHJoKntk3pjkaV8qFojEonSPWmWMfQocZTwDd1bcGG", "name": "Betman"},
    {"address": "7sWQeQLuNcbQas2Y4EoDn1hZ2Ks2sKKGeyrWjffWVJSW", "name": "Files"},
    {"address": "DrHszsqMAMuBrgRJ3XG7ZutDfEETHFW6W7vxA1vSQ2Ub", "name": "lynk"},
    {"address": "4S9U8HckRngscHWrW418cG6Suw62dhEZzmyrT2hxSye5", "name": "polar"},
    {"address": "87MZqjjJgpuFvaU8GyQJKbZGnCFFhX82qAjBGLRXPfcn", "name": "nyhrox"},
    {"address": "DsqRyTUh1R37asYcVf1KdX4CNnz5DKEFmnXvgT4NfTPE", "name": "Classic"},
    {"address": "sAdNbe1cKNMDqDsa4npB3TfL62T14uAo2MsUQfLvzLT", "name": "prosper"},
    {"address": "EcJWNtETrzdbj8s2dXpaE4Tu4r7fxALD6TNw9H8S6ksz", "name": "NothingShocked"},
    {"address": "DpNVrtA3ERfKzX4F8Pi2CVykdJJjoNxyY5QgoytAwD26", "name": "Gorilla"},
    {"address": "ATmKENkRrL1JQQnoUNAQvkiwgjiHKUkzyncxTGxyzQL1", "name": "Trump1"},
    {"address": "CNudZYFgpbT26fidsiNrWfHeGTBMMeVWqruZXsEkcUPc", "name": "Good1"},
    {"address": "HbCxe8yWQJWnK3f3FX4oohgm87FZuPYD4Ydszqxgkwft", "name": "Stacker"},
    {"address": "ARSdp5MFL1bjgWddK8dkF3QdttHvy5ZdVjJ6T8BHJimo", "name": "FishFish"},
    {"address": "HyNiuntjo51d5paTG7rX5XLLAAi68GQMN1STwSmvna4F", "name": "Trump3"},
    {"address": "CBaM2xaPdDdhaopd8dD93LJAvextJoPngdKFz8QFP7JD", "name": "Solkcow"},
    {"address": "E7gozEiAPNhpJsdS52amhhN2XCAqLZa7WPrhyR6C8o4S", "name": "Evening"},
    {"address": "Hq9iEGnpQ4KpJ91MjedVeHZcVMCWCsiJDE9i7j7SUUKF", "name": "Maxornext"},
    {"address": "EkdbN4v1v88Z8LjxhXWgLc8m1iZUqxUMS6vzNvEdTJkU", "name": "meechie"},
    {"address": "EHg5YkU2SZBTvuT87rUsvxArGp3HLeye1fXaSDfuMyaf", "name": "Til"},
    {"address": "Av3xWHJ5EsoLZag6pr7LKbrGgLRTaykXomDD5kBhL9YQ", "name": "Heyitsyolo"},
    {"address": "BCagckXeMChUKrHEd6fKFA1uiWDtcmCXMsqaheLiUPJd", "name": "DV"},
    {"address": "3Vsx9RN9jvnKwdMkHxn6Z2cehtffgghk4Kd4MStHT1P6", "name": "Unnamed27"},
    {"address": "Hnnw2hAgPgGiFKouRWvM3fSk3HnYgRv4Xq1PjUEBEuWM", "name": "Unnamed28"},
    {"address": "6S8GezkxYUfZy9JPtYnanbcZTMB87Wjt1qx3c6ELajKC", "name": "Unnamed29"},
    {"address": "9kf7oyNPHZB7TWcZZRewFMFwGNDKSEZKSSumMdaRYiuv", "name": "100kto64Binsider"},
    {"address": "96sErVjEN7LNJ6Uvj63bdRWZxNuBngj56fnT9biHLKBf", "name": "Orange"},
    {"address": "BXNiM7pqt9Ld3b2Hc8iT3mA5bSwoe9CRrtkSUs15SLWN", "name": "Absol"},
    {"address": "215nhcAHjQQGgwpQSJQ7zR26etbjjtVdW74NLzwEgQjP", "name": "Unnamed30"},
    {"address": "EaVboaPxFCYanjoNWdkxTbPvt57nhXGu5i6m9m6ZS2kK", "name": "Unnamed31"},
    {"address": "4nvNc7dDEqKKLM4Sr9Kgk3t1of6f8G66kT64VoC95LYh", "name": "Unnamed32"},
    {"address": "2RssnB7hcrnBEx55hXMKT1E7gN27g9ecQFbbCc5Zjajq", "name": "mostache"},
    {"address": "4BdKaxN8G6ka4GYtQQWk4G4dZRUTX2vQH9GcXdBREFUk", "name": "jijo"},
    {"address": "2YJbcB9G8wePrpVBcT31o8JEed6L3abgyCjt5qkJMymV", "name": "al4nnew"},
    {"address": "518qfCXg9UyASuHukCsUqn5t7PyY9uhDQrfDLQSVvniJ", "name": "TooGoodtobetrue"},
    {"address": "7ABz8qEFZTHPkovMDsmQkm64DZWN5wRtU7LEtD2ShkQ6", "name": "RED"},
    {"address": "4vw54BmAogeRV3vPKWyFet5yf8DTLcREzdSzx4rw9Ud9", "name": "decu"},
    {"address": "581XaxPQ7jGqqFGh3RQhK8wESBrEvFCAry7EDq2NzacH", "name": "Unnamed33"},
    {"address": "JDd3hy3gQn2V982mi1zqhNqUw1GfV2UL6g76STojCJPN", "name": "WEST"},
    {"address": "AJ6MGExeK7FXmeKkKPmALjcdXVStXYokYNv9uVfDRtvo", "name": "Tim"},
    {"address": "CyaE1VxvBrahnPWkqm5VsdCvyS2QmNht2UFrKJHga54o", "name": "Cented"},
    {"address": "GM7Hrz2bDq33ezMtL6KGidSWZXMWgZ6qBuugkb5H8NvN", "name": "Beaver"},
    {"address": "3pZ59YENxDAcjaKa3sahZJBcgER4rGYi4v6BpPurmsGj", "name": "Kadenox"},
    {"address": "Ehqd8q5rAN8V7Y7EGxYm3Tp4KPQMTVWQtzjSSPP3Upg3", "name": "collectible"},
    {"address": "9FNz4MjPUmnJqTf6yEDbL1D4SsHVh7uA8zRHhR5K138r", "name": "danny"},
    {"address": "9yYya3F5EJoLnBNKW6z4bZvyQytMXzDcpU5D6yYr4jqL", "name": "Loopier"},
    {"address": "7iabBMwmSvS4CFPcjW2XYZY53bUCHzXjCFEFhxeYP4CY", "name": "Leens"},
    {"address": "DNfuF1L62WWyW3pNakVkyGGFzVVhj4Yr52jSmdTyeBHm", "name": "GAKE"},
    {"address": "As7HjL7dzzvbRbaD3WCun47robib2kmAKRXMvjHkSMB5", "name": "otta"},
    {"address": "3nvC8cSrEBqFEXZjUpKfwZMPk7xYdqcnoxmFBjXiizVX", "name": "value & time"},
    {"address": "6LChaYRYtEYjLEHhzo4HdEmgNwu2aia8CM8VhR9wn6n7", "name": "Assasin.eth"},
    {"address": "HAN61KQbgzjDBC4RpZJ1ET8v32S4zdKAjoD7EApJ96q6", "name": "Pain"},
    {"address": "5t9xBNuDdGTGpjaPTx6hKd7sdRJbvtKS8Mhq6qVbo8Qz", "name": "smokez"},
    {"address": "BtMBMPkoNbnLF9Xn552guQq528KKXcsNBNNBre3oaQtr", "name": "letterbomb"},
    {"address": "GrD2umbfEBjQKFPDQvmmYNQ5eyRL9SAdWJj9FFMyeaDN", "name": "solstice"},
    {"address": "4cXnf2z85UiZ5cyKsPMEULq1yufAtpkatmX4j4DBZqj2", "name": "WaiterG"},
    {"address": "385NmPu9ETQgqZKT8zRNb786x4B5VPicooWd1Czq5Vby", "name": "Unnamed34"},
    {"address": "86AEJExyjeNNgcp7GrAvCXTDicf5aGWgoERbXFiG1EdD", "name": "𝕻𝖚𝖇𝖑𝖎𝖝"},
    {"address": "3wi8waD5A64D7PLutUYJdhMcrYvDBTqeh3CRFgv1hFtY", "name": "Unnamed35"},
    {"address": "73LnJ7G9ffBDjEBGgJDdgvLUhD5APLonKrNiHsKDCw5B", "name": "-$Waddles"},
    {"address": "71CPXu3TvH3iUKaY1bNkAAow24k6tjH473SsKprQBABC", "name": "发誓要做💎手的王小二"},
    {"address": "HLv6yCEpgjQV9PcKsvJpem8ESyULTyh9HjHn9CtqSek1", "name": "Lyxe"},
    {"address": "8MaVa9kdt3NW4Q5HyNAm1X5LbR8PQRVDc1W8NMVK88D5", "name": "Unnamed36"},
    {"address": "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj", "name": "Euris"},
    {"address": "7VBTpiiEjkwRbRGHJFUz6o5fWuhPFtAmy8JGhNqwHNnn", "name": "HOLDER700K"},
    {"address": "8deJ9xeUvXSJwicYptA9mHsU2rN2pDx37KWzkDkEXhU6", "name": "cooker"},
    {"address": "2byqB8Pypvq6s8W126yJc9SxToTiWTfNFuDU3ZTq9CLT", "name": "Trench"},
    {"address": "72e6QM7gn9MH5u1YpgQbduexm4WAon1cnsSXPqKnLQec", "name": "Unnamed37"},
    {"address": "8fSnLTnRViK83dDesivTsPx2wiRhwti9xoafeMGjEyLJ", "name": "goodtrader4(500kpnl)"},
    {"address": "HtucFepgUkMpHdrYsxMqjBNN6qVBdjmFaLZneNXopuJm", "name": "Unnamed38"},
    {"address": "HUpPyLU8KWisCAr3mzWy2FKT6uuxQ2qGgJQxyTpDoes5", "name": "0xSun"},
    {"address": "4XMPyWFsYdNcCN4FG8geyytyTeUNacn4QundBzMqbGGT", "name": "@Stxticcss"},
    {"address": "8rvAsDKeAcEjEkiZMug9k8v1y8mW6gQQiMobd89Uy7qR", "name": "Casino"},
    {"address": "8RTDA7rQadKhCGyWdzxqhD5pm3mXg9MjmAGxn8BZ1S6C", "name": "Unnamed39"},
    {"address": "7Bffdhza5V7zBK7EyEQ5eFQ4fkxvutjMsiJjJUs9ZfkC", "name": "Unnamed40"},
    {"address": "8zFZHuSRuDpuAR7J6FzwyF3vKNx4CVW3DFHJerQhc7Zd", "name": "Unnamed41"},
    {"address": "3dNTS4e2pwtQsTLgdKNm3p6vVijAfM6c57EajDY4zrpt", "name": "Unnamed42"},
    {"address": "4Be9CvxqHW6BYiRAxW9Q3xu1ycTMWaL5z8NX4HR3ha7t", "name": "Mitch"},
    {"address": "4SbDMrX8Zfj7qZtRKTBSQEavPkc7BP1kiJfT2f3dn8RL", "name": "Jake"},
    {"address": "Hkp22XxZ8xwk93eoYrhduTRkp5aaG4tvfhsqhbADfinS", "name": "Baller"},
    {"address": "6m5sW6EAPAHncxnzapi1ZVJNRb9RZHQ3Bj7FD84X9rAF", "name": "ShockedJS"},
    {"address": "BTf4A2exGK9BCVDNzy65b9dUzXgMqB4weVkvTMFQsadd", "name": "KEV"},
    {"address": "4DdrfiDHpmx55i4SPssxVzS9ZaKLb8qr45NKY9Er9nNh", "name": "Mr Frog"},
    {"address": "Gv7CnRo2L2SJ583XEfoKHKbmWK3wNoBDxVoJqMKJR4Nu", "name": "Robo"},
    {"address": "G3g1CKqKWSVEVURZDNMazDBv7YAhMNTjhJBVRTiKZygk", "name": "insyder"},
    {"address": "719sfKUjiMThumTt2u39VMGn612BZyCcwbM5Pe8SqFYz", "name": "Fashr"},
    {"address": "4Bdn33fA7LLZQuuXuFLSxtPWGAUnMBcreQHfh9MXuixe", "name": "key"},
    {"address": "831qmkeGhfL8YpcXuhrug6nHj1YdK3aXMDQUCo85Auh1", "name": "meechie"},
    {"address": "HrCPnDvDgbpbFxKxer6Pw3qEcfAQQNNjb6aJNFWgTEng", "name": "winged"},
    {"address": "9jyqFiLnruggwNn4EQwBNFXwpbLM9hrA4hV59ytyAVVz", "name": "nach"},
    {"address": "HA1L7GhQfypSRdfBi3tCkkCVEdEcBVYqBSQCENCrwPuB", "name": "HAIL"},
    {"address": "BHREKFkPQgAtDs8Vb1UfLkUpjG6ScidTjHaCWFuG2AtX", "name": "Risk"},
    {"address": "3ZtwP8peTwTfLUF1rgUQgUxwyeHCxfmoELXghQzKqnAJ", "name": "cxltures"},
    {"address": "7SDs3PjT2mswKQ7Zo4FTucn9gJdtuW4jaacPA65BseHS", "name": "Insentos"},
    {"address": "34ZEH778zL8ctkLwxxERLX5ZnUu6MuFyX9CWrs8kucMw", "name": "groovy"},
    {"address": "DZAa55HwXgv5hStwaTEJGXZz1DhHejvpb7Yr762urXam", "name": "ozark"},
    {"address": "5B79fMkcFeRTiwm7ehsZsFiKsC7m7n1Bgv9yLxPp9q2X", "name": "Bandit"},
    {"address": "xXpRSpAe1ajq4tJP78tS3X1AqNwJVQ4Vvb1Swg4hHQh", "name": "aloh"},
    {"address": "J6p2MS1gjygk9Hod8vKUEfcuWqMwfAwqFJyJX7UC8p6b", "name": "dean bulla"},
    {"address": "UxuuMeyX2pZPHmGZ2w3Q8MysvExCAquMtvEfqp2etvm", "name": "Pandora"},
    {"address": "J23qr98GjGJJqKq9CBEnyRhHbmkaVxtTJNNxKu597wsA", "name": "gr3g"},
    {"address": "Di75xbVUg3u1qcmZci3NcZ8rjFMj7tsnYEoFdEMjS4ow", "name": "N'o"},
    {"address": "3BLjRcxWGtR7WRshJ3hL25U3RjWr5Ud98wMcczQqk4Ei", "name": "sebastian"},
    {"address": "EKDDjxzJ39Bjkr47NiARGJDKFVxiiV9WNJ5XbtEhPEXP", "name": "Youniz"},
    {"address": "DYAn4XpAkN5mhiXkRB7dGq4Jadnx6XYgu8L5b3WGhbrt", "name": "the doc"},
    {"address": "2m8Mc2ngJCmpbEEoYhwT9U929z6C4CPKLatWnR775u9a", "name": "boogie"},
    {"address": "9BkauJdFYUyBkNBZwV4mNNyfeVKhHvjULb7cL4gFQaLt", "name": "goob"},
    {"address": "EgnY4zmqXuaqodCLW366jjd2ecki6pvmMF74MkSxMFQW", "name": "eric cryptoman"},
    {"address": "EgzjRCbcdRiPc1bW52tcvGDnKDbQWCzQbUhDBszD2BZm", "name": "rev"},
    {"address": "2T5NgDDidkvhJQg8AHDi74uCFwgp25pYFMRZXBaCUNBH", "name": "idontpaytaxes"},
    {"address": "4dfJdwntJqhArbBPudMMSzgt1MbKY7aNKsnF5KCkWaCo", "name": "iv"},
    {"address": "BkLsbxUeUEP3Yytdt2m84BzSKMnex9qn5HtERmYWqv8Q", "name": "Aroa"},
    {"address": "525LueqAyZJueCoiisfWy6nyh4MTvmF4X9jSqi6efXJT", "name": "Joji"},
    {"address": "EsCk2ewGL1tEnL3zzai7ZUbBjDyYDxYoumVcCYKf6no3", "name": "Rudhi"},
    {"address": "DwtF6KdjB9xgzKhCvcxKQLGU1NezdFFdVo8tLzSb7C8W", "name": "PowAlt2"},
    {"address": "65paNEG8m7mCVoASVF2KbRdU21aKXdASSB9G3NjCSQuE", "name": "Pullup"},
    {"address": "Ci8HDz2LgqVeWiEasyb12EkUUcXum3CQbPLwExDBJiLu", "name": "Profitier"},
    {"address": "J6TDXvarvpBdPXTaTU8eJbtso1PUCYKGkVtMKUUY8iEa", "name": "Pain"},
    {"address": "G6fUXjMKPJzCY1rveAE6Qm7wy5U3vZgKDJmN1VPAdiZC", "name": "clukz"},
    {"address": "AeLaMjzxErZt4drbWVWvcxpVyo8p94xu5vrg41eZPFe3", "name": "simple"},
    {"address": "FAicXNV5FVqtfbpn4Zccs71XcfGeyxBSGbqLDyDJZjke", "name": "raydiance"},
]

def main():
    print("🚀 FULL CONFIGURATION - ALL TRACKERS")
    print("=" * 70)
    print()
    print("Loading ALL 481 CT monitors + ALL 154 whale wallets...")
    print()

    config = AuraLiveConfig()

    # Add ALL 481 CT monitors
    print("📱 Adding ALL 481 CT Monitors...")
    ct_added = 0
    for handle in ct_handles:
        # Determine importance based on handle
        importance = 10 if handle in ["ansem", "elonmusk", "binance", "cz_binance"] else \
                     9 if handle in ["cobie", "saylor", "vitalikbuterin", "pumpdotfun", "solana", "blknoiz06"] else \
                     8 if handle in ["coinbase", "jupiterexchange", "raydiumprotocol", "magiceden"] else 7

        category = "alpha_caller" if importance >= 9 else "general"

        if config.add_ct_monitor(handle, category, importance):
            ct_added += 1
            if ct_added % 50 == 0:
                print(f"  Progress: {ct_added}/481 CT monitors added...")

    print(f"✅ Successfully added {ct_added}/481 CT monitors")
    print()

    # Add ALL 154 whale wallets
    print("🐋 Adding ALL 154 Whale Wallets...")
    whale_added = 0
    for whale in whale_wallets:
        # Determine min transaction value based on name
        min_tx = 20000 if "ANSEM" in whale["name"] or "Super" in whale["name"] else \
                 15000 if whale["name"] in ["clukz", "simple", "raydiance", "Henn100x"] else 10000

        if config.add_whale_wallet(whale["address"], whale["name"], min_tx):
            whale_added += 1
            if whale_added % 20 == 0:
                print(f"  Progress: {whale_added}/154 wallets added...")

    print(f"✅ Successfully added {whale_added}/154 whale wallets")
    print()

    # Show final summary
    summary = config.get_configuration_summary()
    print("=" * 70)
    print("📊 FINAL CONFIGURATION SUMMARY:")
    print(f"  Total CT Monitors: {summary['ct_monitors']['total']}")
    print(f"  Total Whale Wallets: {summary['whale_wallets']['total']}")
    print()
    print("🎉 AURA Live Tracking System is FULLY CONFIGURED!")
    print()
    print("Top CT Monitors (by importance):")
    for m in sorted(summary['ct_monitors']['monitors'], key=lambda x: x['importance'], reverse=True)[:10]:
        print(f"  @{m['handle']:<20} | {m['category']:<15} | {m['importance']}/10")
    print()
    print("Sample Whale Wallets:")
    for w in summary['whale_wallets']['wallets'][:10]:
        print(f"  {w['nickname']:<25} | {w['address'][:8]}...")

if __name__ == "__main__":
    main()
