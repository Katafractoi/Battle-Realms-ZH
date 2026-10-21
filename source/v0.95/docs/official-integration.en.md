# v0.95 r2 official integration guide

For Windows / Steam AppID **1025600**, build **25733254**, player installer revision **r2**. The tested player ZIP is 6,732,946 bytes, SHA256 `3B4461D032D4410B0B62C06FB66C6D0EE41A283D76F783E2015C74C825045F25`. The full text mapping and all 37 resource deltas/targets are unchanged from the earlier A415 package. This source update starts from `5cbfbd5fd9ca65fd3afc2450a517f570615c6e8f`; the resource snapshot retains its original `8d024ba98b6f573fd8608b9cf7028b319d045db9` provenance. The version remains **v0.95** and the Release remains a prerelease.

## Entry points

| Path | Purpose |
| --- | --- |
| `translations/text.csv` | Complete 6,583-row source/current translation mapping, editable in Excel |
| `translations/locations.json` | Stable keys, resource paths, archive entries, text IDs and field types |
| `translations/baseline.json` | Version binding, protected fields, formatting baseline and resource hashes |
| `ui/byte-edits.json` | Exact field changes for three technology-tree LSRs, with original/target bytes and decoded resource hashes |
| `font/generator-config.json`, `font/layout.json` | Jixiang source hash, rendering parameters, accepted sizes, advances and atlas positions |
| `font/extension-common1500.json` | 1,500 new Chinese characters and frequency provenance for the separate font upgrade |
| `resources/patch-manifest.json`, `resources/patches/` | Seed deltas that exactly reconstruct 37 final resources from the specified English originals |
| `tools/`, `native/` | Portable tools retaining the existing LTE/H2O rewrite, font rasterization and blast algorithms |
| `installer/` | Exact r2 source, authenticated legacy compatibility manifest, unchanged build metadata and player instructions; optional compilation/staging guide |
| `licenses/` | Original Jixiang license documents and required blast/Pillow notices |

The 6,583 rows comprise 6,463 LTE strings, 97 map titles and 23 AI names. Empty translations and originally empty map titles are retained. Some dialogue resource identifiers use `#entryN`; use the logical resource key together with the archive, entry and text ID. Where an original English title is empty, the original-name/filename reference status is retained.

The final text includes “杖术师”, “抡石工” and “剑客”, with zero occurrences of the superseded terms. Beyond these three terminology revisions, translation wording is unchanged.

## Initial reconstruction

Provide an independent copy of the English originals, retaining relative paths such as `AIProfiles/`, `Interface/`, `Levels/` and `Sound/`. The tools do not discover Steam or write to a live game automatically.

```powershell
python tools/build_resources.py --base-root <official-copy> --output <new-snapshot>
```

This verifies original and delta hashes and reads back all 37 reconstructed files. Original game resources are supplied by the integrator; the source directory contains no original game bundle.

Text preview uses the Python standard library. Resource rewriting and font verification also require the blast decoder DLL. Run `native/build.ps1` in a Visual Studio x64 Native Tools shell to compile the included sources; supply your own compiler. Font generation additionally requires `pip install -r requirements-font.txt`, using Pillow 12.2.0.

## Later text hotfixes

Edit the UTF-8 CSV `new` column and use `AUTO` or `SET` in `action`. Preserve every row and all other columns. An empty `new` with `AUTO` keeps the current text; use `CLEAR` to empty a field explicitly. Preserve embedded line breaks and UTF-8 encoding when exporting from Excel.

```powershell
python tools/text_hotfix.py preview --csv <edited.csv> --report <preview.json>
python tools/text_hotfix.py build --csv <edited.csv> --resource-root <snapshot-copy> --blast-dll <blast.dll> --hotfix-id <your-id> --output <new-hotfix>
python tools/text_hotfix.py apply-copy --package <new-hotfix> --resource-root <snapshot-copy> --output <new-applied>
python tools/text_hotfix.py restore-copy --applied <new-applied> --output <new-restored>
```

Preview reports each before/after change, missing glyphs and width risks. The tools validate stable IDs, protected columns, placeholders and control codes, preserving the existing whitespace sequence. They do not trim spaces, change line breaks or reflow text. Unknown/duplicate IDs, a wrong base or missing glyphs block generation. Over-budget widths and uncalibrated controls are reported for visual review.

The result is a delta package bound to the complete base resource hashes. Only affected LTE strings, map titles or AI names are rewritten. Unchanged fonts, UI and installer are not rebuilt. `apply-copy` creates `candidate/`, `backup/` and recovery records in a fresh directory without changing its source copy. `restore-copy` checks both hashes before exporting restored copies. Feed reviewed resources into the official build/deployment pipeline; the player installer is unnecessary.

After adopting the font upgrade or another accepted base, update the manifest in the corresponding source copy and run `refresh_snapshot.py` to export a new CSV, baseline and font advances. A hotfix is valid only for its bound base.

## UI and font

`replay_ui.py` replays LSR field changes against the specified English UI archive copy. `verify_jixiang.py` checks 161 supplementary characters with documented generation provenance against the original TTF across ten size groups. `extend_common_font.py` produces a separate +1,500-character candidate and checks preservation of existing glyph metrics, positions, pixels and all nonfont physical entries.

The addition list uses [Jun Da / Middle Tennessee State University's Modern Chinese Character Frequency List](https://lingua.mtsu.edu/chinese-computing/statistics/char/list.php?Which=MO). It excludes existing characters, prioritizes project game vocabulary and fills the remainder by frequency rank. Only characters and ordinal ranks are retained; dictionary definitions are omitted. Install this font upgrade once and establish its new base before generating later text-only hotfixes for its covered characters.

Stage the separate font candidate with `python tools/font_upgrade.py --package <font-upgrade> --resource-root <snapshot-copy> --output <new-font-stage>`. This exports upgraded resources with backups; the earlier `restore-copy` command can export the restored files. Complete game loading/rendering verification before official adoption, then bind the upgraded resource hashes and corresponding deltas into a new source profile.

Supply the original Jixiang TTF separately. Its SHA-256 is `2E81B7F7DF0B954789CF29C08D5654C4B785712CAA192EF725469BE9A6A0BA5C`. The original author certificate and declaration are preserved unchanged. They do not grant unrestricted redistribution of the font software, so the TTF is not bundled. Obtain and use the font under its author's terms.

## Reconstruction and verification boundaries

The specified English originals plus the included seed deltas exactly reconstruct all 37 accepted resources. Text can be edited and rewritten by stable ID. Required UI fields have replayable edits; new glyphs have renderer code, parameters and source hashes.

The complete initial font build inputs have not all been recovered. Full atlases still depend on the exact seed deltas. This material does not claim that CSV and TTF alone rebuild every atlas from scratch, or that the font documents grant unrestricted font software redistribution.

The +1,500-character candidate has passed structure, decode, pixel and delta readback checks. Actual game startup, rendering across sizes and device-specific memory use remain unverified. This upgrade is separate from the published v0.95 player package and does not modify the current Release.

## r2 synchronization and use prerequisites

The comparison in `r2-package-comparison.json` verifies the old and tested r2 ZIPs member by member: 40 unchanged members, three changed members (EXE, source, README), two additions (`compatibility.json`, `build-info.json`), and no deletions. The accepted text, fonts, UI, manifest and 37 deltas are identical. r2 adds trusted-backup selection for certified legacy/current profiles, verified-original restoration, interrupted-operation recovery records, manifest authentication and a per-game-root operation lock. Unknown modifications and untrusted/incomplete backups are refused. See `../installer/player-README.txt` and `../installer/README.md` for the exact behavior and staging requirements.

The historical 25 installer regression checks are recorded separately from this source synchronization; they are not presented as a new full-game run. The EXE and ZIP are never rebuilt or modified here. The build-time “not published” field inside the original ZIP remains unchanged.

Use a legally obtained, hash-matching English game copy and comply with the game rights holder's and font author's terms. Original license documents are preserved; no blanket game/font redistribution license, official endorsement, or expanded rights are granted by this handoff. The raw TTF, complete original game resources, credentials and private conversation records are excluded. Optional +1500 extension code/list is present only as a separate source reference; no expanded-font candidate build or delta is included in this r2 profile.

The private Release's separate `BRZH-v0.95-r2-official-integration.zip` is the handoff bundle. GitHub's automatic “Source code” archives still follow the unchanged `v0.95` tag and do not contain this updated source directory. Use the separate attachment or a pinned main-branch commit. Access requires existing repository authorization; no sharing permission is granted by a URL.
