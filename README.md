# cc-agent

Launch **cheap, file-editing AI sub-agents** (DeepSeek, GLM/z.ai, MiniMax, …) as your coding workers — driven by the Claude Code harness, routed through [claude-hub](https://github.com/zesbe/claude-hub).

A manager model (e.g. Claude Opus) delegates grunt-work coding to a much cheaper model, which gets **full tools** (read/write/edit files, run commands) because the tools belong to the Claude Code harness — not to the model.

```
cc-agent deepseek ./my-project "buat module auth, tulis test, jalankan pytest"
cc-agent zai      ./my-project "refactor utils.py jadi typed, jangan ubah API"
```

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

1. **Claude Code CLI** (`claude`) terpasang & ter-login.
2. **claude-hub** berjalan di `127.0.0.1:8765` — router multi-provider Anthropic-compatible. Lihat https://github.com/zesbe/claude-hub
3. **Profil provider** terdaftar di claude-hub (`profiles.db`), masing-masing punya:
   - `base_url` provider (endpoint Anthropic-compatible, mis. `https://api.deepseek.com/anthropic`)
   - `auth_token` (API key provider) — **disuntik oleh hub, bukan oleh cc-agent**
   - mapping slot: `opus_model`, `sonnet_model`, `haiku_model`
4. `bash`, `curl`, dan akses ke direktori kerja.

> Provider apa pun yang Anthropic-compatible & mendukung `tool_use` bisa dipakai. Sudah teruji: **DeepSeek** (`deepseek-v4-pro`), **z.ai/GLM** (`glm-5.2`).

---

## Install

```bash
git clone https://github.com/zesbe/cc-agent.git
install -m 755 cc-agent/cc-agent ~/.local/bin/cc-agent   # pastikan ~/.local/bin di PATH
```

---

## Pemakaian

```bash
cc-agent <provider> <workdir> "<task>"
echo "<task>" | cc-agent <provider> <workdir>
```

| Arg | Arti | Default |
|-----|------|---------|
| `provider` | nama profil di claude-hub (`deepseek`, `zai`, `minimax`, …) | `deepseek` |
| `workdir`  | direktori yang boleh disentuh agent (dibuat bila belum ada) | `$PWD` |
| `task`     | instruksi (argumen atau via stdin) | — |

**Env override:**
- `CC_AGENT_TIMEOUT` — batas detik (default `300`)
- `CC_HUB_URL` — URL hub (default `http://127.0.0.1:8765`)

Log tiap run disimpan ke `<workdir>/.cc-agent.log`.

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
