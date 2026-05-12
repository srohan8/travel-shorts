# Travel Shorts AI — Pricing Strategy

**Generated**: 2026-05-13
**Status**: Pre-launch / MVP
**Competitor data**: See `competitor-profiles/` (OpusClip, Klap, QuickReel)

---

## Summary Recommendation

**Model**: Freemium (OSS free) → 3-tier flat monthly cloud subscription
**Value metric**: Flat monthly (not per-video, not credits)
**Anchor price**: $29/mo Creator tier
**Annual discount**: 30% (more aggressive than standard 17% — seasonal use pattern warrants it)

---

## Pricing Personas

Three distinct segments with very different willingness-to-pay:

| Persona | Who they are | WTP | Right tier |
|---------|-------------|-----|------------|
| **The Once-a-Year Poster** | Shot one holiday, wants to post it, not a recurring user | ~$0 | Free OSS |
| **The Regular Creator** | 2–4 trips/year, wants no setup headaches, YouTube Shorts | $10–18/mo | Solo Cloud |
| **The Semi-Pro Vlogger** | Monthly content, all platforms, quality matters | $20–35/mo | Creator Cloud |
| **The Agency / Power User** | Multiple accounts, bulk processing, API | $40–60/mo | Pro Cloud |

---

## Value Metric Decision: Flat Monthly

**Rejected alternatives:**

| Metric | Why rejected |
|--------|-------------|
| Credits / per-minute | Biggest complaint against OpusClip — anxiety, exhaustion, billing surprises |
| Per-video | Penalises users with large libraries; hard to predict spend |
| Per-Short output | Confusing unit; creators don't think in "Shorts per month" |
| Per-trip | Interesting but hard to define (what counts as a trip?) |

**Flat monthly wins because:**
- Travel creators are occasional, seasonal users — predictable cost is essential
- "Pay once, process everything" is a clean, differentiated message vs. credit-based competitors
- No anxiety during processing → better product experience
- Matches how creators budget (Netflix-style monthly commitment)

---

## Proposed Tier Structure

### Free — Self-Hosted (OSS)

**Price**: $0 forever
**Who it's for**: Anyone — technical or not. The only requirement is setting up your own AI.
**What's included**: **Everything.** All features, all platforms.
- Smart crop, multi-segment stitching, vibe selector, travel score, all filters
- YouTube Shorts + Instagram Reels + TikTok output
- Run history (local)
- Open source — self-hostable, auditable, no vendor dependency

**The one thing you bring**: Your AI connection — Gemini API key (free tier at aistudio.google.com) or a locally-running Ollama model.

**Setup required**: Python, ffmpeg, dependencies. One-time, ~10 minutes for technical users.

**Conversion trigger**: "I don't want to set this up" or "I keep hitting Gemini rate limits" or "I want to use it on my phone"

> **Principle**: We don't gate features. We gate convenience. Every user — paying or not — gets the full product.

---

### Solo Cloud — $14/mo · $120/yr ($10/mo) — save 29%

**Who it's for**: Any creator who wants zero setup — sign in, start creating
**What's included**:
- Every feature from the OSS version, cloud-hosted — no Python, no ffmpeg, no API key needed
- Managed AI: we absorb the API costs, no rate limits, no key required
- All output formats: YouTube Shorts, Instagram Reels, TikTok
- Up to 4 trips/month (15 videos per trip)
- Cloud run history (access from any device)
- Mobile-friendly web app
- Email support

**What you're paying for**: Convenience, not features. The product is identical to OSS — we just run it for you and handle the AI bills.

**Rationale**: $14 is impulse-buy territory for someone who just got back from Bali. Below a restaurant meal. $1 less than OpusClip Starter ($15) with a genuinely better product (content plan vs. clips only).

---

### Creator Cloud — $29/mo · $240/yr ($20/mo) — save 31% ⭐ Recommended

**Who it's for**: Regular travel creator who processes multiple trips and wants priority everything
**What's included**:
- Everything in Solo
- Unlimited trips (no monthly video cap)
- Choice of AI provider (Gemini, OpenAI GPT-4o-mini, Claude Haiku) — pick the best model for your content
- Priority AI processing queue (no waiting behind free-tier jobs)
- Priority email support (< 24h response)

**Rationale**: At $20/mo annual, this undercuts Klap Starter ($23/mo annual) while including all features and better support. Matches OpusClip Pro ($29) and QuickReel Pro ($29) on price, but delivers a full content plan — hooks, captions, hashtags, posting schedule — that neither competitor offers.

---

### Pro Cloud — $59/mo · $480/yr ($40/mo) — save 32%

**Who it's for**: Full-time travel creators, creator agencies, power users
**What's included**:
- Everything in Creator
- API access (automate trip processing, integrate with your own tools)
- 2 team seats (manage multiple accounts or collaborate with an editor)
- Bulk processing (entire folder structures, multiple trips at once)
- Custom brand templates saved to cloud (fonts, colour presets, watermark)
- Dedicated support + priority roadmap input

**Rationale**: Positioned just below Klap Pro ($63/mo annual), which has the worst support reputation in the space (~2.9/5 Trustpilot). Their unhappy Pro users are the primary acquisition target for this tier.

---

## Pricing Comparison vs. Competitors

| | Travel Shorts AI | OpusClip | Klap | QuickReel |
|--|----------------|---------|------|-----------|
| **Free tier** | ✓ Full features, no expiry | ✓ Limited (60 min, watermarked) | ✗ None | ✗ Fake (paywall at signup) |
| **All features on free** | ✓ Everything | ✗ Gated behind paid | ✗ No free tier | ✗ No free tier |
| **Entry paid** | $14/mo | $15/mo | $23/mo (annual only) | $9/mo |
| **Mid tier** | $29/mo | $29/mo | $63/mo | $29/mo |
| **Content plan** | ✓ Full (hooks, captions, hashtags, schedule) | ✗ Clips only | ✗ Clips + captions | ✗ Clips + captions |
| **Travel-specific AI** | ✓ | ✗ | ✗ | ✗ |
| **Privacy (no video upload)** | ✓ All tiers | ✗ | ✗ | ✗ |
| **Annual required** | ✗ | ✗ | ✓ | ✗ |
| **Credits / limits** | ✗ Flat | ✓ Credits expire | ✓ Video caps | ✓ Credits |

---

## What NOT to Gate

**Everything.** Every feature is free in the OSS version.

The paid cloud tiers gate **infrastructure**, not features:

| What's gated | Free OSS | Solo $14 | Creator $29 | Pro $59 |
|-------------|---------|---------|------------|--------|
| All features (crop, segments, vibe, score, filters, all platforms) | ✓ | ✓ | ✓ | ✓ |
| Managed AI (no setup, no key) | ✗ | ✓ | ✓ | ✓ |
| No rate limits (we absorb API costs) | ✗ | ✓ | ✓ | ✓ |
| Cloud run history (any device) | ✗ | ✓ | ✓ | ✓ |
| Mobile web app | ✗ | ✓ | ✓ | ✓ |
| Unlimited trips/month | ✗ (local, unlimited) | 4 trips | Unlimited | Unlimited |
| AI provider choice | BYO | Gemini | Gemini/GPT/Claude | Gemini/GPT/Claude |
| Priority processing | ✗ | ✗ | ✓ | ✓ |
| API access | ✗ (run locally) | ✗ | ✗ | ✓ |
| Team seats | ✗ | 1 | 1 | 2 |

**The message**: "We don't charge for features. We charge for not having to think about setup, API keys, or rate limits."

---

## Annual vs. Monthly Trade-off

Travel creators are seasonal users — they may only want the product for 1–3 months around a trip. This argues FOR accessible monthly pricing, not locking to annual.

**Strategy**: Make monthly accessible, make annual compelling.
- Monthly: Full price
- Annual: 30% off = 3.6 months free — material enough to convert the semi-committed

**Don't follow Klap's mistake**: Annual-only pricing creates distrust. Monthly option is essential.

---

## "Trip Pass" — Future Option (not for launch)

A one-time $9 Trip Pass (process one trip, no subscription) could capture the once-a-year poster who won't subscribe but would pay once. Adds pricing complexity — revisit after launch once conversion data exists.

---

## Launch Pricing Strategy

**Phase 1 (launch):** Offer 50% off first 3 months for early users. Anchor: "Lock in before we raise prices." Creates urgency without a permanent discount.

**Phase 2 (traction):** Remove launch discount, hold current prices. Review after 100 paying customers.

**Phase 3 (data):** Run Van Westendorp survey with existing users to validate price points. Adjust if conversion data suggests resistance.

---

## Pricing Page Recommendations

**Structure**: Monthly/Annual toggle at top (Annual default with "Save 30%" badge) → 3 paid tiers + "Free (self-hosted)" link below

**Recommended tier**: Highlight Creator with "Most popular" badge

**Key copy anchors**:
- "No credits. No limits. One flat price."
- "The only AI that writes your captions — not just cuts your clips."
- "Your footage never leaves your machine" (Free tier) / "Processed securely in our cloud" (Paid)

**Trust signals**:
- "Cancel anytime" — prominently displayed (Klap's cancellation issues are known)
- "No credit card for free tier"
- Open source badge (links to GitHub)
- Privacy statement (video never uploaded, for paid: encrypted, deleted after processing)

**FAQ must-haves**:
- "What's the difference between the free and paid versions?" (Setup vs. no-setup)
- "Does the AI upload my videos?" (No, frames only — even in cloud)
- "What counts as a 'trip'?" (For Solo tier)
- "Can I cancel anytime?" (Yes — emphasise this)

---

## Risk Flags

| Risk | Mitigation |
|------|-----------|
| OSS free tier cannibalises paid | Fine — technical users prefer OSS; cloud targets non-technical. They're different segments. |
| $29 feels high pre-launch with no social proof | Launch discount + founder story ("built for this exact problem") |
| Seasonal churn (one trip, then cancel) | Annual discount; run history makes re-subscribing easy ("your old trips are still there") |
| Competitors undercut on price | Don't race to the bottom — compete on content plan + privacy, not on price |
| "Why pay when I can self-host for free?" | Cloud = no setup, no rate limits, mobile access, cloud history. Different value prop. |
