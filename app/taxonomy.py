"""The vocabulary of the site.

Two lists do the heavy lifting:
  FORMER_LIVES  - the job you had when jobs still meant something
  NOW_DOING     - the things you actually do on a Tuesday

Everything else (the Plurality Score, the generated title, the filters)
is derived from those two.
"""

# --- Who you used to be -----------------------------------------------------
# Deliberately specific. "Lawyer" lands; "professional services" does not.
FORMER_LIVES = [
    "Lawyer",
    "CMO",
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
    "Software Engineer",
    "Data Analyst",
    "Chef",
    "Musician",
    "Actor",
    "Police Officer",
    "Soldier",
    "Civil Servant",
    "Estate Agent",
    "Therapist",
    "Translator",
    "Photographer",
    "Retail Buyer",
    "Founder",
    "Something I can no longer explain",
]

# --- What you actually do now -----------------------------------------------
# Verbs, not titles. Titles are the thing that broke.
NOW_DOING = [
    "Ship software I never learned to write",
    "Design things",
    "Write things",
    "Sell things",
    "Build agents",
    "Automate other people's jobs",
    "Automate my own job",
    "Clean data nobody else will touch",
    "Do the research",
    "Do the strategy",
    "Do the finance",
    "Do the legal",
    "Do the hiring",
    "Run the ops",
    "Make the videos",
    "Make the decks",
    "Teach people this",
    "Translate between humans and machines",
    "Fix it when it breaks at 2am",
    "Advise people older than me",
    "Prototype in an afternoon",
    "Say no to consultants",
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
    """How many distinct things this person does. The whole joke, quantified.

    Capped at 10 so nobody wins by ticking every box, and floored at 1 so
    nobody reads as a zero.
    """
    return max(1, min(10, len(now_doing)))


PLURALITY_LABELS = [
    (1, "Monogamous", "You still have a job title. Enjoy it while it lasts."),
    (2, "Dabbling", "The edges are starting to blur."),
    (3, "Slashie", "You now need a slash in your job title."),
    (4, "Unclassifiable", "HR has stopped trying to categorise you."),
    (5, "Fully Plural", "You are several people in a trench coat."),
    (7, "Load-Bearing", "If you stopped, three departments would notice."),
    (9, "Feral", "There is no org chart that contains you."),
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
    "Post-", "Recovering ", "Semi-retired ", "Formerly-", "Ex-", "Reformed ",
]
TITLE_SUFFIX = [
    "-Adjacent Operator", " Who Now Ships Code", " Turned Systems Person",
    " With A Terminal Open", " (Load-Bearing)", " At Large",
]
