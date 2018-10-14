# UoM COMP90054 Contest Project

*This is a PRIVATE repository for COMP90054 project2.*

## Team Members
+ Team Name: Pelican
  + **Kangping Xue 878962**
  + **Xiang Gao 919108**
  + **Ming Jin 947351**

## Youtube Presentation
[A recorded oral presentation](https://youtu.be/W_GWYphGCkE)

## Theoritical and Experimental Design
The two techniques used in our agent:
+ Heuristic Search(A*)
+ Game Theory

### Theoritical Design
+ Attacker Agent
  + Using A* to find the optimal path to get foods or capsules
  + Using A* to find the safest route to escape from opponent's ghosts
  + Using Game Theory to determine a dominant stategy between foods and capsules
+ Defender Agent:
  + Using A* to find the best way to catch their Pacman
  + Using A* to escape from their "Super" Pacman

### Experimental Design
+ Attacker Agent
  + Go back home after eating enough foods
  + Go back home after detecting opponent's ghost
  + Help our defender to catch our opponent's ghost if attacker in our domain
  + Using Game Theory to find the best opportunity to eat the capsule
  + The strategy after eating a capsule(e.g. Super state)
+ Defender Agent:
  + Pratrol around our border
  + If one of our food has been eaten, it will be forced to that position in order to increase the chance to discover and catch their Pacman
  + Keep in distance with their "Super" Pacman

## Performance in Several Scenarios
| Scenario            | Performance|
| -------------       |:-----------------:| 
| **RANDOM1:** medium size, two capsules, many alleys|   Medium        |
| **JumboCapture:** large size, two capsules, few alleys, many foods     |    Medium             | 
| **Contest09:** medium size, zero capsule, many alleys     | Low             | 
| **RANDOM10:** medium size, two capsules (near the border), few alleys     | High             |

### Description:
For the first scenario, our agents have a medium performance. Since there are many alleys, it is hard for our attacker to detect their ghosts. As a result, it may get a chance to be forced to the dead end. A mechanism of dead end detection may improve our agents' performance in the future.

For the second scenario, our agents' performance is acceptable as well, although our attacker may not be greedy enough to eat as many foods as possible. When the agent has eaten a certain number of foods, it may go back home and send foods back, which may affect our scores to some extent. However, this mechanism can improve our performance in most scenarios because it is too risky to carry too many foods in the enemy area.

As for the third scenario, our agents' performance is unsatisfactory. Apart from complicated alleys (i.e. many dead ends and narrow roads), our agents cannot trade off capsules and foods using the game theory.

In terms of the last scenario, our agents perform fairly well. The capsules are near our border, and therefore it is easy for our attacker to determine whether to eat capsules or foods with the game theory. In addition, our agents can always find an optimal path to reach the goal safely because of few alleys.

## Challenges
+ How to detect enemies that are not in the field of our view
+ How to find the balance between the nearest foods and capsules
+ How to act when our "Super Time" is almost running out
+ How to keep in distance with opponent's ghosts and "Super" Pacman

## Future Improvement
+ Dead end detection: avoiding enter the dead end if there are ghosts nearby
+ Detour mechanism: using a sophisticate stategy to find another optimal entry to their field when our attacker faces their defender directly in the border
+ Enemy trajectory prediction: predicting the route of their Pacman and find a route to intercept it before reaching their domain
