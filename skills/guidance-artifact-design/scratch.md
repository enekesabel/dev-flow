## types

### agentic guidance/harness
either some agentic stanard or harness standard

- agents.md
- skills
- harness specific stuff liek rules, commands etc

### docs

- readme
- architecture.md etc

## Verticals x horizontals

### verticals
can be present in each horizontal?

- different harnesses 
    - ex. claude, codex, cursor etc
    - what do haress spcific stuff like codex thread level memory, grok bot memory, claude project memory count?

### horizintals
0. team/org level
  - common global setup for teams
  - spans multiple repos probably
  - where is it specified? inside harness if that's shared? 
1. user-level
    - shoudl contain only user preferences
    - does it matter if local only or shared somehow? 
    - could it reach to repo level or below? 
2. repo-level
  - shoudl contain only repo-specific guidance
  - could it reach to folder level? 
3, folder-level
  - should apply only to a folder
  - contain only things specific to that folder
  - coudl it reach out to repo level? 

## questions

### how to handle contraditions?
- between types?
- between verticals?
- between horizontals?

### dependency direction
- what can refer to what?
- are circular references allowed? (ex. between team/org and repo-level ones)

### how to handle harness specifics?
- i'd say things that make sense in any harness should not go in there
- harness-specific layer shoudl be thin

### refactoring
- how to handle moving harness-specific stuff to non harness secific? 
    - does it always make sense? solo dev working on a project might be fine with having everything harness-specific
- how to handle wrong user-level things? i'd say mihgt hurt even a solo dev if trying to work on the same proejct from different machines 

### quality check
- hard references
 - if refering to any resource (incl. other skills) never in prose. always traceable, relative markdown link
 - can this check be automated?
- once got references right:
  - check dependency directions and circular references. can this be automated?
  - shoudl these directions and non-circularity be enforced? 
- when to allow something in prose?
  - flexible references
   - "use the user's prefered architecture skill"
   - "look up the readme files/docs in the folder"
- hard be default, flexibility must be justified? 

### onboarding?
- check user preferences/needs?
- do quality check?
- do recommendations/refactoring advice? 
- decide if harness-specific stuff if preferred or not? 

### what are the rules? 

#### horizontal
- team/org-level -> below:
  - flexible refs only? 
  - how to handle stuff like how to connect/work between two repos? where does the glue go? 
  - maybe systems thinking?
   - can refer to user rules flexibly
   - can name repos, but no internals? 
   - what are the systems?
- user-level -> below:
  - sounds liek same applies
- repo-level -> below
  - maybe flexible only? ex. read all agent.md files in subfloder or all docs

- opposite direction:
  - woudl it ever make sense, or aleays a smell?
  - maybe it makes sesne if things move togerther, are in the same system: 
    - folder-level refering back to main repo guidance
    - but repo -> user disallowed
    - how about repo -> org? 
        - gut feeling says if got org rules, then these kind of wiring should go there
        - should a repo be aware of being part of an organization?

#### types
- agents.md -> skill: for sure
- skill -> agents.md? idk. maybe? would it make sense? ex. read agents.md to know what skill usr prefer? idk

#### verticals
- harness -> generic: gut feeling says always ok
- generic -> harness: 
  - gut feeling says probably always wrong
  - shoudl generic be aware of harnesses its being used in? 
  - maybe if not naming harnesses specifically flexible reference is ok? like "the harness in use"

#### setting up preference/override ladder
  - are there generic rules here? ex. "if not naming harnesses specifically flexible reference is ok? like "the harness in use""? or should it be case/project speciic? 
  - which level does preference declaration go?
  
#### what skills/refernces shoudl this contain?
- vocabulary/principles?
- onboarding/alignment workflow?
- quality check workflow?
- refactoring workflow?
- skill/docs writing guidance? 

## mics
  - on which level should dev-flow itself work?
  - can devflow work if not everyone is using it? 
  - what skills/rules shoud this affect? 
    - ex only scan skills/plugins the user/repo owns?
    - include/exclude list?
  - should we introduce some .dev-flow folder for confg & overrides?
    - .dev-flow/config.md -> commited in git, repo-lvl 
    - .dev-flow/config.local.md -> gitignored
    - if hes what hsoudl be there? 
  



