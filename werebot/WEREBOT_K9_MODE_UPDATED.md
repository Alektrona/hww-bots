# Werebot K9 Mode

Transform your messages into cryptic emoji messages! 🎨✨

Named after /u/K9moonmoon, famous for legendary cryptic emoji-only messages in the HWW community!

## What It Does

Werebot **replaces** words in your message with emojis where possible, creating a K9-style cryptic message.

## Usage

```
WEREBOT K9 your message here
```

**Werebot replies with a K9-ified (emoji-replaced) version!**

## Examples

### Example 1: Simple Message

**Input:**
```
WEREBOT K9 I love this game
```

**Output:**
```
## 🎨 K9-ified Message:

I ❤️ this 🎮

*K9-ified by Were-Bot in honor of /u/K9moonmoon* 🐕🌙
```

Notice: "love" → ❤️ and "game" → 🎮 (words replaced!)

### Example 2: Werewolf Game

**Input:**
```
WEREBOT K9 The wolf killed the doctor at night
```

**Output:**
```
## 🎨 K9-ified Message:

The 🐺 🔪 the ⚕️ at 🌙

*K9-ified by Were-Bot in honor of /u/K9moonmoon* 🐕🌙
```

Much more cryptic! Words are replaced with emojis.

### Example 3: Voting

**Input:**
```
WEREBOT K9 I vote for Alice because she is suspicious
```

**Output:**
```
## 🎨 K9-ified Message:

I 🗳️ for Alice because she is 🤨

*K9-ified by Were-Bot in honor of /u/K9moonmoon* 🐕🌙
```

### Example 4: More Cryptic

**Input:**
```
WEREBOT K9 I think the wolves killed the doctor last night
```

**Output:**
```
## 🎨 K9-ified Message:

I 🤔 the 🐺 🔪 the ⚕️ last 🌙

*K9-ified by Were-Bot in honor of /u/K9moonmoon* 🐕🌙
```

Super cryptic - but decipherable!

### Example 5: Questions

**Input:**
```
WEREBOT K9 Who do you think is suspicious
```

**Output:**
```
## 🎨 K9-ified Message:

Who do you 🤔 is 🤨

*K9-ified by Were-Bot in honor of /u/K9moonmoon* 🐕🌙
```

### Example 6: Game Announcement

**Input:**
```
WEREBOT K9 The town wins! Great game everyone!
```

**Output:**
```
## 🎨 K9-ified Message:

The 🏘️ 🏆! 👍 🎮 everyone!

*K9-ified by Were-Bot in honor of /u/K9moonmoon* 🐕🌙
```

## How It Works

1. Bot extracts your message after "K9"
2. Splits message into words
3. For each word, checks if there's an emoji mapping
4. **If found, REPLACES the word with the emoji** ← KEY!
5. **If not found, keeps the original word**
6. Preserves punctuation and formatting

**This creates more cryptic, K9-style messages!**

## Emoji Dictionary

Were-Bot has 500+ word-to-emoji mappings!

### Werewolf/Mafia Game Terms

**Roles:**
- wolf, werewolf, wolves → 🐺
- town, townie, villager → 🏘️👤
- seer, oracle → 🔮
- doctor, healer, medic → ⚕️
- cop, detective, investigator → 👮🕵️
- bodyguard, guardian, protector → 🛡️
- vigilante, vig, hunter → 🔫🎯
- jester, fool → 🤡
- godfather, mafia → 🤵🕴️
- witch, wizard → 🧙
- mayor → 👔
- veteran → 🎖️
- arsonist → 🔥
- vampire, vamp → 🧛
- cultist, cult → 👹

**Actions:**
- kill, killed, murder, attack → 🔪
- die, died, dead, death → 💀
- lynch, hang, execute → 🪢
- vote, voting, ballot → 🗳️
- protect, save, guard → 🛡️
- investigate, inspect, check → 🔍
- heal, revive → 💊
- poison, poisoned → ☠️
- shoot, shot → 🔫
- block, blocked, roleblock → 🚫
- frame, framed → 🖼️
- convert, recruit → 🔄

**Game States:**
- night, dark, nighttime → 🌙
- day, daytime, morning → ☀️🌅
- phase, turn → ⏰
- game, match, round → 🎮
- start, begin → ▶️
- end, finish, over → ⏹️
- win, won, victory, winner → 🏆
- lose, lost, defeat, loser → 💔

**Suspicion & Social:**
- sus, suspicious, suspect, sketchy → 🤨
- trust, trusted → 🤝
- claim, claims, claiming → 📢
- lie, lying, liar, fake → 🤥
- truth, honest, real → ✅
- guilty, evil, scum → 😈
- innocent, good, townie → 😇
- soft, softing → 🫣
- hard, hardclaim → 💪

### Emotions & Reactions

- happy, smile, glad, joy → 😊
- sad, upset → 😢
- cry, crying → 😭
- angry, mad, rage, furious → 😠😡
- laugh, lol, lmao, rofl, haha → 😂
- think, thinking, hmm, hmmm → 🤔
- confused, confuse, huh → 😕
- shock, shocked, omg, gasp → 😱
- worry, worried, nervous, anxious → 😰
- scared, afraid, fear, terrified → 😨
- excited, hype, pumped → 🤩
- bored, boring, meh → 😑
- tired, sleep, sleepy, exhausted → 😴
- cool, nice, great, awesome → 😎👌👍🔥
- yay, yeet, woohoo → 🎉
- oof, ouch, yikes → 😬
- bruh, facepalm, smh → 🤦
- shrug, idk, dunno → 🤷
- eyes, look, looking, watch, see → 👀
- skull, rip, ded → 💀
- salty, salt → 🧂
- mood, same, facts, fr → 💯

### Common Words

- love, heart, like → ❤️👍
- hate, dislike → 💔👎
- yes, yeah, yep, yup → ✅
- no, nope, nah → ❌
- ok, okay, alright → 👌
- maybe, perhaps, possibly → 🤷
- please, pls → 🙏
- thanks, thank, thx, ty → 🙏
- sorry, sry, oops → 😅
- wow, whoa, woah → 😮
- wait, hold, stop → ✋
- go, next, continue → ➡️
- back, return, previous → ⬅️
- up → ⬆️
- down → ⬇️
- new, fresh → 🆕
- old, ancient → 👴
- fast, quick, speed → ⚡
- slow, slowly → 🐌
- big, large, huge → 📏
- small, tiny, little → 🤏
- hot, fire, lit, heat → 🔥
- cold, freeze, frozen → 🥶
- ice → 🧊

### Numbers

- zero, none → 0️⃣
- one, first → 1️⃣
- two, second → 2️⃣
- three, third → 3️⃣
- four, fourth → 4️⃣
- five, fifth → 5️⃣
- six, sixth → 6️⃣
- seven, seventh → 7️⃣
- eight, eighth → 8️⃣
- nine, ninth → 9️⃣
- ten, tenth → 🔟
- hundred → 💯

### Time

- time, clock, hour → ⏰
- today → 📅
- tonight → 🌙
- tomorrow, future → 📆🔮
- yesterday, past → 📆📜
- now, current → ⚡
- soon, later, wait → ⏳
- early → 🌅
- late → 🌙

### Celebrations

- party, celebrate, celebration → 🎉🎊
- congratulations, congrats, gratz, grats → 🎊
- birthday, bday, cake → 🎂
- gift, present → 🎁
- cheers, toast → 🍻🥂

### Food & Drink

**Food:**
- food, eat, eating, hungry → 🍔🍴🤤
- pizza → 🍕
- burger → 🍔
- taco → 🌮
- burrito → 🌯
- sandwich → 🥪
- hotdog → 🌭
- fries → 🍟
- pasta, spaghetti → 🍝
- ramen → 🍜
- sushi → 🍣
- rice → 🍚
- chicken → 🍗
- meat, steak → 🥩
- salad, veggies, vegetables → 🥗
- fruit, apple → 🍎
- banana → 🍌
- orange → 🍊
- strawberry → 🍓
- watermelon → 🍉
- grapes → 🍇
- bread, toast → 🍞
- bagel → 🥯
- cheese → 🧀
- egg → 🥚
- bacon → 🥓
- dessert, sweet → 🍰
- candy → 🍬
- cookie → 🍪
- chocolate → 🍫
- donut → 🍩
- icecream, cream → 🍦

**Drinks:**
- drink, beverage → 🥤
- coffee, latte → ☕
- tea → 🍵
- water → 💧
- milk → 🥛
- juice → 🧃
- beer → 🍺
- wine → 🍷
- champagne → 🍾
- cocktail → 🍹
- martini → 🍸
- shot → 🥃

### Animals

- dog, puppy, doggo, pupper → 🐕
- cat, kitty, kitten → 🐱
- bird → 🐦
- duck → 🦆
- fish → 🐟
- shark → 🦈
- whale → 🐋
- dolphin → 🐬
- snake → 🐍
- dragon → 🐉
- bear → 🐻
- panda → 🐼
- koala → 🐨
- monkey → 🐵
- gorilla → 🦍
- lion → 🦁
- tiger → 🐯
- leopard → 🐆
- fox → 🦊
- raccoon → 🦝
- squirrel → 🐿️
- rabbit, bunny → 🐰
- hamster → 🐹
- frog → 🐸
- turtle → 🐢
- lizard → 🦎
- bug → 🐛
- bee → 🐝
- butterfly → 🦋
- spider → 🕷️
- unicorn, pegasus → 🦄
- ghost → 👻
- alien → 👽
- robot → 🤖

### Nature

**Weather:**
- sun, sunny, sunshine → ☀️
- moon, lunar → 🌙
- star, stars, sparkle, shine → ⭐✨
- cloud, cloudy → ☁️
- rain, rainy → 🌧️
- storm → ⛈️
- snow, snowy, winter → ❄️
- wind, windy, breeze → 💨
- lightning, thunder → ⚡
- rainbow, colorful → 🌈

**Plants:**
- flower, flowers → 🌸🌺
- rose → 🌹
- tree, forest, woods → 🌲
- plant, leaf, leaves → 🌱🍃

**Geography:**
- mountain, hill → ⛰️
- ocean, sea, wave → 🌊
- beach → 🏖️
- island → 🏝️
- desert → 🏜️
- earth, world, globe → 🌍🌎🌏
- planet, space, galaxy → 🪐🌌

### Places & Travel

- home, house → 🏠
- building, office, work → 🏢💼
- school, university, college → 🏫🎓
- hospital → 🏥
- pharmacy → 💊
- store, shop, mall → 🏪🛍️
- restaurant → 🍽️
- cafe → ☕
- hotel, motel → 🏨
- airport, plane, flight → ✈️
- train → 🚂
- subway → 🚇
- bus → 🚌
- car → 🚗
- taxi → 🚕
- truck → 🚚
- bike, bicycle → 🚲
- boat → ⛵
- ship → 🚢
- rocket, spaceship → 🚀
- castle → 🏰
- tower → 🗼
- city → 🌆
- country, map → 🗺️
- flag, banner → 🚩

### Objects

**Tech:**
- phone, mobile, cell → 📱
- computer, laptop, pc → 💻
- keyboard → ⌨️
- mouse → 🖱️
- camera, photo → 📷📸
- picture → 🖼️
- tv, television, screen → 📺

**Office:**
- book, books, read, reading → 📖📚
- pen → 🖊️
- pencil → ✏️
- write, writing → ✍️
- paper, document → 📄
- note → 📝
- mail, email → 📧
- letter → ✉️

**Other:**
- gift, box, package → 🎁📦
- money, cash, dollar, rich → 💰💵
- coin → 🪙
- credit, card → 💳
- key → 🔑
- lock → 🔒
- unlock → 🔓
- tool, wrench → 🔧
- hammer → 🔨
- knife → 🔪
- sword → ⚔️
- shield → 🛡️
- gun, pistol, weapon → 🔫
- bomb, explosive, boom → 💣💥
- bell → 🔔
- alarm → ⏰
- light, bulb, lamp → 💡
- candle → 🕯️
- torch → 🔦
- battery, power, energy → 🔋⚡
- pill, medicine, drug → 💊
- bandage, band → 🩹
- mirror, reflection → 🪞
- door → 🚪
- window → 🪟
- chair → 🪑
- couch → 🛋️
- bed → 🛏️
- toilet → 🚽
- shower → 🚿
- bath → 🛁
- soap, clean → 🧼
- trash, garbage, waste → 🗑️

### Activities & Hobbies

**Entertainment:**
- music, song, sound → 🎵🔊
- guitar → 🎸
- piano → 🎹
- drum → 🥁
- art, paint → 🎨
- draw, drawing → ✏️
- dance, dancing → 💃
- ballet → 🩰
- sing, singing, karaoke → 🎤
- movie, film, cinema → 🎬🎦
- video, camera, record → 📹⏺️

**Sports:**
- sport, sports → ⚽
- soccer → ⚽
- football → 🏈
- basketball → 🏀
- baseball → ⚾
- tennis → 🎾
- volleyball → 🏐
- golf → ⛳
- bowling → 🎳
- pool → 🎱
- hockey → 🏒
- skating → ⛸️
- swim, swimming → 🏊
- run, running, jog → 🏃
- bike, biking, cycling → 🚴
- gym, workout, exercise, lift → 🏋️
- yoga, meditate, meditation → 🧘

**Other:**
- camping, tent, camp → 🏕️⛺
- fishing, fish → 🎣
- cooking, cook, chef → 👨‍🍳
- garden, gardening → 🌻

### Symbols & Misc

**Math:**
- plus, add → ➕
- minus, subtract → ➖
- multiply, times → ✖️
- divide, division → ➗
- equals, equal → 🟰
- percent, percentage → 💯

**Common Symbols:**
- question, ask → ❓
- exclamation, important → ❗
- warning, caution, alert → ⚠️
- forbidden, banned, prohibit → 🚫
- check, correct, right → ✅
- cross, wrong, incorrect → ❌
- heart, hearts → ❤️💕
- broken, heartbreak → 💔
- peace → ☮️
- yin, yang → ☯️
- recycle, eco → ♻️
- infinity, infinite, forever → ♾️
- trademark → ™️
- copyright → ©️
- registered → ®️
- info, information → ℹ️

### Colors

- red, crimson → 🔴
- orange, tangerine → 🟠
- yellow, gold → 🟡
- green, lime → 🟢
- blue, navy → 🔵
- purple, violet → 🟣
- brown, tan → 🟤
- black, dark → ⚫
- white, light → ⚪
- pink, rose → 🩷
- rainbow, colorful → 🌈

### People & Relationships

- person, people, human → 🧑👥
- man, guy, dude, bro → 👨
- woman, girl, lady → 👩👧
- boy, kid, child, baby → 👦👶
- family, parents → 👪👨‍👩‍👧‍👦
- friend, friends, buddy, pal → 👫👭
- couple, love, romance → 💑❤️💕
- wedding, marriage → 💒
- bride → 👰
- groom → 🤵
- king, prince → 🤴
- queen, princess → 👸
- crown, royal → 👑
- angel → 👼
- devil, demon → 😈👹
- mermaid → 🧜
- fairy → 🧚
- elf → 🧝
- zombie, mummy → 🧟
- ninja → 🥷
- pirate → 🏴‍☠️

### Gaming Slang & Expressions

- gg, wp → 🎮👍
- ez → 😎
- rekt, pwned, owned → 💀
- noob, newbie, beginner → 🆕
- pro, expert, master → 🏆
- boss, legend → 😎⭐
- goat → 🐐
- flex, flexing, strong → 💪
- weak → 😢
- soft → 🧸
- savage, brutal, ruthless → 😈
- cringe, awkward, uncomfortable → 😬
- based, valid, legit → 💯✅
- cap, lie, fake → 🧢🤥
- nocap, truth, real → 🚫🧢💯
- bet, deal, agree → 💯🤝
- vibe, vibes, energy → ✨⚡
- chaotic, chaos, crazy → 🌪️🤪
- chill, relax, calm → 😌

## Cryptic Examples

### Before & After Comparison

**Normal message:**
```
I think Alice is the wolf because she voted for the doctor
```

**K9 Mode:**
```
WEREBOT K9 I think Alice is the wolf because she voted for the doctor

→ I 🤔 Alice is the 🐺 because she 🗳️ for the ⚕️
```

**Normal message:**
```
The wolves killed Bob at night and the town is sad
```

**K9 Mode:**
```
WEREBOT K9 The wolves killed Bob at night and the town is sad

→ The 🐺 🔪 Bob at 🌙 and the 🏘️ is 😢
```

## Use Cases

### Cryptic Voting

```
WEREBOT K9 I vote for Alice she is suspicious
→ I 🗳️ for Alice she is 🤨
```

### Night Actions

```
WEREBOT K9 The wolves hunt the doctor
→ The 🐺 hunt the ⚕️
```

### Celebrations

```
WEREBOT K9 We won great game
→ We 🏆 👍 🎮
```

### Questions

```
WEREBOT K9 Who do you think is the wolf
→ Who do you 🤔 is the 🐺
```

## Tips for Maximum Cryptic-ness

### Use Dictionary Words

The more words from the dictionary, the more cryptic:

**Less cryptic:**
```
WEREBOT K9 Alice probably did the thing
→ Alice probably did the thing
(No replacements)
```

**More cryptic:**
```
WEREBOT K9 Alice is suspicious she voted weird
→ Alice is 🤨 she 🗳️ weird
(More replacements!)
```

### Keep It Simple

Short sentences work best:

```
WEREBOT K9 Wolf killed doctor
→ 🐺 🔪 ⚕️

vs.

WEREBOT K9 I believe the person who is the wolf killed the person who is the doctor
→ (Less effective)
```

### Use Game Terms

Game-specific words are heavily represented:

```
WEREBOT K9 The seer investigated the wolf at night
→ The 🔮 👀 the 🐺 at 🌙
```

## Punctuation Handling

Punctuation is preserved:

```
WEREBOT K9 I love this! It is great.
→ I ❤️ this! It is 👍.
```

```
WEREBOT K9 Who is suspicious? I think Alice!
→ Who is 🤨? I 🤔 Alice!
```

## Why "K9 Mode"?

Named after /u/K9moonmoon, a legendary player in the r/HogwartsWerewolves community known for:
- Creating incredibly cryptic emoji-only messages
- Using emojis to replace words (not just enhance them!)
- Making people decode their messages
- Bringing unique style to every game!

This feature is a tribute to their iconic posting style! 🐕🌙✨

While not as complex as true K9 cryptography, it captures the spirit of emoji-replacement communication!

## Examples by Scenario

### Death Announcement
```
WEREBOT K9 Bob was killed by the wolves last night
→ Bob was 🔪 by the 🐺 last 🌙
```

### Suspicion
```
WEREBOT K9 I think Alice is suspicious she is the wolf
→ I 🤔 Alice is 🤨 she is the 🐺
```

### Victory
```
WEREBOT K9 The town wins congratulations
→ The 🏘️ 🏆 🎊
```

### Confusion
```
WEREBOT K9 I am confused who do you think is suspicious
→ I am 😕 who do you 🤔 is 🤨
```

### Investigation
```
WEREBOT K9 The seer should investigate the suspicious player
→ The 🔮 should 👀 the 🤨 player
```

---

Create cryptic K9-style messages! 🐕🌙✨
*In honor of /u/K9moonmoon's legendary emoji style!*
