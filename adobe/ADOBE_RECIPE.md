# Best Use of Adobe — 10-minute opener recipe

**Goal:** one wow asset, a ~10-second muted animated title card that opens the pitch. An Apex Predator dinosaur (“CI guardian”) sorts red test failures into two piles — flaky tests into a teal quarantine cage, real bugs through a blocked gate — then the real Drex probability chart lands, and the card ends on **Flaky or real? Drex knows.** and **48% lower cost · 8× faster**.

**Timebox: 10 minutes on your laptop.** Sign in with your personal Adobe ID (not a work account). The deck is already wired: when you are done, save the export as `adobe/opener.mp4` in this folder, refresh `pitch/index.html`, and the opener plays automatically on slide 1. If the file is missing, slide 1 stays the current title card.

The opener is **muted and looping** in the deck (browsers block autoplay-with-sound), so the story has to work with no audio. Do not rely on voiceover or “Animate from audio.”

If Firefly video is slow or queued at minute 4, jump to the [2-minute fallback](#2-minute-fallback-express-only).

---

## Why this wins “Best Use of Adobe”

- You use **Adobe Firefly’s own models** (Firefly Image + Firefly Video), not a partner model like Veo or Flux, so the work is clearly Adobe’s.
- You assemble it in **Adobe Express**, and the second beat is our **real Drex histogram**, not a generated fake chart.
- The character is on-theme for the Apex Predator track.

---

## Brand kit (paste these into Express and Firefly)

| Token | Hex | Use |
|---|---|---|
| Background | `#F7F7F4` | Canvas, light set |
| Ink | `#14161A` | Titles, body |
| Teal accent | `#0E7C66` | “Drex knows.”, rules, kicker, stats |
| Accent soft | `#E3F2EE` | Pills, chips |
| Muted | `#5B6270` | Captions, credit |
| Line | `#E3E4E0` | Hairlines |
| Card | `#FFFFFF` | Chart card |

Typeface: **Inter** (Adobe Fonts, already in Express). Weights: ExtraBold (800) for the title, Bold (700) for the kicker and stats.

**Do not ask Firefly to render the tagline.** Firefly garbles letters. All typography is added in Express, or use the ready-made PNGs in this folder.

---

## Files already prepared for you (upload these)

All of these live in `adobe/`:

| File | What it is |
|---|---|
| `charts/prob_histogram_1920x1080.png` | **The hero chart.** Real Drex P(flaky) histogram, punched to a transparent 1920×1080 frame, sitting on a white rounded card with a teal top edge. Use this in the opener. |
| `charts/prob_histogram_1920x1080_deckbg.png` | Same chart on the deck background `#F7F7F4`. Use this in the fallback. |
| `charts/drex_vs_llm_1920x1080.png` (+ `_deckbg`) | Head-to-head vs Llama / DeepSeek, same treatment. Optional, not required for the opener. |
| `charts/cost_before_after_1920x1080.png` (+ `_deckbg`) | Learning / cost-table chart. Optional. |
| `tagline.png` | Transparent typography lockup: kicker, “Flaky or real? / Drex knows.”, and “48% lower cost · 8× faster.” |
| `tagline_lower_third.png` | Same words as a 1920×1080 lower-third overlay with a soft cream scrim. Drop on top of the Firefly clip at the end. |
| `stats_chip.png` | Teal pill, “48% lower cost · 8× faster.” |
| `credit_line.png` | “Made with Adobe Firefly + Adobe Express.” The deck also injects this credit automatically when `opener.mp4` is present. |
| `fallback_layout_reference.png` | Visual guide for the 2-minute fallback. **Do not export this as the final slide** — rebuild it in Express so the work is Adobe’s. |

---

## The 10-second storyboard

| Time | What the audience sees |
|---|---|
| 0:00–0:05 | Firefly clip. The dinosaur CI guardian comes to life and sorts red failed-test tiles: left into a teal quarantine cage, right through a dark blocked gate. Static camera, light `#F7F7F4` set. |
| 0:05–0:08 | The real histogram card (`prob_histogram_1920x1080.png`) fades or slides in over the lower or center of the frame. Two clean clusters, empty middle band. |
| 0:08–0:10 | Tagline locks: **Flaky or real? Drex knows.** then **48% lower cost · 8× faster.** Hold until you hit →. |

On stage: let the 10 seconds play without talking, then advance. The title copy is still there as a fallback if the file is missing.

---

## Step-by-step (about 8–10 minutes)

### 1. Sign in (30 seconds)

- Open [https://firefly.adobe.com](https://firefly.adobe.com) and sign in with your personal Adobe ID.
- A free Adobe account includes daily Firefly generations for images, video, and audio. If a staff member offered Adobe credit, redeem it first.
- Use **Firefly Image** and **Firefly Video** (Adobe’s models). Skip partner models (Veo, Flux, Imagen, etc.) so the prize case is cleanly “Adobe.”

### 2. Generate the character still (about 90 seconds)

1. On the Firefly home page, choose **Image** in the left panel, then **Generate image**. Direct help: [Generate images from text](https://helpx.adobe.com/firefly/web/work-with-images/generate-images/generate-images-from-text-descriptions.html).
2. Settings (left):
   - **Model:** Firefly Image 4, Firefly Image 4 Ultra, or Firefly Image 5 (all Adobe). Prefer Image 4 or 4 Ultra if you want four variations in one go.
   - **Aspect ratio:** Widescreen / 16:9.
   - **Content type:** Art.
3. Paste **Prompt 1** below into the prompt box. Leave **Enhance prompt** on if you like — it is the sparkle icon next to Generate.
4. Click **Generate**. Pick the frame where the dinosaur is clearly sorting, the background is light, and the lower third is reasonably uncluttered. If the model wrote letters on the cage or gate, discard that one (or keep it only if the letters are off-screen enough to crop).
5. Download the still (PNG or JPG) to your laptop. Optional but useful: open it in Firefly **Edit image** and run **Remove background** only if the set came out muddy; we actually want to keep the light set.

### 3. Animate it with Image to Video (about 2 minutes, including generate time)

1. In the left panel choose **Video**, then **Generate video**. Help: [Generate videos using images](https://helpx.adobe.com/firefly/web/work-with-audio-and-video/work-with-video/generate-videos-using-images.html) and [Generate videos using text prompts](https://helpx.adobe.com/firefly/web/work-with-audio-and-video/work-with-video/generate-videos-using-text-prompts.html).
2. Settings:
   - **Model:** Firefly Video (the default Adobe model). Firefly Video clips are about **5 seconds at 24 fps**.
   - **Aspect ratio:** Widescreen (16:9).
   - **Resolution:** 1080p if it is offered; otherwise the default is fine (Express will sit on a 1920×1080 canvas).
   - **Camera motion:** **Static**. A title card should not zoom or shake.
   - Under **Frames**, upload your still as the **First** frame. If you also generated Prompt 4, upload that as the **Last** frame so the clip ends on a clean pose for the tagline.
3. Paste **Prompt 2** into the prompt box. Click **Generate**. Typical wait is under two minutes.
4. Preview. You want: tiles falling, a clear sort into cage vs. gate, no wild morphing, no invented typography. If it is close, keep it — Express will cover the end with the chart and tagline. If it is a mess, generate once more; if you are past minute 4, jump to the fallback.
5. Download the MP4.

*(Optional, only if you have time: hover the result and try **Generate sound effects** with “soft whoosh of falling tiles, a light cage latch, a solid gate thud, no music, no speech.” You will not hear this in the deck because the opener is muted, so skip it unless you also want a louder hallway-TV version.)*

### 4. Assemble the 10-second card in Adobe Express (about 4 minutes)

1. Open [https://new.express.adobe.com](https://new.express.adobe.com). Help: [Create videos in Adobe Express](https://helpx.adobe.com/express/web/video-creation-and-editing/create-videos/video.html) and [Animate design elements](https://helpx.adobe.com/express/web/audio-and-animation/animation.html).
2. Choose **Video** → create from scratch. Set the size to **1920 × 1080** (16:9 / YouTube / presentation). Set the background color to `#F7F7F4`.
3. Upload from this `adobe/` folder:
   - the Firefly MP4
   - `charts/prob_histogram_1920x1080.png`
   - `tagline.png` and/or `tagline_lower_third.png`
   - `stats_chip.png` (optional)
   - `credit_line.png` (optional — the deck also draws this credit)
4. **Scene A, 0:00–0:05.** Drop the Firefly clip on the canvas, scale to fill (or fit, if you need to avoid cropping the dinosaur). Trim to ~5 seconds. Add a short **Fade in** (0.3 s) on the clip.
5. **Scene B, 0:05–0:08.** Click **+ Add scene**, or stack the histogram on top of a 3-second hold of the last video frame. Place `prob_histogram_1920x1080.png` in the center (or slightly upper-center, leaving room for the tagline). Select the chart → **Animation** → **In** → Fade or Slide up, speed Medium. The transparent frame already includes the white rounded card, so you do not need to draw a background.
6. **Scene C, 0:08–0:10.** Keep the chart on screen. Overlay `tagline_lower_third.png` (full-bleed) **or** place `tagline.png` in the lower third and scale until it is readable from the back of a room. Animation → **In** → Fade or Typewriter / Fade-up, speed Medium. Hold through 0:10. Add a 0.3 s fade at the very end so the loop in the deck is gentle.
7. Optional credit: put `credit_line.png` in the bottom-left at a small size, or type “Made with Adobe Firefly + Adobe Express” in Inter, `#5B6270`, 22 px. The HTML deck will also show this credit when the file is present, so this is belt-and-suspenders.
8. Do **not** add a soundtrack for the deck version (it will be muted).
9. **Download** → MP4, 1920×1080, highest quality available.

### 5. Drop it into the deck (30 seconds)

1. Save the file exactly as:

   ```
   drex-flaky/adobe/opener.mp4
   ```

   Same folder as this recipe. Do not nest it in a subfolder, and do not rename it.
2. Open `pitch/index.html` (refresh if it is already open). Slide 1 should now be the opener: autoplay, muted, looping, with the Adobe credit in the corner. Press → to continue to the problem slide. If the title card still appears, the file name or location is wrong.
3. On stage: let the 10 seconds play, then hit → and start the spoken intro.

---

## Ready-to-paste Firefly prompts

Copy everything inside each block. If a generation adds letters, logos, a dark background, or a moving camera, regenerate once with the same prompt; do not hand-edit the prompt mid-hackathon unless the first result is clearly the wrong scene.

### Prompt 1 — character still (Text to Image, 16:9, Art, Firefly Image 4 / 4 Ultra / 5)

```
A stylized apex-predator dinosaur as a friendly but formidable "CI guardian" standing in a clean, modern, light control-room set. Premium motion-graphics / slightly clay-3D character design, smooth surfaces, dark charcoal body with teal (#0E7C66) markings, intelligent eyes, not photorealistic, not scary, not a cartoon mascot, not cute-chibi. Warm off-white background and floor (#F7F7F4), soft studio lighting, subtle teal rim light. In front of the dinosaur, a stream of small red rectangular failed-test tiles falls from above. With its left claw the dinosaur gently places some tiles into a teal wire quarantine cage on the left, marked only with a padlock icon. With its right claw it ushers other tiles toward a solid dark blocked gate on the right, marked only with a red shield / stop icon. Widescreen 16:9 cinematic composition, the dinosaur slightly off-center, generous empty margin in the lower third of the frame for later typography. Editorial product-key-visual, high-end, uncluttered. No typography, no letters, no numbers, no logos, no watermarks, no UI screenshots, no captions.
```

### Prompt 2 — Image to Video (First frame = Prompt 1 still; camera = Static; Firefly Video, 16:9)

```
The dinosaur CI guardian comes to life in smooth, polished, presentation-ready motion. Red failed-test tiles drift down from above. The dinosaur calmly sorts them: some are placed into the teal quarantine cage on the left, others are firmly sent through the dark blocked gate on the right. Subtle floating dust motes, soft teal rim light, light off-white set. Static camera, no zoom, no pan, no tilt, no handheld shake, no morphing of the character's design. 16:9, 24 fps, high-end motion-graphics quality. No typography, no letters, no numbers, no logos, no subtitles, no watermarks, no captions.
```

### Prompt 3 — Text to Video backup (use only if Image to Video is weak or unavailable; same settings: Firefly Video, 16:9, Static)

```
A 5-second 16:9 motion-graphics title card. A stylized apex-predator dinosaur, premium clay-3D / editorial character with charcoal and teal (#0E7C66) markings, stands in a clean light off-white (#F7F7F4) control-room and acts as a CI guardian. Red rectangular failed-test tiles fall from above. The dinosaur sorts them in two streams: flaky tests into a teal wire quarantine cage with a padlock icon on the left, real bugs through a dark blocked gate with a red shield icon on the right. Static camera, soft studio lighting, subtle teal rim light, smooth looping-friendly motion, no camera shake. No typography, no letters, no numbers, no logos, no subtitles, no watermarks.
```

### Prompt 4 — end-frame still (optional, Text to Image, 16:9; upload as the Last frame in Generate video)

```
The same stylized apex-predator CI-guardian dinosaur and the same clean light off-white (#F7F7F4) control-room set, same charcoal-and-teal character design, same soft studio lighting and teal rim light. End pose: the dinosaur stands protectively between a now-full teal quarantine cage on the left and a closed dark blocked gate on the right, looking toward the camera with a calm, confident expression, one claw resting near the cage. The center and the entire lower third of the 16:9 frame are clean and uncluttered, leaving a clear light area for typography. Widescreen editorial key visual. No typography, no letters, no numbers, no logos, no watermarks, no UI.
```

---

## 2-minute fallback (Express only)

Use this if Firefly video is queued, slow, or off-looking. It still counts as Adobe Express, and it still puts the real histogram — the punchline of the talk — on screen.

1. Open [https://new.express.adobe.com](https://new.express.adobe.com) → **Video** (or a 1920×1080 page if you only need a still), custom size **1920 × 1080**, background `#F7F7F4`.
2. Match the layout in `fallback_layout_reference.png` (left teal bar is optional; titles on the left or top, chart in the center). **Rebuild it. Do not upload the reference as the final art.**
3. Upload `charts/prob_histogram_1920x1080_deckbg.png` (or the transparent card version) and place it in the center.
4. Add text in Inter, or place `tagline.png`:
   - Kicker, `#0E7C66`, Bold, letter-spaced: `CALIBRATED  ·  APEX PREDATOR`
   - Title, `#14161A` ExtraBold: `Flaky or real?`
   - Title, `#0E7C66` ExtraBold: `Drex knows.`
   - Stats, `#0E7C66` Bold: `48% lower cost  ·  8× faster`
   - Small credit, `#5B6270`: `Made with Adobe Express`
5. Select the chart → Animation → **In** → Fade or a slow Zoom (Ken Burns), 8–10 seconds total. Fade the tagline in at 0:02. Hold to 0:10.
6. Download as MP4, 1920×1080, and save it as `adobe/opener.mp4`. Refresh the deck.

A still PNG will not hook the deck — the deck looks specifically for `adobe/opener.mp4`. If you only have time for a still, create a 10-second Express video that holds the still with a slow zoom, then export MP4.

---

## Features researched (November 2026) — what we are and are not using

Used in this recipe, with current public docs:

- **Firefly Text to Image** at [firefly.adobe.com](https://firefly.adobe.com) — free daily generations, up to four variations on Image 4, 16:9, Art/Photo, Enhance prompt. [Help](https://helpx.adobe.com/firefly/web/work-with-images/generate-images/generate-images-from-text-descriptions.html).
- **Firefly Generate Video**, text-to-video and image-to-video, including first + last frames, camera motion (we want **Static**), 16:9, Firefly Video at ~5 s / 24 fps, commercially safe Adobe-model output. [Help (text)](https://helpx.adobe.com/firefly/web/work-with-audio-and-video/work-with-video/generate-videos-using-text-prompts.html), [Help (images)](https://helpx.adobe.com/firefly/web/work-with-audio-and-video/work-with-video/generate-videos-using-images.html). Partner models such as Veo 3.1 can go 4/6/8 seconds; skip them for this prize.
- **Adobe Express video editor** at [new.express.adobe.com](https://new.express.adobe.com) — 16:9 1920×1080 canvas, upload your own media, add scenes, trim, **In / Looping / Out** animation on text and images, download MP4. [Help](https://helpx.adobe.com/express/web/video-creation-and-editing/create-videos/video.html), [animation](https://helpx.adobe.com/express/web/audio-and-animation/animation.html).

Not used, on purpose:

- **Adobe Express “Animate characters” / Animate from audio** ([docs](https://helpx.adobe.com/express/web/video-creation-and-editing/edit-videos/animate-characters.html), [feature page](https://www.adobe.com/express/feature/video/animation/audio)). It lip-syncs stock cartoon characters to a voice recording. Our opener is muted, and the stock character library will not give us a branded Apex Predator guardian, so this would look generic rather than on-theme.

---

## Submission line

Paste this into the project description, in place of the Adobe placeholder:

> The opener was generated with Adobe Firefly and assembled in Adobe Express from our real Drex probability chart.

If you had to use the Express-only fallback, use this instead:

> The opener was assembled in Adobe Express from our real Drex probability chart.

---

## Stage note

If `opener.mp4` is in place, the spoken script still starts after the opener. Stand quietly for the 10 seconds, advance on the tagline, then: “Hi, I’m Alexandra…” If the file is missing, slide 1 is the existing title and you start talking immediately.
