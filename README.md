# UoM COMP90054 Contest Project

*This is a PRIVATE repository for COMP90054 project2.*

## Team Members
+ Team Name: Pelican
  + **Kangping Xue 878962**
  + **Xiang Gao 919108**
  + **Ming Jin 947351**
## Youtube Presentation
This is the presentation video
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
  + The strategy after eating a capsule(e.g. Super state)
+ Defender Agent:
  + Pratrol around our border
  + If one of our food has been eaten, it will be forced to that position in order to increase the chance to discover and catch their Pacman
  + Keep in distance with their "Super" Pacman
## Performance in Several Scenarios
| Agent         | Size of Map   | Number of Capusles  | Experimental Score|
| ------------- |:-------------:| -------------------:|------------------:|
| Offensive     | 30*20         | 2                   | 16                |
| Offensive     | 30*20         | 2                   | 12                |
| Offensive     | 30*20         | 2                   | -1                |

| Agent         | Size of Map   | Number of Capusles  | Experimental Score|
| ------------- |:-------------:| -------------------:|------------------:|
| Defensive     | 30*20         | 2                   | 16                |
| Defensive     | 30*20         | 2                   | 12                |
| Defensive     | 30*20         | 2                   | -1                |
## Challenges
+ How to detect enemies that are not in the field of our view
+ How to find the balance between the nearest foods and capsules
+ How to act when our "Super Time" is almost running out
+ How to keep in distance with opponent's ghosts and "Super" Pacman
## Future Improvement
+ Dead end detection: avoiding enter the dead end if there are ghosts nearby
+ Detour mechanism: using a sophisticate stategy to find another optimal entry to their field when our attacker faces their defender directly in the border
+ Enemy trajectory prediction: predicting the route of their Pacman and find a route to intercept it before reaching their domain
