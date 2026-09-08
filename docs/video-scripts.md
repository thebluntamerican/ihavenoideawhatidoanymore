# Videos for ihavenoideawhatidoanymore.com

Three films, in the order they earn their keep. Each is written to be shot on a
phone or generated in a text-to-video tool — no crew, no budget, no location.

The site already ships two motion pieces in code (the drifting-word hero and the
job-title slot machine). These are the ones that need a camera or a generator.

A note on the register: the joke is **recognition, not mockery**. Everyone in
these films is good at their job. That's the problem. Play it deadpan and let
the audience laugh; play it wacky and it dies.

---

## 1. "The Handover" — 35s — the launch film

The one you post first. It has to make a stranger feel seen in nine seconds.

| # | Shot | Duration | Audio |
|---|------|----------|-------|
| 1 | Extreme close-up: a business card being slid across a desk. It reads **SENIOR ASSOCIATE, LITIGATION**. | 2s | Room tone. A clock. |
| 2 | Same hand picks it up, turns it over. Back is blank. | 2s | — |
| 3 | Hard cut. Same person, same desk, different light. Three monitors now. Terminal open. Same suit, no tie. | 2s | A single keystroke. |
| 4 | Close-up: they're writing on the back of the card in biro. We see fragments: "builds th—", "does the—", "sort of—". Each one crossed out. | 5s | Biro scratch, amplified. |
| 5 | Cut to a different person entirely. Kitchen table. Card reads **CHIEF MARKETING OFFICER**. Same blank back. Same biro. | 3s | — |
| 6 | Rapid montage, 6 cuts, ~0.5s each: six people, six cards, six blank backs. Teacher. Accountant. Journalist. Chef. Nurse. Salesperson. | 3s | Each cut lands on a beat. Tempo builds. |
| 7 | Cut to black. Silence for a full beat — longer than feels safe. | 1.5s | Nothing. |
| 8 | White type on black, one line at a time: "You still know how to do your job." | 2s | — |
| 9 | "You just can't say what it is." | 2s | — |
| 10 | Cut to the site's hero animation, screen-recorded — the headline cycling *do → am → sell → charge*. | 4s | Music returns, single sustained note. |
| 11 | Card back, finally written on, held to camera. It just says the URL. | 4s | — |
| 12 | End card: **ihavenoideawhatidoanymore.com** on the cream paper background. Under it, small: "A directory of plural people." | 3s | Note resolves. |

**Casting**: six real people, not actors. Ask them to hold their own old
business card if they still have one. Several will, and that's the shot.

**The one rule**: nobody smiles at the camera until shot 11.

---

## 2. "So What Do You Do?" — 15s — the social loop

Vertical. Built to loop seamlessly, so the last frame matches the first.

**Setup**: a dinner party. Two people. One asks the question.

- **0.0s** — Wide, over the shoulder. Friendly stranger: *"So what do you do?"*
- **0.5s** — Cut to our person. They open their mouth.
- **0.7s** — **Freeze frame.** Everything stops. A caption appears in the site's
  mono type, top of frame: `PROCESSING`.
- **1.0–9.0s** — The freeze holds. Over it, lines type on and delete, one after
  another, each one abandoned mid-thought:
  ```
  I'm in legal—  no.
  I build—  well, I don't "build", I—
  It's sort of operations but also—
  I used to be a lawyer?
  I do about six thi—
  ```
  Every line deletes itself. The typing gets faster and less confident.
- **9.5s** — Freeze releases. Our person, out loud, flat: *"Consulting."*
- **10.5s** — The stranger, satisfied: *"Ah, nice."* They turn away.
- **11.5s** — Hold on our person's face. They know what they just did.
- **12.5s** — Mono caption, bottom: `there is a better answer.`
- **13.5s** — URL. Cut back to the wide shot so it loops.

**Why it works**: everyone who qualifies for this site has given the dishonest
four-second answer this week. This is the whole product in fifteen seconds.

---

## 3. "Profile Card" — 10s — the template you reuse forever

Not one film. A **format** you re-render for every member. This is the growth
engine: people share the one with their own name on it.

Storyboard, 10 seconds, vertical, all typography — no camera needed:

1. **0–1.5s** — Cream background. A single black word types on: their old job.
   `LAWYER`
2. **1.5–2.5s** — It glitches, using the same shake as the site's headline, and
   shatters into the things they actually do — one per line, arriving fast:
   ```
   ships software
   does the legal
   builds agents
   automates her own job
   teaches this
   ```
3. **2.5–5.5s** — Lines stack until they overflow the frame.
4. **5.5–7s** — Everything collapses to one number, huge, in signal orange:
   **5**
   Underneath, in mono: `PLURALITY SCORE`
5. **7–8.5s** — The label lands with a stamp effect: **FULLY PLURAL**
   Small print: *"You are several people in a trench coat."*
6. **8.5–10s** — Their name, then the URL.

**Make it automatable.** Every value in that list already exists on the profile
page — former life, the doing list, the score, the label. Build it once as an
HTML page that reads `/p/{slug}`, then screen-record it per member (or render
frames headlessly). One template, unlimited films, and each one is a person
posting about themselves.

Do this third, but design it first — it's the only one that compounds.

---

## Production notes

**If you're shooting it.** Films 1 and 2 are a phone, a window, and one
afternoon. Shoot everything at 60fps so the freeze-frames are clean. Get more
coverage of hands than you think you need — hands carry both films.

**If you're generating it.** Films 1 and 2 have a fatal weakness for
text-to-video: faces and legible text are exactly what those tools do worst, and
both scripts depend on both. Generate the B-roll (desks, monitors, kitchen
tables, hands) and lay the type over it yourself. Film 3 is pure typography, so
build it in code or After Effects, never a generator.

**Type and colour** — matching the site exactly:

| Use | Value |
|---|---|
| Display | Instrument Serif |
| Machine voice / captions | IBM Plex Mono, uppercase, `.16em` letter-spacing |
| Paper | `#F2EEE4` |
| Ink | `#12110F` |
| Signal (the one accent) | `#FF4A1C` |
| Acid (highlights, stamps) | `#D9FF3D` |

**Sound**: one sustained note and real room tone beats a music bed. The silence
in shot 7 of film 1 is doing more work than any track would.

**Captions**: burn them in. Most of this plays on mute.
