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
Each player is created with an initial set of skill attributes across six key areas:
* Offence
* Spark
* Technique
* Defence
* Authority
* Fitness

These attributes are initially sampled from a normal distribution defined in the configuration and then centralised and rebalanced to ensure consistency across the player pool.

### Age and Development
* Players are assigned an age (typically between 15 and 40) and a birth date derived relative to the simulation's start date
* A **"peakAge"** and **"peakRating"** are generated using bounded random values
* Current rating is calculated as a function of distance from peak age:
  * Pre-peak: Rating increases
  * Post-peak: Rating declines
  * Rate of change controlled by configurable growth and decline parameters

### Skill Transitions
The simulation includes a subtle "transition" mechanism where, as players age:
* Certain skills (e.g., "spark") gradually decrease
* Other skills (e.g., "authority") increase to represent accumulated game intelligence

Visualisation tools produce plots of predicted ratings over time and radar charts displaying skill distribution.

## Team Formation and Tactical Selection

Clubs are assigned a "favourite formation" chosen randomly from available formations, weighted by popularity. The team selection process follows these steps:

1. Copy personnel requirements from chosen formation
2. For each required position:
   * Evaluate all available players
   * Calculate "selectRating" based on:
     * Positional rating
     * Fatigue adjustment
     * Recent form
     * Home/away differential
3. Select highest-rated player for each position
4. Complete tactical lineup aggregates into team object with offensive/defensive ratings

## Match Simulation and Outcome Determination

### Match Process
1. Team potential computation:
   * Difference between offensive strength and opposing defensive strength
2. Goal generation:
   * Potential value indexes Gaussian probability distribution
   * Home/away multipliers applied

### Performance Tracking
Individual player contributions tracked through:
* Offensive/defensive contributions
* Goal/assist likelihoods
* Fatigue adjustments
* Complex performance index calculations

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