"""The vocabulary of the site.

Two lists do the heavy lifting:
  FORMER_LIVES  - the job you had when jobs still meant something
  NOW_DOING     - the things you actually do on a Tuesday

Everything else (the Plurality Score, the generated title, the filters)
is derived from those two.
"""

# --- The job you still have -------------------------------------------------
# Present tense, deliberately. Almost nobody here has left their job - they
# added to it. The CMO is still the CMO; she also prototypes the product now.
# This is the title on the email signature, not a past life.
FORMER_LIVES = [
    "Lawyer",
    "CEO",
    "CMO",
    "CFO",
    "COO",
    "Head of Retention",
    "Marketing Manager",
    "Salesperson",
    "Management Consultant",
    "Investment Banker",
    "Journalist",
    "Teacher",
    "Doctor",
    "Nurse",
    "Academic",
    "Accountant",
    "Architect",
    "Recruiter",
    "Copywriter",
    "Graphic Designer",
    "Product Manager",
    "Operations Manager",
    "Software Engineer",
    "Data Analyst",
    "Chef",
    "Musician",
    "Actor",
    "Civil Servant",
    "Estate Agent",
    "Therapist",
    "Photographer",
    "Retail Buyer",
    "Founder",
    "Something with no clean name",
]

# --- What you added on top of it --------------------------------------------
# The things that are NOT in the job description. Verbs, and specific ones -
# "builds the flows she used to brief out" is the whole idea in one line.
NOW_DOING = [
    "Build the flows I used to brief out",
    "Prototype the product myself",
    "Ship software I never learned to write",
    "Run finance from the terminal",
    "Write the AI strategy",
    "Build my own second brain",
    "Build agents",
    "Automate the repetitive stuff",
    "Automate my own job",
    "Make messy data usable",
    "Do the research",
    "Do the strategy",
    "Do the legal",
    "Do the hiring",
    "Run the ops",
    "Design things",
    "Write things",
    "Sell things",
    "Make the videos",
    "Make the decks",
    "Teach people this",
    "Translate between humans and machines",
    "Fix it when it breaks",
    "Advise people who've done it longer",
    "Prototype in an afternoon",
    "Build it instead of buying it",
]

# --- The tools you actually have open ---------------------------------------
STACK = [
    "Claude", "ChatGPT", "Gemini", "Claude Code", "Cursor", "Copilot",
    "Replit", "Lovable", "v0", "n8n", "Zapier", "Make", "Figma",
    "Notion", "Airtable", "Supabase", "Railway", "Vercel", "Python",
    "SQL", "Excel (still)", "A notebook (paper)",
]

# --- What you're open to ----------------------------------------------------
OPEN_TO = [
    "Full-time roles",
    "Fractional work",
    "Advisory",
    "Consulting projects",
    "Co-founding something",
    "Collaborating for fun",
    "Nothing, I'm just here for the company",
]

# Only these mean "you may contact me about work".
HIREABLE = {
    "Full-time roles", "Fractional work", "Advisory",
    "Consulting projects", "Co-founding something",
}


def plurality_score(now_doing):
    """How many things this person does BEYOND the job title. The joke, quantified.

    Capped at 10 so nobody wins by ticking every box, and floored at 1 so
    nobody reads as a zero.
    """
    return max(1, min(10, len(now_doing)))


PLURALITY_LABELS = [
    (1, "Focused", "One thing, done properly. Nothing wrong with that."),
    (2, "Two-Track", "The edges have started to blur."),
    (3, "Slashie", "Your job title now needs a slash in it."),
    (4, "Multi-Tool", "Whatever the week needs, you can be it."),
    (5, "Fully Plural", "Five jobs, one person, no good word for it yet."),
    (7, "Load-Bearing", "If you stopped, three departments would notice."),
    (9, "Whole Department", "No org chart fits you. That's their problem, not yours."),
]


def plurality_label(score):
    """Return (label, blurb) for a score."""
    match = PLURALITY_LABELS[0]
    for threshold, label, blurb in PLURALITY_LABELS:
        if score >= threshold:
            match = (threshold, label, blurb)
    return match[1], match[2]


# Fragments used to mint an absurd-but-accurate job title from a profile.
TITLE_PREFIX = [
    "Full-Stack ", "Hybrid ", "Multi-Threaded ", "Second-Act ",
    "Composite ", "Unclassifiable ",
]
TITLE_SUFFIX = [
    " Who Also Ships Code", " With A Terminal Open", " (Load-Bearing)",
    " And Four Other Jobs", " Turned Systems Thinker", " At Large",
]
