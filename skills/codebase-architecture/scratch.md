system architecture: how we think about the system, how it runs in the real world

codebase architecture: how that system is represented in static code

## topics
how to organize files, screaming architecture, discoverable codebase, vertical slices x horizontal layers

## questions
- how does this connect to system-architecture? 
- can we actually separate containers with file organization and folders?
  - sometimes yes, sometimes no
  - ex. react frontend and convex BE living in separate folder: some yes
  - with frameworks like laravel with some orm or convex: maybe can't separate DB container
  - how about deployment glue?
  - gut feeling: 
    - they do not map 1-1. 
    - containers are hard to graps. are we sure what is the criteria to make one? 
  - different kinds of containers: // does this make sense? 
    - can be bounded/separated by code (ex. BE, FE in some framewroks)
    - can't de separated: ex. DB in case of using an orm?

## package by layer vs package by feature
- i think it's not that black and white
- some repos can decide for one or another but most of the times its not that simple
- presume: each repo is a monorepose. simplest case: one package
- inside one package one can package by feature or package by layer
- the value is making vertical slices x horizontal layers explicit, and enforcing them via rules, not forcing a single layout throughot the whole repo
- how about:
  - DO NOT FIGHT THE FRAMEWORK
  - group by deployment/phisical boundary? maybe container where it can be separated by code/framework allows? 
  - ex in case of fynk: 
    - laravel backend 
    - vue frontend
    - not fighting the framework :) 
    - both packaged by layer inside for the time being
    - FE is a mix:
      - some vertical slices are separated
      - inside them no horizonta layers explicitly
      - horiontal layers grew withour rules
      
## example - FE:
- one slice per feature
- where does composition/glue go?
    - composition/core: composes features
        - app
            - tests: 
                - smoke probably
        - pages:
            - tests (e2e probably)
        - router??-> wiring, part of app
    - features
      - inside a slice
        - queries/api
        - feature-specific components?
        - routes?? -> probably not. slices shoudl be thin, no composition
        - tests? -> probably unit/isolation, maybe contract. e2e woudl need composition
        - not all feature slices have to touch all horizontal layers.
            - changing app layout wont touch api, but still worth a slice
    - shared: 
        - what we can't decide yet or truly shared/independent/generic fucntionality? 
        - gut feeling: no glue, generics only.
        - does not know of any single feature 
        - shoudl we separate/differentiate utils that support horizontals (ex. generic api base or query) from reusable things like time parsing, email/password validation etc? -> gut feeling: maybe not, all target non-functional
        - tests: strictly isolation/unit

- what differentiates a feature/use-case from a service:
 - i'd say side-effects staefulness. usecases are stateful. services are not. both might cross any layers
 - services might serve both functional requirements and non-functional requirements
 - usecases always serve functional
   - is it true though? ex is changing layout a fucntional one? good ux. is a non-functional requirement. but changing layout is stateful
 - is ftateful vs stateless a good differentiation though? where to draw the line?
   - ex. does logging or modifying some timespamt like "last read" count? 
     - i'd say if the modification leaves the system (ex displayed to the user or reaches external service then yes?)
     - but woudl then "email validation" service call if it's logged count as a usecase?
       - gut feeling: no, because probably logging - even though it's a side effect - does not modify app behaviour. if we'd show to the user how many times they validated email then it becomes a useces, then yes. 

- actually mihgt not even need hard rules. can follow anyhting that works like feature-sliced
- true value is still in making vertical x horizontal explicit and enforced. actual layout is up to user preference. consistency is what matters
- can features depend on eachother? what woudl prevent circular dependencies? ex. "select users" for team and "select team" for users
  - what shoudl be a slice here? where shoud a generic 'team selector' component go?  can be present in each slice that includes assigning a team
  - gut feeling: 
    - "select team" is not a complete usecase. 
    - features shoudl be usecases and should not depend
    - maybe shared still makes sense for business functionality? if yes, then blanket shard might be wrong. 
    - shared can be both service provider for use-cases (verticals) and maybe a structurer for horizontals? 
    - do not be afraid for having a lot of vertical slices and shared services
  - when does organizing stuff into modules make sense?
    - gut feelig: since we dont read code anymore, maybe matters less. agents can make sense of a features folder with 1000 slices

## rdd stereotypes
- information holder
- structurer
- service provider
- interfacer
- controller
- coordinator

how does this helps?
should we try to assign them? 

## khalil's stereotypical achitecture
- incoming
- outgoing
- application
- stateful
- stateless

## difference i want to make - but maybe he ment the same
- incoming vs outgoing not meaning ports (ex. db not being necessarily outgoing). it means data/signal leaving to external system or actor 
- ex FE ui: both incoming about outgoing
- reminder email: outgoing
- api client: both
- 

## horizontal stereotypes distilled -> best-practice first
 - composition 
   - infrastructural
   - composes app core
   - wires up application interface
   - does not know usecases or below
   - ideally with ports & adapters
 - application interface (or maybe app controller???)
   - the boundaries of the system
   - incoming & outgoing
 - application core // i suppose a lot of time not separated from interface
   - coordinates usecases (& services?)
 - use-cases
   - granular, stateful
   - may use services
   - may use patterns
 - services
   - stateless (in the sense as discussed above)
   - might use patterns
 - patterns
   - reusable
   - know nothing about anyhting above


### where it might  not hold
- how about a reusable "assign to te modal"?
  - ideally should be a service
  - in a lot of cases, if the implementation is hardcoded - ex there's a switch based on "target entity" like "user, project etc" then it's a smell
  - how to identify this smell? how to resolve that? what to do in the meantime? 
- does this hold for BE as well? -> i'd suppose yes
  - composition: app, bootstrap, wiring
  - app interface: possibly the controller layer
  - app core: maybe not separated, depends on framework?
  - use-cases: in laravel services
  - services: laravel services
  - patterns: idk, up do developer i'd say
- how does it fit the repo layout? is this supposed to be per package? 
  - i'd suppose it works per system/independently deployable unit/container or per "group" as defined above
  - also holonic: ex. in case of fynk both FE and BE might have core
    - maybe the framework doesnt make the core or composition that evident: ex laravel wiring
    - how to make it still traceable?
- stereotypes != folder layout


## how do they help:
- regardless of physical folder layout, they can be tagged with stereotypes // can they? 
- steretoypes help to encode the concrete layers and slices, and the dependency directions
- tagging makes it traceable and violations visible

## shat to do when the frameworks fights this kind of thinking? 
- in most brownfild codebases they will mix

## how will this be a skill?

### goal: min-max getting as close to the horizontal stereotypes as:
- framework allows
  - do not fight the framework
- complexity requires
  - not all stereotypes might be required everywhere
  - let them grow organically, but once there alwasy enforce

### evolution ladder & what it enables
1. application interface
  - test the production app e2e through its interfaces
2. making composition explicit
  - reduces incidental complexity
  - enables integration testing through app interfaces
  - enables unit testing with through app interfaces

- onboarding:
 - discover the repo with the help of system-architecture
    - still g2 learn how systems thinking might help even more
    - will help to identify app interface/boundaries
 - identify the main groups/top level folders that make sense without fighting the framework
 - identify what might fight the framework
 - identify systems: tell: they have a core
 - then per system: 
   - identify places of composition
