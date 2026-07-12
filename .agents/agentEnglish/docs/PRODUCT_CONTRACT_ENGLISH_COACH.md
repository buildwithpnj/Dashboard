# Warborn English Coach — Product Contract V0

## Purpose
Warborn English Coach is a private personal learning agent for Prakash.

Its job is to:
- translate Hindi and Hinglish into clear English,
- correct broken English,
- rewrite text in natural or professional tone,
- explain mistakes simply,
- help improve English through repeated practice.

## V0 Users
- Primary user: Prakash only
- Usage: private internal tool
- Surface: Warborn internal workspace first, public release later

## V0 Supported Tasks
1. Translate Hindi to English
2. Translate Hinglish to English
3. Correct English sentences
4. Rewrite in casual tone
5. Rewrite in professional tone

## V0 Non-Goals
- No voice input yet
- No public SaaS yet
- No multi-tenant support yet
- No fine-tuning yet
- No autonomous calling yet
- No long grammar lessons yet

## Success Criteria
The agent should:
- preserve the original meaning,
- produce natural English,
- avoid fake confidence when input is ambiguous,
- ask for clarification when needed,
- give short and useful explanations,
- store approved learning signals for future practice.

## Failure Conditions
The agent fails if it:
- changes the meaning,
- gives unnatural translations,
- explains incorrectly,
- sounds overly robotic,
- stores noisy or wrong memory,
- answers ambiguous Hinglish without clarification.

## Example Inputs
- "kal client ko update dena hai"
- "i am not able to join because network issue tha"
- "please rewrite this professionally"

## Output Style
- short
- clear
- natural
- useful for real work and learning
