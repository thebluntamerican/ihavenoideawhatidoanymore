"""Populate the directory with a few example profiles, for local development.

Run:  .venv/bin/python seed.py
These are invented people. Delete them before you launch.
"""
import json
from sqlalchemy import select
from app.db import SessionLocal, Profile, init_db, make_slug, new_token
from app.taxonomy import plurality_score

PEOPLE = [
    dict(name="Marguerite Okonjo-Bell", location="London",
         headline="Ex-litigator who now builds the tools the firm refused to buy.",
         former_life="Lawyer", former_life_detail="11 years, two firms, one burnout",
         now_doing=["Ship software I never learned to write", "Do the legal",
                    "Build agents", "Automate my own job", "Teach people this"],
         stack=["Claude", "Claude Code", "Python", "Excel (still)"],
         open_to=["Fractional work", "Advisory"],
         superpower="Reading a 90-page contract and turning it into something a machine can act on.",
         still_cant="Explain my job to my mother. Or CSS."),
    dict(name="Tobias Vandermeer", location="Amsterdam",
         headline="Ran marketing for a £400m brand. Now mostly writes Python at midnight.",
         former_life="CMO", former_life_detail="Three companies, one of them twice",
         now_doing=["Do the strategy", "Automate other people's jobs", "Make the decks",
                    "Do the research", "Prototype in an afternoon", "Say no to consultants",
                    "Advise people older than me"],
         stack=["Claude", "Cursor", "n8n", "Figma", "SQL"],
         open_to=["Advisory", "Consulting projects", "Co-founding something"],
         superpower="Killing a six-month roadmap in one afternoon by just building the thing.",
         still_cant="Sit through a agency credentials deck without visibly ageing."),
    dict(name="Priyanka Raghunathan", location="Remote / Lisbon",
         headline="Sold enterprise software for a decade. Now I build what I used to promise.",
         former_life="Salesperson", former_life_detail="Enterprise SaaS, quota-carrying, 9 years",
         now_doing=["Sell things", "Build agents", "Clean data nobody else will touch",
                    "Fix it when it breaks at 2am"],
         stack=["ChatGPT", "Claude", "Airtable", "Supabase", "Zapier"],
         open_to=["Full-time roles", "Fractional work"],
         superpower="Knowing exactly which part of the demo is a lie, because I used to write it.",
         still_cant="Stop opening the CRM out of habit."),
    dict(name="Callum Ferreira-Nowak", location="Manchester",
         headline="Newsroom refugee. Now somewhere between researcher, editor and engineer.",
         former_life="Journalist", former_life_detail="Local, then national, then neither",
         now_doing=["Write things", "Do the research", "Make the videos",
                    "Translate between humans and machines", "Teach people this"],
         stack=["Claude", "Gemini", "Notion", "A notebook (paper)"],
         open_to=["Consulting projects", "Collaborating for fun"],
         superpower="Finding the one number in a 200-page report that changes the story.",
         still_cant="Write a headline I don't hate by Thursday."),
    dict(name="Ingrid Solheim-Baptiste", location="Oslo",
         headline="Taught Year 6 for fifteen years. Turns out that's excellent training for this.",
         former_life="Teacher", former_life_detail="Primary, 15 years, still have the laminator",
         now_doing=["Teach people this", "Design things", "Run the ops", "Do the hiring"],
         stack=["Claude", "Notion", "Figma"],
         open_to=["Nothing, I'm just here for the company"],
         superpower="Explaining a hard thing to someone who has decided in advance to be bored.",
         still_cant="Stop counting people as I walk into a room."),
    dict(name="Emeka Brannigan-Adeyemi", location="Dublin",
         headline="Was an accountant. Now I do six jobs and the accounts are the easy one.",
         former_life="Accountant", former_life_detail="Big four, then a startup, then chaos",
         now_doing=["Do the finance", "Run the ops", "Automate my own job",
                    "Clean data nobody else will touch", "Prototype in an afternoon",
                    "Ship software I never learned to write", "Do the hiring",
                    "Fix it when it breaks at 2am", "Say no to consultants"],
         stack=["Claude", "Claude Code", "Python", "SQL", "Railway", "Excel (still)"],
         open_to=["Fractional work", "Co-founding something"],
         superpower="Building the internal tool three weeks before anyone agrees we need it.",
         still_cant="Take a holiday without checking the pipeline."),
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
