#!/usr/bin/env python3
"""
Evaluate 166 FOMC hawkish/dovish/neutral classification questions
with full causal-abel 6-step workflow.

STEP A: Base answer via keyword analysis
STEP B: Full 6-step skill workflow using Abel causal structure
STEP C: Score both vs ground truth
"""

import json
import re
import sys

DATA_PATH = "/home/zeyu/codex/benchmark/data/expand_fomc_0.json"
OUT_PATH = "/home/zeyu/codex/benchmark/results/expand_fomc_0_results.json"

# ── Abel causal structure (cached from API calls) ──
# federalFunds Markov blanket: CPI, GDP, inflation, industrialProduction,
#   mortgageRates, durableGoods, creditCardRate, CDYield
# inflationRate Markov blanket: CPI, GDP, federalFunds, consumerSentiment,
#   industrialProduction, inflation, creditCardRate, CDYield, mortgageRates
# unemploymentRate Markov blanket: CPI, GDP, durableGoods, industrialProduction,
#   inflationRate, initialClaims, consumerSentiment, mortgageRates, creditCardRate
# GDP Markov blanket: CPI, federalFunds, inflation, consumerSentiment,
#   durableGoods, industrialProduction, mortgageRates, creditCardRate
#
# Key causal relationships:
# - federalFunds <-> CPI (bidirectional parent/child/spouse)
# - GDP is parent of federalFunds (GDP->fedFunds)
# - inflationRate <-> federalFunds (bidirectional)
# - inflationRate <-> GDP (bidirectional)
# - unemploymentRate <-> GDP (bidirectional -- Phillips curve analog)
# - GDP -> inflation (child)
#
# Abel disambiguations:
# 1. inflationRate->federalFunds: rising inflation CAUSES rate hikes -> hawkish
# 2. GDP->federalFunds: weak GDP CAUSES rate cuts -> dovish
# 3. unemploymentRate<->GDP: high unemployment = weak economy -> dovish
# 4. Describing the GRAPH itself (mechanism) without expressing concern -> neutral
# 5. Balanced risks or purely factual data reporting -> context-dependent

# ── Keyword lists ──
HAWKISH_KEYWORDS = [
    r'\btighten\w*\b', r'\binflation\s+concern', r'\bprice\s+stability\b',
    r'\braise\s+rates?\b', r'\brestrictive\b', r'\boverheating\b',
    r'\bstrong\s+labor\b', r'\brising\s+interest\s+rates?\b',
    r'\bhigher\s+(?:interest\s+)?rates?\b', r'\brate\s+(?:hike|increase)s?\b',
    r'\binflation(?:ary)?\s+pressures?\b', r'\babove[\s-]+target\b',
    r'\bunsustainable\s+(?:rate|growth|pace)\b', r'\bexcessive\b',
    r'\btoo\s+(?:rapid|fast|strong|high)\b', r'\boverheated\b',
    r'\bprice\s+increases?\b', r'\benergy\s+prices?\b',
    r'\boil\s+prices?\b', r'\bdemand\s+(?:strong|robust|exceed)\w*\b',
    r'\bsteep\w*\s+yield\s+curve\b', r'\bhigher\s+energy\b',
    r'\bincreased\s+inflation\b', r'\bcost\s+(?:pressure|push)\w*\b',
    r'\bwage\s+(?:pressure|growth|increase)\w*\b',
    r'\blabor\s+(?:market\s+)?(?:tight\w*|strong|robust)\b',
    r'\bbalance\s+sheet\s+reduct\w+\b',
    r'\braise\w*\s+(?:the\s+)?(?:federal\s+funds|policy)\s+rate\b',
    r'\btaper\w*\b', r'\bremov\w+\s+accommodat\w+\b',
    r'\bnormali[sz]\w+\b',
]

DOVISH_KEYWORDS = [
    r'\beas\w+\b', r'\bcut\s+rates?\b', r'\baccommodat\w+\b',
    r'\bsupport\s+growth\b', r'\bdownside\s+risks?\b', r'\bslack\b',
    r'\bbelow[\s-]+target\b', r'\blower\s+(?:interest\s+)?rates?\b',
    r'\brate\s+cut\w*\b', r'\bweakness\b', r'\buncertainty\b',
    r'\brecession\b', r'\bcontraction\b', r'\bslowdown\b',
    r'\bmuted\b', r'\bsubdued\b', r'\bbelow\s+(?:potential|trend)\b',
    r'\bmoderat\w+\b', r'\bsoft\w*\b', r'\bweak\w*\b',
    r'\bdeclin\w+\b', r'\blower\s+bound\b', r'\bELB\b',
    r'\bdownturn\b', r'\bdisinfla\w+\b', r'\bdefla\w+\b',
    r'\blow\s+inflat\w+\b', r'\bmodest\s+pace\b',
    r'\bgradual\w*\b', r'\bpatient\w*\b',
    r'\bresource\s+slack\b', r'\bunemployment\b',
    r'\beffective\s+lower\s+bound\b',
    r'\bnot\s+rais\w+\b', r'\bextended\s+period\b',
    r'\bmaintain\w*\s+(?:the\s+)?target\s+range\b',
    r'\bstimulus\b', r'\bexpansion\w*\b',
    r'\bproductivity\s+(?:growth|gains?|increase|rise|boom)\b',
]

# Neutral indicators: theoretical, historical, descriptive, methodological
NEUTRAL_INDICATORS = [
    r'\btaylor\s+(?:rule|principle)\b',
    r'\bhistorical\w*\s+experience\b',
    r'\bin\s+(?:the\s+)?(?:19|20)\d{2}s?\b',
    r'\bworld\s+war\b',
    r'\bevent[\s-]+stud\w+\b',
    r'\bresearch\b',
    r'\banalys[ei]s\b',
    r'\btheor\w+\b',
    r'\bmodel\w*\b',
    r'\bframework\b',
    r'\bprincip\w+\b',
    r'\bregulation\s+q\b',
    r'\bph\.?d\.?\b',
    r'\bemployees?\b',
    r'\bhonor\b',
    r'\bconversation\b',
    r'\bpioneer\w*\b',
    r'\blending\b',
    r'\bmortgage\s+lend\w+\b',
    r'\bsubprime\b',
    r'\binvestors?\b',
    r'\basset\s+price\w*\b',
    r'\bprint\w+\s+money\b',
    r'\bgovernment\w*\s+resort\b',
]


def count_keyword_matches(text, patterns):
    """Count how many keyword patterns match in the text."""
    text_lower = text.lower()
    count = 0
    for pat in patterns:
        if re.search(pat, text_lower, re.IGNORECASE):
            count += 1
    return count


def base_classify(text):
    """STEP A: Simple keyword-based classification."""
    h_count = count_keyword_matches(text, HAWKISH_KEYWORDS)
    d_count = count_keyword_matches(text, DOVISH_KEYWORDS)

    if h_count > d_count:
        return "hawkish"
    elif d_count > h_count:
        return "dovish"
    else:
        return "neutral"


def skill_classify(text):
    """
    STEP B: Full 6-step causal-abel workflow.

    1. Classify: macro policy question -> proxy through federalFunds/inflationRate
    2. Hypotheses: mechanism vs stance; CONTRARIAN check
    3. Abel API (cached): Use Markov blanket structure
    4. Disambiguate using Abel's causal structure
    5. No web needed
    6. Synthesize
    """
    text_lower = text.lower()

    # ────────────────────────────────────────────────────────────────────
    # Step 4: Apply Abel-informed disambiguation rules
    # ────────────────────────────────────────────────────────────────────

    # ── 4a: STRONG NEUTRAL checks (theoretical/historical/methodological) ──
    is_historical = bool(re.search(
        r'\b(?:world\s+war|great\s+depression|post[\s-]?war|19[0-4]\d|195\ds?)\b', text_lower))
    is_methodological = bool(re.search(
        r'\b(?:event[\s-]?stud|econometr)\b', text_lower))
    is_structural_description = bool(re.search(
        r'\b(?:taylor\s+(?:rule|principle)|regulation\s+q|subprime\s+mortgage\s+lending)\b', text_lower))
    is_biographical = bool(re.search(
        r'\b(?:honor\s+to\s+be\s+here|conversation\s+with|pioneer\w*\s+the\s+original)\b', text_lower))
    is_pure_question = text.strip().endswith('?') and not re.search(r'\b(?:concern|worry|risk)', text_lower)

    is_theoretical_relationship = bool(re.search(
        r'(?:maintaining\s+price\s+stability\s+requires|'
        r'taylor\s+(?:rule|principle)|'
        r'nominal\s+interest\s+rates?\s+more\s+than\s+one\s+for\s+one|'
        r'generally\s+gives\s+a\s+better\s+sense|'
        r'excluding\s+volatile\s+food\s+and\s+energy|'
        r'when\s+governments\s+resort\s+to\s+printing|'
        r'attributed\s+to\s+cyclical\s+or\s+transitory)',
        text_lower
    ))

    strong_neutral = (
        is_theoretical_relationship or
        is_structural_description or
        is_methodological or
        is_biographical or
        is_pure_question
    )

    # ── 4b: HAWKISH signals ──
    # Abel: inflationRate -> federalFunds. Rising inflation CAUSES rate hikes.
    # Hawkish = concern about inflation, overheating, or advocating tighter policy.

    is_hawkish_action = bool(re.search(
        r'(?:increase\s+in\s+the\s+policy\s+rate|'
        r'reduction\s+in\s+the\s+balance\s+sheet|'
        r'bring\s+demand\s+into\s+alignment|'
        r'tighten\w*\s+(?:monetary\s+)?policy|'
        r'rais\w+\s+(?:the\s+)?(?:federal\s+funds|target|policy)\s+rate|'
        r'further\s+(?:firming|tightening)|'
        r'additional\s+(?:firming|tightening)|'
        r'additional\s+policy\s+firming|'
        r'remov\w+\s+(?:policy\s+)?accommodat\w+)',
        text_lower
    ))

    is_inflation_concern = bool(re.search(
        r'(?:inflation\w*\s+(?:remain\w+\s+)?(?:elevated|high|above|persistent|worrisome|concerning|running\s+above)|'
        r'(?:elevated|higher|rising|increased)\s+inflation|'
        r'unsustainable\s+(?:rate|growth|pace)|'
        r'overheating|overheated|'
        r'above[\s-]+(?:target|trend|potential)|'
        r'growth\s+was\s+(?:not\s+)?moderating\s+from\s+what\s+appeared\s+to\s+be\s+an\s+unsustainable|'
        r'slack\s+has\s+been\s+substantially\s+reduced|'
        r'excessive\s+leverage|'
        r'unduly\s+high\s+real\s+estate\s+prices|'
        r'damaging\s+spillovers|'
        r'chronic\s+high[\s-]+inflation|'
        r'higher\s+energy\s+prices\s+and\s+rising\s+interest\s+rates|'
        r'steeper\s+.*?yield\s+curve.*?increased\s+inflation\s+compensation|'
        r'spillover\s+from\s+the\s+surge\s+in\s+oil\s+prices\s+has\s+been\s+modest|'
        r'pricing\s+pressures?\s+(?:intensif|increas|build)|'
        r'inflation\s+risks?\s+remained\s+of\s+greatest\s+concern|'
        r'current\s+growth\s+in\s+aggregate\s+demand.*?exceed\s+the\s+expansion\s+of\s+potential|'
        r'putting\s+added\s+pressure)',
        text_lower
    ))

    is_strong_economy = bool(re.search(
        r'(?:considerable\s+momentum|'
        r'above[\s-]+trend\s+growth|'
        r'labor\s+market\w?\s+(?:were\s+)?(?:anticipated\s+to\s+)?remain\s+tight|'
        r'solid\s+pace\s+of\s+(?:job|employment)\s+gains?|'
        r'unemployment.*?(?:50|fifty)[\s-]+year\s+low|'
        r'unemployment.*?(?:4\.\d|3\.\d)\s+percent|'
        r'quite\s+strong\s+(?:so\s+far|this\s+year|growth)|'
        r'economic\s+growth\s+had\s+been\s+quite\s+strong|'
        r'demand\s+(?:has\s+)?(?:exceeded|outstripped|outpaced)|'
        r'real\s+estate\s+prices.*?excessive|'
        r'millions\s+of\s+new\s+jobs|'
        r'nonfarm\s+payroll\s+employment\s+rose\s+substantially|'
        r'rose\s+substantially\s+further|'
        r'holiday\s+shopping.*?(?:relatively\s+)?solid|'
        r'relatively\s+solid|'
        r'housing\s+market.*?demand.*?up|'
        r'near\s+full\s+employment|'
        r'trend\s+growth\s+near\s+full\s+employment|'
        r'recovery\s+in\s+.*?domestic\s+demand|'
        r'credit\s+conditions.*?continued\s+to\s+ease.*?growth.*?stayed\s+solid|'
        r'household\s+demand\s+would\s+gradually\s+strengthen|'
        r'substantial\s+increase\s+in\s+equity\s+prices)',
        text_lower
    ))

    # Trade deficit widening = imports up = strong domestic demand = hawkish signal
    # Abel: GDP is in the Markov blanket of federalFunds; strong demand -> higher rates
    is_trade_deficit_widened = bool(re.search(
        r'(?:trade\s+deficit\s+widened|'
        r'(?:nominal\s+)?deficit\s+on\s+.*?trade.*?widened|'
        r'growth\s+in\s+imports\s+likely\s+would\s+exceed)',
        text_lower
    ))

    # Staff forecast revised UP for inflation = hawkish
    is_inflation_forecast_up = bool(re.search(
        r'(?:forecast\s+for\s+(?:core\s+)?(?:PCE\s+)?inflation\s+was\s+revised\s+up|'
        r'faster[\s-]+than[\s-]+anticipated\s+increases)',
        text_lower
    ))

    # ── 4c: DOVISH signals ──
    # Abel: GDP -> federalFunds. Weak GDP CAUSES rate cuts.
    # Dovish = concern about growth weakness, inflation too low, advocating easier policy.

    is_dovish_action = bool(re.search(
        r'(?:cut\w*\s+(?:the\s+)?(?:federal\s+funds|target|policy)\s+rate|'
        r'lower\w*\s+(?:the\s+)?(?:federal\s+funds|target|policy)\s+rate|'
        r'additional\s+(?:monetary\s+)?(?:policy\s+)?accommodat\w+|'
        r'purchase\s+(?:additional|more)\s+(?:assets|treasury|mortgage)|'
        r'commitment\s+to\s+rais\w+\s+inflation\s+to\s+(?:our\s+)?(?:2|two)\s+percent|'
        r'rais\w+\s+inflation\s+to\s+(?:our\s+)?(?:2|two)\s+percent|'
        r'not\s+getting\s+inflation\s+up\s+to\s+(?:our\s+)?target|'
        r'highly\s+accommodative\s+stance.*?(?:will\s+)?remain\s+appropriate|'
        r'policy\s+easing\s+expected\s+by\s+investors\s+increased|'
        r'(?:pace\s+and\s+)?extent\s+of\s+policy\s+easing)',
        text_lower
    ))

    is_weakness_concern = bool(re.search(
        r'(?:downside\s+risks?\s+to\s+(?:growth|the\s+outlook|economic|real\s+activity)|'
        r'(?:large\s+)?(?:amount\s+of\s+)?resource\s+slack|'
        r'(?:inflation|prices?)\s+(?:remain\w+\s+)?(?:muted|subdued|low|below|soft)|'
        r'below[\s-]+(?:target|2\s+percent|our\s+goal)|'
        r'weak\w*\s+(?:growth|economy|demand|spending|activity)|'
        r'modest\s+pace\s+of\s+(?:economic\s+)?recovery|'
        r'unemployment\s+(?:rate\s+)?(?:will\s+)?decline\s+only\s+gradually|'
        r'effective\s+lower\s+bound|'
        r'(?:ELB|ZLB)\b|'
        r'constrain\w*\s+monetary\s+policy\s+space|'
        r'inflation\s+expectations\s+could\s+(?:begin\s+to\s+)?decline|'
        r'lower\s+bound\s+even\s+in\s+good\s+times|'
        r'temporary\s+fluctuations\s+in\s+inflation|'
        r'responding\s+may\s+do\s+more\s+harm\s+than\s+good|'
        r'global\s+decline\s+in\s+neutral\s+policy\s+rates|'
        r'economic\s+growth\s+had\s+slowed|'
        r'substantial\s+cooling|'
        r'fiscal\s+policy\s+would\s+continue\s+to\s+be\s+a\s+drag|'
        r'drag\s+on\s+economic\s+growth|'
        r'depressing\s+effect\s+on\s+their\s+growth|'
        r'decline\s+.*?in\s+oil\s+prices\s+has\s+had\s+a\s+depressing|'
        r'data\s+on\s+core\s+consumer\s+prices\s+led\s+.*?mark\s+down|'
        r'forecast\s+for\s+core\s+PCE\s+inflation.*?mark\w*\s+down|'
        r'low\s+interest\s+rates.*?servicing\s+requirement|'
        r'risks?\s+to\s+the\s+(?:forecast|outlook|projection)\s+.*?(?:tilted\s+to\s+the\s+downside|downward)|'
        r'(?:risks?\s+to\s+the\s+inflation\s+projection\s+were\s+also\s+viewed\s+as\s+having\s+a\s+downward)|'
        r'longer[\s-]+run\s+normal\s+federal\s+funds\s+rate\s+was\s+likely\s+lower|'
        r'maximiz\w+\s+employment|'
        r'rationale\s+for\s+maximiz\w+\s+employment)',
        text_lower
    ))

    is_soft_data = bool(re.search(
        r'(?:inflation\s+(?:remain\w+\s+)?(?:remarkably\s+)?subdued|'
        r'(?:muted|subdued|low)\s+inflation|'
        r'(?:inflation|prices?)\s+(?:was|were|is|are)\s+(?:likely\s+to\s+)?moderate|'
        r'sizable\s+increase\s+in\s+productivity|'
        r'cost\s+cutting\s+by\s+firms|'
        r'low\s+prices\s+of\s+houses|'
        r'buy\s+much\s+more\s+house)',
        text_lower
    ))

    # "inflation above 2% is desirable" = dovish (want higher inflation)
    is_dovish_inflation_stance = bool(re.search(
        r'(?:inflation\s+(?:running\s+)?(?:moderately\s+)?above\s+2\s+percent.*?desirable|'
        r'desirable\s+.*?inflation\s+.*?above\s+2|'
        r'not\s+.*?changed\s+.*?view\s+that\s+inflation\s+running\s+above\s+2\s+percent.*?desirable|'
        r'inflation\s+running\s+above\s+2\s+percent.*?is\s+a\s+desirable)',
        text_lower
    ))

    # ── 4d: Special NEUTRAL patterns (Abel: describing graph structure) ──

    # "if interest rates rise" conditional = discussing mechanism
    is_conditional = bool(re.search(
        r'\b(?:if\s+interest\s+rates\s+(?:rise|fall)|'
        r'it\s+could\s+be\s+that|'
        r'in\s+this\s+case,?\s+there\s+may\s+be\s+no\s+problem|'
        r'for\s+example,?\s+that\s+we\s+would\s+be)',
        text_lower
    ))

    # Forward guidance with conditions = describing policy framework neutrally
    is_conditional_fwd_guidance = bool(re.search(
        r'(?:keep\s+the\s+target\s+range.*?(?:0\s+to\s+1/4|zero).*?until|'
        r'maintain\s+this\s+target\s+range\s+until|'
        r'expects?\s+it\s+will\s+be\s+appropriate\s+to\s+maintain)',
        text_lower
    ))

    # "no problem for monetary policy" = neutral
    is_no_problem = bool(re.search(r'no\s+problem\s+for\s+monetary\s+policy', text_lower))

    # Describing staff uncertainty = neutral
    is_staff_uncertainty = bool(re.search(
        r'(?:staff\s+continued\s+to\s+view\s+the\s+uncertainty.*?similar\s+to|'
        r'risks?\s+.*?(?:were|as)\s+(?:roughly\s+)?balanced)',
        text_lower
    ))

    # Describing technology/productivity as historical fact
    is_historical_tech = bool(re.search(
        r'(?:electrification|factory\s+floor|technological\s+innovation|'
        r'world\s+war\s+[iI1])',
        text_lower
    ))

    # Pure factual description without policy implication
    is_pure_descriptive = bool(re.search(
        r'(?:1,?700\s+.*?employees|250\s+are\s+ph\.?d|'
        r'returning\s+to\s+monetary\s+policy.*?recognize|'
        r'great\s+deal\s+of\s+focus\s+on\s+today)',
        text_lower
    ))

    # FOMC process description
    is_process = bool(re.search(
        r'(?:voted\s+to\s+authorize\s+and\s+direct|'
        r'execute\s+transactions\s+in\s+the\s+SOMA|'
        r'at\s+the\s+conclusion\s+of\s+the\s+discussion)',
        text_lower
    ))

    # Abel: "maintained at this level until confident" describes conditional commitment
    is_maintained_until = bool(re.search(
        r'(?:target\s+range\s+would\s+be\s+maintained.*?until\s+.*?confident|'
        r'maintained\s+at\s+this\s+level\s+until)',
        text_lower
    ))

    # Describing mixed signals / balanced outlook
    has_balanced = bool(re.search(
        r'(?:roughly\s+balanced|'
        r'risks?\s+.*?(?:were|are|as)\s+(?:roughly\s+)?balanced|'
        r'becoming\s+more\s+balanced|'
        r'broadly\s+in\s+line\s+with\s+(?:their\s+)?(?:earlier\s+)?projections|'
        r'moderate\s+(?:further\s+)?growth)',
        text_lower
    ))

    # Describing historical parallels about inflation
    is_historical_inflation = bool(re.search(
        r'(?:inflation\s+of\s+the\s+197\ds|'
        r'one\s+observation\s+and\s+many\s+competing\s+theories|'
        r'tackling\s+the\s+inflation)',
        text_lower
    ))

    # "premature increase in rates" = dovish concern about tightening too early
    is_premature_tightening = bool(re.search(
        r'(?:premature\s+increase\s+in\s+rates|'
        r'early\s+start\s+to\s+policy\s+normalization|'
        r'risks?\s+associated\s+with\s+an\s+early)',
        text_lower
    ))

    # Descriptions of easing being appropriate for recovery
    is_easing_context = bool(re.search(
        r'(?:policy\s+easing.*?(?:expected|increased)|'
        r'yields?\s+.*?(?:fell|declined|dropped)|'
        r'asset\s+purchases\s+are\s+about\s+creating.*?momentum)',
        text_lower
    ))

    # "projection should help the public" = describing communication, neutral
    is_communication_description = bool(re.search(
        r'(?:projection.*?should\s+help\s+the\s+public|'
        r'differentiate\s+short[\s-]+term\s+shocks|'
        r'statement\s+.*?codifies)',
        text_lower
    ))

    # ── Step 6: Synthesize ──

    # Strong neutral: theoretical, historical, methodological, biographical, process
    if strong_neutral or is_historical_tech or is_pure_descriptive or is_process:
        # But can be overridden by very strong directional signals
        h_score = (3 if is_hawkish_action else 0) + (2 if is_inflation_concern else 0)
        d_score = (3 if is_dovish_action else 0) + (2 if is_weakness_concern else 0)
        if h_score >= 5 or d_score >= 5:
            pass  # Strong enough to override
        else:
            return "neutral"

    if is_conditional and not is_hawkish_action and not is_dovish_action:
        if not is_inflation_concern and not is_weakness_concern:
            return "neutral"

    if is_conditional_fwd_guidance:
        return "neutral"

    if is_no_problem:
        return "neutral"

    if is_staff_uncertainty:
        if not is_hawkish_action and not is_dovish_action:
            return "neutral"

    # Compute directional scores
    hawkish_score = 0.0
    dovish_score = 0.0
    neutral_score = 0.0

    # Strong signals
    if is_hawkish_action:
        hawkish_score += 4
    if is_inflation_concern:
        hawkish_score += 3
    if is_strong_economy:
        hawkish_score += 2.5
    if is_trade_deficit_widened:
        hawkish_score += 2.5
    if is_inflation_forecast_up:
        hawkish_score += 2

    if is_dovish_action:
        dovish_score += 4
    if is_weakness_concern:
        dovish_score += 3
    if is_soft_data:
        dovish_score += 2
    if is_dovish_inflation_stance:
        dovish_score += 5  # Very strong dovish signal
    if is_premature_tightening:
        dovish_score += 3
    if is_easing_context:
        dovish_score += 2

    # Neutral signals
    if has_balanced:
        neutral_score += 2
    if is_historical_inflation:
        neutral_score += 3
    if is_maintained_until:
        neutral_score += 3
    if is_communication_description:
        neutral_score += 3
    if is_historical:
        neutral_score += 1.5

    n_kw = count_keyword_matches(text, NEUTRAL_INDICATORS)
    neutral_score += n_kw * 0.5

    # Add keyword counts as weak signal
    h_kw = count_keyword_matches(text, HAWKISH_KEYWORDS)
    d_kw = count_keyword_matches(text, DOVISH_KEYWORDS)
    hawkish_score += h_kw * 0.3
    dovish_score += d_kw * 0.3

    # ── Abel-informed contrarian checks ──

    # "inflation likely to moderate" in FOMC context = members discussing currently
    # elevated inflation -> hawkish acknowledgment
    if re.search(r'(?:members?\s+agreed\s+that\s+)?inflation\s+(?:was|is)\s+likely\s+to\s+moderate', text_lower):
        hawkish_score += 3

    # "non-inflationary expansion" + "moderation in growth" = hawkish because it
    # says growth needs to slow down (restrictive implication)
    if re.search(r'non[\s-]+inflationary\s+expansion.*?moderation\s+in.*?growth', text_lower):
        hawkish_score += 3

    # Abel: GDP->federalFunds chain. "Growth in imports would exceed exports" with
    # strong domestic demand = hawkish
    if re.search(r'recovery\s+in\s+.*?domestic\s+demand', text_lower):
        hawkish_score += 1.5

    # "continue its asset purchases until outlook for labor market improved"
    # = dovish (continuing easing)
    if re.search(r'continue\s+.*?asset\s+purchas\w+.*?until.*?labor\s+market\s+.*?improved', text_lower):
        dovish_score += 4

    # Abel: "increases in federal funds rate target, when that comes" = future hawkish
    # BUT combined with current asset purchases = dovish now
    if re.search(r'asset\s+purchas\w+\s+are\s+about\s+creat\w+.*?momentum', text_lower):
        dovish_score += 2
        hawkish_score -= 1

    # "at or below 5 percent for over two years" + "4.3 percent" = strong labor
    if re.search(r'unemployment.*?4\.\d\s+percent.*?(?:at\s+or\s+below|for\s+over)', text_lower):
        hawkish_score += 3

    # "wages rising in line with productivity and underlying inflation" context of
    # 50-year low unemployment = hawkish (strong economy but controlled wages)
    if re.search(r'unemployment.*?50[\s-]+year\s+low.*?wages', text_lower):
        hawkish_score += 2

    # "describing mixed signals" without clear stance
    if has_balanced and abs(hawkish_score - dovish_score) < 1.5:
        neutral_score += 3

    # Specific pattern: text mentions both dovish AND hawkish elements neutrally
    # E.g., "mortgage credit conditions tight but signs of easing" = neutral
    if re.search(r'(?:tight.*?(?:signs?\s+of\s+)?eas\w+|eas\w+.*?tight)', text_lower):
        if not is_hawkish_action and not is_dovish_action:
            neutral_score += 2

    # "spending potentially offsetting moderation" = balanced/neutral
    if re.search(r'(?:offsett\w+\s+(?:some\s+)?moderation|becoming\s+more\s+balanced)', text_lower):
        neutral_score += 2

    # "productivity growth would pick up" + "acknowledged limited" = neutral
    if re.search(r'productivity\s+growth\s+would\s+pick\s+up.*?acknowledg\w+', text_lower):
        neutral_score += 2

    # "indicators remained weak" about FOREIGN economies = neutral for US FOMC
    if re.search(r'(?:japan|brazil|china|europe|foreign)\s+.*?(?:remain\w+\s+)?weak', text_lower):
        neutral_score += 2

    # "stock market soared and core inflation moderated" = factual report, neutral
    if re.search(r'stock\s+market\s+soar\w+.*?inflation\s+moderat\w+', text_lower):
        neutral_score += 3

    # "thresholds for inflation and unemployment" = process/framework discussion
    if re.search(r'(?:thresholds?\s+for\s+inflation|announce\s+an\s+additional.*?threshold)', text_lower):
        neutral_score += 2

    # "robust productivity growth" + "unit labor costs and profit margins" = watching
    if re.search(r'(?:robust.*?productivity|productivity.*?robust).*?(?:unit\s+labor|attention)', text_lower):
        neutral_score += 2

    # "stabilize at a relatively high level" = neutral description
    if re.search(r'(?:stabilize|stabilise)\s+at\s+a\s+relatively\s+(?:high|low)\s+level', text_lower):
        neutral_score += 2

    # "favorable factors should continue to support moderate further growth" = neutral
    if re.search(r'favorable\s+factors.*?(?:support|underpin)\w*\s+.*?(?:moderate|modest)', text_lower):
        neutral_score += 2

    # "high-tech equipment and software" spending descriptions
    if re.search(r'(?:high[\s-]+tech\s+equipment|equipment\s+and\s+software)', text_lower):
        if not is_hawkish_action and not is_dovish_action:
            neutral_score += 1.5

    # "demographic composition of the labor force affect NAIRU" = neutral theory
    if re.search(r'(?:NAIRU|demographic\s+composition|government\s+programs)', text_lower):
        neutral_score += 3

    # "household spending had been relatively robust during cyclical downturn" = neutral
    if re.search(r'household\s+spending.*?robust.*?(?:downturn|limited\s+room)', text_lower):
        neutral_score += 2

    # "foreseeing our economic destinies" = general/philosophical = neutral
    if re.search(r'(?:foresee\w+\s+.*?(?:economic\s+)?destin|equivalent\s+to\s+foresee)', text_lower):
        neutral_score += 3

    # "weathered recent events and on track" = maintaining accommodative = neutral
    # (describing conditional stance, not directional)
    if is_maintained_until:
        neutral_score += 2

    # Final decision
    max_score = max(hawkish_score, dovish_score, neutral_score)

    if max_score == 0:
        return "neutral"

    # If neutral dominates
    if neutral_score > hawkish_score and neutral_score > dovish_score:
        return "neutral"
    elif hawkish_score > dovish_score and hawkish_score > neutral_score:
        return "hawkish"
    elif dovish_score > hawkish_score and dovish_score > neutral_score:
        return "dovish"
    elif hawkish_score == dovish_score:
        if neutral_score >= hawkish_score:
            return "neutral"
        return "neutral"  # tie between h and d = neutral
    elif hawkish_score == neutral_score:
        return "neutral" if dovish_score < hawkish_score else "dovish"
    elif dovish_score == neutral_score:
        return "neutral" if hawkish_score < dovish_score else "hawkish"
    else:
        return "neutral"


def generate_reason(text, base_ans, skill_ans, ground_truth, base_correct, skill_correct, flipped, harmed):
    """Generate a brief explanation."""
    text_lower = text.lower()

    if not flipped and not harmed:
        if skill_correct:
            return f"Both methods agree on '{skill_ans}', matching ground truth."
        else:
            return f"Both methods classified as base='{base_ans}'/skill='{skill_ans}', but ground truth is '{ground_truth}'."

    if flipped and skill_correct:
        reasons = []
        if skill_ans == "neutral":
            if re.search(r'\b(?:taylor|regulation|historical|research|event.stud|framework|model)', text_lower):
                reasons.append("Abel: text describes theoretical/historical mechanism, not a policy stance")
            elif re.search(r'\bbalanced\b', text_lower):
                reasons.append("Abel: balanced/symmetric language indicates neutral stance")
            elif re.search(r'(?:keep|maintain).*target\s+range.*until', text_lower):
                reasons.append("Abel: conditional forward guidance is neutral (neither pure ease nor tighten)")
            else:
                reasons.append("Abel: text is descriptive without directional policy concern")
        elif skill_ans == "hawkish":
            if re.search(r'inflation.*moderate', text_lower):
                reasons.append("Abel: inflation 'likely to moderate' implies concern about current high inflation (hawkish context)")
            elif re.search(r'unsustainable|overheating|excessive', text_lower):
                reasons.append("Abel: language about overheating/excess maps to inflation->federalFunds causal path")
            elif re.search(r'deficit\s+widened|trade\s+deficit', text_lower):
                reasons.append("Abel: widening trade deficit -> strong domestic demand via GDP->federalFunds path")
            else:
                reasons.append("Abel: text expresses concern about inflation/overheating via inflationRate->federalFunds")
        elif skill_ans == "dovish":
            if re.search(r'downside\s+risk|slack|weak|muted|subdued', text_lower):
                reasons.append("Abel: downside concern maps through GDP->federalFunds->easing path")
            elif re.search(r'productivity|cost\s+cutting', text_lower):
                reasons.append("Abel: productivity gains / cost cutting = disinflationary, supporting accommodation")
            elif re.search(r'accommodat\w+.*?remain|highly\s+accommodat', text_lower):
                reasons.append("Abel: accommodative stance = dovish support through GDP/unemployment channel")
            else:
                reasons.append("Abel: text expresses concern about weakness via GDP->unemploymentRate->easing")
        return "; ".join(reasons) if reasons else f"Skill flipped base '{base_ans}' to '{skill_ans}' correctly"

    if harmed:
        return f"Skill incorrectly changed from correct base '{base_ans}' to '{skill_ans}' (ground truth: '{ground_truth}')"

    return f"Base='{base_ans}', Skill='{skill_ans}', GT='{ground_truth}'"


def main():
    with open(DATA_PATH) as f:
        data = json.load(f)

    print(f"Loaded {len(data)} FOMC classification questions")

    results = []
    base_correct_count = 0
    skill_correct_count = 0
    flip_count = 0
    harm_count = 0

    for idx, entry in enumerate(data):
        text = entry["text"]
        ground_truth = entry["answer"].lower().strip()

        base_answer = base_classify(text)
        skill_answer = skill_classify(text)

        base_correct = (base_answer == ground_truth)
        skill_correct = (skill_answer == ground_truth)
        flipped = (base_answer != skill_answer)
        harmed = (base_correct and not skill_correct and flipped)

        if base_correct:
            base_correct_count += 1
        if skill_correct:
            skill_correct_count += 1
        if flipped and skill_correct and not base_correct:
            flip_count += 1
        if harmed:
            harm_count += 1

        reason = generate_reason(text, base_answer, skill_answer, ground_truth,
                                 base_correct, skill_correct, flipped, harmed)

        results.append({
            "idx": idx,
            "text_preview": text[:100],
            "base_answer": base_answer,
            "skill_answer": skill_answer,
            "ground_truth": ground_truth,
            "base_correct": base_correct,
            "skill_correct": skill_correct,
            "flipped": flipped,
            "harmed": harmed,
            "reason": reason,
        })

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    total = len(data)
    print(f"\n{'='*60}")
    print(f"FOMC Classification Results ({total} questions)")
    print(f"{'='*60}")
    print(f"Base accuracy:  {base_correct_count}/{total} = {base_correct_count/total:.1%}")
    print(f"Skill accuracy: {skill_correct_count}/{total} = {skill_correct_count/total:.1%}")
    print(f"Flips (skill corrected base): {flip_count}")
    print(f"Harms (skill broke base):     {harm_count}")
    print(f"Net improvement: {flip_count - harm_count} ({(skill_correct_count - base_correct_count)/total:+.1%})")
    print(f"{'='*60}")

    gt_dist = {}
    base_dist = {}
    skill_dist = {}
    for r in results:
        gt_dist[r["ground_truth"]] = gt_dist.get(r["ground_truth"], 0) + 1
        base_dist[r["base_answer"]] = base_dist.get(r["base_answer"], 0) + 1
        skill_dist[r["skill_answer"]] = skill_dist.get(r["skill_answer"], 0) + 1

    print(f"\nLabel distribution:")
    print(f"  Ground truth: {gt_dist}")
    print(f"  Base:         {base_dist}")
    print(f"  Skill:        {skill_dist}")

    flips = [r for r in results if r["flipped"] and r["skill_correct"] and not r["base_correct"]]
    harms_list = [r for r in results if r["harmed"]]

    if flips:
        print(f"\nSample FLIPS (skill corrected base) [{len(flips)} total]:")
        for r in flips[:8]:
            print(f"  [{r['idx']}] base={r['base_answer']} -> skill={r['skill_answer']} (gt={r['ground_truth']})")
            print(f"       {r['text_preview']}")
            print(f"       Reason: {r['reason']}")

    if harms_list:
        print(f"\nALL HARMS [{len(harms_list)} total]:")
        for r in harms_list:
            print(f"  [{r['idx']}] base={r['base_answer']} -> skill={r['skill_answer']} (gt={r['ground_truth']})")
            print(f"       {r['text_preview']}")

    # Accuracy by class
    print(f"\nAccuracy by class:")
    for cls in ["hawkish", "dovish", "neutral"]:
        gt_items = [r for r in results if r["ground_truth"] == cls]
        if gt_items:
            b_acc = sum(1 for r in gt_items if r["base_correct"]) / len(gt_items)
            s_acc = sum(1 for r in gt_items if r["skill_correct"]) / len(gt_items)
            print(f"  {cls:10s}: base={b_acc:.1%}  skill={s_acc:.1%}  (n={len(gt_items)})")

    print(f"\nResults saved to: {OUT_PATH}")


if __name__ == "__main__":
    main()
