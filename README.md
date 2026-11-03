# FitB ads

Finished FitB marketing videos. Open the player at **https://g-sutherland-stack.github.io/fitb-ads/** on any screen with a browser: tap once, it goes full screen and plays the wall on a loop.

## Wall pop-out (landscape, with sound)

The wall of 49 member clips keeps playing; one clip comes forward, plays with its own sound, returns to its spot, then the next. After every ten clips a promo plays full screen. 1920×1080, 30 fps, 10 min 35 s, in five parts that the player joins:

- [Part 1](wall/fitb-wall-popout-landscape-part1.mp4) · [Part 2](wall/fitb-wall-popout-landscape-part2.mp4) · [Part 3](wall/fitb-wall-popout-landscape-part3.mp4) · [Part 4](wall/fitb-wall-popout-landscape-part4.mp4) · [Part 5](wall/fitb-wall-popout-landscape-part5.mp4)

The 15-second ad set, the 30-second feature videos and the video walls stay on the `marketing-ads` branch of the app repo.

## 30-second promos (landscape, with music)

Five themed promos in the style of the weight-loss promo: a dark green kinetic title, a sage page with giant pixel letters and a phone card, and a "Free. No paywall, no trial." close. 1920×1080, 30 s, FitB music.

- [Tracking](promos/fitb-promo-tracking-30s-landscape.mp4) · [Trainers](promos/fitb-promo-trainers-30s-landscape.mp4) · [Gym](promos/fitb-promo-gym-30s-landscape.mp4) · [Recovery](promos/fitb-promo-recovery-30s-landscape.mp4) · [Weight loss](promos/fitb-promo-weight-loss-30s-landscape.mp4)

`promos/build-promos.py` renders them; the copy, the big word and the app screens for each are the `PROMOS` list at the top.

## 24-second promo sets, one per style (voice-over + music)

Four more sets in the other four styles of the uploaded promos, five themes each (tracking, trainers, gym, recovery, weight loss), 1920×1080, 24 s, a spoken voice-over over the FitB music.

| Style | From | Files |
|---|---|---|
| Pixel | weight_loss_guesswork_original | [promos/pixel](promos/pixel) |
| Dark centred | weight_loss_guesswork_landscape | [promos/dark](promos/dark) |
| Blobs | weight_loss_guesswork_original_2 | [promos/blobs](promos/blobs) |
| Kinetic | weight_loss_guesswork_alt | [promos/kinetic](promos/kinetic) |

`promos/build-sets.py` renders them (needs `build-promos.py` beside it, Piper TTS and the `en-gb-southern_english_female-low` voice); the copy, voice-over lines and app screens per theme are the `THEMES` list.
