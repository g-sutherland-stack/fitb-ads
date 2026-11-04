# FitB ads

Finished FitB marketing videos. Open the player at **https://g-sutherland-stack.github.io/fitb-ads/** on any screen with a browser: tap once, it goes full screen and plays the wall on a loop.

## Wall pop-out (landscape, with sound)

The wall of 49 member clips keeps playing; one clip comes forward, plays with its own sound, returns to its spot, then the next. After every ten clips a promo plays full screen. 1920×1080, 30 fps, 10 min 35 s, in five parts that the player joins:

- [Part 1](wall/fitb-wall-popout-landscape-part1.mp4) · [Part 2](wall/fitb-wall-popout-landscape-part2.mp4) · [Part 3](wall/fitb-wall-popout-landscape-part3.mp4) · [Part 4](wall/fitb-wall-popout-landscape-part4.mp4) · [Part 5](wall/fitb-wall-popout-landscape-part5.mp4)

The 15-second ad set, the 30-second feature videos and the video walls stay on the `marketing-ads` branch of the app repo.

## Promo sets, one per style (24 s, music)

Five sets, one in the style of each uploaded promo, five themes each (tracking, trainers, gym, recovery, weight loss). No two videos share a layout: inside each style the letters run the other way, the phone scrolls the app or plays a real member clip, three phones fan out, cards swap sides, colours shift per theme and the close changes. Each style folder has a `contact-sheet.jpg` (five themes by four moments) to see the set at a glance. 1920×1080, 24 s, each style with its own original music bed (no voice-over). Play them from the Pages site to hear them in the browser, e.g. https://g-sutherland-stack.github.io/fitb-ads/promos/plans/fitb-plans-weight-loss-24s.mp4

| Style | Your reference video | Files | Music |
|---|---|---|---|
| Plans (landscape pixel page) | plans_built_around_your_goal_original_landscape | [promos/plans](promos/plans) | bright house, 122 bpm, C major |
| Pixel (portrait page, blurred sides) | weight_loss_guesswork_original_landscape | [promos/pixel](promos/pixel) | chiptune, 150 bpm, E minor |
| Dark centred (receipt card) | weight_loss_guesswork_landscape | [promos/dark](promos/dark) | warm minimal, 88 bpm, D minor |
| Blobs (serif, organic shapes) | weight_loss_guesswork_original_2_landscape | [promos/blobs](promos/blobs) | playful marimba, 108 bpm swung, G major |
| Kinetic (gold word, photo card) | weight_loss_guesswork_alt_landscape | [promos/kinetic](promos/kinetic) | driving, 126 bpm, F minor |

`promos/build-sets.py` renders them (with `build-promos.py` beside it for the shared drawing code, Piper TTS and the `en-gb-southern_english_female-low` voice); the copy and app screens per theme are the `THEMES` list.

The five music beds are in [music/](music) as WAV, composed in `music/build-tracks.py` (fully synthesised, free to use).

## The 51-minute wall loop

Three walls (the 1-50 clips, then the 50-100 clips in two walls), every member clip coming forward in full with its own sound, a promo after a random 3, 4 or 5 clips drawn from all 53 promos with sound (music-only, voice-over and the original three with audio), the same person never twice in a row. 1920×1080 master; the copy here is 720p in 5 parts under 100 MB. Play it on a loop at **https://g-sutherland-stack.github.io/fitb-ads/loop/** (tap once to start), or join the parts with ffmpeg and loop the file in VLC. `loop/build-loop.py` is the builder.
