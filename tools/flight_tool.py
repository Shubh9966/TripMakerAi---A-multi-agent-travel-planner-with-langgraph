
# ============================================================
# 1. IMPORTS & ENVIRONMENT SETUP
# ============================================================

import os
# Environment variables read karne ke liye.
# Example: API keys ko .env file se read karna.

import re
# Regular Expressions (regex) ke liye.
# Text ke andar patterns search karne mein help karta hai.
# Example: "from Dhaka to Tokyo" mein locations identify karna.

import certifi
# Trusted SSL certificates provide karta hai.
# HTTPS requests ke SSL verification mein help karta hai.

import airportsdata
# Airport database provide karta hai.
# Isse airport ke IATA code, city aur country information mil sakti hai.

import pycountry
# Countries ki information aur country codes ke liye.
# Example: India -> IN, Japan -> JP.

import requests
# HTTP requests bhejne ke liye.
# AviationStack API ko call karne mein use hoga.

from dotenv import load_dotenv
# .env file ke environment variables load karne ke liye.


load_dotenv()
# .env file ke variables memory/environment mein load ho jayenge.
# Example:
# AVIATIONSTACK_API_KEY=your_api_key


os.environ["SSL_CERT_FILE"] = certifi.where()
# SSL certificate file ka path set kar rahe hain.
# certifi.where() trusted certificates ka location return karta hai.

os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
# Requests library ke liye CA certificate bundle ka path set kar rahe hain.
# Secure HTTPS connections ke liye useful.


# ============================================================
# 2. API KEY & DEFAULT SETTINGS
# ============================================================

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
# .env se AviationStack API key read kar rahe hain.
# API key API ko authenticate karne ke liye use hoti hai.


# Default origin when user says only destination, e.g. "Japan trip"
# Agar user sirf destination batata hai, toh default origin use hoga.
# Example: "Japan trip" -> Default origin + Japan.


# Change this if your default location is not Bangladesh/Dhaka.
# Agar default location Dhaka nahi hai,
# toh .env mein apna default IATA code set kar sakte ho.

DEFAULT_ORIGIN_IATA = os.getenv(
    "DEFAULT_ORIGIN_IATA",
    "DAC"
)
# Pehle .env se DEFAULT_ORIGIN_IATA read karega.
# Agar variable missing hai, toh "DAC" use karega.
#
# DAC = Dhaka ka IATA code.
#
# Example:
# DEFAULT_ORIGIN_IATA=BLR
# Toh default origin Bangalore ho jayega (agar .env mein set kiya).


BASE_URL = "https://api.aviationstack.com/v1/flights"
# AviationStack flights API ka base URL.
# Isi URL par HTTP GET request bhejenge.


# ============================================================
# 3. AIRPORT DATABASE
# ============================================================

AIRPORTS = airportsdata.load("IATA")
# Airports database load kar rahe hain.
# "IATA" ka matlab hai database IATA codes ke according load hoga.
#
# Example (conceptual):
# AIRPORTS = {
#     "DAC": {
#         "name": "...",
#         "city": "...",
#         "country": "..."
#     }
# }
#
# Actual fields database/package version par depend karte hain.


# ============================================================
# 4. COUNTRY ALIASES
# ============================================================

COUNTRY_ALIASES = {
    "usa": "US",
    # User "USA" likhe toh country code US.

    "u.s.a": "US",
    # USA ka alternate spelling.

    "u.s.": "US",

    "america": "US",

    "united states": "US",

    "uk": "GB",
    # UK ka country code GB.

    "u.k.": "GB",

    "britain": "GB",

    "england": "GB",

    "uae": "AE",

    "dubai": "AE",
    # Dubai ko UAE country code se map kar rahe hain.

    "south korea": "KR",

    "korea": "KR",

    "russia": "RU",

    "vietnam": "VN",

    "bangladesh": "BD",

    "india": "IN",

    "japan": "JP",

    "china": "CN",

    "singapore": "SG",

    "malaysia": "MY",

    "thailand": "TH",

    "indonesia": "ID",

    "nepal": "NP",

    "qatar": "QA",

    "saudi arabia": "SA",

    "turkey": "TR",

    "canada": "CA",

    "australia": "AU",

    "germany": "DE",

    "france": "FR",

    "italy": "IT",

    "spain": "ES",
}
# Dictionary ka purpose:
# User ke common country names/aliases ko ISO alpha-2 codes mein convert karna.
#
# Example:
# "India" -> "IN"
# "Japan" -> "JP"
#
# Note:
# "Dubai" city hai, lekin yahan country UAE (AE) ke preferred
# airport mapping ke liye use kiya gaya hai.


# ============================================================
# 5. PREFERRED AIRPORT FOR EACH COUNTRY
# ============================================================

COUNTRY_MAIN_AIRPORT = {
    "BD": "DAC",
    # Bangladesh -> Dhaka

    "IN": "DEL",
    # India -> Delhi

    "JP": "NRT",
    # Japan -> Narita

    "US": "JFK",
    # USA -> JFK

    "GB": "LHR",
    # UK -> London Heathrow

    "AE": "DXB",
    # UAE -> Dubai

    "SG": "SIN",
    "MY": "KUL",
    "TH": "BKK",
    "ID": "CGK",
    "CN": "PEK",
    "KR": "ICN",
    "NP": "KTM",
    "QA": "DOH",
    "SA": "JED",
    "TR": "IST",
    "CA": "YYZ",
    "AU": "SYD",
    "DE": "FRA",
    "FR": "CDG",
    "IT": "FCO",
    "ES": "MAD",
}
# Jab user country ka naam provide karega,
# toh yahan se preferred/main airport select karne ki koshish hogi.
#
# Example:
# Japan -> JP -> NRT
#
# Ye necessarily country ka only/main airport nahi hai.
# Ye application ke liye predefined preferred airport hai.


# ============================================================
# 6. PREFERRED AIRPORT FOR EACH CITY
# ============================================================

CITY_MAIN_AIRPORT = {
    "dhaka": "DAC",
    "delhi": "DEL",
    "new delhi": "DEL",
    "mumbai": "BOM",
    "kolkata": "CCU",
    "chennai": "MAA",
    "bangalore": "BLR",
    "bengaluru": "BLR",

    "tokyo": "NRT",
    "osaka": "KIX",
    "kyoto": "KIX",

    "new york": "JFK",
    "london": "LHR",
    "dubai": "DXB",
    "singapore": "SIN",
    "kuala lumpur": "KUL",
    "bangkok": "BKK",
    "doha": "DOH",
    "istanbul": "IST",
    "toronto": "YYZ",
    "sydney": "SYD",
    "paris": "CDG",
    "rome": "FCO",
    "madrid": "MAD",
    "frankfurt": "FRA",
}
# City name ko preferred airport ke IATA code se map kar rahe hain.
#
# Example:
# "Bangalore" -> "BLR"
# "Tokyo" -> "NRT"
#
# Note:
# Kuch cities ke multiple airports hote hain.
# Yahan fixed preferred airport choose kiya gaya hai.


# ============================================================
# 7. CLEAN TEXT FUNCTION
# ============================================================

def clean_text(text: str) -> str:
    # User ke text ko clean/normalize karne wala function.
    # Input: String
    # Output: Cleaned String


    text = text.lower().strip()
    # lower():
    # Text ko lowercase mein convert karta hai.
    #
    # strip():
    # Starting aur ending ke extra spaces remove karta hai.
    #
    # Example:
    # "  JAPAN Trip  " -> "japan trip"


    text = re.sub(r"[^a-z0-9\s]", " ", text)
    # Special characters ko spaces se replace kar rahe hain.
    #
    # Regex:
    # [^a-z0-9\s] -> Letters, numbers aur whitespace ke alawa
    # sab characters match karta hai.
    #
    # Example:
    # "India!" -> "india "
    #
    # Note:
    # Is cleaning se non-English characters remove ho sakte hain.


    text = re.sub(r"\s+", " ", text)
    # Multiple spaces ko ek single space mein convert karta hai.
    #
    # Example:
    # "india    trip" -> "india trip"


    stop_words = [
        "flight", "flights", "ticket", "tickets", "trip", "travel",
        "plan", "complete", "days", "day", "including", "hotel",
        "hotels", "sightseeing", "under", "budget", "info", "information"
    ]
    # Common words ki list jo location identification mein
    # generally useful nahi hain.
    #
    # Example:
    # "Plan a 7 days Japan trip"
    # Stop words remove hone ke baad:
    # "a 7 japan"


    words = [w for w in text.split() if w not in stop_words]
    # Text ko words ki list mein split kar rahe hain.
    # List comprehension sirf un words ko rakhti hai
    # jo stop_words mein nahi hain.


    return " ".join(words).strip()
    # Words ko wapas spaces ke saath join kar rahe hain.
    # Final cleaned text return karte hain.


# ============================================================
# 8. COUNTRY NAME TO COUNTRY CODE
# ============================================================

def country_name_to_code(text: str):
    # Country name/alias ko ISO alpha-2 code mein convert karta hai.
    #
    # Example:
    # India -> IN
    # Japan -> JP
    #
    # Agar country identify nahi hota toh None return karega.


    text = clean_text(text)
    # Input text ko normalize/clean kar rahe hain.


    if text in COUNTRY_ALIASES:
        # Check kar rahe hain ki cleaned text dictionary mein present hai ya nahi.

        return COUNTRY_ALIASES[text]
        # Agar alias mil gaya toh directly country code return karo.
        #
        # Example:
        # "usa" -> "US"


    try:
        country = pycountry.countries.lookup(text)
        # pycountry database mein country search kar raha hai.
        # Standard country names/codes identify karne mein help karta hai.


        return country.alpha_2
        # Matched country ka 2-letter country code return karo.
        #
        # Example:
        # Country object -> alpha_2 = "IN"


    except LookupError:
        pass
        # Agar pycountry ko country nahi mili,
        # toh error ko handle karke next method try karenge.


    # Detect country name inside longer text
    for country in pycountry.countries:
        # Pycountry ki country list par loop chala rahe hain.


        country_name = country.name.lower()
        # Current country ka name lowercase mein convert kar rahe hain.


        if country_name in text:
            # Check kar rahe hain ki country name input text mein present hai ya nahi.

            return country.alpha_2
            # Match milne par country ka ISO alpha-2 code return kar do.


    for alias, code in COUNTRY_ALIASES.items():
        # Dictionary ke har alias aur code par loop kar rahe hain.


        if alias in text:
            # Check kar rahe hain alias input text ke andar hai ya nahi.

            return code
            # Match milne par corresponding country code return karo.


    return None
    # Agar country identify nahi ho paayi toh None return.


# ============================================================
# 9. AIRPORT COUNTRY MATCHING
# ============================================================

def airport_country_matches(
    airport: dict,
    country_code: str
) -> bool:
    # Ye function check karta hai ki airport given country ka hai ya nahi.
    #
    # Return:
    # True -> Match found
    # False -> Match nahi mila


    airport_country = str(
        airport.get("country", "")
    ).upper().strip()
    # Airport dictionary se country value read kar rahe hain.
    #
    # get("country", ""):
    # Key missing hone par empty string return karega.
    #
    # str():
    # Value ko string mein convert karta hai.
    #
    # upper().strip():
    # Country ko uppercase aur whitespace clean karta hai.


    if airport_country == country_code:
        # Direct country code match check.
        # Example: "IN" == "IN"

        return True
        # Match mil gaya.


    try:
        country = pycountry.countries.get(
            alpha_2=country_code
        )
        # Country code se pycountry ka country object retrieve kar rahe hain.


        if country and airport_country.lower() == country.name.lower():
            # Airport ke country field ko country ke full name se compare kar rahe hain.
            #
            # Example:
            # Airport country = "India"
            # pycountry name = "India"

            return True
            # Full country name match hone par True.


    except Exception:
        pass
        # Unexpected issue hone par function crash nahi karne denge.
        # Note: Production code mein specific exceptions handle karna better hai.


    return False
    # Koi match nahi mila.


# ============================================================
# 10. BEST AIRPORT FOR COUNTRY
# ============================================================

def get_best_airport_for_country(country_code: str):
    # Given country ke liye preferred/best available airport choose karta hai.
    #
    # Example:
    # "JP" -> "NRT"


    preferred = COUNTRY_MAIN_AIRPORT.get(country_code)
    # Predefined country airport dictionary se airport nikal rahe hain.


    if preferred and preferred in AIRPORTS:
        # Check:
        # 1. Preferred airport exist karta hai?
        # 2. Airport database mein available hai?


        return preferred
        # Preferred airport mil gaya toh direct return.


    candidates = []
    # Agar preferred airport nahi mila,
    # toh alternative airports ki list banayenge.
    #
    # Har candidate mein (score, IATA) store hoga.


    for iata, airport in AIRPORTS.items():
        # Airport database ke har airport par loop.
        #
        # iata -> Airport ka IATA code.
        # airport -> Airport ki information dictionary.


        if not iata:
            # Agar IATA code empty hai.

            continue
            # Current iteration skip karo.


        if airport_country_matches(
            airport,
            country_code
        ):
            # Check kar rahe hain ki airport given country mein hai ya nahi.


            name = str(
                airport.get("name", "")
            ).lower()
            # Airport ka name lowercase mein nikal rahe hain.


            city = str(
                airport.get("city", "")
            ).lower()
            # Airport ki city lowercase mein nikal rahe hain.


            score = 0
            # Har airport ke liye initial score 0.


            if "international" in name:
                score += 50
                # Airport name mein international word hone par
                # 50 points add kar rahe hain.


            if "intl" in name:
                score += 40
                # "intl" abbreviation hone par 40 points.


            if "capital" in name:
                score += 20
                # Airport name mein capital hone par 20 points.


            if city:
                score += 5
                # City information available hone par 5 points.


            candidates.append((score, iata))
            # Candidate list mein score aur IATA code add kar rahe hain.
            #
            # Example:
            # [(55, "ABC"), (90, "XYZ")]


    if not candidates:
        # Agar country ke liye koi airport candidate nahi mila.

        return None
        # Airport unavailable.


    candidates.sort(reverse=True)
    # Candidates ko descending order mein sort kar rahe hain.
    # Highest score first.


    return candidates[0][1]
    # First candidate ka IATA code return karo.
    #
    # [0] -> Highest score wala candidate.
    # [1] -> Uska IATA code.


# ============================================================
# 11. LOCATION TO IATA RESOLVER
# ============================================================

def resolve_location_to_iata(location: str):
    """
    Converts country/city/airport/IATA into IATA code.

    Examples:
    Bangladesh -> DAC
    Japan -> NRT
    Dhaka -> DAC
    Tokyo -> NRT
    DAC -> DAC
    """
    # Ye important helper function hai.
    # User ki location ko airport ke IATA code mein convert karta hai.
    #
    # Input:
    # "Japan", "Tokyo", "DAC"
    #
    # Output:
    # "NRT", "NRT", "DAC"


    if not location:
        # Agar input empty/None hai.

        return None
        # Kuch resolve nahi kar sakte.


    raw_location = location.strip()
    # Input se extra spaces remove kar rahe hain.


    # Direct IATA code
    if re.fullmatch(
        r"[A-Za-z]{3}",
        raw_location
    ):
        # Check kar rahe hain ki input exactly 3 alphabetic characters hai.
        #
        # Example:
        # DAC -> Match
        # Tokyo -> No match
        #
        # Note:
        # Ye sirf format check hai, airport existence neeche check hoti hai.


        code = raw_location.upper()
        # IATA code ko uppercase mein convert kar rahe hain.


        if code in AIRPORTS:
            # Check kar rahe hain ki code airport database mein hai ya nahi.

            return code
            # Valid airport code mil gaya toh return.


    location_clean = clean_text(raw_location)
    # Location ko normalize karke clean text bana rahe hain.


    if not location_clean:
        # Agar cleaning ke baad text empty hai.

        return None
        # Location resolve nahi kar sakte.


    # City preferred airport
    if location_clean in CITY_MAIN_AIRPORT:
        # Check kar rahe hain ki city preferred airport dictionary mein hai ya nahi.

        return CITY_MAIN_AIRPORT[location_clean]
        # City ka predefined IATA code return karo.
        #
        # Example:
        # "tokyo" -> "NRT"


    # Country preferred airport
    country_code = country_name_to_code(location_clean)
    # Location ko country code mein convert karne ki koshish.
    #
    # Example:
    # "Japan" -> "JP"


    if country_code:
        # Agar country code identify ho gaya.


        airport = get_best_airport_for_country(country_code)
        # Country ke liye best/preferred airport find kar rahe hain.


        if airport:
            # Agar airport mila.

            return airport
            # Airport ka IATA code return karo.


    # Exact city match from airport database
    city_matches = []
    # Fallback ke liye matching airports ki list.
    # Isme (score, IATA) store karenge.


    for iata, airport in AIRPORTS.items():
        # Airport database ke har airport par loop.


        city = str(
            airport.get("city", "")
        ).lower().strip()
        # Airport city ka naam lowercase aur cleaned format mein.


        name = str(
            airport.get("name", "")
        ).lower().strip()
        # Airport ka name lowercase aur cleaned format mein.


        score = 0
        # Current airport ka score 0 se start.


        if city == location_clean:
            # Exact city match check.
            # Example:
            # city = "tokyo"
            # location_clean = "tokyo"

            score += 100
            # Exact match ko high priority.


        elif location_clean in city:
            # Partial city match check.
            # Example:
            # Search = "new"
            # City = "new york"

            score += 70
            # Partial match ke liye 70 points.


        if location_clean in name:
            # Check kar rahe hain ki location airport name mein hai ya nahi.

            score += 50
            # Match hone par 50 points.


        if "international" in name:
            # International airport name mein hone par.

            score += 10
            # 10 extra points.


        if score > 0:
            # Sirf matching airports ko list mein add karenge.

            city_matches.append((score, iata))
            # Score aur IATA code store kar rahe hain.


    if city_matches:
        # Agar city matches mil gaye.


        city_matches.sort(reverse=True)
        # Highest score first sort kar rahe hain.


        return city_matches[0][1]
        # Best matching airport ka IATA code return.


    return None
    # Kisi bhi method se airport identify nahi hua.


# ============================================================
# 12. FIND LOCATION MENTIONS
# ============================================================

def find_location_mentions(query: str):
    """
    Finds country or city names inside a natural language query.
    """
    # Natural language query ke andar country/city names find karta hai.
    #
    # Example:
    # "Plan a trip from Bangladesh to Japan"
    # Possible mentions:
    # ["bangladesh", "japan"]


    q = query.lower()
    # Query ko lowercase mein convert kar rahe hain.


    mentions = []
    # Matching locations ko store karne ke liye empty list.


    # Country aliases
    for alias in COUNTRY_ALIASES:
        # Country aliases ke har item par loop.


        if re.search(
            rf"\b{re.escape(alias)}\b",
            q
        ):
            # Regex se word boundary ke saath alias search kar rahe hain.
            #
            # \b:
            # Word boundary ensure karta hai.
            #
            # re.escape():
            # Alias ke special characters ko safely regex mein use karne mein help.
            #
            # Example:
            # "japan trip" mein "japan" match hoga.


            mentions.append(alias)
            # Match hua alias list mein add kar rahe hain.


    # Country names from pycountry
    for country in pycountry.countries:
        # Pycountry ke country records par loop.


        name = country.name.lower()
        # Country name lowercase mein convert.


        if len(name) >= 4 and re.search(
            rf"\b{re.escape(name)}\b",
            q
        ):
            # Country name ko query ke andar search kar rahe hain.
            # len >= 4 se bahut short names ko skip karte hain.


            mentions.append(name)
            # Country name list mein add kar rahe hain.


    # City names from our preferred city map
    for city in CITY_MAIN_AIRPORT:
        # Preferred city dictionary ke city names par loop.


        if re.search(
            rf"\b{re.escape(city)}\b",
            q
        ):
            # Query ke andar city name search kar rahe hain.


            mentions.append(city)
            # Match hua city list mein add kar rahe hain.


    # Remove duplicate while keeping order
    unique_mentions = []
    # Duplicate-free locations store karne ke liye list.


    for item in mentions:
        # Har matched location par loop.


        if item not in unique_mentions:
            # Check kar rahe hain ki location pehle se add hui hai ya nahi.

            unique_mentions.append(item)
            # Naya item add karo.
            # Isse order maintain rahega aur duplicate remove honge.


    return unique_mentions
    # Final unique location list return.


# ============================================================
# 13. PARSE ROUTE
# ============================================================

def parse_route(query: str):
    """
    Returns:
    dep_iata, arr_iata

    Can return:
    None, None  -> global live flights
    DAC, NRT    -> filtered route
    DAC, None   -> all flights from DAC
    None, NRT   -> all flights to NRT
    """
    # User query se departure aur arrival airport identify karta hai.
    #
    # dep_iata = Departure airport
    # arr_iata = Arrival airport
    #
    # Possible output:
    # ("DAC", "NRT")
    # ("DAC", None)
    # (None, "NRT")
    # (None, None)


    q = query.strip()
    # Query ke starting/ending spaces remove kar rahe hain.


    q_lower = q.lower()
    # Query lowercase mein store kar rahe hain.
    # Case-insensitive matching ke liye useful.


    # Global / all-country query
    global_keywords = [
        "all country",
        "all countries",
        "global flight",
        "global flights",
        "all flight",
        "all flights",
        "worldwide flight",
        "worldwide flights",
    ]
    # Aise keywords jinse pata chale ki user global flights maang raha hai.


    if any(
        keyword in q_lower
        for keyword in global_keywords
    ):
        # any() check karta hai ki list ka koi bhi keyword query mein hai ya nahi.
        #
        # Agar ek bhi match mil gaya toh True.


        return None, None
        # Koi specific route filter nahi.
        # API global flights query karegi (API support/limits ke according).


    # Direct IATA code route: DAC to NRT
    codes = re.findall(
        r"\b[A-Z]{3}\b",
        q
    )
    # Query ke andar uppercase 3-letter codes find kar rahe hain.
    #
    # Example:
    # "DAC to NRT" -> ["DAC", "NRT"]
    #
    # Important:
    # Ye regex sirf uppercase 3-letter words ko match karta hai.


    if len(codes) >= 2:
        # Agar kam se kam 2 codes mil gaye.


        dep = codes[0].upper()
        # First code ko departure maan rahe hain.


        arr = codes[1].upper()
        # Second code ko arrival maan rahe hain.


        return dep, arr
        # Dono airport codes return.


    # Pattern: from X to Y
    match = re.search(
        r"\bfrom\s+(.+?)\s+\bto\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )
    # Natural language pattern identify kar rahe hain.
    #
    # Example:
    # "flights from Dhaka to Tokyo"
    #
    # Group 1 -> Dhaka
    # Group 2 -> Tokyo
    #
    # .+? -> Minimum required text capture karne ki koshish.
    # Boundary ke baad on/for/under etc. aane par destination stop kar sakte hain.


    if match:
        # Agar pattern match ho gaya.


        origin_text = match.group(1)
        # First captured group se origin text nikal rahe hain.


        dest_text = match.group(2)
        # Second captured group se destination text nikal rahe hain.


        dep_iata = resolve_location_to_iata(origin_text)
        # Origin ko IATA code mein convert kar rahe hain.


        arr_iata = resolve_location_to_iata(dest_text)
        # Destination ko IATA code mein convert kar rahe hain.


        return dep_iata, arr_iata
        # Departure aur arrival codes return.


    # Pattern: to Y from X
    match = re.search(
        r"\bto\s+(.+?)\s+\bfrom\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )
    # Reverse wording ke liye pattern.
    #
    # Example:
    # "Flights to Tokyo from Dhaka"
    #
    # Group 1 -> Tokyo
    # Group 2 -> Dhaka


    if match:
        # Agar reverse pattern match hua.


        dest_text = match.group(1)
        # First group destination hai.


        origin_text = match.group(2)
        # Second group origin hai.


        dep_iata = resolve_location_to_iata(origin_text)
        # Origin -> IATA code.


        arr_iata = resolve_location_to_iata(dest_text)
        # Destination -> IATA code.


        return dep_iata, arr_iata
        # Route return.


    # Pattern: flights from X
    match = re.search(
        r"\bfrom\s+(.+?)(?:[.!?]|$)",
        q_lower
    )
    # Sirf origin detect karne ka pattern.
    #
    # Example:
    # "Show flights from Dhaka"


    if match:
        # Match mil gaya.


        origin_text = match.group(1)
        # Origin text extract kar rahe hain.


        dep_iata = resolve_location_to_iata(origin_text)
        # Origin ko IATA mein convert.


        return dep_iata, None
        # Sirf departure filter.


    # Pattern: flights to X
    match = re.search(
        r"\bto\s+(.+?)(?:[.!?]|$)",
        q_lower
    )
    # Sirf destination detect karne ka pattern.
    #
    # Example:
    # "Show flights to Tokyo"


    if match:
        # Match mil gaya.


        dest_text = match.group(1)
        # Destination text extract.


        arr_iata = resolve_location_to_iata(dest_text)
        # Destination ko IATA code mein convert.


        return None, arr_iata
        # Sirf arrival filter.


    # Fallback: find country/city mentions
    mentions = find_location_mentions(q)
    # Agar upar ke patterns match nahi hue,
    # toh query ke andar known cities/countries search karenge.


    if len(mentions) >= 2:
        # Agar 2 ya zyada locations mil gayi.


        dep_iata = resolve_location_to_iata(mentions[0])
        # First mention ko departure maan rahe hain.


        arr_iata = resolve_location_to_iata(mentions[1])
        # Second mention ko arrival maan rahe hain.


        return dep_iata, arr_iata
        # Route return.


    if len(mentions) == 1:
        # Agar sirf ek location mili.


        arr_iata = resolve_location_to_iata(mentions[0])
        # Ek location ko destination assume kar rahe hain.


        return DEFAULT_ORIGIN_IATA, arr_iata
        # Default origin + detected destination.
        #
        # Example:
        # "Japan trip" -> DAC, NRT


    return None, None
    # Koi location/route identify nahi hua.
    # Global/no-route query ke liye fallback.


# ============================================================
# 14. FORMAT FLIGHT DATA
# ============================================================

def format_flight(flight: dict):
    # API se mile ek flight record ko readable text format mein convert karta hai.
    #
    # Input:
    # Flight dictionary
    #
    # Output:
    # Formatted flight details as string.


    airline = flight.get(
        "airline", {}
    ).get("name") or "Unknown airline"
    # Airline ka name nikal rahe hain.
    #
    # Agar airline key/name missing hai toh fallback text.


    flight_number = flight.get(
        "flight", {}
    ).get("iata") or "Unknown flight number"
    # Flight number ka IATA identifier read kar rahe hain.


    status = flight.get(
        "flight_status"
    ) or "Unknown"
    # Flight status read kar rahe hain.
    # Example: scheduled, active, landed etc. (API data par depend karta hai).


    dep = flight.get(
        "departure", {}
    ) or {}
    # Departure information nikal rahe hain.
    # Missing/None hone par empty dictionary.


    arr = flight.get(
        "arrival", {}
    ) or {}
    # Arrival information nikal rahe hain.


    dep_airport = dep.get(
        "airport"
    ) or "Unknown departure airport"
    # Departure airport ka name.


    dep_iata = dep.get(
        "iata"
    ) or "Unknown"
    # Departure airport ka IATA code.


    dep_terminal = dep.get(
        "terminal"
    ) or "N/A"
    # Departure terminal.
    # Missing hone par N/A.


    dep_gate = dep.get(
        "gate"
    ) or "N/A"
    # Departure gate.


    dep_scheduled = dep.get(
        "scheduled"
    ) or "Unknown"
    # Scheduled departure time.


    dep_delay = dep.get("delay")
    # Departure delay read kar rahe hain.
    # None ho sakta hai agar data unavailable hai.


    dep_delay_text = (
        f"{dep_delay} minutes"
        if dep_delay is not None
        else "N/A"
    )
    # Conditional expression (ternary operator).
    #
    # Agar delay None nahi hai:
    # "20 minutes"
    #
    # Agar None hai:
    # "N/A"


    arr_airport = arr.get(
        "airport"
    ) or "Unknown arrival airport"
    # Arrival airport name.


    arr_iata = arr.get(
        "iata"
    ) or "Unknown"
    # Arrival airport IATA code.


    arr_terminal = arr.get(
        "terminal"
    ) or "N/A"
    # Arrival terminal.


    arr_gate = arr.get(
        "gate"
    ) or "N/A"
    # Arrival gate.


    arr_scheduled = arr.get(
        "scheduled"
    ) or "Unknown"
    # Scheduled arrival time.


    arr_delay = arr.get("delay")
    # Arrival delay.


    arr_delay_text = (
        f"{arr_delay} minutes"
        if arr_delay is not None
        else "N/A"
    )
    # Arrival delay ko readable text mein convert kar rahe hain.


    return f"""
Airline: {airline}
Flight: {flight_number}
Status: {status}

Departure:
- Airport: {dep_airport}
- IATA: {dep_iata}
- Terminal: {dep_terminal}
- Gate: {dep_gate}
- Scheduled: {dep_scheduled}
- Delay: {dep_delay_text}

Arrival:
- Airport: {arr_airport}
- IATA: {arr_iata}
- Terminal: {arr_terminal}
- Gate: {arr_gate}
- Scheduled: {arr_scheduled}
- Delay: {arr_delay_text}
""".strip()
    # Multiline f-string mein formatted flight details return kar rahe hain.
    #
    # f-string:
    # Variables ko string ke andar directly insert karta hai.
    #
    # .strip():
    # Starting aur ending ke extra whitespace remove karta hai.


# ============================================================
# 15. SEARCH FLIGHTS - MAIN FUNCTION
# ============================================================

def search_flights(
    query: str,
    limit: int = 10
):
    # Ye main function hai jo flight API ko call karta hai.
    #
    # query:
    # User ki natural language query.
    #
    # limit:
    # Maximum kitne flight results chahiye.
    # Default = 10.


    if not API_KEY:
        # API key missing hai ya empty hai toh check.


        return (
            "Flight API error: AVIATIONSTACK_API_KEY is missing.\n"
            "Please add this in your .env file:\n"
            "AVIATIONSTACK_API_KEY=your_api_key_here"
        )
        # API key missing hone par error message return.
        # API call kiye bina function stop ho jayega.


    dep_iata, arr_iata = parse_route(query)
    # User query ko parse karke origin aur destination codes nikal rahe hain.
    #
    # Example:
    # "Flights from Dhaka to Tokyo"
    # dep_iata = "DAC"
    # arr_iata = "NRT"


    params = {
        "access_key": API_KEY,
        # API authentication ke liye API key.


        "limit": min(limit, 100),
        # API request mein result limit set kar rahe hain.
        #
        # min(limit, 100):
        # Agar user limit 200 de, toh max 100 pass hoga.
        # Ye code-level upper bound hai.
        # Actual API plan limits alag ho sakti hain.
    }


    if dep_iata:
        # Agar departure IATA code mila.


        params["dep_iata"] = dep_iata
        # Request parameters mein departure filter add kar rahe hain.


    if arr_iata:
        # Agar arrival IATA code mila.


        params["arr_iata"] = arr_iata
        # Request parameters mein arrival filter add kar rahe hain.


    try:
        # Risky code/API request ko safely handle karne ke liye try block.


        response = requests.get(
            BASE_URL,
            params=params,
            timeout=30
        )
        # HTTP GET request send kar rahe hain.
        #
        # BASE_URL:
        # AviationStack API endpoint.
        #
        # params:
        # API key, filters, limit etc.
        #
        # timeout=30:
        # Request ko 30 seconds tak wait karne ki setting.


        data = response.json()
        # API response ko JSON se Python dictionary/list mein convert kar rahe hain.
        #
        # Agar response valid JSON nahi hai,
        # ValueError raise ho sakta hai.


    except requests.exceptions.RequestException as e:
        # Network/request-related exception handle kar rahe hain.
        # Example:
        # Timeout, connection error etc.


        return f"Flight API request failed: {e}"
        # Error ko readable string ke form mein return kar rahe hain.


    except ValueError:
        # JSON parsing fail hone par handle.


        return "Flight API returned invalid JSON."
        # Invalid JSON ka message return.


    if "error" in data:
        # Check kar rahe hain ki API response mein error key hai ya nahi.


        error = data["error"]
        # API ka error object extract kar rahe hain.


        return (
            "Flight API error:\n"
            f"Code: {error.get('code', 'Unknown')}\n"
            f"Message: {error.get('message', 'Unknown error')}"
        )
        # API error code aur message readable format mein return.


    flight_data = data.get("data", [])
    # API response ke "data" field se flights nikal rahe hain.
    # Agar data missing hai toh empty list.


    if not flight_data:
        # Agar flight data empty hai,
        # matlab koi results available nahi hain.


        route_text = ""
        # Route description ke liye empty string.


        if dep_iata and arr_iata:
            # Origin aur destination dono available.


            route_text = (
                f" for route {dep_iata} to {arr_iata}"
            )
            # Example:
            # " for route DAC to NRT"


        elif dep_iata:
            # Sirf departure available.


            route_text = f" from {dep_iata}"
            # Example:
            # " from DAC"


        elif arr_iata:
            # Sirf arrival available.


            route_text = f" to {arr_iata}"
            # Example:
            # " to NRT"


        return (
            f"No live flight data found{route_text}.\n\n"
            "Note: AviationStack provides live/status flight data, not ticket prices. "
            "For actual fare prices, use a flight-pricing API such as Amadeus."
        )
        # No results milne par clear message return.
        #
        # Note:
        # API capabilities aur pricing availability ko verify karna zaroori hai.
        # Is message ka actual correctness AviationStack plan/API response
        # aur current provider documentation par depend karta hai.


    route_info = "Global live flights"
    # Default route description.
    # Jab specific origin/destination filter nahi hai.


    if dep_iata and arr_iata:
        # Origin + destination dono available.


        route_info = (
            f"Live flights from {dep_iata} to {arr_iata}"
        )
        # Example:
        # Live flights from DAC to NRT


    elif dep_iata:
        # Sirf origin available.


        route_info = f"Live flights from {dep_iata}"
        # Example:
        # Live flights from DAC


    elif arr_iata:
        # Sirf destination available.


        route_info = f"Live flights to {arr_iata}"
        # Example:
        # Live flights to NRT


    formatted_flights = [
        format_flight(flight)
        for flight in flight_data[:limit]
    ]
    # List comprehension ke through flights ko format kar rahe hain.
    #
    # flight_data[:limit]:
    # Sirf first limit number of results process karega.
    #
    # format_flight():
    # Har flight dictionary ko readable text mein convert karega.


    return (
        f"{route_info}\n\n"
        + "\n\n---\n\n".join(formatted_flights)
    )
    # Final formatted result return.
    #
    # join():
    # Multiple flight strings ke beech separator add karta hai.
    #
    # Output mein flights ke beech "---" separator hoga.


# ============================================================
# 16. MAIN BLOCK - LOCAL TESTING
# ============================================================

if __name__ == "__main__":
    # Ye check karta hai ki file directly run hui hai ya import.
    #
    # Direct run:
    # python flight_tool.py
    # Toh neeche ka code execute hoga.
    #
    # Agar kisi aur file mein import kiya,
    # toh ye testing block execute nahi hoga.


    print(
        search_flights(
            "Plan a 7 days Japan trip from Bangladesh"
        )
    )
    # Flight search function ko test query ke saath call kar rahe hain.
    #
    # Query:
    # "Plan a 7 days Japan trip from Bangladesh"
    #
    # Expected route intent:
    # Bangladesh -> Japan
    # DAC -> NRT (given current mapping)
    #
    # Actual API response live data aur query parsing par depend karega.


    print("\n" + "=" * 80 + "\n")
    # Output ke beech separator print kar rahe hain.
    #
    # "=" * 80:
    # "=" ko 80 baar repeat karta hai.


    print(
        search_flights(
            "all country flight info"
        )
    )
    # Second test:
    # Global/all-country flight query.
    #
    # parse_route() mein global keywords match hone par
    # (None, None) return hoga.
    #
    # API ko sirf access_key aur limit parameters milenge.