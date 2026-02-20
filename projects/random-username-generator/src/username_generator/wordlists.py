# =============================================================================
# wordlists.py — Word Banks for Username Generation
# =============================================================================
# Curated word lists designed to produce fun, memorable, SFW usernames.
#
# Design decisions:
#   - All words are lowercase (casing applied by the generator)
#   - No offensive, controversial, or ambiguous words
#   - Biased toward vivid, concrete, fun words (not "nice" or "thing")
#   - Sized for good variety without bloat (~100-150 per list)
#   - Tuples (immutable) instead of lists — these never change at runtime
# =============================================================================

# Descriptive words that pair well with nouns — skewed toward
# personality traits, physical qualities, and vibe words
ADJECTIVES: tuple[str, ...] = (
    "acoustic", "ancient", "aquatic", "arctic", "astral",
    "blazing", "bold", "bouncy", "brave", "breezy",
    "calm", "celestial", "chaotic", "cheeky", "clever",
    "cobalt", "comet", "copper", "cosmic", "cozy",
    "crimson", "crystal", "curious", "cyber", "daring",
    "dazzling", "deep", "digital", "dizzy", "dreamy",
    "drifting", "dusty", "dynamic", "eager", "electric",
    "emerald", "epic", "eternal", "fancy", "fearless",
    "fierce", "fizzy", "fluffy", "flying", "foggy",
    "frozen", "funky", "fuzzy", "galactic", "gentle",
    "ghostly", "giant", "glacial", "glowing", "golden",
    "grand", "groovy", "hasty", "hidden", "hollow",
    "humble", "hushed", "icy", "idle", "infinite",
    "iron", "jade", "jazzy", "jolly", "keen",
    "kinetic", "laser", "lazy", "liquid", "little",
    "lone", "lost", "lucky", "lunar", "magic",
    "maple", "mellow", "mighty", "misty", "molten",
    "neon", "nimble", "noble", "nova", "obsidian",
    "olive", "ombre", "orbital", "outer", "pale",
    "phantom", "pixel", "plasma", "polar", "prism",
    "proud", "quantum", "quick", "quiet", "radical",
    "rapid", "rebel", "rogue", "royal", "ruby",
    "rugged", "rustic", "salty", "savage", "scarlet",
    "secret", "shadow", "sharp", "shiny", "silent",
    "silver", "sleek", "sneaky", "snowy", "solar",
    "sonic", "spicy", "steel", "stellar", "stormy",
    "subtle", "super", "swift", "tidal", "tiny",
    "toasty", "topaz", "toxic", "turbo", "twilight",
    "ultra", "velvet", "vivid", "void", "wandering",
    "wicked", "wild", "winter", "wired", "witty",
    "zen", "zippy", "zonal",
)

# Concrete nouns — animals, objects, nature, space, food, tech
# Reddit-style usernames work best with nouns that are easy to visualize
NOUNS: tuple[str, ...] = (
    "alpaca", "anchor", "anvil", "aurora", "avalanche",
    "badger", "bandit", "beacon", "bear", "bison",
    "blizzard", "bolt", "breeze", "buffalo", "cactus",
    "canyon", "captain", "caribou", "cascade", "castle",
    "cheetah", "cipher", "cliff", "cobra", "comet",
    "condor", "coral", "coyote", "crane", "crater",
    "crow", "crystal", "current", "dagger", "dawn",
    "dolphin", "dragon", "drift", "eagle", "eclipse",
    "ember", "falcon", "fern", "firefly", "flame",
    "flare", "fox", "frost", "galaxy", "gargoyle",
    "gazelle", "glacier", "glitch", "gorilla", "griffin",
    "hawk", "horizon", "husky", "hydra", "iceberg",
    "igloo", "jaguar", "jelly", "kestrel", "kite",
    "knight", "kraken", "lagoon", "lancer", "lemur",
    "leopard", "lightning", "lion", "llama", "lynx",
    "mammoth", "mantis", "maple", "marlin", "maverick",
    "meteor", "moose", "moth", "mustang", "nebula",
    "ninja", "nomad", "nova", "obsidian", "octopus",
    "onyx", "orca", "osprey", "otter", "owl",
    "panther", "parrot", "pegasus", "penguin", "phoenix",
    "pilot", "pine", "pirate", "pixel", "planet",
    "porcupine", "prism", "puffin", "puma", "python",
    "quartz", "raven", "reef", "rhino", "ridge",
    "rocket", "sage", "salmon", "samurai", "sapphire",
    "scorpion", "serpent", "shark", "sparrow", "sphinx",
    "squid", "stag", "starling", "summit", "thunder",
    "tiger", "titan", "tornado", "toucan", "trident",
    "turtle", "typhoon", "viper", "volcano", "voyager",
    "walrus", "wasp", "whale", "wizard", "wolf",
    "wolverine", "wombat", "wren", "yak", "yeti",
    "zebra", "zenith", "zephyr",
)

# Action verbs for "NounVerber" patterns (e.g., StarGazer, MoonWalker)
# Stored as present tense — the "er" suffix is added by the generator
VERBS: tuple[str, ...] = (
    "bind", "blaze", "break", "build", "burn",
    "carve", "cast", "catch", "chase", "climb",
    "craft", "crash", "cross", "crush", "dance",
    "dash", "dive", "dodge", "dream", "drift",
    "drop", "fade", "find", "fling", "float",
    "forge", "gaze", "glide", "grind", "guard",
    "hack", "haunt", "howl", "hunt", "jump",
    "keep", "launch", "leap", "lurk", "march",
    "mine", "morph", "push", "race", "raid",
    "ride", "roam", "run", "rush", "sail",
    "seek", "shade", "shape", "shift", "shred",
    "sing", "sink", "skip", "slash", "slide",
    "sling", "smash", "snap", "spark", "spin",
    "sprint", "stalk", "stomp", "storm", "strike",
    "surf", "surge", "sweep", "swing", "tame",
    "trace", "track", "trap", "trek", "vault",
    "walk", "wander", "warp", "watch", "weave",
    "whirl", "wield", "zap",
)
