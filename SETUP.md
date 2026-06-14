# Panduan Setup cc-agent (langkah demi langkah)

Tujuan: bisa "menyuruh" provider murah (DeepSeek / GLM / dll) ngoding & edit file
beneran, dikendalikan harness Claude Code. Panduan ini fokus **DIRECT MODE**
(tanpa claude-hub) karena paling simpel & lintas-mesin.

---

## 0. Konsep singkat (biar paham yang lagi disetup)

```
Manager (kamu / Claude)
   │  cc-agent <provider> <dir> "task"
   ▼
claude (Claude Code, headless)  ← TANGAN: baca/tulis/edit file, run command
   │  ANTHROPIC_BASE_URL = endpoint provider
   ▼
DeepSeek / GLM / ...            ← OTAK
```

**Tool itu milik harness Claude Code, bukan milik model.** Kita cuma menukar
"otak"-nya ke provider murah lewat 4 environment variable.

---

## 1. Prasyarat

- **Claude Code CLI** terpasang → cek: `claude --version`
- **bash** + **curl**
- **API key** dari provider yang Anthropic-compatible (DeepSeek, z.ai/GLM, dll)

---

## 2. Pasang script cc-agent

```bash
git clone https://github.com/zesbe/cc-agent.git
install -m 755 cc-agent/cc-agent ~/.local/bin/cc-agent
# pastikan ~/.local/bin ada di PATH:
echo $PATH | tr ':' '\n' | grep -q "$HOME/.local/bin" && echo "PATH OK" || \
  echo 'export PATH="$HOME/.local/bin:$PATH"  # tambahkan ke ~/.bashrc'
which cc-agent   # harus muncul path-nya
```

---

## 3. Setup provider (DIRECT MODE)

Buat **satu file env per provider** di `~/.config/cc-agent/`.

```bash
mkdir -p ~/.config/cc-agent && chmod 700 ~/.config/cc-agent
```

### DeepSeek → `~/.config/cc-agent/deepseek.env`

```bash
cat > ~/.config/cc-agent/deepseek.env <<'EOF'
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_AUTH_TOKEN=sk-GANTI_DENGAN_KEY_KAMU
ANTHROPIC_MODEL=deepseek-v4-pro
ANTHROPIC_SMALL_FAST_MODEL=deepseek-v4-flash
EOF
chmod 600 ~/.config/cc-agent/deepseek.env
```

### z.ai / GLM → `~/.config/cc-agent/zai.env`

```bash
cat > ~/.config/cc-agent/zai.env <<'EOF'
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
ANTHROPIC_AUTH_TOKEN=GANTI_DENGAN_KEY_KAMU
ANTHROPIC_MODEL=glm-5.2
ANTHROPIC_SMALL_FAST_MODEL=glm-4.5-air
EOF
chmod 600 ~/.config/cc-agent/zai.env
```

> Arti 4 variabel:
> - `ANTHROPIC_BASE_URL` — endpoint Anthropic-compatible provider
> - `ANTHROPIC_AUTH_TOKEN` — API key provider
> - `ANTHROPIC_MODEL` — model utama (boleh nama non-Claude, mis. `glm-5.2`)
> - `ANTHROPIC_SMALL_FAST_MODEL` — model kecil untuk task background Claude Code

---

## 4. ⚠️ Dua jebakan paling sering (BACA INI)

1. **z.ai: base_url JANGAN diakhiri `/v1`.**
   Claude Code otomatis menambah `/v1/messages`. Kalau base sudah
   `…/anthropic/v1`, hasilnya `…/v1/v1/messages` → error
   **"model may not exist or you may not have access"**.
   ✅ Benar: `https://api.z.ai/api/anthropic`

2. **Nama model harus PERSIS** seperti yang dikenal provider. Cek daftar resmi:
   ```bash
   curl -s https://api.z.ai/api/anthropic/v1/models \
     -H "authorization: Bearer KEY_KAMU" -H "anthropic-version: 2023-06-01"
   ```
   z.ai valid (per Jun 2026): `glm-4.5`, `glm-4.5-air`, `glm-4.6`, `glm-4.7`,
   `glm-5`, `glm-5.1`, `glm-5.2`.

---

## 5. Coba jalankan

```bash
mkdir -p /tmp/coba
cc-agent deepseek /tmp/coba "Buat hello.py berisi print('halo'). Jalankan python3 hello.py."
# lihat hasil:
cat /tmp/coba/hello.py
```

Kalau muncul file `hello.py` dan jalan → **setup berhasil.** 🎉
Log tiap run ada di `<workdir>/.cc-agent.log`.

### Cara pakai umum

```bash
cc-agent <provider> <workdir> "<instruksi>"
echo "<instruksi panjang>" | cc-agent <provider> <workdir>
```

| Arg | Arti |
|-----|------|
| `provider` | nama file env tanpa `.env` (`deepseek`, `zai`, …) |
| `workdir` | folder yang BOLEH disentuh agent (dikurung di sini) |
| `task` | instruksi (argumen atau via stdin) |

Override: `CC_AGENT_TIMEOUT` (detik, default 300), `CC_FORCE_HUB=1` (paksa hub),
`CC_AGENT_CONFIG_DIR` (lokasi file env).

---

## 6. Banyak agent kerja sama (kolaborasi)

Beberapa provider membangun satu codebase paralel. Kunci: **tulis kontrak dulu**
dan **bagi file ownership**.

```bash
mkdir -p proj
# (1) tulis proj/CONTRACT.md berisi signature fungsi tiap modul

# (2) lepas 2 agent paralel, file berbeda
cc-agent deepseek proj "Baca CONTRACT.md. HANYA buat storage.py sesuai kontrak." > a.log 2>&1 &
cc-agent zai      proj "Baca CONTRACT.md. HANYA buat cli.py + test. Jangan bikin storage.py." > b.log 2>&1 &
wait

# (3) manager integrasi + jalankan test
```

Contoh jadi: [`examples/task-tracker/`](examples/task-tracker/).

---

## 7. Mode HUB (opsional)

Kalau punya banyak provider / ingin key terpusat, pakai
[claude-hub](https://github.com/zesbe/claude-hub). cc-agent otomatis pakai hub
kalau **tidak ada** file `~/.config/cc-agent/<provider>.env`. Paksa hub dengan
`CC_FORCE_HUB=1`.

---

## 8. Troubleshooting

| Gejala | Sebab & solusi |
|--------|----------------|
| `model may not exist or no access` | base_url z.ai pakai `/v1` (hapus), atau nama model salah (cek `/v1/models`) |
| `no direct config and hub unreachable` | file `<provider>.env` tak ada DAN hub mati. Buat env (langkah 3) atau nyalakan hub |
| agent diam / timeout | naikkan `CC_AGENT_TIMEOUT`, cek `.cc-agent.log` di workdir |
| hasil ngaco | model murah memang kadang salah — **selalu verifikasi** (re-run test). Pakai model lebih kuat bila perlu |
| `claude: command not found` | Claude Code belum terpasang / tak di PATH |

---

## 9. Keamanan (wajib)

- File `*.env` berisi **API key** → `chmod 600`, simpan di `~/.config/cc-agent/`,
  **JANGAN** commit ke git (sudah di-`.gitignore`).
- Agent jalan `--permission-mode bypassPermissions` = **edit/hapus tanpa nanya**.
  Selalu kurung di `workdir` spesifik, jangan arahkan ke `$HOME` atau root repo penting tanpa sadar.
- Jangan pernah menempel API key di chat / issue / commit. Kalau telanjur, **rotate** segera.
- **Selalu verifikasi hasil** sebelum dipakai — manager yang bertanggung jawab, bukan agent.
