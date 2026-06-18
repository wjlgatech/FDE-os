*Delta — Part 1 of The Last Mile, a series on Forward Deployed Engineering*

# The French Restaurant and the Spy Agency

## How Palantir invented the most copied job in AI — and why almost everyone copies it wrong

Picture a great French restaurant. Not a chain — a real one, where the waiter knows which table is celebrating an anniversary and which one is a first date that's going badly. Watch what the waitstaff actually do. They aren't a delivery layer bolted onto the kitchen. They *are* the kitchen, pushed forward into the dining room. They taste the dish before it goes out. They read the room. They walk back and tell the chef the duck is too salty for table six, and the chef *changes the duck*. The service isn't separate from the product. The service is part of how the food gets made.

That image — according to people who were there — is where one of the most valuable and most misunderstood jobs in technology was born.

Palantir's co-founder Alex Karp reportedly looked at how excellent French restaurants operate and drew a conclusion most software companies would have called heresy: **the delivery mechanism has to be part of the product, and it has to be opinionated.** As Ted Mabrey, Palantir's head of global commercial, put it, "The waitstaff is an intrinsic part of the kitchen... the delivery mechanism has to be a part of the product." ([Mabrey, "Sorry, that isn't an FDE," 2024](https://tedmabrey.substack.com/p/sorry-that-isnt-an-fde))

The role that came out of that conviction is the Forward Deployed Engineer. Today every frontier AI lab — Anthropic, OpenAI, Google — is hiring them as fast as they can. a16z calls it the hottest job in startups. Over 100 YC companies are building around it. But to understand why it's suddenly everywhere, you have to start with the spy agency.

## "Get on a plane first, ask questions later"

Rewind to 2006. Palantir is a tiny, strange company trying to sell software to intelligence agencies — customers who, by definition, cannot tell you what they actually do. You can't email a CIA analyst a requirements questionnaire. The work is classified, the workflows live in people's heads, and the real problem is buried under three layers of bureaucracy and one layer of "we can't talk about that."

Traditional enterprise software has an answer for this, and the answer is bad: gather requirements, build to spec, ship, and act surprised when the customer says it solves the wrong problem. The flaw is structural. A requirements document is a flattened, lossy compression of a reality the customer can't fully articulate in the first place.

Palantir's employee number thirteen, Shyam Sankar, made a different bet. Instead of pulling the problem back to headquarters, he pushed the engineers forward — onto the customer's site, into the actual room where the work happened. Sankar became, in Palantir's telling, the first Forward Deployed Engineer, "pioneering the company's definitional engineering model." ([Shyam Sankar bio](https://www.shyamsankar.com/about)) The term itself was borrowed from the military, where "forward deployed" means operating at the point of action, not from a base in the rear. Internally, Palantir gave the role a codename you should remember, because it's the name of this series: **Delta.**

The guiding principle, as eight-year Palantir veteran Nabeel Qureshi later described it, came from the economist Tyler Cowen: *"context is that which is scarce."* The most valuable thing in enterprise software isn't the code. It's the tacit knowledge of how a messy, political, real organization actually works — knowledge that only exists on site, in the building, next to the person doing the job. Palantir's cultural bias became blunt to the point of comedy: **"get on a plane first, ask questions later."** ([Qureshi, "Reflections on Palantir," 2024](https://nabeelqu.co/reflections-on-palantir))

## Two kinds of engineers

Here's the part most people miss. The Forward Deployed Engineer only works as one half of a pair.

Qureshi describes Palantir as split into two types of engineers. There were the engineers who worked with customers — the FDEs, the Deltas — who went on site three or four days a week and built whatever solved the problem in front of them. And there were the engineers who worked on the core product, the "PD" team, who rarely visited a customer at all. The official Palantir framing draws the line cleanly: *"A Dev's focus is one capability, many customers, while a Delta's focus is one customer, many capabilities."* ([Palantir, "Dev versus Delta"](https://blog.palantir.com/dev-versus-delta-demystifying-engineering-roles-at-palantir-ad44c2a6e87))

Read that twice, because the whole machine is in that sentence.

The Delta goes deep on *one customer* and makes everything work for them — fast, hacky, duct-taped if necessary. The Dev goes wide across *many customers* and turns the best of those hacks into clean, scalable product. The Delta writes code that gets the job done by Friday. The Dev writes code that survives a million users. Qureshi names this directly: FDEs produce "technical debt and hacky workarounds," PD engineers "write software that scales cleanly," and the secret of the company is that **deep enterprise value requires both at once.**

It is, by design, a deeply uncomfortable arrangement. Mabrey doesn't sugarcoat it: "The FDE has a conflict-riddled relationship with core product teams defined by constant contradictions. FDEs are encouraged to build custom software. Devs are encouraged to forget their roadmaps to swarm high value opportunities. Devs are also encouraged to ignore FDEs... This is a very messy way to build product. It is also the only way we have discovered to do it."

Think of it like a river delta — the other meaning of the name. A river carries sediment for a thousand miles, and at the delta, where it finally meets the sea, all that accumulated material gets deposited and the land turns green. The FDE is the place where everything the company learns in the field gets deposited into the product. The mess is where things grow.

## The mess that built a $200-billion company

It would be easy to read all this as a charming story about a quirky culture. It isn't. It's the origin story of a business model.

Every painful, manual thing the Deltas did on site became a signal for what the product team should automate. Data integration done by hand became ingestion tooling. Hand-built dashboards became visualization tools. Bespoke apps became an app-building platform. Stack enough of those up and you get **Foundry** — now more than half of Palantir's revenue, and the reason a company that looked, in 2016, like "a Silicon Valley services company" was running roughly **80% gross margins** by 2023. For comparison, Accenture — the gold standard of the actual services business — runs around 32%. ([Qureshi, 2024](https://nabeelqu.co/reflections-on-palantir))

That's the magic trick. Palantir looked like a consulting company and earned like a software company. The Forward Deployed Engineer is how you pull off the disguise.

There's a side effect worth noting, too. Because Deltas operated with enormous autonomy — each deployment was essentially a mini-startup, owned end to end — Palantir became a famous factory for founders. Qureshi's line: *"There are usually more ex-Palantir founders than there are ex-Googlers in each YC batch, despite there being ~50x more Google employees."* The role doesn't just deploy software. It manufactures the exact temperament that starts companies: comfort with ambiguity, ownership of outcomes, and a willingness to get on the plane.

## Why the copies mostly fail

For most of Palantir's life, this model was mocked. Critics looked at all those engineers embedded on customer sites and saw an unscalable consulting shop wearing a software costume. Mabrey's retort is one of my favorite lines in all of this: "We were criticized for a very long time for this approach... The criticism created a chilling effect and resulting conformity in how software companies were built. The resulting dead zone gave us a two decade head start."

The criticism *was the moat.* As long as everyone "knew" that real software companies don't embed engineers with customers, Palantir got two decades to compound a model nobody would copy.

That dead zone is now over. The FDE is being lionized, studied, and cloned at every AI lab and Series A startup in the Valley. But here's Mabrey's warning, and it's the thread that runs through the rest of this series: most copies "replicate the form but not the function." They hire someone, slap "Forward Deployed Engineer" on the business card, fly them to a customer — and skip the part where the field work actually feeds the product, where the mess actually deposits sediment, where the duck actually gets less salty. They build, in his words, tribute bands. They get the costume and miss the song.

So the question this series is really about isn't "what is a Forward Deployed Engineer?" Everyone has a definition and most of them are wrong (that's Part 2). The real question is the one Palantir answered in a French restaurant twenty years ago:

**When the model is brilliant but the customer can't tell you what they need, who do you send forward — and how do you make sure what they learn comes home?**

That's the whole game. In the AI era, it's the only game. And almost nobody is playing it right.

## Why Delta exists

This series isn't only analysis. It's the front door to three things we're building — because reading about Forward Deployed Engineering and *doing* it are very different sports:

- **The Course** — the FDE craft, made learnable. How to get on the plane, read the room, build the hacky thing that works by Friday, and feed it back into product. The instincts Palantir trained with a Keith Johnstone book and a one-way plane ticket, turned into something you can actually study.
- **The Toolkit** — the open-source stack a Delta actually deploys: MCP servers, agent skills, eval harnesses, deployment scaffolding. The "paved superhighway" half of the model, in code you can fork.
- **The Community** — where forward deployed engineers trade the real stuff: the 2 a.m. production fires, the political knife-fights, the wins nobody outside the building will ever hear about. The wisdom that only exists in the field, finally pooled in one place.

Every post in this series opens a door to one of them. Today's door is the last one. If the French restaurant story lit something up in you, you already think like a Delta — so come find the others who do. That's where this series is headed, and that's where the desert starts to bloom.

---

*Next in Delta — Part 2: "One Name, Three Jobs." An analysis of 1,000 job postings reveals that "Forward Deployed Engineer" secretly describes three completely different jobs — and which one you mean determines whether you're building Palantir or a staffing agency.*

**The one line to remember:** *The service isn't separate from the product. The service is how the product learns.*

---

### Sources
- Ted Mabrey, "Sorry, that isn't an FDE," Sep 2024 — https://tedmabrey.substack.com/p/sorry-that-isnt-an-fde
- Nabeel Qureshi, "Reflections on Palantir," Oct 2024 — https://nabeelqu.co/reflections-on-palantir
- Palantir Blog, "Dev versus Delta: Demystifying engineering roles at Palantir" — https://blog.palantir.com/dev-versus-delta-demystifying-engineering-roles-at-palantir-ad44c2a6e87
- Shyam Sankar, bio/about — https://www.shyamsankar.com/about
- The Pragmatic Engineer, "What are Forward Deployed Engineers, and why are they so in demand?" 2025 — https://newsletter.pragmaticengineer.com/p/forward-deployed-engineers

*Note: the "French restaurant" origin is attributed to Alex Karp via Ted Mabrey's first-hand account; the mid-2000s dating and Sankar-as-first-FDE framing are consistent across Palantir alumni sources but the exact internal timeline varies between tellings.*
