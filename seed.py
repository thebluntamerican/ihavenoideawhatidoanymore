"""Populate the directory with a few example profiles, for local development.

Run:  .venv/bin/python seed.py
These are invented people. Delete them before you launch.
"""
import json
from sqlalchemy import select
from app.db import SessionLocal, Profile, init_db, make_slug, new_token
from app.taxonomy import plurality_score

PEOPLE = [
    dict(name="Priyanka Raghunathan", location="Remote / Lisbon",
         headline="Still owns retention. Now also builds the flows she used to brief out.",
         former_life="Head of Retention",
         former_life_detail="Nine years in lifecycle and CRM, still doing it",
         now_doing=["Build the flows I used to brief out", "Make messy data usable",
                    "Build agents", "Automate the repetitive stuff",
                    "Prototype in an afternoon"],
         stack=["Claude", "Claude Code", "SQL", "Airtable", "n8n"],
         open_to=["Fractional work", "Advisory"],
         superpower="Shipping the winback sequence in an afternoon instead of a quarter.",
         still_cant="Explain to my CEO why this isn't just 'using ChatGPT'."),
    dict(name="Tobias Vandermeer", location="Amsterdam",
         headline="Runs marketing for a \u00a3400m brand. Also prototypes the product now.",
         former_life="CMO", former_life_detail="Three companies, one of them twice",
         now_doing=["Prototype the product myself", "Do the strategy",
                    "Write the AI strategy", "Make the decks",
                    "Ship software I never learned to write", "Build it instead of buying it",
                    "Advise people who've done it longer"],
         stack=["Claude", "Cursor", "Figma", "n8n", "SQL"],
         open_to=["Advisory", "Consulting projects", "Co-founding something"],
         superpower="Settling a six-month roadmap argument by building the thing on Sunday.",
         still_cant="Sit through an agency credentials deck without visibly ageing."),
    dict(name="Emeka Brannigan-Adeyemi", location="Dublin",
         headline="Still signs off the accounts. Also runs finance from a terminal.",
         former_life="CFO", former_life_detail="Big four, then a startup, then this",
         now_doing=["Run finance from the terminal", "Make messy data usable",
                    "Automate my own job", "Build it instead of buying it",
                    "Do the research", "Run the ops", "Fix it when it breaks",
                    "Do the hiring", "Build agents"],
         stack=["Claude", "Claude Code", "Python", "SQL", "Railway", "Excel (still)"],
         open_to=["Fractional work", "Co-founding something"],
         superpower="Closing the month in two days because the reconciliation runs itself.",
         still_cant="Take a holiday without checking the pipeline."),
    dict(name="Callum Ferreira-Nowak", location="Manchester",
         headline="Runs a 40-person company. Also built the second brain it runs on.",
         former_life="CEO", former_life_detail="Second time doing this, first time enjoying it",
         now_doing=["Build my own second brain", "Write the AI strategy",
                    "Do the research", "Prototype in an afternoon", "Teach people this"],
         stack=["Claude", "Claude Code", "Notion", "Gemini", "A notebook (paper)"],
         open_to=["Advisory", "Collaborating for fun"],
         superpower="Answering board questions in the meeting, because the data is already there.",
         still_cant="Convince my chair that this isn't a phase."),
    dict(name="Marguerite Okonjo-Bell", location="London",
         headline="Still practising. Also builds the tools the firm refused to buy.",
         former_life="Lawyer", former_life_detail="11 years, two firms, thousands of contracts",
         now_doing=["Do the legal", "Ship software I never learned to write",
                    "Build agents", "Automate my own job", "Teach people this"],
         stack=["Claude", "Claude Code", "Python", "Excel (still)"],
         open_to=["Fractional work", "Advisory"],
         superpower="Turning a 90-page contract into something a machine can act on.",
         still_cant="Explain my job to my mother. Or CSS."),
    dict(name="Ingrid Solheim-Baptiste", location="Oslo",
         headline="Fifteen years teaching Year 6. Turns out that's excellent training for this.",
         former_life="Teacher", former_life_detail="Primary, still in the classroom",
         now_doing=["Teach people this", "Design things", "Make the videos",
                    "Translate between humans and machines"],
         stack=["Claude", "Notion", "Figma"],
         open_to=["Nothing, I'm just here for the company"],
         superpower="Explaining a hard thing to someone who decided in advance to be bored.",
         still_cant="Stop counting people as I walk into a room."),
]


def run():
    init_db()
    with SessionLocal() as s:
        for row in PEOPLE:
            if s.scalar(select(Profile).where(Profile.name == row["name"])):
                print(f"  skip  {row['name']} (already here)")
                continue
            p = Profile(
                slug=make_slug(row["name"], s), name=row["name"],
                headline=row["headline"], location=row["location"],
                former_life=row["former_life"],
                former_life_detail=row["former_life_detail"],
                now_doing_json=json.dumps(row["now_doing"]),
                stack_json=json.dumps(row["stack"]),
                open_to_json=json.dumps(row["open_to"]),
                superpower=row["superpower"], still_cant=row["still_cant"],
                contact_email=f"{row['name'].split()[0].lower()}@example.com",
                edit_token=new_token(),
                plurality=plurality_score(row["now_doing"]),
            )
            s.add(p)
            print(f"  added {p.name}  ({p.plurality}x plural)")
        s.commit()


if __name__ == "__main__":
    run()
