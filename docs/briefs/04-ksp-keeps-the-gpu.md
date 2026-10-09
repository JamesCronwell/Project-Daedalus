# BRIEF 04: KSP keeps the GPU - Horse off while playing, more commit headroom, Adrenalin's extras off

```
Status:     next
Commits:    -
Track:      habits
Machine:    Crusader
Touch:      docs/guides/ (new: pagefile, Adrenalin), docs/RUNBOOK-crusader.md, docs/PLUMBING.md, docs/CHANGELOG.md,
            docs/START_HERE.md (§1, §6), this brief; on Crusader, with the owner's yes and a CHANGELOG entry first: two
            desktop shortcuts ("Horse off", "Horse on")
Don't touch: Windows system settings (the pagefile is set by the owner, from the guide), Adrenalin's settings (the owner
            clicks), LM Studio's settings, the KSP installs (Calypso's), Hephaestus's bridge-kit scripts (called
            unchanged), the AMD driver (only through task 4, with its own yes)
Suggested model: sonnet   (guides, two shortcuts and records)
Effort level:    high     (the pagefile sizing and the shortcuts' exact commands need checking, not guessing)
Parallel:   no   (a machine change; BRIEF 02 is idle until its Task 5)
Owner time: applying the pagefile from the guide and rebooting (~5 min); the Adrenalin guide (~5 min); a yes for the
            shortcuts; then a few KSP sessions with Horse off
Done when:  (1) the pagefile is the agreed custom size after a reboot (read back read-only); (2) both shortcuts work:
            "Horse off" leaves `lms ps` without huihui, and "Horse on" brings it back loaded with the MTP draft and
            16384 context, by Hephaestus's own loader; (3) the Adrenalin guide is applied (the owner confirms); (4) at
            least two KSP sessions with Horse off end without a DXGI device-removed crash (Calypso's log check);
            (5) RUNBOOK, PLUMBING and the CHANGELOG record it all, with rollbacks
```

## Handover   (last stop: -)
```
State:     not started
Next:      Task 1
Ask owner: -
Dirty:     -
```

## Why
On 2026-10-09 at 20:16, KSP_x64 crashed in `d3d11.dll`, and the AMD Bug Report Tool popped up.

**Calypso's triage** (Unity crash folder `Crash_2026-10-09_171645386`):
- DXGI_ERROR_DEVICE_REMOVED, 388 failed creates, 19 seconds after a VAB scene switch;
- no out-of-memory error, and no TDR logged.

**Daedalus's read-only look:**
- **No driver timeouts:** in 30 days, no event 4101, no WHEA hardware error and no unexpected reboot.
- **Memory near the limit:** commit stood at 94-95% of its limit, both at the crash and again at 21:17.
- **Horse sits on the GPU.** LM Studio's `llama-server` (Vulkan) holds about 20 GB of commit. Hephaestus's logon loader
  (`bridge-kit\start-horse-server.ps1`) loads `huihui-qwen3.8-27b-abliterated` with `--gpu max`, so the whole model
  sits in the 24 GB of VRAM that KSP's Parallax and Scatterer also use.
- **The driver:** 32.0.31041.1004, dated 2026-08-17. The newest found is Adrenalin 26.9.1 (2026-09-03, "Optional"),
  whose fixes target RDNA 4.

**The owner's choices** (Orchestrator - Daedalus chat, 2026-10-09):
- Daedalus takes the machine side and the Adrenalin extras; Calypso's lighter graphics settings were declined.
- Horse is unloaded and reloaded by hand around KSP: "I'll do C", because another watcher would watch over watching
  software.
- Two desktop shortcuts: "yes, with the shortcuts".

**Hephaestus's terms:**
- no JIT loading and no idle unload, because Horse's gate waits for "loaded" and nothing reloads it;
- the reload goes through its own loader, which keeps the MTP draft and the 16384 context;
- no time of day needs Horse warm;
- a bigger pagefile is fine by it.

## Tasks
1. **The shortcuts,** on the owner's desktop, each running a visible PowerShell window that says what it did:
   - **"Horse off":** `C:\Users\User\.lmstudio\bin\lms.exe unload huihui-qwen3.8-27b-abliterated`, then `lms ps`.
   - **"Horse on":** `powershell -NoProfile -ExecutionPolicy Bypass -File "C:\- Tools\- LLM\WH40K\bridge-kit\start-horse-server.ps1"`.
     Hephaestus's loader, unchanged; it's idempotent and confirms the server.

   Test both once with the owner present, reading `lms ps` before and after.
2. **The pagefile guide** (`docs/guides/pagefile.md`).
   - **Research the size, then propose it.** It's a custom size on C: (425 GB free), large enough that commit doesn't
     sit at the limit. Today the limit is about 90 GB, with a peak of 123 GB reported at the crash. A starting point
     to check: initial 48 GB, maximum 96 GB.
   - **The owner applies it.** The guide gives the exact clicks: System Properties → Advanced → Performance → Virtual
     memory. It's a system setting, so Claude never changes it.
   - **After the reboot,** read the result back read-only.
   - **The rollback:** "Automatically manage paging file size" back on.
3. **The Adrenalin guide** (`docs/guides/adrenalin-ksp.md`). For KSP's profile, or globally while playing: the overlay
   and metrics, Instant Replay and recording, Anti-Lag, Chill, Boost, HYPR-RX and Image Sharpening, off. Note each
   setting's current value first, so it can be switched back.
4. **The driver,** only if a KSP session with Horse off still ends in device removed. Then propose a clean install of
   a "Recommended" release: keep the current version's installer for rollback, and use AMD's own cleanup. That's its
   own yes, and its own CHANGELOG entry.
5. **Records.**
   - RUNBOOK-crusader: before KSP, Horse off; after, Horse on.
   - PLUMBING: the two shortcuts, and Horse's place on the GPU.
   - START_HERE: §1 and §6.
   - Tell Calypso and Hephaestus when it's in place.

## Rollback
- **The shortcuts:** delete the two `.lnk` files from the desktop (the owner, or with their yes).
- **The pagefile:** the owner switches "Automatically manage paging file size" back on, then reboots.
- **Adrenalin:** switch each setting back to the value the guide recorded.
- **The driver,** if task 4 runs: reinstall the recorded version from its kept installer.
