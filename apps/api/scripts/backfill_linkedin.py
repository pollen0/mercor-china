"""
Backfill LinkedIn URLs for founders in seeded companies.

Updates the `settings.founders` JSONB on Organization records.
Run: cd apps/api && python -m scripts.backfill_linkedin
"""
import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

# Mapping: company_name -> {founder_name: linkedin_url}
# These are publicly available LinkedIn profile URLs.
FOUNDER_LINKEDIN = {
    # === seed_a16z_jobs.py ===
    "Whatnot": {
        "Grant LaFontaine": "https://linkedin.com/in/grantlafontaine",
        "Logan Head": "https://linkedin.com/in/logan-head",
    },
    "Ramp": {
        "Eric Glyman": "https://linkedin.com/in/eglyman",
        "Karim Atiyeh": "https://linkedin.com/in/karimatiyeh",
    },
    "Glean": {
        "Arvind Jain": "https://linkedin.com/in/arvindjain1",
        "Tony Gentilcore": "https://linkedin.com/in/tonygentilcore",
    },
    "Anduril Industries": {
        "Palmer Luckey": "https://linkedin.com/in/palmer-luckey-a5a75943",
        "Brian Schimpf": "https://linkedin.com/in/brian-schimpf",
        "Trae Stephens": "https://linkedin.com/in/traestephens",
    },
    "Benchling": {
        "Sajith Wickramasekara": "https://linkedin.com/in/sajithw",
        "Ashu Singhal": "https://linkedin.com/in/ashu-singhal",
    },
    "Figma": {
        "Dylan Field": "https://linkedin.com/in/dylanfield",
        "Evan Wallace": "https://linkedin.com/in/evanwallace",
    },
    "Vercel": {
        "Guillermo Rauch": "https://linkedin.com/in/guillermo-rauch-b834b917b",
    },
    "Flock Safety": {
        "Garrett Langley": "https://linkedin.com/in/garrettlangley",
        "Matt Feury": "https://linkedin.com/in/mattfeury",
    },
    "Replit": {
        "Amjad Masad": "https://linkedin.com/in/amjadmasad",
        "Haya Odeh": "https://linkedin.com/in/hayaodeh",
    },
    "Northwood Space": {
        "Bridgit Mendler": "https://linkedin.com/in/bridgitmendler",
        "Shaurya Luthra": "https://linkedin.com/in/shauryaluthra",
    },
    "Astranis": {
        "John Gedmark": "https://linkedin.com/in/johngedmark",
        "Ryan McLinko": "https://linkedin.com/in/ryanmclinko",
    },
    "Neuralink": {
        "Elon Musk": "https://linkedin.com/in/elonrmusk",
    },
    "Genesis Therapeutics": {
        "Evan Feinberg": "https://linkedin.com/in/evanfeinberg",
        "Ben Sklaroff": "https://linkedin.com/in/bensklaroff",
    },
    "Lightspark": {
        "David Marcus": "https://linkedin.com/in/davidmarcus",
    },
    "Radiant Nuclear": {
        "Doug Bernauer": "https://linkedin.com/in/dougbernauer",
        "Bob Urberger": "https://linkedin.com/in/boburberger",
    },
    "Zipline": {
        "Keller Rinaudo Cliffton": "https://linkedin.com/in/kellerrinaudo",
        "Jeremy Baker": "https://linkedin.com/in/jeremybaker11",
        "Keenan Wyrobek": "https://linkedin.com/in/keenanwyrobek",
    },
    "Vanta": {
        "Christina Cacioppo": "https://linkedin.com/in/ccacioppo",
        "Matt Spitz": "https://linkedin.com/in/mattspitz",
    },

    # === seed_a16z_batch2_jobs.py ===
    "Tanium": {
        "Orion Hindawi": "https://linkedin.com/in/orionhindawi",
    },
    "Snyk": {
        "Guy Podjarny": "https://linkedin.com/in/guypod",
        "Danny Grander": "https://linkedin.com/in/dannygrander",
    },
    "Substack": {
        "Chris Best": "https://linkedin.com/in/hamish",
        "Jairaj Sethi": "https://linkedin.com/in/jairajsethi",
    },

    # === seed_accel_jobs.py ===
    "Dropbox": {
        "Drew Houston": "https://linkedin.com/in/drewhouston",
    },
    "CrowdStrike": {
        "George Kurtz": "https://linkedin.com/in/georgekurtz",
    },
    "DocuSign": {
        "Tom Gonser": "https://linkedin.com/in/tomgonser",
    },
    "Qualtrics": {
        "Ryan Smith": "https://linkedin.com/in/ryanqsmith",
        "Jared Smith": "https://linkedin.com/in/jaredsmith",
    },

    # === seed_bessemer_jobs.py ===
    "Bevi": {
        "Sean Grundy": "https://linkedin.com/in/seangrundy",
        "Eliza Becton": "https://linkedin.com/in/elizabecton",
        "Frank Lee": "https://linkedin.com/in/frankleepe",
    },

    # === seed_contrary_jobs.py ===
    "Armada": {
        "Dan Wright": "https://linkedin.com/in/danwright6",
    },
    "Leland": {
        "John Koelliker": "https://linkedin.com/in/johnkoelliker",
        "Zando Ward": "https://linkedin.com/in/zandoward",
    },
    "AtoB": {
        "Vignan Velivela": "https://linkedin.com/in/vignan",
        "Harshita Arora": "https://linkedin.com/in/harshitaarora",
    },
    "Hallow": {
        "Alex Jones": "https://linkedin.com/in/alexjoneshallow",
        "Erich Kerekes": "https://linkedin.com/in/erichkerekes",
        "Alessandro DiSanto": "https://linkedin.com/in/alessandrodisanto",
    },

    # === seed_dragoneer_jobs.py ===
    "Discord": {
        "Jason Citron": "https://linkedin.com/in/jasoncitron",
    },
    "Chime": {
        "Chris Britt": "https://linkedin.com/in/chrisbritt",
    },
    "Samsara": {
        "Sanjit Biswas": "https://linkedin.com/in/sanjitbiswas",
    },
    "Snowflake": {
        "Benoit Dageville": "https://linkedin.com/in/benoitdageville",
    },
    "Strava": {
        "Michael Horvath": "https://linkedin.com/in/michael-horvath-3b83094",
    },
    "Wealthfront": {
        "Andy Rachleff": "https://linkedin.com/in/rachleff",
    },
    "AppFolio": {
        "Klaus Schauser": "https://linkedin.com/in/klausschauser",
        "Jon Walker": "https://linkedin.com/in/jonwalker1",
    },
    "Instacart": {
        "Apoorva Mehta": "https://linkedin.com/in/apoorvamehta",
    },

    # === seed_khosla_jobs.py ===
    "Okta": {
        "Todd McKinnon": "https://linkedin.com/in/toddmckinnon",
        "Frederic Kerrest": "https://linkedin.com/in/frederickerrest",
    },
    "Arista Networks": {
        "Andy Bechtolsheim": "https://linkedin.com/in/andybechtolsheim",
        "David Cheriton": "https://linkedin.com/in/david-cheriton-860b7712",
        "Ken Duda": "https://linkedin.com/in/kenduda",
    },
    "BambooHR": {
        "Ben Peterson": "https://linkedin.com/in/benpeterson",
    },
    "Zendar": {
        "Vinayak Nagpal": "https://linkedin.com/in/vinayaknagpal",
        "Jimmy Wang": "https://linkedin.com/in/jinweiwang",
    },
    "Upstart": {
        "Dave Girouard": "https://linkedin.com/in/davegirouard",
    },
    "World": {
        "Alex Blania": "https://linkedin.com/in/alexblania",
        "Sam Altman": "https://linkedin.com/in/samaltman",
    },
    "Square": {
        "Jack Dorsey": "https://linkedin.com/in/jackdorsey1",
    },
    "Glydways": {
        "Mark Seeger": "https://linkedin.com/in/markseeger",
        "Gokul Hemmady": "https://linkedin.com/in/gokulhemmady",
    },

    # === seed_legend_jobs.py ===
    "Pony.ai": {
        "James Peng": "https://linkedin.com/in/jamespeng",
        "Tiancheng Lou": "https://linkedin.com/in/tianchenglou",
    },

    # === seed_lightspeed_jobs.py ===
    "Snap Inc.": {
        "Evan Spiegel": "https://linkedin.com/in/evanspiegel",
    },
    "Databricks": {
        "Ali Ghodsi": "https://linkedin.com/in/alighodsi",
        "Ion Stoica": "https://linkedin.com/in/ionstoica",
        "Matei Zaharia": "https://linkedin.com/in/mateizaharia",
    },
    "Rippling": {
        "Parker Conrad": "https://linkedin.com/in/parkerconrad",
    },
    "Nominal": {
        "Cameron McCord": "https://linkedin.com/in/cameronmccord",
        "Bryce Strauss": "https://linkedin.com/in/brycestrauss",
        "Jason Hoch": "https://linkedin.com/in/jasonhoch",
    },
    "Epic Games": {
        "Tim Sweeney": "https://linkedin.com/in/timsweeney",
    },
    "Nutanix": {
        "Dheeraj Pandey": "https://linkedin.com/in/dheerajpandey",
        "Mohit Aron": "https://linkedin.com/in/mohitaron",
        "Ajeet Singh": "https://linkedin.com/in/ajeetsingh1",
    },
    "Guardant Health": {
        "Helmy Eltoukhy": "https://linkedin.com/in/helmy-eltoukhy-8a48604",
        "AmirAli Talasaz": "https://linkedin.com/in/amirali-talasaz-4476652",
    },
    "CertiK": {
        "Ronghui Gu": "https://linkedin.com/in/ronghuigu",
    },
    "Kodiak Robotics": {
        "Don Burnette": "https://linkedin.com/in/donburnette",
    },

    # === seed_nea_jobs.py ===
    "Plaid": {
        "Zach Perret": "https://linkedin.com/in/zachperret",
    },
    "Robinhood": {
        "Vlad Tenev": "https://linkedin.com/in/vladtenev",
    },
    "MongoDB": {
        "Dwight Merriman": "https://linkedin.com/in/dmerriman",
        "Eliot Horowitz": "https://linkedin.com/in/eliothorowitz",
        "Kevin P. Ryan": "https://linkedin.com/in/kevinryan",
    },
    "Coursera": {
        "Andrew Ng": "https://linkedin.com/in/andrewyng",
    },
    "Patreon": {
        "Jack Conte": "https://linkedin.com/in/jackconte",
    },
    "Virtru": {
        "John Ackerly": "https://linkedin.com/in/johnackerly",
    },
    "Together AI": {
        "Vipul Ved Prakash": "https://linkedin.com/in/vipulvedprakash",
    },
    "Fizz": {
        "Teddy Solomon": "https://linkedin.com/in/teddy-solomon",
        "Ashton Cofer": "https://linkedin.com/in/ashtoncofer",
    },

    # === seed_pearvc_jobs.py ===
    "Addepar": {
        "Joe Lonsdale": "https://linkedin.com/in/joelonsdale",
        "Eric Poirier": "https://linkedin.com/in/ericpoirier",
    },
    "WindBorne Systems": {
        "John Dean": "https://linkedin.com/in/johndeanwb",
        "Kai Marshland": "https://linkedin.com/in/kaimarshland",
    },
    "Conduit Tech": {
        "Shelby Breger": "https://linkedin.com/in/shelbybreger",
        "Marisa Reddy": "https://linkedin.com/in/marisareddy",
    },
    "Affinity": {
        "Ray Zhou": "https://linkedin.com/in/rayzhou",
        "Shubham Goel": "https://linkedin.com/in/shubhamgoel",
    },

    # === seed_precursor_jobs.py ===
    "Juniper Square": {
        "Alex Robinson": "https://linkedin.com/in/alexrobinson",
        "Adam Ginsburg": "https://linkedin.com/in/agins",
        "Yonas Fisseha": "https://linkedin.com/in/yonasfisseha",
    },

    # === seed_sequoia_jobs.py ===
    "Harvey": {
        "Winston Weinberg": "https://linkedin.com/in/winstonweinberg",
    },
    "Clay": {
        "Kareem Amin": "https://linkedin.com/in/kareemamin",
    },
    "Notion": {
        "Ivan Zhao": "https://linkedin.com/in/ivanzhao",
    },
    "Zip": {
        "Rujul Zaparde": "https://linkedin.com/in/rujulzaparde",
        "Lu Cheng": "https://linkedin.com/in/lucheng",
    },
    "Stripe": {
        "Patrick Collison": "https://linkedin.com/in/patrickcollison",
    },
    "Semgrep": {
        "Isaac Evans": "https://linkedin.com/in/isaacevans",
        "Luke O'Malley": "https://linkedin.com/in/lukeomalley",
    },
    "Mercury": {
        "Immad Akhund": "https://linkedin.com/in/immadakhund",
        "Jason Zhang": "https://linkedin.com/in/jasonzhang1",
    },
    "Verkada": {
        "Filip Kaliszan": "https://linkedin.com/in/filipkaliszan",
        "Benjamin Bercovitz": "https://linkedin.com/in/benbercovitz",
    },
    "The Boring Company": {
        "Elon Musk": "https://linkedin.com/in/elonrmusk",
        "Steve Davis": "https://linkedin.com/in/stevedavis",
    },
    "Vise": {
        "Samir Vasavada": "https://linkedin.com/in/samirvasavada",
    },
    "DoorDash": {
        "Tony Xu": "https://linkedin.com/in/xutony",
        "Stanley Tang": "https://linkedin.com/in/stanleytang",
        "Andy Fang": "https://linkedin.com/in/andyfang",
    },
    "Brex": {
        "Pedro Franceschi": "https://linkedin.com/in/pedrofranceschi",
        "Henrique Dubugras": "https://linkedin.com/in/hdubugras",
    },

    # === seed_tcv_jobs.py ===
    "Spotify": {
        "Daniel Ek": "https://linkedin.com/in/danielek",
    },
    "CCC Intelligent Solutions": {
        "Githesh Ramamurthy": "https://linkedin.com/in/githeshramamurthy",
    },
    "Hinge Health": {
        "Daniel Perez": "https://linkedin.com/in/danielperez",
        "Gabriel Mecklenburg": "https://linkedin.com/in/gabrielmecklenburg",
    },
    "Attentive": {
        "Brian Long": "https://linkedin.com/in/brianlong",
        "Andrew Jones": "https://linkedin.com/in/andrewjones",
    },
    "OneTrust": {
        "Kabir Barday": "https://linkedin.com/in/kabirbarday",
    },

    # === seed_tigerglobal_jobs.py ===
    "Toast": {
        "Aman Narang": "https://linkedin.com/in/amannarang",
        "Steve Fredette": "https://linkedin.com/in/stevefredette",
        "Jonathan Grimm": "https://linkedin.com/in/jonathangrimm",
    },
    "Confluent": {
        "Jay Kreps": "https://linkedin.com/in/jaykreps",
        "Jun Rao": "https://linkedin.com/in/junrao",
    },
    "GitLab": {
        "Sid Sijbrandij": "https://linkedin.com/in/sijbrandij",
        "Dmitriy Zaporozhets": "https://linkedin.com/in/dzaporozhets",
    },

    # === seed_yc_batch2.py ===
    "Sonauto": {
        "Mikey Shulman": "https://linkedin.com/in/mikeyshulman",
        "Ryan Tremblay": "https://linkedin.com/in/ryantremblay",
    },
    "Cloudglue": {
        "Amy": "",
        "Kevin": "",
        "Matt": "",
    },
    "Ember": {
        "Charlene Wang": "https://linkedin.com/in/charlenewang",
        "Warren Wang": "https://linkedin.com/in/warrenwang",
    },
    "Promptless": {
        "Frances": "",
        "Prithvi": "",
    },
    "Tandem": {
        "Sean Miller": "https://linkedin.com/in/seanmiller",
        "Rafi Sands": "https://linkedin.com/in/rafisands",
        "Brendan Suh": "https://linkedin.com/in/brendansuh",
    },
    "Bucket Robotics": {
        "Matt Puchalski": "https://linkedin.com/in/mattpuchalski",
    },
    "CreativeMode": {
        "Wilson Spearman": "https://linkedin.com/in/wilsonspearman",
        "Jeffrey": "",
    },

    # === seed_2048ventures_jobs.py ===
    "Laminar": {
        "Annie Lu": "https://linkedin.com/in/annielu",
    },

    # === Batch 2 backfill (web-searched 2026-02-13) ===
    "Aircall": {
        "Olivier Pailhes": "https://linkedin.com/in/olivier-pailhes-50a443",
        "Jonathan Anguelov": "https://linkedin.com/in/jonathan-anguelov-14346611",
        "Xavier Durand": "https://linkedin.com/in/xdurand",
        "Pierre-Baptiste Bechu": "https://linkedin.com/in/pbechu",
    },
    "Algolia": {
        "Nicolas Dessaigne": "https://linkedin.com/in/nicolasdessaigne",
        "Julien Lemoine": "https://linkedin.com/in/julienlemoine",
    },
    "Armada": {
        "Dan Wright": "https://linkedin.com/in/danwright6",
        "Jon Runyan": "https://linkedin.com/in/jon-runyan-3868a6",
    },
    "AtoB": {
        "Vignan Velivela": "https://linkedin.com/in/vignan",
        "Harshita Arora": "https://linkedin.com/in/harshitaarora",
        "Tushar Misra": "https://linkedin.com/in/tusharmisra",
    },
    "Chegg": {
        "Osman Rashid": "https://linkedin.com/in/osmanrashid",
        "Aayush Phumbhra": "https://linkedin.com/in/aayush",
    },
    "Chime": {
        "Chris Britt": "https://linkedin.com/in/chrisbritt",
        "Ryan King": "https://linkedin.com/in/ryanaking",
    },
    "Clay": {
        "Kareem Amin": "https://linkedin.com/in/kareemamin",
        "Nicolae Rusan": "https://linkedin.com/in/nicolaerusan",
    },
    "Confluent": {
        "Jay Kreps": "https://linkedin.com/in/jaykreps",
        "Jun Rao": "https://linkedin.com/in/junrao",
        "Neha Narkhede": "https://linkedin.com/in/nehanarkhede",
    },
    "Coursera": {
        "Andrew Ng": "https://linkedin.com/in/andrewyng",
        "Daphne Koller": "https://linkedin.com/in/daphne-koller-4053a820",
    },
    "Credit Karma": {
        "Kenneth Lin": "https://linkedin.com/in/kennethjlin",
    },
    "CrowdStrike": {
        "George Kurtz": "https://linkedin.com/in/georgekurtz",
        "Dmitri Alperovitch": "https://linkedin.com/in/dmitrialperovitch",
    },
    "Discord": {
        "Jason Citron": "https://linkedin.com/in/jasoncitron",
        "Stanislav Vishnevskiy": "https://linkedin.com/in/svishnevskiy",
    },
    "Dropbox": {
        "Drew Houston": "https://linkedin.com/in/drewhouston",
        "Arash Ferdowsi": "https://linkedin.com/in/arashferdowsi",
    },
    "Eudia": {
        "Omar Haroun": "https://linkedin.com/in/omarharoun",
    },
    "Harvey": {
        "Winston Weinberg": "https://linkedin.com/in/winstonweinberg",
        "Gabriel Pereyra": "https://linkedin.com/in/gabepereyra",
    },
    "Intercom": {
        "Des Traynor": "https://linkedin.com/in/destraynor",
        "Ciaran Lee": "https://linkedin.com/in/ciaran-lee-51bb402",
        "David Barrett": "https://linkedin.com/in/david-barrett-208845",
    },
    "LaunchDarkly": {
        "Edith Harbaugh": "https://linkedin.com/in/edithharbaugh",
        "John Kodumal": "https://linkedin.com/in/jkodumal",
    },
    "Leland": {
        "John Koelliker": "https://linkedin.com/in/johnkoelliker",
        "Zando Ward": "https://linkedin.com/in/zandoward",
        "Erika Mahterian": "https://linkedin.com/in/erikamahterian",
    },
    "Lucid Software": {
        "Karl Sun": "https://linkedin.com/in/karlsun",
        "Ben Dilts": "https://linkedin.com/in/bendilts",
    },
    "Mercury": {
        "Immad Akhund": "https://linkedin.com/in/immadakhund",
        "Jason Zhang": "https://linkedin.com/in/jasonzhang1",
        "Max Tagher": "https://linkedin.com/in/maximilian-tagher-641ba147",
    },
    "Nextdoor": {
        "Nirav Tolia": "https://linkedin.com/in/niravtolia",
        "Sarah Leary": "https://linkedin.com/in/sarahleary",
        "Prakash Janakiraman": "https://linkedin.com/in/pjanakiraman",
        "David Wiesen": "https://linkedin.com/in/davidwiesen",
    },
    "Northwood Space": {
        "Bridgit Mendler": "https://linkedin.com/in/bridgitmendler",
        "Shaurya Luthra": "https://linkedin.com/in/shauryaluthra",
        "Griffin Cleverly": "https://linkedin.com/in/griffincleverly",
    },
    "Notion": {
        "Ivan Zhao": "https://linkedin.com/in/ivanzhao",
        "Simon Last": "https://linkedin.com/in/simon-last-41404140",
    },
    "Patreon": {
        "Jack Conte": "https://linkedin.com/in/jackconte",
        "Sam Yam": "https://linkedin.com/in/samyam",
    },
    "Plaid": {
        "Zach Perret": "https://linkedin.com/in/zachperret",
        "William Hockey": "https://linkedin.com/in/william-hockey-04536710",
    },
    "Rippling": {
        "Parker Conrad": "https://linkedin.com/in/parkerconrad",
        "Prasanna Sankar": "https://linkedin.com/in/myprasanna",
    },
    "Robinhood": {
        "Vlad Tenev": "https://linkedin.com/in/vladtenev",
        "Baiju Bhatt": "https://linkedin.com/in/bprafulkumar",
    },
    "Semgrep": {
        "Isaac Evans": "https://linkedin.com/in/isaacevans",
        "Luke O'Malley": "https://linkedin.com/in/lukeomalley",
        "Drew Dennison": "https://linkedin.com/in/drewdennison",
    },
    "Snap Inc.": {
        "Evan Spiegel": "https://linkedin.com/in/evanspiegel",
        "Bobby Murphy": "https://linkedin.com/in/bobby-murphy-558927b4",
    },
    "Snowflake": {
        "Benoit Dageville": "https://linkedin.com/in/benoitdageville",
        "Thierry Cruanes": "https://linkedin.com/in/thierry-cruanes-3927363",
    },
    "Snyk": {
        "Guy Podjarny": "https://linkedin.com/in/guypod",
        "Danny Grander": "https://linkedin.com/in/dannygrander",
        "Assaf Hefetz": "https://linkedin.com/in/assaf-hefetz",
    },
    "Sonauto": {
        "Mikey Shulman": "https://linkedin.com/in/mikeyshulman",
        "Ryan Tremblay": "https://linkedin.com/in/ryantremblay",
        "Hayden Housen": "https://linkedin.com/in/hhousen",
    },
    "Spotify": {
        "Daniel Ek": "https://linkedin.com/in/danielek",
        "Martin Lorentzon": "https://linkedin.com/in/martin-lorentzon-40a37933",
    },
    "Strava": {
        "Michael Horvath": "https://linkedin.com/in/michael-horvath-3b83094",
        "Mark Gainey": "https://linkedin.com/in/mark-gainey-b6536",
    },
    "Substack": {
        "Chris Best": "https://linkedin.com/in/hamish",
        "Jairaj Sethi": "https://linkedin.com/in/jairajsethi",
        "Hamish McKenzie": "https://linkedin.com/in/hamishmckenzie",
    },
    "Tanium": {
        "Orion Hindawi": "https://linkedin.com/in/orionhindawi",
    },
    "The RealReal": {
        "Julie Wainwright": "https://linkedin.com/in/juliewainwright",
    },
    "Together AI": {
        "Vipul Ved Prakash": "https://linkedin.com/in/vipulvedprakash",
        "Ce Zhang": "https://linkedin.com/in/ce-zhang-6aa37419",
    },
    "Twilio": {
        "Jeff Lawson": "https://linkedin.com/in/jeffiel",
        "Evan Cooke": "https://linkedin.com/in/emcooke",
        "John Wolthuis": "https://linkedin.com/in/john-wolthuis-2493a61",
    },
    "Udemy": {
        "Eren Bali": "https://linkedin.com/in/erenbali",
        "Gagan Biyani": "https://linkedin.com/in/gaganbiyani",
        "Oktay Caglar": "https://linkedin.com/in/oktay-caglar-b8768414a",
    },
    "Upstart": {
        "Dave Girouard": "https://linkedin.com/in/davegirouard",
        "Paul Gu": "https://linkedin.com/in/gupaul",
    },
    "Verkada": {
        "Filip Kaliszan": "https://linkedin.com/in/filipkaliszan",
        "Benjamin Bercovitz": "https://linkedin.com/in/benbercovitz",
        "James Ren": "https://linkedin.com/in/james-ren-2607285",
    },
    "Virtru": {
        "John Ackerly": "https://linkedin.com/in/johnackerly",
        "Will Ackerly": "https://linkedin.com/in/wra",
    },
    "Vise": {
        "Samir Vasavada": "https://linkedin.com/in/samirvasavada",
        "Runik Mehrotra": "https://linkedin.com/in/runik-mehrotra",
    },
    "Wealthfront": {
        "Andy Rachleff": "https://linkedin.com/in/rachleff",
        "Dan Carroll": "https://linkedin.com/in/daniel-carroll-20a52b6",
    },
    "WindBorne Systems": {
        "John Dean": "https://linkedin.com/in/johndeanwb",
        "Kai Marshland": "https://linkedin.com/in/kaimarshland",
        "Andrew Sushko": "https://linkedin.com/in/andrey-sushko",
    },
}


def run_backfill():
    """Update LinkedIn URLs in Organization settings.founders JSONB."""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    updated_orgs = 0
    updated_founders = 0
    skipped = 0

    try:
        # Get all organizations with founders in settings
        result = db.execute(text(
            "SELECT id, name, slug, settings FROM organizations WHERE settings IS NOT NULL"
        ))
        rows = result.fetchall()

        for row in rows:
            org_id, org_name, org_slug, org_settings = row
            if not org_settings or not isinstance(org_settings, dict):
                continue

            founders = org_settings.get("founders", [])
            if not founders:
                continue

            # Check if any founder has an empty linkedin
            has_empty = any(
                isinstance(f, dict) and f.get("linkedin", "") == ""
                for f in founders
            )
            if not has_empty:
                continue

            # Try to match by org name
            linkedin_map = FOUNDER_LINKEDIN.get(org_name, {})
            if not linkedin_map:
                # Try partial matching
                for company_name, mapping in FOUNDER_LINKEDIN.items():
                    if company_name.lower() in org_name.lower() or org_name.lower() in company_name.lower():
                        linkedin_map = mapping
                        break

            if not linkedin_map:
                skipped += 1
                continue

            # Update founders
            changed = False
            for founder in founders:
                if not isinstance(founder, dict):
                    continue
                if founder.get("linkedin", "") != "":
                    continue  # Already has URL

                name = founder.get("name", "")
                linkedin_url = linkedin_map.get(name, "")
                if linkedin_url:
                    founder["linkedin"] = linkedin_url
                    updated_founders += 1
                    changed = True

            if changed:
                # Update the settings JSONB
                import json
                db.execute(
                    text("UPDATE organizations SET settings = :settings WHERE id = :id"),
                    {"settings": json.dumps(org_settings), "id": org_id}
                )
                updated_orgs += 1
                print(f"  Updated {org_name}: {sum(1 for f in founders if f.get('linkedin'))} founders with LinkedIn")

        db.commit()

        print(f"\n{'='*50}")
        print(f"Backfill complete:")
        print(f"  Organizations updated: {updated_orgs}")
        print(f"  Founders updated: {updated_founders}")
        print(f"  Organizations skipped (no mapping): {skipped}")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("LinkedIn URL Backfill Script")
    print("="*50)
    run_backfill()
