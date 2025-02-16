# Soccer Simulation

At its heart, the simulation is built on several layers of configuration and dynamic processes.

## Configuration and Setup

The simulation is initialised with a suite of configuration settings that determine the size and structure of the simulated universe. This includes:

* Number of systems
* Leagues per system
* Clubs per league
* Players per club

Time is managed by defining a start date and allowing the simulation to "time travel" through days or gameweeks, updating state as it progresses. Formations are predefined with both a personnel layout—for instance, a "4-4-2" or "3-5-2" arrangement—and a popularity weight that probabilistically influences which formation a club will adopt.

## Detailed Player Development Model

### Initial Attributes

Each player is initialised with six key skill attributes – offence, spark, technique, defence, authority, and fitness. For each attribute, a raw value is drawn from a bounded normal distribution (with a mean of 1, standard deviation of 0.375, and limits between 0.25 and 1.75) and then adjusted by a normalising factor (mean 0.5, standard deviation 0.05, and capped between 0 and 0.5). After sampling, the distribution is centralised so that the average skill is set to 1, and a rebalancing routine ensures that no attribute exceeds its specified bounds. This careful normalisation and rebalancing ensure that the overall player pool maintains consistent and realistic skill profiles.

### Age and Development

Upon creation, each player is assigned an age chosen randomly within a defined range (15 to 40 years). Their birth date is computed relative to the simulation’s start date, introducing a natural spread in ages. In addition, each player receives a peak age (typically around 27 years, with a standard deviation of 2 and limits from 22 to 32) and a corresponding peak rating (with an average of roughly 66.67, a standard deviation of 10, and bounded between 20 and 100). A player’s current rating is then computed as a function of their age relative to their peak age. During the pre-peak phase the rating increases gradually as the player develops, while after reaching peak age the rating declines. The rate of improvement and decline is determined by configurable growth speed factors (with mean values of about 0.75 for improvement and 0.875 for decline), allowing the simulation to capture diverse developmental trajectories.

### Skill Transitions

As players age, certain skills transition to reflect changing strengths. In particular, the simulation implements a gradual reduction in the “spark” attribute – which represents a player’s ability to create something from nothing – and a corresponding increase in “authority,” reflecting the gain in game intelligence and leadership. This transition is applied continuously during both the developmental (pre-peak) and ageing (post-peak) phases with a typical gradient of –0.01. Additionally, the fitness attribute is subject to a decline during the post-peak phase at a slightly steeper rate (around –0.015), representing the natural physical degradation with age.

### Visualisation

The system also provides visualisation tools that plot predicted ratings over time – marking the point of peak age – and generate radar charts to illustrate the distribution of skill attributes. These tools help users track individual development and maintain overall balance within the player pool.

## Team Formation and Tactical Selection

Each club is first assigned a "favourite formation" by randomly selecting from the available formations – with the probability of selection weighted by each formation’s popularity. Once the formation is chosen, its personnel requirements (i.e. the number of players needed for each position) are deep‐copied from the configuration.

The team selection algorithm then proceeds iteratively. While there are still unfilled positions, the system scans every required position with a remaining player quota. For each such position, it evaluates every available player (from the club’s squad) who is not already selected and, unless in test mode, is not injured. For each candidate, a "selectRating" is computed as follows:

- The player’s positional rating for the required position is used as the base value.
- This rating is reduced by an amount proportional to the player’s fatigue.
- It is then increased slightly based on the player’s recent form (with the increment scaled as one-tenth of the product of the rating and the form value).
- Finally, the rating is multiplied by a home/away differential factor (for example, around 1.025 for home fixtures and 0.975 for away matches).

The player with the highest computed selectRating for the position is then selected, and the required count for that position is decremented. This process repeats until all positions specified by the formation are filled. The final tactical lineup is then aggregated into a team object – which subsequently calculates overall offensive and defensive ratings based on the contributions of the selected players.

## Match Simulation and Outcome Determination

### Match Process

At the start of a match, each team’s potential is computed by subtracting the opposing team’s defensive strength from its own offensive strength. This differential quantifies the likelihood of generating scoring opportunities. The resulting potential value (rounded to an integer) is then used to look up a corresponding Gaussian probability distribution—with specific mean (mu) and standard deviation (sigma) parameters—preconfigured for goal scoring. A random sample from this distribution determines the number of goals a team scores, while venue factors (such as home or away status) further adjust the effective strength through multipliers applied earlier in team selection.

### Performance Tracking

The simulation meticulously tracks individual player contributions during a match. Each player’s involvement is captured through detailed metrics including their offensive and defensive actions, and specific probabilities for scoring goals or providing assists—values that are modulated by their positional attributes. In addition, performance is influenced by fatigue, with increased fatigue reducing a player’s effective output. These factors are all integrated into a complex performance index that reflects overall contribution, ensuring that subsequent evaluations (such as player ratings and team selection) are grounded in realistic match dynamics.

## League Progression and Statistical Updates

After each match, the system:
* Updates league tables
* Maintains historical match records
* Tracks key statistics:
  * Games played
  * Wins/draws/losses
  * Goals for/against
  * Goal difference
  * Points

## Persistence, Visualisation, and Notification

The system features:
* State serialisation using GridFS and database storage
* Email notifications upon simulation completion
* Detailed reports and visualisations
* League position tracking over time

## Additional Nuances and Easter Eggs

The simulation includes special treatments for certain clubs, with adjusted peak ratings to emulate historical reputations.

## Summary

The simulation achieves sophisticated balance through:

1. **Detailed Statistical Models**
   * Player growth and decline based on age
   * Experience-based development

2. **Tactical Formation Logic**
   * Player condition consideration
   * Optimal lineup selection

3. **Probabilistic Match Simulation**
   * Team potential translation
   * Realistic goal outcomes

4. **Continuous Updates**
   * League standings
   * Player performance metrics
   * Gameweek progression