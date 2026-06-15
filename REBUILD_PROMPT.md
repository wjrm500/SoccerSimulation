# THE FOOTBALL UNIVERSE ENGINE — Master Build Prompt

> A single, self-contained specification for building a deeply-simulated, statistically-grounded, emergent football (soccer) world from scratch. This is not a list of files to write; it is an exhaustive description of the *systems, processes, mathematics, data model, and engineering discipline* required to produce a simulation that is more ambitious, more detailed, more correct, and more beautiful than anything that has come before it.
>
> It is the spiritual successor to a hand-built simulation that proved the core idea works. That predecessor's wisdom is embedded throughout this document as **inherited calibration** — concrete numbers, formulas, and design decisions that were tuned by hand over years and *should be preserved as the starting point*, then improved with intent. Treat those numbers as the result of expensive empirical tuning, not as arbitrary constants to discard.

---

## 0. How to read and execute this prompt

You are an expert simulation engineer, systems architect, sports modeller, and disciplined software craftsperson. You will build the system described below. Obey these meta-rules:

1. **The data model and the deterministic engine core are the keel of the ship.** Weigh them more heavily than anything else. Every other feature hangs off them. If you get the entity model, the time model, and the determinism model right, everything else is tractable. If you get them wrong, no amount of feature work will save you.
2. **The simulation core must be pure, deterministic, and persistence-agnostic.** No I/O, no database, no framework, no global singletons, no wall-clock time, no un-seeded randomness inside the engine. The engine is a pure function of `(state, seed, decisions) -> (new_state, events)`. Everything else (storage, web, rendering, scheduling jobs) is an adapter around that core.
3. **Build in vertical slices, test relentlessly, and never let the suite go red.** Each milestone (Section 27) must be fully working and fully tested before the next begins. "Test the living daylights out of it" is a hard requirement, not a sentiment (Section 23).
4. **Prefer data-driven design over hard-coding.** Formations, positions, skill archetypes, competition formats, country definitions, calibration constants — all live in versioned configuration/data, not in code branches.
5. **When this document gives a formula or constant, implement it exactly, behind a named, documented, individually-overridable configuration constant.** Then make it tunable. The realism of this simulation is an emergent property of thousands of small calibrations; they must all be visible, named, and adjustable in one place (Section 26).
6. **Reproducibility is sacred.** The same seed + same inputs + same decisions must produce byte-identical results forever, across machines and across save/load cycles. This is both a feature and your single most powerful testing tool (Section 23.5).

Where this document says **[INHERITED]**, the value or rule comes from the proven predecessor and should be your default. Where it says **[NEW]**, it is an ambition the predecessor never reached. Where it says **[DECISION]**, you must make a deliberate, documented choice and record it in an architecture decision record (ADR).

---

## 1. The Raison d'être — what we are actually building

We are building a **living football universe**: a self-contained world in which footballers are *born* with latent, uncertain potential; *develop* and *decline* along individual age curves; are organised into *clubs* drawn from *real geography*; play out *seasons* of *competitions* via a *calibrated probabilistic match engine*; and accumulate *rich individual and collective histories* — goals, assists, form swings, injuries, awards, transfers, trophies, rises and falls — that a user can explore, influence, or steer across *decades of simulated time*.

The magic — the thing that made the predecessor worth rebuilding — is **plausible emergence from calibrated statistics**. Nobody scripts that a 19-year-old winger will break out, get injured in March, lose form, recover, and earn a big-money move. It *emerges* from the interaction of well-tuned distributions: a latent peak rating that resolves with age, a skill profile matched to positions by geometric similarity, a fatigue/form/injury loop, a goal-probability table calibrated to real scoring rates, and formation/position archetypes weighted by real-world frequency. The result feels real because the *generative process* is honest, not because outcomes are faked.

Our ambition is to extend that honest generative process across **five new axes** the predecessor only gestured at:

- **Chronology (time):** not one season, but an unbounded chain of seasons — youth intake, aging, regeneration, retirement, records, dynasties, eras.
- **Geography (space):** not one country, but many — real cities, nations, confederations, with reputation gradients and distinct footballing cultures.
- **Competition (structure):** not one league, but pyramids with promotion/relegation, domestic cups, continental tournaments, super cups, playoffs, internationals — all expressed through one general competition abstraction.
- **Economy (resources):** transfers, valuations, wages, contracts, budgets, scouting, loans, agents — a market that moves players between clubs for plausible reasons.
- **Agency (people & the user):** managers with identities and tactics; a user who can spectate, manage a club, or act as commissioner of the whole world, with meaningful decision points during the simulation rather than fire-and-forget batch runs.

And one axis of **identity**: players, clubs, and managers should feel like *characters* — names, nationalities, avatars/visual identities, personalities, traits, career narratives, and persistent histories. **Names are central to the fascination here, not a cosmetic afterthought.** Nations may be real (England, Uruguay, Japan), but *every* city name, club name, and person name in the world must be **invented** — never copied from a real place or person — and yet feel utterly *place-accurate*: a generated Uruguayan should read as plausibly Uruguayan, a Japanese name as Japanese, an English club as English. This demands real, serious **procedural name generation grounded in the statistical and morphological character of real naming** (Section 10.5), so a user can scroll a fourth-tier squad list and feel, viscerally, *where in the world they are*.

And underpinning all exploration: a **beautiful, fast, data-rich user interface** (Section 21). The simulation is the engine, but the UI is how the user falls in love with the world it produces — every entity clickable, every number a story, every chart alive. Treat the UI as a first-class deliverable, not a thin viewer bolted on at the end.

**Design pillars (in priority order):**

1. **Correctness & determinism** — the same inputs always produce the same world.
2. **Emergent plausibility** — realism comes from calibrated generative processes, not scripted outcomes.
3. **Extensibility** — every dimension (positions, competitions, countries, eras) is data-driven and open to extension without rewrites.
4. **Performance at scale** — tens of thousands of players across dozens of countries over decades must remain tractable.
5. **Explorability, beauty & narrative** — the world must be richly queryable, *beautifully presented*, and able to tell stories about itself. A stunning, fast, exploratory UI (Section 21) and authentic, invented-but-place-accurate nomenclature (Section 10.5) are part of this pillar, not optional polish.
6. **Engineering excellence** — clean architecture, exhaustive tests, full reproducibility, observability, and tooling for balancing.

---

## 2. Lessons inherited from the predecessor — keep, fix, elevate

The predecessor was a Flask app with an RQ/Redis worker that built a `Universe` of `System → League → Club → Player`, "time-travelled" 300 days through one double-round-robin season, pickled the entire live object graph into MongoDB GridFS, and let users browse the frozen result. Study these lessons; they are dearly bought.

### 2.1 Ideas to KEEP and elevate (these are the soul of the thing)

- **Latent potential that resolves with age.** Each player has a hidden `peak_rating` and `peak_age`; their current rating is a deterministic function of how far their current age is from their peak. Crucially, the predecessor *jittered the peak rating every day with variance `50 / age²`* — so a teenager's ceiling is volatile (wonderkids and busts), and an established pro's ceiling is stable. **This "potential uncertainty that shrinks with age" mechanic is brilliant and must be preserved and expanded.** [INHERITED]
- **Skill profiles as distributions, positions as archetypes, matched by geometry.** A player isn't "a striker"; he has a six-dimensional skill *shape*, and his suitability for each position is the cosine similarity between his shape and that position's ideal shape. His best position emerges; his ratings per position emerge. **Keep this. It is the right abstraction.** [INHERITED]
- **A calibrated goal-probability table.** Match scorelines are not ad hoc; an offence-minus-defence "potential" integer indexes a hand-tuned table of `(mean, sigma)` for a Gaussian goal count, calibrated so an even matchup yields ~1.5 goals. **Keep the table-driven, empirically-calibrated approach.** [INHERITED]
- **The fatigue → form → injury → selection loop.** Players accumulate fatigue per match, recover daily as a function of fitness, can get injured when fatigued, gain/lose form relative to expectation, and that form+fatigue feeds back into who gets selected and how well they rate. **This feedback loop is the engine of week-to-week narrative. Keep and deepen it.** [INHERITED]
- **Performance index & Man of the Match.** A per-player, per-match 0–10 rating built from rating-advantage (sigmoid), contribution-weighted team over/under-performance, and context-weighted goal/assist credit (goals worth more in close, low-scoring games). **Keep this multi-factor, context-aware rating.** [INHERITED]
- **Real-world weighting everywhere.** Formation popularity weights (4-4-2 ~22%, 4-2-3-1 ~21%, 4-3-3 ~13% …), and naming driven by real frequency *distributions*. **Realism-by-frequency is cheap and powerful. Keep it — but elevate it.** The predecessor drew player names directly from real frequency-weighted name lists. We go further and harder: we use real naming data only to *learn the statistical and morphological character* of each place, then **generate wholly invented names** that fit it (Section 10.5). Same fascination, more integrity, infinite variety. [INHERITED → NEW]
- **"Club DNA" easter eggs.** The author nudged certain clubs' player ratings up/down (±10 peak rating). Generalise this into a principled **club reputation/strength prior** that biases generated player quality — and keep room for affectionate hand-tuned exceptions. [INHERITED → NEW]
- **A universe-global player pool.** Players were owned by a universe-level `PlayerController`, not by clubs. This is exactly the right foundation for transfers, free agency, and cross-border movement. **Keep player identity independent of club membership.** [INHERITED]
- **Time-series capture per player.** Ratings, peak ratings, and form were stored per date for graphing. **Keep first-class historical time series — and make them cheap (Section 17.6).** [INHERITED]

### 2.2 Things to FIX (the predecessor's real constraints)

- **Single season, single league, single country actually used.** The model supported multiple systems/leagues, but the UI only ever read `systems[0].leagues[0]`, and time only ran for one 300-day season. A telling commit renamed `tournament` to `league` "as league is only tournament, must have been a future plan." **We deliver the future plan: multi-season chronology, full pyramids, many competitions, many countries.** [FIX → NEW]
- **Pickling a live object graph as the save format.** The entire `Universe` (with NumPy state, circular references, matplotlib-adjacent objects) was joblib-pickled into GridFS. This is fragile, version-brittle, memory-heavy, unqueryable, and unmigrate-able. **Replace with a real, explicit, versioned, queryable persistence model — ideally event-sourced with snapshots (Section 20).** [FIX]
- **A module-global singleton `Universe`.** `Universe()` returned a process-global `_instance`. This makes concurrency, testing, and running multiple worlds impossible. **The engine must hold no global mutable state; a world is an explicit value you pass around.** [FIX]
- **Un-seeded randomness.** Direct `random` / `np.random` calls with no seed → non-reproducible. **All randomness flows through an explicit, seeded, splittable RNG carried in the simulation context (Section 6.4).** [FIX]
- **O(players × days) full recomputation every day.** Every player's skill distribution, position ratings, etc. were recomputed every single day for the whole universe. At one country this was fine; across decades and dozens of countries it is fatal. **Recompute lazily/on-event, cache derived values, and tick efficiently (Section 24).** [FIX]
- **No goalkeeper.** The predecessor had nine outfield archetypes and selected *ten* players, abstracting goalkeeping into team defence. This is a defensible simplification but a real gap. **Introduce a proper Goalkeeper position and goalkeeping skills, select eleven, and model shot-stopping explicitly (Section 7.4, 14).** [FIX → NEW]
- **No transfers, no managers, no promotion/relegation, no cups.** The `free_agent_players` list existed but was never used. **All delivered here.** [FIX → NEW]
- **Fire-and-forget batch UX.** Users started a job, waited, then browsed a frozen world. **Add interactive, steppable, decision-driven simulation modes (Section 19).** [FIX → NEW]

### 2.3 The single most important inherited insight

> **Realism is a generative property, not a content property.** The predecessor never wrote "Player X is good." It wrote distributions and curves whose *interaction* produced good and bad players, breakouts and busts, hot and cold streaks. Everything new we add — economy, managers, competitions, chronology — must obey the same principle: **model the generating process honestly, calibrate it against reality, and let outcomes emerge.** Never script a result you could generate.

---

## 3. Ubiquitous language (domain glossary)

Use these terms consistently in code, data, tests, and UI. Precise shared language prevents whole classes of bugs.

- **World** — the entire simulation universe (renamed from "Universe" for clarity); the root aggregate. Contains everything and owns the clock and the RNG seed.
- **Confederation** — a continental grouping of nations (e.g. a Europe-like, South-America-like body). Owns continental competitions. [NEW]
- **Nation / Country** — a footballing nation. Has geography (cities/regions), a league pyramid, a reputation tier, a national team, and a footballing "culture" profile. (Generalises the predecessor's **System**.)
- **Pyramid** — the ordered stack of **Divisions** within a nation, linked by promotion/relegation.
- **Division (Tier)** — one rung of a pyramid; a league competition with a set of member clubs for a season.
- **Competition** — *any* organised contest: a league, a domestic cup, a continental cup, a super cup, a playoff, an international tournament. One general abstraction (Section 11).
- **Season** — one chronological cycle of competitions for the world (e.g. 2000–01). The unit of chronology.
- **Club** — a persistent football club with identity, squad, finances, stadium, reputation, philosophy, board, and history.
- **Squad** — the set of players currently registered to a club.
- **Player** — a persistent footballer identity, independent of club membership. Owned by the world, registered to clubs over time.
- **Manager** — a persistent managerial identity who runs a club (or nation), with tactical preferences and a career record. [NEW]
- **Position** — an archetypal role with an ideal skill profile (GK, CB, FB, WB, CDM, CM, CM-style variants, COM, WM, WF, CF — see Section 7.4).
- **Formation** — a named arrangement of positions (e.g. 4-2-3-1) with a real-world popularity weight.
- **Tactic** — a manager/club's chosen formation plus instructions and player roles for a match or period. [NEW]
- **Selection / Select / Lineup** — the chosen XI: a Lineup is a set of **Selects**, each a binding of (Player, Position, contextual rating). (Renames the predecessor's "Team"/"Selection"/"Select".)
- **Fixture** — a scheduled meeting of two clubs in a competition on a date.
- **Match** — the simulated playing of a Fixture.
- **Tick** — one atomic step of the simulation clock (default: one day) (Section 6).
- **Event** — an immutable record that something happened (a goal, a transfer, an injury, a tick, a season rollover). The substance of the event-sourced history (Section 20).
- **Report** — a derived, read-optimised summary (match report, player report, season report) projected from events/state.
- **Attribute / Skill** — one dimension of a player's ability (Section 7.3).
- **Rating** — a scalar 0–100 summarising overall current ability (derived from peak rating and age curve).
- **Form** — a short-term modifier reflecting recent over/under-performance.
- **Fatigue** — accumulated physical load reducing effectiveness and raising injury risk.
- **Reputation** — a club's/player's/nation's standing, driving seeding, attractiveness, and generation priors.
- **Decision** — an externally-supplied choice (from the user or an AI agent) that the deterministic engine consumes at a decision point (Section 19.3).

---

## 4. Architecture & technology approach

### 4.1 The cardinal rule: a pure engine core inside an impure shell

Adopt a **hexagonal / ports-and-adapters** architecture with a strict dependency direction: *adapters depend on the core; the core depends on nothing.*

```
                ┌─────────────────────────────────────────────┐
                │                 ADAPTERS                     │
                │  (impure: I/O, frameworks, time, network)    │
                │                                              │
                │  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
                │  │ Web/API  │  │ Persist- │  │  Job/Tick  │  │
                │  │  layer   │  │  ence    │  │  scheduler │  │
                │  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
                │       │             │              │         │
                │  ┌────┴─────────────┴──────────────┴──────┐  │
                │  │            APPLICATION LAYER            │  │
                │  │  (use-cases, orchestration, decisions)  │  │
                │  └────────────────────┬───────────────────┘  │
                └───────────────────────┼──────────────────────┘
                                        │  (depends inward only)
                ┌───────────────────────┴──────────────────────┐
                │                ENGINE CORE                    │
                │  (PURE, DETERMINISTIC, no I/O, no globals)     │
                │                                               │
                │  Domain model · Generators · Match engine ·   │
                │  Development model · Economy · Competitions · │
                │  Scheduler · Tick reducer · RNG · Calibration │
                └───────────────────────────────────────────────┘
```

- **Engine core**: pure domain logic. Given a world state, a seeded RNG, and a set of decisions, it advances the world and emits events. It never reads a clock, opens a socket, or touches a database. It is the part you test exhaustively and the part whose determinism you guarantee.
- **Application layer**: orchestrates use-cases ("advance one tick", "process a transfer window", "start a new season", "resolve a user decision"), gathers decisions, calls the core, and hands results to persistence and presentation.
- **Adapters**: web/API, persistence, background job runner, notifications, rendering. These are replaceable and must contain *no* simulation logic.

The core must be runnable headless in a single process with zero external services — that is how the test suite runs it ten thousand times.

### 4.2 Language, runtime, and stack [DECISION]

Choose deliberately and record the choice in an ADR. Strong default recommendation, biased toward correctness, performance headroom, and testability:

- **Primary language: a statically-typed, high-performance language for the engine core** is ideal, but if continuity with the predecessor's ecosystem and modelling ergonomics matter most, **Python 3.12+ with strict typing (full type hints, `mypy --strict` or `pyright` in strict mode), `numpy` for vectorised math, and performance-critical hot paths optimised (vectorisation, and if needed `numba`/`cython`/a native extension) is acceptable** — *provided* the determinism, typing, and performance requirements below are met without compromise.
  - If you choose Python: forbid un-seeded global random; wrap all randomness (Section 6.4); pin and lock dependencies; treat `mypy`/`pyright` strict as a gate.
  - A compiled core (e.g. Rust) with thin bindings is a legitimate and arguably superior alternative for the match engine and tick loop given the scale ambitions — choose based on the team's leverage and record the trade-off.
- **Persistence**: a real database with explicit schema and migrations (Section 20). Relational (PostgreSQL) is the recommended default for the queryable read model and integrity; an append-only event store can live alongside it. Do **not** pickle live objects.
- **Presentation/API**: a clean HTTP/JSON (or GraphQL) API over the read model; a modern web frontend. Keep all rendering out of the engine. (The predecessor server-rendered matplotlib PNGs; we expose data and render client-side, with charts as data.)
- **Background processing**: a durable job/queue system for long simulations, with progress reporting and cancellation. Long sims must be resumable from snapshots.

> Whatever stack you pick, the **engine-core purity, determinism, strict typing, dependency locking, and test discipline are non-negotiable** and stack-independent.

### 4.3 Module boundaries within the core

Organise the engine core into cohesive, individually-testable modules with explicit interfaces:

- `domain/` — entities, value objects, identifiers, invariants (no behaviour that needs RNG or config beyond pure rules).
- `generation/` — world generation: nations, clubs, players, managers, names, geography priors.
- `development/` — player aging, rating curves, skill transitions, potential resolution, retirement, regeneration.
- `tactics/` — formations, roles, instructions, lineup selection/optimisation.
- `match/` — the match engine (one or more fidelity levels).
- `ratings/` — performance index, form, fatigue, injuries, player/match reports.
- `competition/` — competition formats, scheduling, standings, qualification, promotion/relegation, seeding.
- `calendar/` — the world calendar, fixture scheduling across competitions, congestion.
- `economy/` — valuations, wages, contracts, budgets, transfers, negotiations, loans, scouting.
- `agents/` — AI decision-makers (AI managers, AI boards, AI clubs in the market).
- `chronology/` — season rollover, history, awards, records, eras.
- `engine/` — the tick reducer, the world reducer, the RNG, the event log, decision intake.
- `calibration/` — all tunable constants and the calibration harness (Section 26).

Each module exposes pure functions and immutable (or carefully-owned) data. Cross-module calls go through narrow, typed interfaces.

---

## 5. THE DATA MODEL — engineer this with rocket-ship precision

This is the keel. Spend disproportionate care here. The model must be: explicit, normalised where it matters, denormalised only deliberately for read performance, fully typed, with stable identifiers, clear ownership/aggregates, enforceable invariants, and a versioning story. Below is the canonical entity model. Treat every entity as both an in-memory domain type *and* a persisted schema with migrations.

### 5.1 Identifiers and value objects

- **Every entity has a stable, opaque, globally-unique identifier** (`PlayerId`, `ClubId`, `NationId`, `CompetitionId`, `SeasonId`, `MatchId`, `FixtureId`, `ManagerId`, `TransferId`, `ContractId`, etc.). IDs are assigned deterministically from the world seed and a per-type monotonic counter so that the same seed yields the same IDs. IDs never collide across types. IDs are never reused.
- **Value objects** (immutable, equality-by-value): `Date` (in-world calendar date), `Money` (integer minor units + currency), `SkillProfile` (the vector of skills), `Rating` (0–100), `Reputation` (bounded scalar or tier), `GeoPoint` (lat/long), `Name` (forename, surname, display rules), `AgeCurveParams`, `ContractTerms`. Value objects carry validation in their constructors and cannot exist in an invalid state.
- **No primitive obsession.** A money amount is `Money`, never a bare float. A skill vector is `SkillProfile`, never a loose dict. This prevents an entire class of unit/scaling bugs (the predecessor mixed raw floats freely).

### 5.2 The world (root aggregate)

```
World
  id, seed, schemaVersion, createdAtTick
  clock: { currentDate, startDate, tickUnit }
  rngState  (the master RNG state; see §6.4)
  calibration: CalibrationSet (versioned; §26)
  confederations: [Confederation]
  nations: [Nation]
  competitions: [Competition]        // all competitions across all nations + continental
  clubs: [Club]                      // all clubs, all nations
  players: [Player]                  // the global player pool (active, free agents, retired)
  managers: [Manager]
  seasons: [Season]                  // chronology: every season ever
  currentSeasonId
  market: TransferMarket             // open windows, listings, in-flight negotiations
  records: RecordBook                // all-time records, awards, halls of fame
  eventLog: append-only event stream (or pointer to it; §20)
  config: WorldConfig                // generation knobs, enabled features, scale
```

The World is the single source of truth. All mutation happens through the engine reducers. Nothing outside the engine mutates world state.

### 5.3 Geography

```
Confederation { id, name, code, nations:[NationId], continentalCompetitions:[CompetitionId], reputation }
Nation {
  id, name, code, confederationId,
  reputationTier,                 // drives generation strength & seeding (§10.3)
  cultureProfile,                 // footballing-style priors (§10.4): pace, physicality, technical bias, formation preferences
  geography: { regions:[Region], cities:[City] },
  pyramid: PyramidId,
  nationalTeam: ClubId-like NationalTeam reference,
  nameModel: NameModel,             // generative model for INVENTED but place-accurate names (§10.5)
  currency, calendarProfile        // when its season runs, winter break, etc.
}
Region { id, name (invented), nationId, namingProfile, cities:[CityId] }   // regions may bias local naming
City { id, name (invented, place-accurate), regionId, nationId, geo:GeoPoint, population, footballReputation }
```

Nations and their `NameModel`s are seeded reference data (Section 10.2/10.5); cities, regions, club names, and person names are all **generated** (invented, deterministic, place-accurate) at world creation from those models — *not* drawn from real-place lists. This is the deliberate evolution of the predecessor's MongoDB `cities`/`systems`/`forenames`/`surnames` collections: real data informs the *generator*, the world contains only invented names.

### 5.4 Competition structure

```
Pyramid { id, nationId, tiers:[DivisionId ordered top→bottom], promotionRelegationRules }
Competition {
  id, name, type: enum(LEAGUE | DOMESTIC_CUP | LEAGUE_CUP | CONTINENTAL | SUPER_CUP | PLAYOFF | INTERNATIONAL | FRIENDLY),
  scope: enum(DOMESTIC_TIER | DOMESTIC_KNOCKOUT | CONTINENTAL | INTERNATIONAL),
  nationId | confederationId,
  format: CompetitionFormat,        // §11: the rules object (round-robin, knockout, group+knockout, etc.)
  reputation, prizeModel, qualificationRules, seedingRules,
  // per-season instances live in Season (below) to keep chronology clean
}
```

Crucially, **the persistent `Competition` is the format/identity; each season produces a `CompetitionInstance`** (the actual edition with its participants, fixtures, standings, and winner). This separation is what makes chronology clean.

### 5.5 Season & chronology

```
Season {
  id, label ("2000-01"), startDate, endDate, ordinal,
  competitionInstances: [CompetitionInstance],
  transferWindows: [Window],
  awards: [Award],          // player of the season, golden boot, etc.
  status: enum(SCHEDULED | IN_PROGRESS | COMPLETE)
}
CompetitionInstance {
  id, competitionId, seasonId,
  participants: [ClubId | NationId],
  stages: [Stage],          // group stage, round of 16, final, or a single league stage
  fixtures: [FixtureId],
  standings: StandingsView,  // for league/group stages
  bracket: BracketView,      // for knockouts
  result: { winnerId, runnerUpId, finalRankings },
  status
}
Stage { id, name, type, rounds:[Round], qualifiesTo:[StageRef] }
Round { id, name, fixtures:[FixtureId], legs:int }
```

This makes "Manchester-like club won the 2003-04 top tier and reached the continental semi-final" a first-class, queryable fact, not a derived guess.

### 5.6 Club

```
Club {
  id, name, shortName, nickname, founded,
  cityId, nationId,
  identity: { primaryColour, secondaryColour, crestSpec, stadiumName },  // §9.6 visual identity
  reputation,                       // §9.2 drives generation, attractiveness, seeding
  philosophy,                       // youth-vs-buy, attacking-vs-defensive, etc. (§9.4)
  finances: { balance:Money, wageBudget:Money, transferBudget:Money, income, expenditure, debt },
  stadium: { capacity, quality },
  facilities: { trainingQuality, youthAcademyQuality },
  board: BoardProfile,              // expectations, patience, wealth (§9.5)
  squad: [PlayerId],                // current registrations
  managerId | null,
  tacticDefault: TacticId,
  history: ClubHistory,             // honours, season-by-season finishes, legends
  fanbase: { size, expectations, mood }
}
```

A **NationalTeam** is modelled as a special Club whose squad is selected from a nation's eligible players (Section 18.7).

### 5.7 Player — the central character

```
Player {
  id,
  identity: {
    name: Name, nationality: NationId, secondaryNationality?,
    birthDate: Date, appearance: AvatarSpec (§7.10),
    personality: PersonalityProfile (§7.8), traits: [Trait] (§7.7)
  },
  potential: {
    peakRating: float,              // latent ceiling, jitters with age (§7.2)
    peakAge: float,                 // ~N(27,2)∈[22,32] [INHERITED]
    growthSpeed: { incline, decline },  // [INHERITED] §7.2
    retirementThreshold: float,     // [INHERITED]
    potentialVolatilityModel        // variance shrinks with age (§7.2)
  },
  skills: SkillProfile,             // the latent skill *shape* (§7.3), age-modulated
  derived (cached, recomputed lazily; §24.3): {
    rating, positionSuitabilities, positionRatings, bestPosition,
    skillValues (= rating × skill shape)
  },
  condition: { fatigue, form, morale, sharpness, injury: Injury|null },
  registration: { clubId|null, status: enum(ACTIVE|FREE_AGENT|RETIRED|YOUTH),
                  shirtNumber?, role? },
  contract: ContractId | null,      // §16.4
  career: PlayerHistory (§17.6),    // appearances, goals, assists, ratings time series, transfers, honours, injuries
  valuation: Money (derived; §16.2)
}
```

**Ownership / aggregate rules:** Players are owned by the World's global pool, *referenced* by clubs via `squad`. Moving a player is a transactional change to registration + contract + both clubs' squads + a Transfer event — never a silent pointer swap (the predecessor mutated `player.club` directly; we make it an explicit, audited transaction). A player's identity and history persist across club changes and into retirement.

### 5.8 Manager

```
Manager {
  id, name, nationality, birthDate, appearance,
  tacticalProfile: { preferredFormations:WeightedList, attackingBias, pressingBias,
                     riskTolerance, youthPreference, transferAggression },
  ability: { tacticalSkill, manManagement, development, recruitment },  // bounded scalars
  reputation, clubId|null, career: ManagerHistory
}
```

### 5.9 Match-time entities (ephemeral but recorded)

```
Fixture { id, competitionInstanceId, stageId, roundId, date, homeClubId, awayClubId, neutralVenue, leg, status }
Lineup { clubId, formationId, selects:[Select], tactic:Tactic }
Select { playerId, position, contextualRating }     // immutable binding
Match (computed) -> emits: MatchReport, [PlayerReport], [Goal], [Injury], [Card], [SubstitutionEvent]
MatchReport { fixtureId, homeReport:TeamReport, awayReport:TeamReport, ... }
TeamReport { lineup, expectedGoals, actualGoals, outcome, goals:[Goal], playerReports:{playerId:PlayerReport} }
PlayerReport { playerId, position, minutesPlayed, performanceIndex, goals, assists,
               keyEvents, fatigueDelta, formDelta, manOfTheMatch, preMatchForm, selectRating }
Goal { minute, scorerId, assisterId|null, type }
```

### 5.10 Economy entities

```
Contract { id, playerId, clubId, wage:Money, signedDate, expiryDate, releaseClause:Money?, bonuses, status }
TransferListing { id, playerId, askingPrice:Money?, loanAvailable:bool, listedBy:ClubId, window }
Negotiation { id, playerId, fromClubId, toClubId, state-machine state, currentOffer, history }
Transfer { id, playerId, fromClubId|null, toClubId, fee:Money, date, type:enum(PERMANENT|LOAN|FREE|YOUTH_PROMOTION), window }
TransferMarket { openWindows:[Window], listings, activeNegotiations, recentTransfers }
```

### 5.11 History, records, awards

```
RecordBook { allTime: {...}, perNation:{...}, perCompetition:{...}, halls:{playersHall, managersHall} }
Award { id, type, seasonId, competitionInstanceId?, recipientId, value }
PlayerHistory { seasons:[PlayerSeasonLine], transfers:[TransferId], injuries:[Injury], honours:[Award], ratingsTimeSeries, formTimeSeries }
ClubHistory { honours:[Award], seasonFinishes:[{seasonId, competitionId, finalPosition}], legends:[PlayerId], records }
```

### 5.12 Invariants the model must enforce (a non-exhaustive checklist)

The persistence layer and domain constructors must make these *impossible to violate*:

- A player is registered to at most one club at a time (excluding loans, which are modelled explicitly with parent + loan club).
- A club's `squad` contains exactly the set of players whose registration points to it.
- A contract's player and club references are consistent with the player's registration.
- Sum of points/goals in a standings view equals the sum derived from its fixtures' results.
- A knockout bracket is internally consistent (winners advance to the correct slot).
- Every fixture belongs to exactly one competition instance/stage/round and has a valid date inside the season.
- No player appears in two simultaneous fixtures.
- Skill profile components and ratings are always within their declared bounds.
- Money never silently goes negative without an explicit debt/overdraft model.
- Every state-changing fact has a corresponding event in the log (Section 20).

Write these as explicit invariant checks runnable over any world state (Section 23.6) — they are your safety net.

---

## 6. Determinism, the simulation clock, and the tick engine

### 6.1 The world advances by ticks

The default **tick = one in-world day** [INHERITED: the predecessor advanced one day at a time]. The tick unit is configurable, but day-granularity is the right default: it lets fixtures, training, recovery, injuries, contract expiries, transfer windows, and aging all resolve naturally on a calendar.

A tick is a **pure reduction**:

```
tick(worldState, rng, decisions) -> (worldState', [events])
```

The reducer, in deterministic order:

1. **Resolve scheduled fixtures** for the current date across all competitions (Section 14), gathering required decisions (lineups/tactics) from managers/AI/user (Section 19).
2. **Apply match outcomes**: update standings/brackets, player conditions (fatigue/form/injuries), club finances (gate receipts, prize money), histories, and emit events.
3. **Advance players** (Section 7.9): age, resolve potential drift, update ratings/skills *lazily or as scheduled*, progress injury recovery, decay form/fatigue.
4. **Process daily economy/calendar hooks**: contract expiries, transfer-window logic, scouting progress, board reviews, training effects.
5. **Advance the clock** by one tick.
6. **Check for stage/season boundaries** and trigger rollovers (Section 18) when reached.

Order is fixed and documented; determinism depends on it.

### 6.2 Performance-aware ticking

The predecessor recomputed *every player in the universe every day*. We will not. Most days, most players do nothing that changes their derived values beyond a smooth age delta. Strategy (Section 24):

- **Lazy derived state**: `rating`, `positionRatings`, etc. are computed on demand from `(peakRating, peakAge, age, skills)` and cached with an invalidation key (the inputs). They are recomputed only when read after an input changes.
- **Scheduled recomputation cadence**: continuous aging effects (rating drift, skill transitions, potential jitter) need not be applied literally every day; apply them on a coarser cadence (e.g. weekly) or compute them *analytically as a function of age* at read time, so a player who doesn't play for a month costs almost nothing. **Prefer closed-form age functions over per-day iteration wherever the predecessor used per-day iteration.**
- **Event-driven condition updates**: fatigue/form/injury change at matches and on a simple daily recovery rule that can be applied lazily (compute recovery from "days since last update").

The observable behaviour must remain equivalent to the honest daily model; only the computation is optimised. Prove equivalence with tests (Section 23).

### 6.3 Multiple simulation cadences

Support running the engine at different *granularities of user attention* without changing results:

- **Instant-sim a whole season** (batch) — for background/AI worlds and fast-forwarding.
- **Step day-by-day** — for interactive observation.
- **Step match-by-match / decision-by-decision** — for a managing user (Section 19).

All three are the same reducer driven by different loops, producing identical results for identical decisions and seed.

### 6.4 The RNG model (the heart of determinism)

- A single **master seed** (a 256-bit value) is fixed at world creation and stored in the World.
- Use a **splittable / counter-based PRNG** (e.g. PCG, philox, or splitmix-style). From the master seed, derive **independent sub-streams** by hashing a stable key path, e.g. `rng_for("match", matchId)`, `rng_for("generation", "player", playerId)`, `rng_for("development", playerId, tick)`.
- **Never** draw from a shared mutable global stream where ordering across unrelated subsystems would couple their randomness. Sub-stream derivation by stable key means a match's randomness is independent of whether another match was simulated first — essential for parallelism (Section 24) and for reproducibility under reordering.
- The engine receives RNG *as an argument*; it never reaches for `random`/`np.random` directly. Lint/ban global RNG usage in the core.
- Persisted worlds store enough RNG state (or rely purely on key-derived sub-streams from the immutable master seed + deterministic IDs) that resuming a save reproduces the exact future. Prefer the **pure key-derived approach**: future randomness depends only on `(masterSeed, stableKeys)`, so no mutable RNG cursor needs persisting at all. This is the cleanest determinism story and the recommended design.

### 6.5 Determinism acceptance test

A standing requirement: **build world from seed S, run N ticks → hash the full state. Save at tick k, reload, run remaining ticks → hash must match.** Run two worlds from seed S in parallel processes → identical. This test gates every release (Section 23.5).

---

## 7. THE PLAYER MODEL — exhaustive

The player is the protagonist. This section specifies, in full, how a player is generated, how they develop and decline, how their skills map to positions, and how their condition evolves. Inherited formulas are given exactly; preserve them as defaults behind named constants, then extend.

### 7.1 Generation overview

At world creation (and at each youth intake, Section 17), players are generated with: identity (name from nation-weighted distributions, nationality, birth date, appearance, personality, traits), latent potential (peak rating, peak age, growth speeds, retirement threshold), and a latent skill profile shaped toward a plausible position. Generation is biased by the **club/nation reputation prior** (better clubs/nations generate stronger players — the principled generalisation of the predecessor's ±10 easter egg).

### 7.2 Latent potential and the rating curve [INHERITED — preserve exactly, then extend]

- **Peak age** `~ Normal(μ=27, σ=2)`, clamped `∈ [22, 32]`.
- **Peak rating** `~ Normal(μ=66.67, σ=10)`, clamped `∈ [20, 100]`. (μ = 100/3·2.) Bias the mean up/down by the club/nation reputation prior (Section 10.3).
- **Growth speed**: `incline ~ Normal(0.75, 0.1) ∈ [0.25, 1.25]`; `decline ~ Normal(0.875, 0.1) ∈ [0.375, 1.375]`.
- **Retirement threshold** `~ Normal(0.80, 0.025) ∈ [0.70, 0.90]`.
- **Current rating** as a function of age:
  ```
  distanceFromPeak = |peakAge − age|
  direction = (age < peakAge) ? "incline" : "decline"
  fulfilment = 1 − (distanceFromPeak^1.5 · 0.01 · growthSpeed[direction])
  rating = peakRating · fulfilment
  ```
  So rating rises toward the peak before peakAge and falls after, with the steepness governed by the per-direction growth speed. (Pre-peak players improve; post-peak players decline — the predecessor's exact model.)
- **Potential resolution with age (the wonderkid mechanic):** periodically (the predecessor did this daily; we may do it on a weekly cadence for performance, see Section 6.2) re-sample peak rating with **variance that shrinks as age grows**:
  ```
  peakRating ← clamp(Normal(μ=peakRating, σ=50 / age²), [20,100])
  ```
  At 16, σ ≈ 0.20·... (volatile ceiling — breakouts and busts); by 30, σ is tiny (settled). **This is essential to the feel; keep it.** [NEW extension: make the volatility model a named, swappable strategy so we can experiment with e.g. faster early resolution, "late bloomer" archetypes, or trait-driven volatility.]
- **Retirement:** when declining and `rating < peakRating · retirementThreshold`, the player retires. Generated players may be created near/after peak, so some retire early in their simulated life — keeping the age pyramid realistic. [INHERITED]

**[NEW] Development is not purely passive.** In the predecessor, development was a pure function of age. We enrich it (without breaking the age-curve backbone) so that *playing time, club facilities, manager development ability, and form* nudge a young player's potential resolution and rating fulfilment:

- Regular minutes and good form bias the weekly peak-rating re-sample slightly upward (toward fulfilling potential); persistent non-selection or long injuries bias it slightly downward (stagnation). The age curve remains the dominant term; these are modifiers within calibrated bounds.
- Training quality and manager development ability scale the magnitude of upside resolution for under-peak players.
This makes squad decisions and club quality *matter* for development — a core ambition — while preserving emergent plausibility.

### 7.3 The skill profile [INHERITED, then extended]

Inherited six skills (keep their meaning precisely):

- **offence** — goal threat / finishing / attacking output.
- **spark** — *the ability to create something from nothing* (flair, dribbling, the unpredictable). Declines with age.
- **technique** — control, passing, first touch, all-round ball skill.
- **defence** — defensive ability, tackling, positioning, blocking.
- **authority** — *how well a player takes control of a situation* (game intelligence, leadership, composure). Increases with age.
- **fitness** — stamina, athleticism, physical output. Declines post-peak.

**[NEW] Add goalkeeping skills** to support a real GK (Section 7.4): **handling**, **reflexes**, **command** (area control/aerial), and **distribution**. Outfield players have negligible goalkeeping skills; goalkeepers' six "outfield" skills are dominated by authority/technique with low offence. Keep the model uniform: every player has the full skill vector; positions weight it differently.

**[NEW, optional but recommended] Sub-attributes for depth & narrative** (pace, strength, aerial, finishing, passing, dribbling, tackling, positioning, composure, work-rate, leadership, flair). Model these as a finer layer *derived from and consistent with* the core skills (so the core math stays simple and calibrated, while the UI and scouting can show rich detail). Keep the *match engine* driven by the calibrated core skills; use sub-attributes for presentation, scouting reports, and trait effects. This gives FM-like richness without destabilising the calibrated core.

**Generation of the skill profile** [INHERITED, preserve]:

1. Sample each core skill `~ Normal(μ=1, σ=0.375)`, clamp `∈ [0.25, 1.75]`.
2. **Centralise**: scale so the mean across skills = 1 (`value · n / Σ`).
3. **Rebalance**: iteratively pull any out-of-bounds skills back in-bounds while keeping the mean ~1 (the predecessor's `rebalance_skill_distribution` loop — preserve its behaviour).
4. **Position normalisation pull**: identify the player's best-fit position (Section 7.5) and nudge the skill shape toward that position's ideal archetype by a random factor `~ Normal(0.5, 0.05) ∈ [0, 0.5]`, *to curb excessive weirdness* (so generated players resemble coherent footballers, not noise). [INHERITED — keep this exact intent.]
5. **Re-centralise** mean to 1.

The skill *profile* is a *shape* (mean ~1). The player's actual **skill values** = `rating · shape` — i.e. ability scales the shape up to the player's current level. [INHERITED]

### 7.4 Positions and archetypes [INHERITED + GK NEW]

Positions are data-driven archetypes, each an ideal skill shape. Inherited outfield archetypes (preserve these exact vectors as defaults — they encode real positional identity):

| Pos | offence | spark | technique | defence | authority | fitness |
|-----|--------:|------:|----------:|--------:|----------:|--------:|
| CF (Centre Forward)              | 1.52 | 1.06 | 1.03 | 0.69 | 0.95 | 0.75 |
| WF (Wing Forward)                | 1.19 | 1.35 | 1.08 | 0.75 | 0.69 | 0.94 |
| COM (Centre Off. Mid)            | 1.05 | 1.42 | 1.48 | 0.66 | 0.73 | 0.66 |
| WM (Wing Mid)                    | 1.06 | 1.24 | 1.06 | 0.81 | 0.76 | 1.07 |
| CM (Centre Mid)                  | 0.87 | 0.92 | 1.04 | 0.86 | 1.28 | 1.03 |
| CDM (Centre Def. Mid)            | 0.73 | 0.84 | 0.95 | 1.10 | 1.23 | 1.15 |
| WB (Wing Back)                   | 0.75 | 1.03 | 1.03 | 1.05 | 0.68 | 1.46 |
| FB (Full Back)                   | 0.73 | 0.92 | 0.94 | 1.24 | 0.93 | 1.24 |
| CB (Centre Back)                 | 0.72 | 0.77 | 0.92 | 1.35 | 1.26 | 0.98 |

**[NEW] Add GK (Goalkeeper)** as a tenth archetype: dominated by the new goalkeeping skills (handling, reflexes, command, distribution) plus high authority and technique, very low offence/spark/fitness-as-running. Goalkeeping suitability is computed over the *full extended* skill vector. Selecting an XI now requires exactly one GK plus ten outfield players (formations sum to 11; see Section 13).

**[DECISION]** You may also split CM into the COM/CM/CDM trio's natural variants or add LB/RB/LW/RW handedness for richer tactics — but keep the archetype set data-driven so it can grow without code changes.

### 7.5 Position suitability via geometric similarity [INHERITED — preserve exactly]

```
suitability(player, position) = 1 − cosineDistance(playerSkillShape, positionIdealShape)
                              = cosineSimilarity(playerShape, positionShape)
adjusted = 1 − (1 − suitability)^(2/3)        // sharpen contrast
// then normalise across positions so the best position = 1.0
```

- **bestPosition** = argmax suitability.
- **positionRatings[pos]** = `rating · suitability[pos]` — the player's effective rating *in that position*. A natural CB played at CF rates poorly; a versatile player rates well across several. [INHERITED]

### 7.6 Skill transitions with age [INHERITED — preserve]

As players age, the skill *shape* shifts continuously, applied relative to `distanceFromPeakAge`:

- **spark → authority**, gradient `−0.01`, applied in *both* incline and decline phases. (Young flair players mature into composed, authoritative ones.)
- **fitness decays** post-peak only, gradient `−0.015`. (Physical decline with age.)

After each transition, rebalance to keep skills in bounds; then re-apply the best-position normalisation and re-centralise. Implement transitions as a **data-driven list** so we can add more (e.g. **offence → technique** as forwards become craftier, **fitness/pace decline** steeper for pace-reliant traits) without touching code. [INHERITED structure, NEW transitions optional.]

### 7.7 Traits [NEW]

Discrete, low-frequency modifiers that create memorable players. Examples: *Wonderkid* (lower early potential volatility downside / higher upside), *Glass* (injury-prone), *Iron* (injury-resistant, slower fitness decline), *Late Bloomer* (peak age shifted later, slower early fulfilment), *Mercurial* (higher form variance), *Loyal* (resists transfers), *Big-Game Player* (performance index boost in high-stakes/close matches), *Leader* (authority boost, dressing-room morale), *Set-Piece Specialist* (goal/assist factor boost on dead balls), *Injury-Returner risk*. Traits are sampled at generation (weighted, some correlated with personality), are visible in scouting (sometimes hidden until revealed), and feed as named modifiers into the relevant subsystems. Keep each trait's effect a small, calibrated, individually-testable modifier.

### 7.8 Personality [NEW]

A small set of bounded personality dimensions (e.g. *ambition, professionalism, loyalty, temperament, consistency*) that influence: development response to playing time, transfer/contract behaviour, form volatility, and dressing-room/morale interactions. Personality is also a narrative surface (scouting, press). Keep effects modest and calibrated.

### 7.9 The per-tick player update [INHERITED loop, performance-refactored]

Conceptually (the predecessor's `advance()`), each player each tick: maybe gets injured (if fatigued), ages, recovers fatigue/form, drifts potential, recomputes rating/skills/positions, and stores a history sample. **Refactor for performance (Section 6.2):**

- Aging and rating are *closed-form functions of age*; compute lazily at read time, not by daily mutation.
- Potential drift and skill transitions apply on a **weekly cadence** (or are folded into the closed-form read), preserving observable behaviour.
- Fatigue/form recovery apply as `f(daysSinceLastUpdate)` lazily.
- Injury checks occur on ticks where the player has accumulated fatigue (i.e. recently played), not for every idle player every day.
- History time-series samples are recorded at meaningful cadence (Section 17.6), not necessarily daily for every one of tens of thousands of players.

### 7.9.1 Fatigue, form, injuries, morale, sharpness [INHERITED + NEW]

- **Fatigue** [INHERITED]: increases per match by a value driven by the player's fitness relative to the match's mean fitness (fitter players fatigue less). Inherited band roughly `∈ [0.05, 0.45]` per match around a base of 0.25, modulated by fitness difference. Recovers daily by `√(fitnessValue)/100`. High fatigue reduces selection rating and raises injury risk.
- **Injuries** [INHERITED]: when `Normal(fatigue, 0.25) > 0.75`, the player is injured; injury length sampled from a decaying distribution over 1–365 days (probability ∝ `1.05^(−day)`, normalised) — many short knocks, a long tail of serious injuries. Injured players are unselectable and recover by counting down. **[NEW]** Injury risk and length modulated by traits (*Glass*/*Iron*), age (older players injure more, recover slower), pitch/condition, and recent congestion. Add injury *types* and severity tiers for narrative and for rehab/return-to-fitness (sharpness) mechanics.
- **Form** [INHERITED]: changes per match by `(performanceIndex − baseRating)/5` minus a gravity term (`form · 0.1`) that pulls extreme form back toward zero; decays daily toward 0 (`form −= form/25`). Form feeds selection and select-rating. **[NEW]** Trait *Mercurial*/personality *consistency* scale form variance.
- **[NEW] Morale**: a slower-moving emotional state driven by results, playing time, club success, contract situation, and manager man-management. Affects form variance and transfer requests.
- **[NEW] Sharpness/match fitness**: returning from injury or pre-season, players lack sharpness (a temporary cap on effective rating) that builds with minutes. Adds realism to rotation and returns.

### 7.10 Identity & avatars [NEW]

- **Names** [INHERITED fascination → NEW engine]: every player's forename + surname is **invented yet place-accurate**, produced by the nation's `NameModel` (Section 10.5) — *not* sampled from a list of real names. The predecessor sampled real frequency-weighted name lists (and handled "Mc"/"O'" capitalisation); we keep that fascination but replace list-sampling with genuine generation so names are both authentic *and* original. A player's name is a deterministic function of `(nationModel, regionNamingProfile, playerId, birthEra)`. **This is a headline feature, specified in full in Section 10.5 — treat it with the seriousness the user demands.**
- **Avatars** [NEW]: a deterministic, procedurally-generated visual identity per player — a parametric face/kit spec derived from the player's seed (skin tone, hair, features, etc.), rendered client-side. No external assets required; the spec is data, the rendering is presentation. Same player → same avatar forever.
- **Histories** [NEW]: every player carries a queryable career — clubs, seasons, appearances, goals, assists, average ratings, honours, transfers, injuries, and the rating/form time series the predecessor already captured (Section 17.6). This is the narrative payload that makes the world worth exploring across decades.

---

## 8. THE CLUB MODEL [mostly NEW; foundations INHERITED]

### 8.1 Identity & geography
Clubs are anchored to **invented cities** within nations (the predecessor's city-per-system mechanism, but with generated city names — Section 10.5), one or more clubs per significant city. **Club names are invented and place-accurate**: generated from the city/region name plus the nation's club-naming conventions (e.g. an English-style "<Place> United / City / Town / Rovers / Albion / Wanderers", a Spanish-style "Real / Atlético / Deportivo / CD <Place>", an Italian-style "<Place> Calcio / AC / FC", a Brazilian-style "<Place> EC / SC / Atlético <Place>") — see Section 10.5.4. Each club also gets a nickname, founding year, colours, crest spec, and stadium. User-supplied custom club/city names remain supported (the predecessor allowed custom club names that displaced random cities), and an *optional* opt-in pack of affectionate real-name overrides may exist for personal play — but the **default world contains only invented names.**

### 8.2 Reputation
A bounded scalar (or tier) that drives: quality of generated/attracted players, seeding in competitions, fan size, finances, and transfer attractiveness. Reputation updates over chronology based on results and trophies — *this is how dynasties and fallen giants emerge*. The predecessor's ±10 club easter egg becomes a principled **reputation→generation prior**: high-reputation clubs generate/sign stronger squads. Keep affectionate hand-tuned overrides possible for specific named clubs.

### 8.3 Finances & economy hooks
Each club has a balance, wage budget, transfer budget, income (gate receipts scaled by stadium/fans/results, prize money, TV/commercial by reputation/tier, transfer sales), and expenditure (wages, transfers, upkeep). Finances gate transfer/wage behaviour (Section 16) and can force sales or enable splurges. Keep money in integer minor units (`Money` value object), never floats.

### 8.4 Philosophy & board
- **Philosophy**: youth-vs-buy, attacking-vs-defensive, possession-vs-direct — biases recruitment, tactics, and youth investment.
- **Board**: expectations (target finish, cup runs), patience, wealth, and willingness to back the manager — drives manager hiring/firing (Section 9) and budgets. Boards react to over/under-performance vs expectation.

### 8.5 Stadium & facilities
Capacity and quality (affect gate income and atmosphere); training quality (affects development, Section 7.2); youth academy quality (affects intake quality/quantity, Section 17.1). These are investable over chronology.

### 8.6 Fanbase
Size (scales with reputation/results/city population) and mood (reacts to results) — feeds income and board pressure, and is a narrative surface.

---

## 9. THE MANAGER MODEL [NEW]

Managers are persistent identities who run clubs (and national teams). They:

- Have a **tactical profile** (preferred formations as a weighted list — reusing the formation-popularity mechanic; attacking/pressing bias; risk tolerance; youth preference; transfer aggression).
- Have **abilities** (tactical skill, man-management, development, recruitment) that *measurably* affect outcomes: tactical skill nudges in-match effectiveness; development boosts youth growth; man-management affects morale/form; recruitment affects scouting accuracy and signing quality.
- **Make decisions** (Section 19.3): squad selection, tactics, transfers, contract offers — via an **AI policy** (Section 9.2) when not user-controlled.
- Have a **career**: clubs managed, trophies, win rates, reputation — and get **hired and fired** by boards based on results vs expectations, creating a managerial merry-go-round.

### 9.1 Manager ↔ club fit & the merry-go-round
Boards hire managers whose reputation/profile fits the club's reputation and philosophy; sustained underperformance triggers sacking; better clubs poach successful managers. This produces emergent managerial careers. Calibrate hire/fire thresholds against plausible turnover rates.

### 9.2 AI manager policy
A deterministic, seeded decision policy that, given a club's state and the world, chooses lineups (Section 13), tactics, transfer targets and bids (Section 16), and contract actions. Must be: cheap (runs for hundreds of clubs per window), plausible (no degenerate behaviour — e.g. not selling all strikers), and tunable by ability/personality. Keep it modular so smarter policies can replace it. **The same policy interface is what a human user implements when they take control of a club** (Section 19).

---

## 10. WORLD GENERATION & GEOGRAPHY [NEW scope; INHERITED seeds]

### 10.1 Generation is deterministic and layered
From the master seed, generate in a fixed order: confederations → nations (with their `NameModel`s loaded from reference data) → geography (regions and **invented cities** with generated names, populations, reputations) → pyramids/divisions → clubs (anchored to cities, with **invented names**, reputations, stadiums, finances, philosophies, boards) → managers (invented names) → players (invented names; squads biased by club/nation reputation) → initial contracts → initial calendar/competitions. Each layer draws from its own RNG sub-stream so changing one layer's logic doesn't reshuffle others. **All names are generated deterministically by the nomenclature engine (Section 10.5).**

### 10.2 Reference data
Ship curated, versioned reference datasets: **nations** (real, with confederation membership, currency, calendar profile, culture profile, and reputation tier), a rough **geography prior** per nation (how many cities/regions, coastal vs inland, population distribution), and — crucially — a per-nation **`NameModel`** (Section 10.5): the statistical+morphological model from which all invented person, city, and club names are generated. The `NameModel` is *derived from* real naming data (frequency distributions, phonotactics, morphology) but ships as a generator, **not** as lists of real names to copy. This is the principled evolution of the predecessor's MongoDB `cities`/`forenames`/`surnames` collections. Make scale configurable: a *small* world (a few nations, a couple of tiers) for fast iteration; a *large* world (dozens of nations, deep pyramids, continental competitions) for ambition. Tests run on small worlds; calibration runs on large.

### 10.3 Reputation gradients & generation priors
Nation reputation tiers and club reputations form a gradient that biases player generation (peak-rating mean shift), squad depth, finances, and seeding. This makes stronger nations/clubs genuinely stronger *and* makes movement up/down the gradient (transfers, promotion) meaningful.

### 10.4 Footballing culture profiles [NEW]
Each nation carries a culture profile (formation preferences, technical/physical/pace bias, youth-development strength, average reputation) so that nations *feel* different — a technical-passing nation vs a physical-direct one — expressed through generation priors and AI tactical preferences. Calibrate lightly; keep it data-driven.

### 10.5 NOMENCLATURE — invented but place-accurate names [NEW — a headline feature, specified in full]

> *The user's words: "while countries can be real, all city names, club names, person names must be invented, but crucially must feel real and place-accurate. Names were always an important part of the fascination of this for me — I remember looking at lists of the most popular surnames in Uruguay. Modelling name distributions is important — so put some real emphasis on name generation."*

This is a **first-class subsystem**, not a string helper. It must be engineered, calibrated, and tested with the same rigour as the match engine. Build it in the `generation/` module as a self-contained, deterministic, data-driven **nomenclature engine** with its own test suite and its own inspection/calibration tool.

#### 10.5.0 The hard requirement
- **Nations may be real. Everything more granular must be invented.** No city name, region name, club name, person name, or stadium name in a default world may be a real-world name. Yet each must be *immediately recognisable as belonging to its place.* A Uruguayan back four should read as Uruguayan; an English non-league squad should read as English; a Japanese midfield as Japanese.
- The engine never *copies*; it *generates*. Real naming data is training/reference material for the **statistical and morphological character** of a place — never a pool to sample verbatim.

#### 10.5.1 The `NameModel` (per nation, possibly per region/ethnicity)
A versioned reference-data artefact per nation, composed of:

1. **Orthographic/phonotactic generators** — character- or syllable-level **n-gram / Markov models** (and/or learned grammars) capturing how names are *spelled and sound* in that language: which letter clusters, onsets/codas, vowel patterns, and endings are characteristic. These are *derived from* real forename/surname corpora but emit novel strings. (E.g. a Spanish surname model readily emits plausible "-ez/-ales/-illo" forms; a Polish one "-ski/-czyk"; a Japanese one plausible kanji-romanisation patterns.) Tune model order so output is *recognisable but not memorised* (too-high order regurgitates real names — forbidden; see the novelty filter).
2. **Morphological rules** — explicit, data-driven formation rules layered over the phonotactic core:
   - **Surname formation patterns**: patronymic (e.g. Nordic "-son/-sen/-dóttir", Icelandic patronymics resolved per generation, Slavic "-ov/-ova / -ić"), occupational, toponymic, descriptive; **gendered surname endings** where the language uses them (e.g. "-ová", "-ska"); **compound/double surnames** (Iberian paternal+maternal); **particles and nobiliary prefixes** ("van", "van der", "de", "da", "di", "del", "von", "Mc/Mac", "O'") with correct casing and sorting; **mononyms** and **nicknames-as-names** where culturally apt (e.g. Brazilian football naming: short forms, diminutives "-inho", playful monikers).
   - **Forename conventions**: given-name inventories per culture and era; multiple given names where common; diminutive/hypocoristic forms.
3. **Frequency distributions (the "Uruguay surnames list" insight)** — model the *shape* of name popularity, which is strongly **Zipfian/long-tailed**: a handful of very common surnames borne by many, a long tail of rare ones. Generate a nation's surname *pool* so that commonness is realistic — many players share the local equivalent of "Smith/González/Sato", while uncommon names appear rarely. **This distributional realism is the soul of the feature**: a squad list should show believable repetition and clustering of surnames, not uniform randomness. Forename popularity likewise follows realistic frequencies (and shifts by era — 10.5.5).
4. **Region/ethnicity mixture** — many nations are not monocultural. A `NameModel` can be a **weighted mixture** of sub-models (regional dialects, historical immigration, diaspora communities) so that, e.g., a nation's pool plausibly includes minority-origin names at realistic proportions, and regional naming biases show through (a player from one region leans toward that region's sub-model).
5. **Place-name conventions** — generators and morphology for **city/region names** (10.5.3) and **club names/nicknames/stadiums** (10.5.4), expressed in the same place's character.

#### 10.5.2 Person-name generation
`generatePersonName(nationModel, regionProfile, entityId, birthEra, secondaryNationality?) -> Name`:
- Deterministic from the entity's id + seed (same player ⇒ same name forever).
- Draw a forename (era- and region-aware) and a surname (from the Zipfian pool with morphology applied), apply particle/casing/compound rules, and assemble a `Name` value object with display variants (full, "F. Surname", surname-only, club-specific disambiguation when two squad-mates share a surname — the predecessor's `get_club_specific_name` behaviour [INHERITED]).
- Handle **secondary nationality / heritage**: dual-eligible players may carry a forename from one culture and surname from another (a rich source of plausible "diaspora" players and international-eligibility intrigue, Section 18.7).
- Correctly handle accents/diacritics, apostrophes, hyphenation, mononyms, and sort keys.

#### 10.5.3 City & region name generation
Invented but morphologically plausible per nation: combine characteristic roots/affixes (e.g. English "-ton/-ham/-ford/-bury/-mouth/-cester", Spanish "San/Santa/-ares", Germanic "-burg/-dorf/-heim", Japanese place morphology) with geography awareness (coastal vs inland affixes, river/hill roots). Deduplicate within a nation; assign plausible populations and a `footballReputation`. Region names follow the same approach at coarser grain.

#### 10.5.4 Club & stadium name generation
From a city/region name + the nation's **club-naming grammar** (a data-driven template set per footballing culture): English "<Place> United/City/Town/Rovers/Albion/Wanderers/Athletic", Iberian "Real/Atlético/Deportivo/CD/Sporting <Place>", Italian "<Place> Calcio / AC/FC <Place>", Brazilian "<Place> EC/SC / Atlético/Grêmio-style <Place>", etc. Generate matching **nicknames** (often derived from colours, local industry, or animals), **founding years**, **colours**, **crest specs**, and **stadium names** (commonly toponymic or honorific, also invented). Ensure intra-nation uniqueness.

#### 10.5.5 Era awareness (chronology)
Because the world runs for decades (Section 18), **naming drifts with time**: forename fashions change generation to generation (a player born in sim-year 2050 should carry era-appropriate given names relative to one born in 2000). Model forename-popularity as a slowly-evolving distribution keyed to birth era; surnames are far more stable. This keeps multi-decade histories feeling authentic rather than frozen.

#### 10.5.6 The novelty & safety filter (non-negotiable)
- **Originality guarantee**: every generated name is checked against a blocklist of real-world referents (a curated set of famous real footballers, clubs, and notable places) and rejected/resampled on collision, so the world never accidentally contains a real star or a real club. Tune n-gram order and add a near-duplicate check to avoid memorising training names.
- **Decency filter**: reject offensive or slur-adjacent strings via a maintained blocklist and heuristic checks. This must run on *all* generated names (person, city, club, stadium).
- Both filters are deterministic (resampling uses the next value in the entity's RNG sub-stream) so reproducibility holds.

#### 10.5.7 Determinism, performance & data-driven extensibility
- Names are pure deterministic functions of `(seed, entityId, model)`; no global state; same seed ⇒ same names across machines and reloads.
- Generation must be cheap enough to name tens of thousands of players plus thousands of cities/clubs at world creation, and each youth-intake season thereafter (Section 17.1), within the world-creation performance budget.
- Every `NameModel` ships as **versioned data** and is community-extendable: adding a new nation = adding a `NameModel`, no engine code changes. Provide a documented authoring format and a script to *derive* a `NameModel` from a real frequency corpus (offline tooling), emitting only the generator, never the source names.

#### 10.5.8 Calibration & inspection tooling (recapture the original fascination)
Build a **name-inspection tool** (part of the balancing dashboard, Section 25) that, for any nation/region/era, generates large sample lists of forenames, surnames, full names, cities, and clubs, with their frequency curves — so a human can *eyeball them and judge whether they "feel right"*, exactly as the user once pored over real Uruguay surname lists. Tuning a nation's `NameModel` until its invented output is indistinguishable-in-flavour from the real place is an explicit, valued part of the work. Add automated checks too: novelty rate = 100% (no real-name collisions), Zipfian fit of the surname distribution within tolerance, character-set/morphology validity, and decency-filter coverage (Section 23).

---

## 11. THE COMPETITION FRAMEWORK [NEW; generalises the predecessor's single league]

One general abstraction expresses every contest. The predecessor's commit history shows the author renamed "tournament" to "league" because "league is the only tournament" — *this section delivers the tournament abstraction they planned.*

### 11.1 CompetitionFormat as a composable rules object
A `CompetitionFormat` declares structure data-drivenly:

- **League (round-robin):** single or double round-robin [INHERITED double round-robin], points (3/1/0 [INHERITED]), tie-breakers (points, GD, GF, head-to-head — ordered, configurable), promotion/relegation slots, continental qualification slots, playoff slots.
- **Knockout:** single/two-leg ties (away-goals optional/legacy), seeding/draw rules, extra time, penalty shootouts (Section 14.6), byes, neutral-venue finals.
- **Group + knockout:** N groups round-robin → top K advance to a knockout bracket (continental-cup style).
- **Playoff:** mini-bracket appended to a league stage (promotion playoffs).
- **Super cup / one-off:** single match between two qualified clubs.

The format object drives the **scheduler** (Section 12), the **standings/bracket** projections, and the **qualification** wiring to other competitions.

### 11.2 The competition graph
Competitions are wired into a directed graph: a top division's final standings *feed* relegation (to the tier below), promotion (from below), and continental qualification (to confederation competitions); cup winners earn continental places and super-cup spots; continental results feed reputation and prize money. Encode these as declarative **qualification rules** evaluated at season rollover (Section 18). This graph is the backbone of chronology.

### 11.3 Promotion & relegation
At season end, apply each pyramid's promotion/relegation rules: swap the bottom K of tier *n* with the top K (plus playoff winners) of tier *n+1*, updating each competition instance's participant set for the next season. Maintain integrity (no club in two tiers; squad sizes still valid). This is a marquee feature the predecessor lacked.

### 11.4 Continental & international competitions
Confederation-level club competitions (group+knockout) seeded from nations' qualification slots; international tournaments for national teams (Section 18.7) on a multi-year cycle (e.g. continental championship + world tournament). These create cross-border drama and elevate player/club/nation reputations.

### 11.5 Seeding, draws, prize money, qualification
- **Seeding**: by reputation/coefficient (a rolling, results-based confederation coefficient per club/nation — calibrate à la real continental coefficients).
- **Draws**: deterministic from the world seed, respecting seeding pots and (optionally) same-nation separation in group stages.
- **Prize money**: per-competition prize models feed club finances, reinforcing the reputation/economy flywheel.

---

## 12. THE CALENDAR & SCHEDULING [NEW scope; INHERITED round-robin]

### 12.1 The world calendar
A season spans a configurable window (the predecessor used a 300-day fixture window inside a 365-day year [INHERITED], starting 2000-01-01). Generalise to real-ish season calendars per nation (autumn-to-spring or calendar-year), with pre-season, winter breaks, and international windows.

### 12.2 Multi-competition fixture scheduling
The scheduler must interleave *all* of a club's competitions (league + domestic cups + continental) onto a single congestion-aware calendar:

- **League scheduling**: a correct **circle/round-robin algorithm** for the league stage, double round-robin with home/away balancing [INHERITED — keep a *correct, tested* round-robin generator; the predecessor's hand-rolled one worked but rebuild it cleanly and test it exhaustively for balance and correctness, including odd numbers via byes].
- **Knockout scheduling**: place ties on appropriate dates between league rounds.
- **Congestion**: avoid (or deliberately model) fixture pile-ups; spread matches; respect minimum rest days; trigger rotation and fatigue consequences (Section 7.9.1). Fixture congestion *should* create real squad-rotation pressure — a feature.
- **International breaks**: pause club competitions; assemble national squads; risk injuries to club players (narrative tension).

### 12.3 Date assignment
Fixtures get concrete in-world dates so the tick engine (Section 6) plays them on the right day. Scheduling is deterministic from the seed. Standings/brackets update as fixtures resolve, exactly as the predecessor updated league tables per gameweek [INHERITED] — but generalised across competition types and stored as projections (Section 20).

---

## 13. SQUAD SELECTION & TACTICS [INHERITED core; NEW depth]

### 13.1 Formation selection
Each club/manager has preferred formations as a **popularity-weighted list** [INHERITED — keep the real-world weights: 4-4-2 ~0.22, 4-2-3-1 ~0.21, 4-3-3 ~0.13, 4-1-4-1 ~0.083, 3-4-2-1 ~0.060, 4-4-1-1 ~0.060, 3-4-3 ~0.059, 3-5-2 ~0.052, …]. **[NEW]** Add a goalkeeper to every formation's personnel so a valid XI = 1 GK + 10 outfield per the formation's outfield distribution. Managers may switch formations by opponent/situation [NEW].

### 13.2 Lineup selection [INHERITED greedy → NEW optimal-capable]
The predecessor selected greedily: repeatedly, across all unfilled positions, pick the single (player, position) with the highest **select rating**, where:

```
selectRating = positionRating(player, pos)
             − positionRating · fatigue                 // fatigue penalty
             + (positionRating · form) / 10             // form bonus
             × homeAwayDifferential                     // home 1.025, away 0.975, neutral 1.0  [INHERITED]
```

Injured players are excluded [INHERITED]. **[NEW]** Improvements while preserving the spirit:

- Make selection a proper **assignment optimisation** (maximise total select rating subject to formation constraints) so clubs field genuinely best XIs; keep the greedy version as a fast fallback and as a baseline test oracle.
- Factor in **rotation** (rest fatigued/at-risk players in congestion), **sharpness**, **morale**, **suspensions/cards**, **squad registration rules**, and **manager preferences** (e.g. youth preference, big-game lineups).
- Respect **squad roles** and **shirt numbers**; pick **set-piece takers** and a **captain** (highest authority/leader).

### 13.3 Tactics & instructions [NEW]
Beyond the XI, a tactic carries instructions (tempo, pressing, defensive line, width, directness) that shift the team's effective offence/defence and event profile in the match engine (Section 14). Manager tactical skill modulates how well instructions are executed. Keep tactic effects calibrated and bounded — they tilt probabilities, they don't dominate them.

### 13.4 Team aggregates [INHERITED — preserve the math]
From a Lineup, compute, exactly as the predecessor did:

- **average rating** of the selects; **normalise** each select rating toward the team average: `(2·self + 1·avg)/3` [INHERITED].
- **per-select offence/defence** from the skill shape × select rating × position offence/defence weighting × the **contribution matrix** [INHERITED]:
  - offence:{offence 1.0, defence 0.0}, spark:{0.9,0.1}, technique:{0.6,0.4}, defence:{0.0,1.0}, authority:{0.2,0.8}, fitness:{0.3,0.7}.
- **team offence/defence** = sums of select offence/defence.
- **goal factors** ∝ `((offence·2 + technique)/3 · selectRating · goalLikelihood[pos])²`, normalised — the per-player goal-scoring probability distribution [INHERITED].
- **assist factors** ∝ `((spark·2 + technique)/3 · selectRating · assistLikelihood[pos])^1.5`, normalised [INHERITED].
- Keep the inherited `goalLikelihood`/`assistLikelihood` per-position tables (CF highest goal likelihood; COM/WM highest assist likelihood; CB lowest assist) [INHERITED]. **[NEW]** Add GK goal/assist likelihood ≈ 0 (except penalties/set-pieces if modelled).

---

## 14. THE MATCH ENGINE [INHERITED statistical core; NEW fidelity & GK]

The match engine is calibrated and probabilistic — *honest generation, not scripted results*. Provide it at (at least) two fidelity levels sharing the same calibration so they agree in aggregate.

### 14.1 Level 0 — instant statistical result [INHERITED — preserve exactly as the baseline]
1. Compute each team's **potential** = `ownOffence − oppDefence` [INHERITED].
2. Index the **goal-probability table** by `round(potential)` ∈ [−100, 100] to get `(μ, σ)` [INHERITED — keep the exact table; it is calibrated so potential 0 → μ=1.5 goals, scaling smoothly to the extremes]. Goals = `clamp(round(Normal(μ, σ)), 0, 100)`.
3. Assign goals to **scorers** (via goal factors) and **assisters** (via assist factors; ~90% of goals assisted [INHERITED]; assister ≠ scorer); minute uniform 1–90 [INHERITED → 1–90+stoppage NEW].
4. Determine outcome (win/draw/loss), update standings/condition/finances, generate player reports (Section 15).

This level alone reproduces the predecessor's proven behaviour and is the **fast path** for simulating thousands of background matches per tick.

### 14.2 Level 1 — minute-by-minute event simulation [NEW]
For matches the user is watching (or for higher fidelity), simulate a timeline of events (chances, goals, cards, injuries, substitutions, momentum) whose *aggregate* distributions match Level 0's calibration. Use a possession/chance model driven by the same team offence/defence and tactics, producing expected-goals-like chances converted by finishing/goalkeeping. **The crucial constraint: Level 1 must be calibrated to agree with Level 0 in expectation** (same long-run scorelines, scorer distributions), so the choice of fidelity never changes the statistical world. Verify with tests (Section 23.4).

### 14.3 Goalkeeping [NEW]
With a real GK, model shot-stopping: a chance's conversion probability is reduced by the keeper's reflexes/handling and the shot quality. In Level 0, fold goalkeeping into the defending team's effective defence (so the calibrated table still applies); in Level 1, resolve saves explicitly. Goalkeepers earn performance ratings from saves/clean sheets, not goals.

### 14.4 Home advantage, venue, conditions [INHERITED + NEW]
Home/away differential (home 1.025, away 0.975, neutral 1.0) applied at selection/strength [INHERITED]. **[NEW]** Optionally extend with crowd size, weather, pitch, and travel/fatigue for away/continental trips — all as small calibrated tilts.

### 14.5 Tactics in the engine [NEW]
Tactic instructions and manager tactical skill shift effective offence/defence and the event profile (more pressing → more chances both ways and more fatigue; deep block → fewer chances conceded but fewer created). Bounded, calibrated tilts only.

### 14.6 Knockout specifics [NEW]
Extra time and penalty shootouts for drawn knockouts: extra time extends the timeline (scaled chance rates); shootouts resolved via a calibrated per-player conversion model (composure/technique/authority vs keeper). Deterministic from the match RNG sub-stream.

### 14.7 Cards & suspensions [NEW]
Model bookings/sendings-off (probability from match intensity, tactics, player discipline/temperament) feeding suspensions that affect future availability — another lever on rotation and squad depth.

---

## 15. PLAYER PERFORMANCE, RATINGS & MATCH REPORTS [INHERITED — preserve the rich model]

After each match, generate a `PlayerReport` per player, exactly in the spirit of the predecessor's `PlayerReportEngine` (this is one of its best parts — preserve the structure and calibration, behind named constants):

- **Base rating** from rating advantage vs opposition average, via a **sigmoid** mapped to a 2.5–7.5 band, with small noise [INHERITED constants: rating scale 5.0, sigmoid divisor 12.5, min 2.5, max 7.5, σ 0.5].
- **Contribution-weighted team performance**: compare actual vs expected goals for/against (expected from the goal-probability table), and credit/blame each player by their **offensive/defensive contribution share**, bounded (boost ∈ [−1.5, 1.5], multiplier 5.0) [INHERITED].
- **Goal/assist credit, context-weighted**: actual goals/assists boost the rating; *expected-but-absent* output applies a small negative; goals are worth more in **close** and **low-scoring** games (goal-difference component and goals-scored component combined 2:1) [INHERITED — keep this elegant context weighting]; assists worth ~75% of goals [INHERITED].
- **Performance index** = clamp(base + offensive boost + defensive boost − goalNeg + goalPos − assistNeg + assistPos, 0, 10) [INHERITED].
- **Man of the Match** = highest performance index in the match [INHERITED].
- **Fatigue increase** and **form change** derived as in Section 7.9.1 [INHERITED].
- **[NEW]** With GK and Level 1 events, incorporate saves, clean sheets, cards, and key events into the report. Add minutes played, substitutions, and (optionally) richer stat lines (shots, passes, tackles) derived consistently from the core model for presentation.

Aggregate player reports into **season stat lines** and **leaderboards** (games, goals, assists, MOTMs, average performance index) exactly as the predecessor's `get_performance_indices` did [INHERITED], generalised across competitions and seasons, with eligibility rules (e.g. minimum appearances for average-rating rankings).

---

## 16. THE TRANSFER MARKET & ECONOMY [NEW — a flagship system]

The predecessor had a global player pool and an unused `free_agent_players` list — the scaffolding for exactly this. Deliver a believable market that moves players for plausible reasons.

### 16.1 Transfer windows
Configurable windows per nation (e.g. summer + winter). Outside windows, no permanent transfers (loans/frees per rules). The calendar (Section 12) opens/closes windows; the tick engine processes market activity during them.

### 16.2 Player valuation
A derived `Money` value from rating, age (peak-age proximity), potential (and its remaining upside), position scarcity, contract length remaining, form/reputation, and buying-club/selling-club context. Valuation must be *stable and explainable* (a function you can unit-test), with market noise. This is the price signal the whole market runs on.

### 16.3 Wages & budgets
Wages scale with rating/reputation and are bounded by club wage budgets; transfer budgets bound fees. Finances (Section 8.3) hard-constrain behaviour — selling clubs can be forced to cash in; rich clubs can overpay. Wage/transfer inflation should be calibrated to avoid runaway economies over decades (a real risk in long sims — test for it, Section 23.7).

### 16.4 Contracts
Players hold contracts (wage, expiry, optional release clause, bonuses). Expiring contracts trigger renewals or **free transfers** (Bosman-style) [the `free_agent_players` concept realised]. Unhappy players (morale/ambition) may request moves. Contract state drives valuation and AI behaviour.

### 16.5 Negotiation as a state machine [NEW]
Transfers proceed through an explicit, deterministic negotiation state machine: interest → bid → counter/accept/reject (club-to-club) → personal terms (player wage/role) → medical (injury risk) → completion or collapse. AI clubs (Section 9.2) generate targets (squad needs × valuation × budget × philosophy) and bids; a user-managed club submits decisions at the same interface (Section 19). All deterministic from seed + decisions.

### 16.6 Loans, youth, and AI market behaviour
- **Loans** (with optional fees, wage splits, recall) for development of young players. Modelled explicitly (parent club + loan club).
- **Youth promotion** from academies into the senior squad (Section 17.1).
- **AI market**: hundreds of clubs must transact plausibly each window without degenerate outcomes (no fire-sales of whole squads, no impossible hoarding). Calibrate net flows, squad-size constraints, and positional needs. Emergent stories (a big club buys the breakout star from a smaller one) should arise naturally from valuations + needs + budgets.

### 16.7 Scouting & information asymmetry [NEW]
Clubs don't see perfect player data; scouting (gated by recruitment ability/facilities) reveals attributes/potential with uncertainty that narrows with scouting investment. This makes recruitment a skill, produces hidden gems and expensive flops, and gives the user meaningful scouting decisions. Keep "true" values in the model; expose "scouted" estimates to decision-makers.

---

## 17. PLAYER LIFECYCLE ACROSS SEASONS [NEW; INHERITED retirement]

### 17.1 Youth intake & regeneration
Each season (typically pre-season), academies generate **youth intakes**: new young players (Section 7.1) whose quantity/quality scale with academy quality, club reputation, and nation culture. This **replenishes the world** so it never runs out of talent across decades — the chronology engine's fuel. Some youth promote to the senior squad, some are loaned, some are released. Calibrate intake so the global talent distribution stays stable over time (no inflation/deflation of average quality — test it, Section 23.7).

### 17.2 Aging & decline
Handled by the age-curve model (Section 7.2). Across seasons, squads naturally age, decline, and must be refreshed — driving the transfer market and youth integration.

### 17.3 Retirement [INHERITED]
Players retire when declining below `peakRating · retirementThreshold` [INHERITED], or at an age ceiling, or via injury. Retired players leave squads but **persist in history** (and may become managers — Section 9, a lovely chronology touch).

### 17.4 The age pyramid
Maintain a realistic distribution of ages across the world at all times (generated initially across 15–40 [INHERITED], replenished by youth intake, drained by retirement). Monitor it as a calibration metric (Section 29).

### 17.5 Records, awards, halls of fame
Per season and all-time: top scorers, most appearances, player/young-player/manager of the season, golden boots per competition, record transfers, longest unbeaten runs, dynasties. Persist in the `RecordBook`. This is the narrative reward for long simulations.

### 17.6 Historical time series [INHERITED — keep, but cheap]
The predecessor stored per-date `rating`, `peakRating`, and `form` per player for graphs. Keep first-class time series, but record at a **sensible cadence** (e.g. weekly or per-appearance) rather than literally daily for every player, to keep storage and compute bounded across decades and tens of thousands of players. Time series power development/form/club-position graphs (Section 21).

---

## 18. SEASON LIFECYCLE & CHRONOLOGY [NEW — the headline ambition]

### 18.1 The season state machine
`SCHEDULED → IN_PROGRESS → COMPLETE → (rollover) → next Season`. The world runs seasons end-to-end, indefinitely, deterministically.

### 18.2 Pre-season
Youth intake (Section 17.1), retirements processed, manager changes resolved, summer transfer window, squad registration, fixture generation for all competitions (Section 12), budgets set by boards.

### 18.3 In-season
The tick engine plays the interleaved calendar (Section 6, 12), updating standings/brackets/condition/finances/history, processing the winter window, international breaks, board reviews (hire/fire), and injuries.

### 18.4 Season end & rollover
Crown competition winners; compute awards/records; apply **promotion/relegation** and **continental/international qualification** via the competition graph (Section 11.2); update **club and player reputations** based on achievements (driving the dynasty/decline flywheel); roll the clock into the next season; generate the next season's competitions and fixtures. Rollover must preserve all invariants (Section 5.12) and be fully tested (Section 23).

### 18.5 Reputation & dynasty dynamics
Sustained success raises club/manager/player/nation reputation → better generation/recruitment/finances → more success (with diminishing returns and regression so dynasties aren't permanent). Calibrate the feedback so the world stays competitive over decades (test for runaway dominance, Section 23.7).

### 18.6 Eras
Over many seasons, the world should exhibit *eras* — a dominant club, a golden generation, a record-breaking scorer — emerging from the same honest processes. The chronology layer surfaces these as narrative.

### 18.7 International football [NEW]
National teams select from each nation's eligible players; international tournaments run on a multi-year cycle; international duty injures club players and builds player reputation. Adds a whole second competitive arena from the same player pool.

---

## 19. USER INVOLVEMENT & INTERACTIVITY [NEW; FIX of fire-and-forget UX]

The predecessor was batch-then-browse. We make the simulation *interactive and steerable*, with clean modes layered on the same deterministic engine.

### 19.1 Modes
- **Spectator/observer**: generate a world and explore it (the predecessor's experience, vastly enriched: chronology, transfers, histories) — fast-forward seasons, browse anything.
- **Manager**: take control of one club — pick squads/tactics, buy/sell, manage finances/contracts/youth — and live the calendar match-by-match or window-by-window, competing against AI managers.
- **Commissioner/sandbox**: god-mode over the whole world — edit, force events, run experiments, tune calibration live.

### 19.2 The simulation "train" (steppable timeline)
Drive the engine at any cadence (season / day / match / decision) with **pause, step, fast-forward, and rewind-to-snapshot**. The user can stop at a decision point, act, and continue — all deterministic. Long fast-forwards run as background jobs with progress and cancellation (the predecessor's progress-reporting via Redis, generalised), resumable from snapshots.

### 19.3 Decisions as first-class engine inputs
The engine never blocks on I/O. Instead, each tick declares the **decisions it requires** (lineups, tactics, transfer responses, contract offers, board choices). The application layer fills them from the **user** (if controlling that club) or the **AI policy** (Section 9.2) otherwise, then feeds them back into the pure reducer. This is the seam that makes the engine both fully autonomous *and* fully user-steerable with identical determinism. A replay of recorded decisions + seed reproduces the exact world — a powerful debugging and "what-if" tool.

### 19.4 Notifications & narrative feed
Surface emergent stories to the user: breakout youngsters, transfer sagas, managerial sackings, records broken, title races, relegation battles. Generated from events (Section 20), not scripted. (The predecessor emailed on completion; generalise to an in-world news/notification feed.)

---

## 20. PERSISTENCE & THE SAVE MODEL [FIX — the biggest engineering upgrade]

Replace the predecessor's "pickle the live object graph into GridFS" with a real, explicit, versioned, queryable, migratable persistence model.

### 20.1 Event sourcing + snapshots (recommended) [DECISION]
- The authoritative history is an **append-only event log**: every state-changing fact (world created, tick advanced, match played, goal scored, transfer completed, injury sustained, season rolled over, decision made) is an immutable, typed, versioned event with the seed/key context needed to reproduce it.
- **Read models / projections** (standings, squads, leaderboards, histories, finances) are derived from events and stored in a queryable database (relational recommended) for fast reads. They are *disposable and rebuildable* from the log.
- **Snapshots** of full world state at season/period boundaries make load and resume O(snapshot + tail of events), not O(replay-everything).
- Because the engine is deterministic and decision-driven (Section 19.3), the log of `(seed, decisions)` is in principle sufficient to reconstruct everything — but persist projections + snapshots for performance.

If full event sourcing is too heavy for the first milestones, start with **explicit versioned snapshots of a normalised relational/document schema** (never pickled objects) and add the event log as the history/audit/narrative layer. Record the choice in an ADR. **Whatever you choose, the save format must be inspectable, queryable, and migratable — pickling live objects is forbidden.**

### 20.2 Schema versioning & migrations
Every persisted shape carries a `schemaVersion`. Provide forward migrations so old saves load into new engine versions. Test migrations (Section 23). This is what lets a world survive across years of development — the predecessor's pickles could not.

### 20.3 Identity, queryability, and scale
Stable IDs (Section 5.1) make everything joinable. The read model must answer rich queries cheaply: "top scorers in the third tier of nation X in season 12", "every club player Y played for", "head-to-head record", "the 2007 final's lineups". Index for these. Design for tens of thousands of players over decades without quadratic blowups.

### 20.4 Caching, TTLs, and housekeeping
Keep the predecessor's pragmatic touches generalised: progress tracking for long jobs, TTL/eviction for transient artefacts, and housekeeping of abandoned worlds — but as explicit, tested infrastructure, not ad-hoc scripts.

---

## 21. THE USER INTERFACE & PRESENTATION LAYER [NEW — a first-class deliverable]

> *The user's words: "we need a UI for this — yes the main thing is the simulation itself, but I also want a beautiful UI to explore all this lovely data."*

The engine produces a vast, living dataset; the UI is how a human **falls in love with it**. It is not a thin admin viewer — it is a designed product. Build it as a modern, component-based web application against the API, with a coherent design system, first-rate data visualisation, and an exploration model that makes the whole world feel like one interlinked, navigable encyclopedia. Keep all rendering and I/O out of the engine (Section 4.1); the UI consumes the read model over the API and renders client-side.

### 21.0 Design vision & principles
- **Beautiful and calm under density.** Football generates enormous data; the craft is presenting it legibly. Take cues from the best sports-data and financial dashboards: clear typographic hierarchy, generous-but-purposeful whitespace, tables that are scannable, numbers that are aligned and formatted, colour used for meaning (form, results, deltas) not decoration.
- **Everything is a clickable entity.** Player, club, manager, nation, competition, season, city, match — every reference anywhere in the UI links to that entity's page. Exploration is *wiki-like*: you start at a title race and three clicks later you're reading the youth-career page of a 17-year-old in the fourth tier of another country. This interlinked drill-down/drill-up is the core interaction and must be effortless.
- **Universal search & command palette.** Instant fuzzy search across all named entities (made delightful by the authentic names of Section 10.5), plus a keyboard command palette for power users (jump to entity, change season, run sim, open comparisons).
- **Narrative-forward.** Surface the stories the world is telling (Section 19.4): title races, relegation fights, breakout youngsters, transfer sagas, record chases, managerial sackings — as a living feed and as highlights on dashboards, all generated from events, never scripted.
- **Fast and responsive.** Virtualise large lists (squads, league-wide player tables of thousands), paginate/stream from the API, cache aggressively client-side, and keep interactions snappy even on a decades-deep world. Responsive from phone to wide desktop (the predecessor already had mobile detection — make it genuinely mobile-first). Accessible to **WCAG 2.1 AA**: keyboard navigation, semantic markup, sufficient contrast, screen-reader support, reduced-motion respect.
- **Themeable & identity-rich.** A design system with light/dark themes; club identity (colours/crests) and player **avatars** (Section 7.10, rendered client-side from the parametric spec) bring colour and character to every page. Crests and avatars are generated data, drawn in the browser — no external assets.
- **Delightful, not gratuitous.** Smooth transitions, tasteful micro-interactions, animated chart reveals, live-updating match views — used to aid comprehension, never to slow the user down.

### 21.1 API
A versioned HTTP/JSON (or GraphQL) API over the read model: worlds, nations, competitions, seasons, standings, brackets, clubs, squads, players (with histories/time series), managers, fixtures/matches (with reports and lineups), the transfer market, leaderboards, records, and the notification feed. Plus control endpoints for the interactive engine (Section 19): create world, step/fast-forward, submit decisions, snapshot/restore. Stable, documented, paginated, and fast.

### 21.2 Views worth carrying forward (the predecessor's surface, generalised)
The predecessor's pages map directly onto richer ones:

- **League table / standings** → standings & brackets for *any* competition, any point in any season [INHERITED → generalised].
- **Results & fixtures** by date/gameweek → full multi-competition calendar with filters [INHERITED → generalised].
- **Player performance leaderboards** (games, goals, assists, MOTMs, performance index, with club/position filters) [INHERITED — keep, extend across competitions/seasons].
- **Player page**: rating, best position, age, **radar chart of the skill shape with a projection to peak** [INHERITED — keep the projection idea], **development graph** (rating & peak-rating over time) [INHERITED], **form graph** [INHERITED], **injury history** [INHERITED], plus NEW: career history, transfers, honours, contract, avatar, scouting report.
- **Club page**: squad with positional ratings and best XI/formation, **league-position-over-time graph** [INHERITED], results, finances, history, board/manager [INHERITED → extended].
- **Fixture/match page**: lineups by position, performance ratings, scorers/assisters with minutes, MOTM, pre/post-match standings, recent form of both clubs [INHERITED — keep all of it], plus NEW: minute-by-minute timeline (Level 1), cards, subs.
- **NEW chronology views**: season archives, all-time records, halls of fame, transfer histories, head-to-heads, era summaries.

Charts are **data over the API**, rendered client-side as **interactive** visualisations (the predecessor server-rendered static matplotlib PNGs — we expose the series and let the client draw live, hoverable, zoomable charts, keeping the engine and server lean).

### 21.3 The signature experiences (build these to delight)
Beyond carrying the predecessor's pages forward, design these flagship experiences:

- **World dashboard / home.** The "state of the world" at a glance: current date, live title races and relegation battles across followed competitions, top performers, biggest recent transfers, breaking narrative feed, and quick entry to any nation/competition.
- **Exploration & entity pages (wiki-like).** Rich, interlinked pages for every entity. The **player page** is the jewel: avatar, identity, current ability and **best-position**, an **interactive skill radar with the projection-to-peak overlay** [INHERITED idea — made interactive], the **rating/peak-rating development graph over a career** [INHERITED], the **form graph** [INHERITED], **injury history** [INHERITED], plus full career history (clubs, season-by-season stat lines, honours, transfers), contract, valuation, and scouted-vs-true attribute uncertainty (Section 16.7). Like a footballer's encyclopedia entry, but alive.
- **Competition hub.** Standings (with an interactive **league-position-over-time** chart [INHERITED]), brackets for knockouts, fixtures/results across the whole season, leaderboards (scorers, assists, ratings, MOTMs), qualification/relegation picture, and the competition's history and roll of honour across seasons.
- **The match experience.** A beautiful match page: lineups laid out on a pitch by formation, scorers/assisters with minutes, performance ratings, MOTM, pre/post-match tables, both clubs' recent form [INHERITED — keep all of it]; and for watched matches, the **Level 1 minute-by-minute live timeline** (Section 14.2) — animated clock, momentum, chances, goals, cards, subs, and a generated commentary feed.
- **Manager mode UI** (Section 19.1): a squad/tactics board (drag players into formation, set roles/instructions/set-piece takers/captain), a transfer centre (scouting, shortlists, the negotiation state machine as a clear flow, budgets), contracts, finances, an inbox/news feed, and board-confidence/expectations. This is where the user *plays*; make it tactile and clear.
- **The simulation "train" controls** (Section 19.2): a persistent, elegant control bar to **play / pause / step (day, match, decision) / fast-forward / scrub** the timeline, with clear progress for long background runs and the ability to stop at decision points. The act of *driving time* should feel good.
- **Chronology & history browser.** Season archives, all-time and per-competition records, halls of fame, dynasty/era summaries, head-to-head records, and transfer histories — the reward for deep, long worlds.
- **Comparison & analysis tools.** Side-by-side player/club/season comparison; filterable, sortable world-wide player tables (virtualised) — the natural home for *browsing squad lists and savouring the authentic names* (Section 10.5), which is much of the fascination.

### 21.4 Frontend technology & architecture [DECISION]
- A modern component-based framework (e.g. a current React/Vue/Svelte-class stack) with a typed language (TypeScript) and a real **design system / component library** (tokens for colour/spacing/type; reusable table, card, chart, badge, pitch components).
- A capable **data-visualisation** layer (e.g. a D3-backed or equivalent charting library) for the radar, development, form, position-over-time, transfer-flow, and timeline charts — all interactive and themable.
- Robust client **state/data management** with caching, pagination, and optimistic updates; **real-time updates** (web-sockets/SSE) for the live match view and long-sim progress.
- **Avatar & crest rendering**: deterministic SVG/canvas drawing from the parametric specs (Sections 7.10, 10.5.4) — generated, not asset-bundled.
- Performance budgets and accessibility are enforced in CI (Section 23): bundle size, interaction latency, Lighthouse/axe checks, and visual-regression tests on key pages.
- Keep the UI a pure consumer of the API: it contains **no simulation logic** (that lives only in the engine core).

---

## 22. ENGINEERING STANDARDS & PROJECT STRUCTURE

Non-negotiable practices (the user asked for best practice "to the letter"):

- **Strict typing everywhere** in the core (full type annotations; `mypy --strict`/`pyright` strict as a CI gate). No untyped public functions.
- **Immutability by default** in the domain; explicit, localised mutation in reducers. No hidden global state (the predecessor's `Universe` singleton is banned).
- **Pure core / impure shell** boundary enforced by structure and by lint rules (the core must not import frameworks, DB drivers, clocks, or RNG globals).
- **Value objects over primitives** (Section 5.1) to kill unit/scaling bugs.
- **Data-driven configuration** (Section 26) — constants are named, centralised, documented, versioned, overridable.
- **Linting & formatting** enforced (the predecessor used ruff + pre-commit — keep and extend; add import-boundary and no-global-RNG lint rules).
- **Dependency pinning & lockfiles**; reproducible builds; pinned toolchain version.
- **Small, cohesive modules** (Section 4.3) with narrow typed interfaces and high unit-test coverage.
- **ADRs** for every significant decision (stack, persistence model, RNG model, GK introduction, fidelity levels).
- **Documentation**: a living architecture doc, module READMEs, and docstrings on all calibrated constants explaining *what they mean and what moving them does*.
- **CI** runs the full test suite, type checks, lints, the determinism gate, and the calibration smoke tests on every change. The suite must stay green.
- **Conventional commits** and a clean history; feature branches; no direct pushes to protected branches.

Suggested top-level structure (adapt to chosen stack):

```
/core            # pure deterministic engine (Section 4.3 modules)
/application      # use-cases, orchestration, decision intake
/adapters
  /persistence    # event store + read-model + migrations
  /api            # HTTP/GraphQL
  /jobs           # background sim runner, progress, cancellation
  /notifications
/data             # versioned reference data (nations, cities, names, formats)
/calibration      # constants + calibration harness + balancing reports
/web              # frontend
/tests            # unit, property, statistical, golden, integration, e2e, invariants
/docs             # ADRs, architecture, module docs
```

---

## 23. TESTING — "test the living daylights out of it"

Testing is a first-class deliverable, not an afterthought. A simulation this complex is only trustworthy if it is verified at many levels. Build the harness early; keep it green always.

### 23.1 Unit tests
Every pure function (generation, development curves, suitability/cosine math, selection, contribution math, goal/assist factors, valuation, scheduling, standings, qualification, negotiation state machine) tested in isolation with known inputs/outputs and edge cases (min/max bounds, empty squads, odd club counts, ties, zero-goal games).

### 23.2 Property-based tests
Use property-based testing to assert invariants over *generated* inputs:

- Skill profiles always sum-to-mean-1 within tolerance and stay in bounds after every transform.
- Position suitabilities are normalised (best = 1.0) and in [0,1].
- Goal/assist factors form valid probability distributions (non-negative, sum to 1).
- Standings derived from fixtures are internally consistent (Section 5.12).
- Round-robin schedules are balanced and complete for any even club count; byes correct for odd counts.
- A valid lineup always has exactly 1 GK + 10 outfield matching the formation, no duplicate players, no injured/suspended players.
- Money never silently goes negative; transfers conserve player registration (exactly one club).
- Promotion/relegation preserves total club counts per pyramid.

### 23.3 Golden / snapshot tests
Freeze the output of a fixed-seed small world over N ticks (standings, top scorers, a sample player's history, a sample match report) as golden files. Any unintended behavioural change fails loudly; intended changes update goldens deliberately in review. This is how you refactor the engine fearlessly.

### 23.4 Statistical / calibration tests
Because outcomes are stochastic, test *distributions*, not single results, over many seeds/matches:

- Average goals per match ≈ calibration target (the inherited table targets ~1.5 at even strength; assert league-wide goals/game lands in a realistic band).
- Home win rate within a realistic range; draw rate plausible.
- Scorer distribution concentrated on forwards/attacking mids per goal-likelihood weights; assists per assist-likelihood weights.
- ~90% of goals assisted [INHERITED]; assister ≠ scorer always.
- Player rating distribution ≈ the intended mean/σ; age pyramid realistic.
- Level 1 match engine agrees with Level 0 in aggregate (same long-run goals/scorers within tolerance) — Section 14.2.
- Performance index distribution centred plausibly (mean ~ mid-scale), MOTM always the max.

### 23.5 Determinism tests (the gate)
- Same seed + same decisions → identical world (hash full state). Run twice, in parallel, in different processes → identical.
- Save at tick k, reload, continue → identical to running straight through (Section 6.5).
- Reordering independent computations (e.g. simulating matches in parallel) → identical results (validates the key-derived RNG, Section 6.4).
This gate runs on every commit and blocks merge on failure.

### 23.6 Invariant checks over arbitrary worlds
A runnable validator that asserts *all* Section 5.12 invariants over any world state. Run it after every milestone's long simulations (e.g. simulate 50 seasons, then validate) to catch slow corruption.

### 23.7 Long-run stability ("soak") tests
Simulate many seasons (e.g. 50–100) on a small/medium world and assert the world stays *healthy*:

- No economic runaway (wage/fee inflation bounded; clubs not all bankrupt or all infinitely rich).
- Talent distribution stable (youth intake balances retirement; average quality flat over time).
- Competitive balance maintained (no single club wins forever; reputation feedback regresses).
- Age pyramid stable; squad sizes valid; no orphaned players/contracts.
- No memory growth/leaks; runtime per season stays roughly constant (performance regression guard).

### 23.8 Integration & end-to-end tests
Persistence round-trips (save/load/migrate), API contract tests, the interactive decision loop (submit decisions → deterministic advance), and a full "create world → manage a club for a season → roll over" e2e.

### 23.9 Performance tests / benchmarks
Benchmark tick throughput, season-simulation time, and memory at defined world scales; fail CI on regressions beyond a threshold. Profile and guard the hot paths (match engine, player development, scheduling).

### 23.10 Fuzz & chaos
Feed malformed decisions, extreme configs (1 club, 1000 clubs, all-injured squads), and adversarial inputs; the engine must fail gracefully or reject invalid input explicitly, never corrupt state.

### 23.11 Nomenclature tests (Section 10.5)
For every nation `NameModel`: **100% novelty** (no generated person/city/club/stadium name collides with the real-world blocklist or memorises a training name); **decency-filter coverage** (no offensive output across large samples); **morphology/character-set validity** (outputs conform to the language's allowed forms, particles, casing, diacritics); **distributional realism** (surname pools fit a Zipfian/long-tailed shape within tolerance; forename popularity shifts plausibly by era); **determinism** (same `(seed, entityId)` ⇒ same name across runs and reloads); and a maintained **golden sample set** per nation so flavour changes are reviewed deliberately. Pair automated checks with the human "feels right" review via the inspection tool.

### 23.12 UI tests (Section 21)
Component/unit tests for the design-system and chart components; **visual-regression** snapshots on key pages (dashboard, player, club, competition, match); **accessibility** checks (axe/WCAG AA: keyboard nav, contrast, semantics, screen-reader labels, reduced-motion); **frontend performance budgets** (bundle size, interaction latency, virtualised large-list rendering, Lighthouse thresholds) enforced in CI; API-contract tests so UI and backend never drift; and e2e journeys (explore a world, follow links across entities, manage a club for a season, watch a live match) in a headless browser.

---

## 24. PERFORMANCE & SCALABILITY

The ambitions (decades × dozens of nations × tens of thousands of players) demand designing for scale from day one — the predecessor's O(players × days) full recompute would not survive this.

### 24.1 Algorithmic discipline
- **Closed-form age/rating** instead of per-day iteration (Section 6.2).
- **Lazy, cached derived state** with input-keyed invalidation (Section 24.3).
- **Two-tier match fidelity**: fast Level 0 for background matches; expensive Level 1 only when watched (Section 14).
- **Efficient scheduling/standings** (no quadratic scans; maintain incremental standings as fixtures resolve).
- Avoid the predecessor's habit of deep-copying large structures per gameweek; use immutable sharing / structural sharing where possible.

### 24.2 Parallelism
Because matches on the same day are independent and RNG is key-derived (Section 6.4), **simulate a day's matches in parallel** deterministically. The reducer composes results in a fixed order so parallelism never changes outcomes (tested in Section 23.5).

### 24.3 Caching & memoisation
Cache `rating`, `positionSuitabilities`, `positionRatings`, team aggregates, and valuations keyed by their exact inputs; recompute only on change. Keep caches bounded and eviction deterministic-irrelevant (caches must never affect results, only speed — assert this).

### 24.4 Memory & data layout
Favour compact, columnar/struct-of-arrays layouts for the hot player-development math (vectorisable), keeping rich object views for the API. Stream/snapshot rather than holding all history in memory. Guard against unbounded growth of time series and event logs (cadence + compaction, Section 17.6/20).

### 24.5 Scale tiers
Make world scale a first-class config: *tiny* (tests), *small* (interactive single-nation), *large* (multi-nation continental), *huge* (whole world). Each tier has performance budgets enforced by benchmarks (Section 23.9).

---

## 25. OBSERVABILITY, REPRODUCIBILITY & BALANCING TOOLS

- **Structured logging & tracing** in the application layer (never in the pure core). Every long run reports progress, timing per phase, and anomalies.
- **The event log is the audit trail** (Section 20): any state can be explained by replaying its events. "Why did this club get relegated / this player retire / this transfer happen?" is answerable from events.
- **Reproduction handle**: every world is fully described by `(masterSeed, config, recordedDecisions)`. Bugs are reported and reproduced by that handle alone — the single most valuable debugging affordance in a stochastic system.
- **Balancing/calibration dashboard** (Section 26): run large sims and visualise the realism metrics (goals/game, win/draw rates, rating/age distributions, economy health, competitive balance, talent stability) so constants can be tuned with evidence, not vibes. The predecessor's matplotlib instincts, elevated into a proper balancing harness.
- **Determinism canary**: a CI job that fails if any state-hash drifts unexpectedly between versions (separating intended changes — update goldens — from accidental ones).

---

## 26. CONFIGURATION, CALIBRATION & DATA-DRIVEN DESIGN

- **One CalibrationSet to rule the constants.** Every tunable number in this document (peak-age/rating distributions, growth speeds, retirement threshold, skill distribution params, position archetypes, formation popularities, contribution matrix, goal/assist likelihoods, the full goal-probability table, home/away differential, fatigue/form/injury constants, performance-index constants, valuation/wage parameters, intake rates, reputation feedback) lives in a **named, documented, versioned configuration object**, not scattered in code.
- **Inherited defaults are the v1 calibration.** Seed the CalibrationSet with the exact inherited values in this document. They are a known-good starting point.
- **Calibration is versioned** so worlds record which calibration generated them (reproducibility across tuning changes).
- **Profiles**: ship calibration profiles (e.g. "realistic", "arcade high-scoring", "low-scoring tactical", per-era) selectable at world creation.
- **Reference data is data**: nations, cities, names, competition formats, and pyramids are versioned data files, not code — extendable without engine changes.
- **Feature flags**: GK modelling, Level 1 match engine, internationals, scouting fog-of-war, etc., are togglable so milestones can ship incrementally and be A/B-calibrated.

---

## 27. BUILD PHASES & MILESTONES (execution order for the one-shot)

Build in vertical, fully-tested slices. Do **not** proceed to the next milestone until the current one is complete, green, deterministic, and invariant-clean. Each milestone is a working simulation.

- **M0 — Foundations.** Project scaffold, strict typing, lint/format/CI, the RNG model (Section 6.4), value objects & IDs (Section 5.1), the event/reducer skeleton, the CalibrationSet (Section 26), and the testing/determinism harness (Section 23.1/23.5). *Exit:* an empty world ticks deterministically; determinism gate green.
- **M1 — Player & development core, and the nomenclature engine.** Player generation, skill profiles, positions (incl. GK), suitability math, age/rating curves, potential resolution, skill transitions, condition (fatigue/form/injury). **Plus the nomenclature engine (Section 10.5) for person names** — at least one fully-tuned nation `NameModel` end-to-end (phonotactics + morphology + Zipfian frequencies + novelty/decency filters + era awareness + inspection tool). *Exit:* player generation/development property+golden+statistical tests pass; closed-form aging verified equivalent to daily model; generated names pass the name-authenticity tests (100% novelty, Zipfian fit, decency coverage) and a human "feels right" review of sample lists.
- **M2 — One league season (parity with the predecessor, done right).** Clubs anchored to **invented, place-accurate cities** with **invented club names** (Section 10.5.3/10.5.4), lineup selection, team aggregates, Level 0 match engine, the calibrated goal table, player reports/performance index/MOTM, double round-robin scheduling, standings, leaderboards, season completion. *Exit:* reproduces the predecessor's statistical behaviour; full calibration tests pass; one season runs deterministically with all invariants holding; city/club names pass authenticity + novelty tests.
- **M3 — Persistence, API & the UI foundation.** Event store + read model + snapshots + migrations (Section 20); API over the read model; and the **UI foundation per Section 21** — the design system, the interlinked entity-exploration model (clickable everything, universal search), and the core pages (world dashboard, competition hub with standings + position-over-time chart, the rich player page with interactive radar/development/form charts, club page, match page) carrying forward and elevating the predecessor's views as *interactive* visualisations. *Exit:* save/load/migrate round-trips; e2e create-and-browse works; the core pages are responsive, accessible (WCAG AA), and pass visual-regression + a11y checks.
- **M4 — Chronology.** Multi-season rollover, youth intake/regeneration, retirement, age pyramid maintenance, records/awards/halls of fame, reputation updates. *Exit:* 50-season soak test passes (Section 23.7): stable talent/economy/balance, all invariants hold across rollovers.
- **M5 — Competition framework.** The general Competition abstraction, pyramids with promotion/relegation, domestic cups, the competition graph & qualification, multi-competition congestion-aware scheduling. *Exit:* a full domestic pyramid runs for many seasons with correct promotion/relegation and cups; brackets/standings invariant-clean.
- **M6 — Economy & transfers.** Valuations, wages, contracts, budgets, the negotiation state machine, AI market policy, loans, free transfers, scouting fog-of-war. *Exit:* multi-season market is plausible and stable (no runaway inflation/fire-sales); emergent transfer stories appear; economy soak test passes.
- **M7 — Managers & AI agency.** Manager identities/abilities/tactics, AI manager policy (selection/tactics/transfers/contracts), board hire/fire, the merry-go-round. *Exit:* managerial careers emerge; AI runs the whole world plausibly; results unchanged determinism gate green.
- **M8 — Geography & continental/international.** Multiple nations (each with a tuned `NameModel`, so every nation's names feel distinctively *theirs* — Section 10.5), confederations, continental club competitions, national teams & international tournaments (incl. dual-nationality eligibility from heritage names, Section 10.5.2), coefficients/seeding, culture profiles. *Exit:* a multi-nation world runs for decades with cross-border transfers and continental/international competitions; each nation's name authenticity reviewed and tested; large-scale performance budgets met.
- **M9 — Interactivity & fidelity.** The steppable simulation train (pause/step/fast-forward/snapshot-rewind), decisions-as-inputs, the manager play mode, the Level 1 minute-by-minute match engine (calibrated to Level 0), the notification/news feed. *Exit:* a user can manage a club through seasons against the AI world; Level 0/Level 1 agree in aggregate; interactive determinism (replay decisions) verified.
- **M10 — Polish, scale, balance & UI delight.** Avatars and crests (client-rendered from parametric specs), traits/personality depth, sub-attributes for presentation, the manager-mode UI and live Level 1 match view, the narrative/news feed, the balancing dashboard (incl. the name-inspection tool), performance hardening at the largest scale tier, full accessibility pass, and full documentation. *Exit:* huge-scale world runs within budget; the UI is genuinely beautiful, fast, accessible, and delightful across devices (visual-regression, a11y, and performance budgets green); calibration dashboard green on all realism metrics; everything documented.

At every milestone: full test suite green, determinism gate green, invariants clean, performance budgets met, ADRs and docs updated.

---

## 28. DEFINITION OF DONE & ACCEPTANCE CRITERIA

A milestone (and the project) is "done" only when:

1. **Deterministic**: same seed + decisions → identical world, across processes and save/load cycles (Section 23.5).
2. **Invariant-clean**: all Section 5.12 invariants hold over arbitrary long-run worlds (Section 23.6).
3. **Calibrated**: all realism metrics (Section 29) land within target bands on statistical tests (Section 23.4).
4. **Stable over time**: long-run soak tests pass — economy, talent, and competitive balance stay healthy across many seasons (Section 23.7).
5. **Performant**: meets the scale tier's performance/memory budgets (Section 23.9, 24).
6. **Typed, linted, documented**: strict types, clean lints, ADRs, and docstrings on calibrated constants — all green in CI.
7. **Reproducible & persistent**: worlds save/load/migrate via the explicit schema (never pickled objects); reproducible from `(seed, config, decisions)`.
8. **Authentically named**: every city/club/person/stadium name is invented (100% novelty vs the real-world blocklist), decent, and place- and era-accurate; each nation's `NameModel` passes its nomenclature tests (Section 23.11) and a human flavour review.
9. **Beautifully presented**: the UI meets the Section 21 design bar — interlinked entity exploration, interactive data-viz, responsive, WCAG AA accessible, within frontend performance budgets, and passing visual-regression + a11y + e2e UI tests (Section 23.12).
10. **Tested at every level**: unit, property, golden, statistical, determinism, invariant, nomenclature, UI, integration, e2e, performance, fuzz — all green.

---

## 29. CALIBRATION TARGETS (realism benchmarks)

Tune toward these (data-driven, adjustable per profile; inherited values are the v1 anchor):

- **Goals/match**: realistic top-league band (≈ 2.5–3.0 total; the inherited table anchors ~1.5 per side at even strength). Distribution right-skewed; clean sheets and high-scoring games both occur.
- **Result split**: home win > draw > away win in plausible proportions; home advantage modest (inherited ±2.5%).
- **Scoring distribution**: forwards/attacking mids dominate goals per goal-likelihood weights; assists spread per assist-likelihood weights; ~90% goals assisted.
- **Player ratings**: world mean ≈ 60–67 with σ ≈ 10 (inherited peak-rating ~N(66.67,10)); a believable elite tail.
- **Age pyramid**: realistic spread 16–38 with mass around mid-20s; peak performance ~27 (inherited).
- **Careers**: realistic appearance/goal totals; breakouts, primes, declines, and retirements occur at plausible rates.
- **Economy**: bounded wage/fee inflation over decades; top clubs richer but not infinitely so; lower clubs solvent.
- **Competitive balance**: strong clubs win more but no permanent monopoly; promotion/relegation churn; occasional upsets and cinderella cup runs.
- **Talent stability**: youth intake balances retirement; average global quality flat over decades.
- **Transfers**: plausible volume and net flows per window; stars gravitate to bigger clubs; bargains and flops both exist.
- **Name authenticity (Section 10.5)**: surname pools fit a Zipfian/long-tailed distribution within tolerance; 100% novelty (no real-name collisions); per-nation samples pass a human "feels right as <nation>" review; forename fashions shift believably across eras. *This is a calibration target, judged with the same seriousness as goals-per-match.*

If a metric drifts out of band, treat it as a calibration bug and fix the constant — with evidence from the balancing dashboard (Section 25).

---

## 30. STRETCH & FUTURE (explicitly out of scope for v1, designed-for)

Leave clean seams (don't build yet, but don't preclude): set-piece/penalty specialists and dead-ball sub-models; weather/pitch/altitude; richer tactical systems (roles, duties, mentality) and in-match tactical AI; financial fair-play and ownership/takeovers; player relationships/cliques and dressing-room dynamics; agents as actors in negotiations; dynamic media/press narratives; data export and a public API for community tooling; multiplayer (multiple users managing clubs in one world); modding (community calibration/reference-data packs); and ML-assisted calibration that tunes constants toward target metrics automatically.

---

## Appendix A — Inherited constants quick reference (v1 calibration anchor)

Implement these exactly as CalibrationSet defaults (Section 26). They are the proven starting point.

- **Time**: tick = 1 day; season fixture window ≈ 300 days within a 365-day year; double round-robin.
- **Player age at generation**: uniform 15–40.
- **Peak age** ~ N(27, 2) ∈ [22, 32]. **Peak rating** ~ N(66.67, 10) ∈ [20, 100].
- **Growth speed**: incline ~ N(0.75, 0.1) ∈ [0.25, 1.25]; decline ~ N(0.875, 0.1) ∈ [0.375, 1.375].
- **Retirement threshold** ~ N(0.80, 0.025) ∈ [0.70, 0.90].
- **Rating curve**: `peakRating · (1 − distanceFromPeak^1.5 · 0.01 · growthSpeed[direction])`.
- **Potential jitter**: `peakRating ← N(peakRating, 50/age²)`, clamped [20,100] (apply weekly).
- **Skill generation**: each skill ~ N(1, 0.375) ∈ [0.25, 1.75]; centralise mean→1; rebalance in-bounds; best-position normalisation pull ~ N(0.5, 0.05) ∈ [0, 0.5]; re-centralise.
- **Skill transitions**: spark→authority gradient −0.01 (both phases); fitness −0.015 (decline only).
- **Position suitability**: `1 − cosineDistance`, sharpened `1 − (1 − s)^(2/3)`, normalised so best = 1.0; positionRating = rating · suitability.
- **Position archetypes**: the nine inherited vectors in Section 7.4 (+ a NEW GK archetype).
- **Formations & popularity**: the inherited weighted set (4-4-2 ~0.2216, 4-2-3-1 ~0.2121, 4-3-3 ~0.1320, 4-1-4-1 ~0.0826, 3-4-2-1 ~0.0596, 4-4-1-1 ~0.0602, 3-4-3 ~0.0589, 3-5-2 ~0.0520, 4-3-1-2 ~0.0323, 5-3-2 ~0.0273, 5-4-1 ~0.0238, 4-5-1 ~0.0101, 3-4-1-2 ~0.0105, 3-5-1-1 ~0.0081, 4-2-2-2 ~0.0056, 4-3-2-1 ~0.0019, 4-1-3-2 ~0.0014) — each NEW-augmented with a GK.
- **Contribution matrix** (skill → {offence, defence}): offence {1.0, 0.0}, spark {0.9, 0.1}, technique {0.6, 0.4}, defence {0.0, 1.0}, authority {0.2, 0.8}, fitness {0.3, 0.7}.
- **Goal likelihood** by position: CF 1.0, WF 0.975, COM 0.95, WM 0.95, CM 0.925, CDM 0.875, WB 0.875, FB 0.85, CB 0.85 (GK ≈ 0).
- **Assist likelihood** by position: COM 1.0, WM 1.0, WF 0.975, CF 0.95, CM 0.95, WB 0.95, FB 0.925, CDM 0.9, CB 0.08 (GK ≈ 0).
- **Goal factor** ∝ `((offence·2 + technique)/3 · rating · goalLikelihood)²`, normalised. **Assist factor** ∝ `((spark·2 + technique)/3 · rating · assistLikelihood)^1.5`, normalised. ~90% of goals assisted; assister ≠ scorer; minute uniform 1–90.
- **Home/away differential**: home 1.025, away 0.975, neutral 1.0.
- **Goal probability table**: the inherited [−100..100] → (μ, σ) table (μ=1.5 at potential 0, σ≈1.225 near zero, both rising smoothly toward the extremes). Reproduce it exactly.
- **Performance index**: base via sigmoid (scale 5.0, divisor 12.5, band 2.5–7.5, σ 0.5); contribution boosts bounded [−1.5, 1.5] with multiplier 5.0; goal/assist context weighting (close & low-scoring games worth more; assists 75% of goals); final clamp [0, 10]; MOTM = max.
- **Fatigue**: per-match increase band ≈ [0.05, 0.45] around base 0.25 (modulated by fitness vs match-mean fitness, σ 0.05); daily recovery `√(fitness)/100`.
- **Injury**: trigger when `N(fatigue, 0.25) > 0.75`; length over 1–365 days with probability ∝ `1.05^(−day)`, normalised.
- **Form**: change `(performanceIndex − baseRating)/5 − form·0.1`; daily decay `form −= form/25`.
- **Team select-rating normalisation**: `(2·self + 1·teamAvg)/3`.
- **Club DNA prior** (generalising the ±10 easter egg): reputation-driven shift on generated peak ratings, with room for named overrides.
- **Names** [INHERITED fascination → NEW engine]: the predecessor sampled forename+surname from real, frequency-weighted lists (with "Mc"/"O'" casing) and used real city names. v1 here **replaces list-sampling with generation**: per-nation `NameModel`s (phonotactics + morphology + Zipfian frequency + era drift + novelty/decency filters) produce **invented but place-accurate** person, city, club, and stadium names (Section 10.5). Keep the frequency-distribution realism (the "Uruguay surnames" long tail); keep club-specific surname disambiguation [INHERITED `get_club_specific_name`]; default worlds contain *no* real city/club/person names.

---

*End of master build prompt. Build the keel first — the data model, the deterministic tick engine, the RNG. Preserve the inherited soul — honest generative statistics. Then extend with ambition — time, geography, competition, economy, agency, identity — and test the living daylights out of every inch of it.*
