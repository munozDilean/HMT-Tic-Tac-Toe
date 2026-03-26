# Professors Observationns

Observations and recommendations from Professor Ashutosh.

## Thursday 3/26/2026 - Stage 2 Presentation

> - Need to rewrite both hypothesis before submission.
> - Adjust the flow (slide 8, Study Logistic).

- Independent Variables:
  - The time that we give the advice based on the context
  - Random advice given arbitrarily
- With these we can measure frustration and trust.
- First Hypothesis: Advice given at a arbitrary interval
- Second Hypothesis: A context aware machine is capable of generating better trust metrics than one lacking context
- Provide the treatments at random.
- For Post survey: NASA-TLX measures subjective load. These are better if done at last, after they are done with both treatments and SUS
- Frustration calculation: Put it on a scale. How frustrated were you in respect to the notifications received, 1 being least 5 being most.
- We don't have FDS
- These are all
- We might not need to use them all, only the ones that we might consider part of our project.

## Tuesday 3/24/2026 - Stage 2 part 1

- We are allowed to use dataset for algorithms and models we need to implement.
- In our scenario, these would mean two models:
  - a dataset for a model on learning how to play tic tac toe.
  - A model that is able to detect when the user is frustrated from the mouse tracking data.
- Good Resources:
  - https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2020.565664/full
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC7701271/
    - https://gitlab.com/iarapakis/the-attentive-cursor-dataset
    - https://github.com/luileito/evtrack

## Thursday 03/19 - Project Day

- When will we get the demographics question.
  - Will be provided during stage 3
- We are supposed to put the pre-survey questions on **Qualtrix**. What about the rest of the questions? And how does it go with the flow of the project?
  - All the questions will be on **Qualtrix**
  - Save data and like mouse movements.

## Thursday 2/19/2026 - Stage 1

- All **pre-survey** question will be on **Qualtrix**
- He will give us the demographics questions

## Tuesday 2/16/2026

Random (every 10 seconds)
Study the mouse pointers
Voice Activation (Not sure about it yet)

Basically to classify confusion
You can use ollama to run and talk to the application
Don’t need a dataset.
Start with Tic-tac-toe, if you are able to do it right, move on to other games like sudoku

### When to give suggestions

Give it randomly, every 10 seconds or 2 minutes
Standard demographics:
Age is an important factor (gotta get this information)
What is your experience with Tic tac toe
Ask FDS (Frustration discomfort scale)
Then execute the game
After the experiment, post questionnaire
How frustrated are you in the experience
FDS
SUS
NASATLX
Objective metrics: Metrics that are not influenced by bias
The moves that you are making
Behavior metrics:
Mouse movements
With this you can measure delay
You will need a timer
You will need a low pass filter
Will remove noise from the data
YOU can use Euclidian distance between points
When distance are below a certain threshold then remove those points
Identify the high points
X-cord gametime
Y-cord speed
Demographics data needed
Human information

### Flow of the Project

1. Pre-survey (experience)
2. Experience
3. Baseline frustration
4. On second treatment don’t ask again but as #2
5. Pre-survey
6. Do the task
7. Treatment 1: Random Game Advice
8. Post-survey questions
9. Two questions
10. FDS and SUS and TLX
11. For Treatment 2 (Nuance) start from #2 and repeat

Two treatments
Random advice
Nuance advice
You should be able to explain this
Replay the game for each treatment
Compare with each other
Questions:
IS behavioral metric objective?
What it subjective?
Should we try to induce frustration
