# KIE Veo 3.1 Fast continuation workflow for branded spokesperson ads

Use this reference when generating multi-part social ads with KIE/Veo where the user wants the same character/story to continue across clips.

## Pattern

1. Draft the story first, not just a prompt. Define:
   - character arc;
   - first 2-second hook;
   - scene-by-scene narration;
   - environment and outfit changes;
   - exact product claims/prices to say.
2. Generate a single concept image first when the user wants to approve the model/person/look before video.
3. Generate clip 1 with `veo3_fast` / Veo 3.1 Fast.
4. Capture and report the task/reference id and seed for clip 1.
5. Generate clip 2 as a continuation using the previous task/reference id/seed in the prompt or API payload field supported by the current KIE endpoint.
6. Repeat for clip 3+ using the immediately previous clip id/seed.
7. Download the videos locally, save create/record JSON, and output a manifest with model, task ids, seeds, narration, and file paths.
8. Verify with ffprobe or equivalent that each MP4 has video + audio streams and expected duration/resolution.
9. Extract thumbnails for QA when possible.

## Postly example structure

For Postly, the strongest story tested was:

1. Messy founder struggling with daily content: cluttered office, sticky notes, blank Facebook/Instagram draft, stressed voice.
2. She discovers Postly marketing agents: UI cards transform chaos into ideas, captions, carousel, AI reel, calendar, auto-post.
3. Freedom/business growth: she is happy in a premium environment/nice car, says posts publish automatically and she can focus on business.
4. Price/value clip: mention the entry offer in 8 seconds, e.g. “Postly сарын 360,000 төгрөгөөс эхэлнэ. Төлөвлөлт, санаа гаргалт, 7 carousel, 5 reel бүгд багтана — маш өндөр үнэ цэнтэй.”

## First 2-second hook guidance

Avoid ordinary talking-head starts. Use a pattern interrupt:

- close-up of messy desk / blank post draft / chaotic calendar;
- the woman sighs, closes the notebook, or taps the table;
- snap-cut to direct eye contact;
- Mongolian hook: “Өдөр бүр юу постлох вэ гэж бодсоор залхсан уу?”

## Voice and subtitles

Veo Mongolian speech can be imperfect. If pronunciation or wording is weak, use the generated video visuals and add a clean Mongolian female voiceover plus exact subtitles in a later editing step.

## Delivery format

When sending results to the user, include for each generation:

- scene title;
- narration text;
- task id;
- seed;
- MEDIA path to MP4;
- short QA note.
