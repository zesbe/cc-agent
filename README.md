# cc-agent

Launch **cheap, file-editing AI sub-agents** (DeepSeek, GLM/z.ai, MiniMax, …) as your coding workers — driven by the Claude Code harness, routed through [claude-hub](https://github.com/zesbe/claude-hub).

A manager model (e.g. Claude Opus) delegates grunt-work coding to a much cheaper model, which gets **full tools** (read/write/edit files, run commands) because the tools belong to the Claude Code harness — not to the model.

```
cc-agent deepseek ./my-project "buat module auth, tulis test, jalankan pytest"
cc-agent zai      ./my-project "refactor utils.py jadi typed, jangan ubah API"
```

**Dua mode (auto-deteksi):**

- **DIRECT** — kalau ada `~/.config/cc-agent/<provider>.env`, agent bicara **langsung** ke endpoint Anthropic provider. Tanpa hub, tanpa proses tambahan. Cocok lintas-mesin (termasuk Windows/Mac).
- **HUB** — kalau tidak, route lewat [claude-hub](https://github.com/zesbe/claude-hub). Berguna kalau punya banyak provider / ingin key terpusat.

> Direct = lebih mandiri (tak butuh hub nyala), bukan signifikan lebih cepat — hop ke localhost-hub <1ms, latency nyata ada di provider.

---

## Kenapa ini ada

Provider murah (DeepSeek/GLM) lewat panggilan API biasa cuma bisa **balas teks** — tidak bisa menyentuh file. `cc-agent` memberi mereka **tangan**: ia menjalankan Claude Code (`claude`) secara headless, tapi mengarahkan "otak"-nya ke provider murah via claude-hub.

| Cara | Otak | Bisa edit file? | Biaya |
|------|------|-----------------|-------|
| Panggilan API teks biasa | DeepSeek/GLM | ❌ | murah |
| **cc-agent** | DeepSeek/GLM | ✅ penuh | murah |
| Claude Code biasa | Claude | ✅ penuh | mahal |

---

## Alur kerja (flow)

```
            ┌─────────────────────────────┐
            │  MANAGER (Claude Opus / kamu)│
            │  rancang + bagi tugas + QA   │
            └──────────────┬──────────────┘
                           │ cc-agent <provider> <dir> "<task>"
                           ▼
            ┌─────────────────────────────┐
            │  claude (headless)          │  ← TANGAN: Read/Write/Edit/Bash
            │  --permission-mode bypass   │
            │  --add-dir <workdir>        │
            └──────────────┬──────────────┘
                           │ ANTHROPIC_BASE_URL = claude-hub
                           ▼
            ┌─────────────────────────────┐
            │  claude-hub  (127.0.0.1:8765)│  ← terjemah slot→model provider
            │  /p/<provider>/v1/messages  │
            └──────────────┬──────────────┘
                           │ Anthropic-compatible /v1/messages (tool_use)
                           ▼
            ┌─────────────────────────────┐
            │  Provider: DeepSeek / z.ai / │  ← OTAK
            │  MiniMax / …                 │
            └─────────────────────────────┘
```

Inti: **tool milik harness, bukan model.** claude-hub menerjemahkan `claude-opus-4-8`/`sonnet`/`haiku` → model provider, lalu meneruskan ke endpoint `/anthropic` provider yang mendukung tool-calling.

---

## Yang dibutuhkan (requirements)

**Selalu:** `claude` (Claude Code CLI) terpasang, `bash`, `curl`.

**Mode DIRECT (rekomendasi, tanpa hub):** satu file `~/.config/cc-agent/<provider>.env` (chmod 600) per provider:

```bash
# ~/.config/cc-agent/deepseek.env
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_AUTH_TOKEN=sk-...
ANTHROPIC_MODEL=deepseek-v4-pro
ANTHROPIC_SMALL_FAST_MODEL=deepseek-v4-flash
```

Contoh lengkap di [`examples/providers/`](examples/providers/).

**Mode HUB:** [claude-hub](https://github.com/zesbe/claude-hub) berjalan di `127.0.0.1:8765` dengan profil provider terdaftar di `profiles.db`.

> Provider apa pun yang Anthropic-compatible & mendukung `tool_use`. Teruji: **DeepSeek** (`deepseek-v4-pro`), **z.ai/GLM** (`glm-5.2`).

### ⚠️ Jebakan yang sering bikin error

- **z.ai base_url JANGAN diakhiri `/v1`.** Claude Code menambah `/v1/messages` sendiri; kalau base sudah `…/anthropic/v1` → jadi `…/v1/v1/messages` → error `model may not exist`. Pakai `https://api.z.ai/api/anthropic`.
- **Nama model harus persis** seperti yang dikenali provider (cek `GET <base>/v1/models`). z.ai valid: `glm-4.5`, `glm-4.5-air`, `glm-4.6`, `glm-4.7`, `glm-5`, `glm-5.1`, `glm-5.2`.
- `ANTHROPIC_MODEL` menerima nama non-Claude (mis. `deepseek-v4-pro`, `glm-5.2`) langsung.

---

## Install

```bash
git clone https://github.com/zesbe/cc-agent.git
install -m 755 cc-agent/cc-agent ~/.local/bin/cc-agent   # pastikan ~/.local/bin di PATH
```

> 📘 **Baru pertama kali? Ikuti [SETUP.md](SETUP.md)** — panduan langkah demi langkah
> (pasang, bikin file env per provider, jebakan umum, troubleshooting).

---

## Pemakaian

```bash
cc-agent <provider> <workdir> "<task>"
echo "<task>" | cc-agent <provider> <workdir>
```

| Arg | Arti | Default |
|-----|------|---------|
| `provider` | nama provider (`deepseek`, `zai`, …) — cocok dgn `<provider>.env` atau profil hub | `deepseek` |
| `workdir`  | direktori yang boleh disentuh agent (dibuat bila belum ada) | `$PWD` |
| `task`     | instruksi (argumen atau via stdin) | — |

**Env override:**
- `CC_AGENT_TIMEOUT` — batas detik (default `300`)
- `CC_HUB_URL` — URL hub (default `http://127.0.0.1:8765`)
- `CC_FORCE_HUB=1` — abaikan config direct, paksa lewat hub
- `CC_AGENT_CONFIG_DIR` — lokasi file `.env` (default `~/.config/cc-agent`)

Log tiap run disimpan ke `<workdir>/.cc-agent.log`. Pemilihan mode: ada `<provider>.env` → DIRECT, selain itu → HUB.

---

## Pola kolaborasi multi-agent

Beberapa agent (provider berbeda) bisa membangun **satu codebase bersama** secara paralel. Kunci suksesnya ada di manager:

1. **Tulis kontrak dulu** (`CONTRACT.md`) — signature fungsi/interface yang pasti, **sebelum** ada yang mengoding.
2. **Bagi kepemilikan file** dengan tegas — agent A pegang `storage.py`, agent B pegang `cli.py`+test. Tidak boleh dua agent menyentuh file yang sama (race condition).
3. **Integrasi + verifikasi di manager** — agent tidak saling melihat; manager yang menyatukan dan menguji end-to-end.

```bash
# contoh: DeepSeek + GLM paralel
cc-agent deepseek ./proj "Implement storage.py sesuai CONTRACT.md. Hanya sentuh storage.py." > a.log 2>&1 &
cc-agent zai      ./proj "Implement cli.py + test sesuai CONTRACT.md. Jangan bikin storage.py." > b.log 2>&1 &
wait
# lalu manager: jalankan test + integrasi
```

Contoh lengkap yang sudah jalan ada di [`examples/task-tracker/`](examples/task-tracker/) — `storage.py` dibuat DeepSeek, `cli.py`+`test_app.py` dibuat GLM, nyambung lewat `CONTRACT.md`.

---

## Disiplin / peringatan

- Agent jalan dengan `--permission-mode bypassPermissions` = **bisa edit/hapus file tanpa konfirmasi**. Selalu kurung di `workdir` spesifik.
- **Selalu verifikasi hasil** (re-run test, spot-check) — model murah lebih sering keliru.
- Jangan commit `profiles.db` claude-hub ke repo publik — isinya API key provider.
- Token client untuk hub cukup `dummy`; hub yang menyuntik token provider asli.

---

## Lisensi

MIT — lihat [LICENSE](LICENSE).
