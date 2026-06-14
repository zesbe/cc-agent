# Contoh: Task Tracker CLI (kolaborasi 2 agent)

Codebase kecil ini dibangun oleh **dua AI provider berbeda** secara paralel,
disatukan lewat kontrak (`CONTRACT.md`) oleh manager (Claude Opus).

| File | Dibuat oleh | Peran |
|------|-------------|-------|
| `CONTRACT.md` | Manager (Opus) | definisi interface — ditulis lebih dulu |
| `storage.py` | **DeepSeek** (`deepseek-v4-pro`) | data layer (load/save/add/complete/remove) |
| `cli.py` | **GLM / z.ai** (`glm-5.2`) | CLI argparse (add/list/done/rm) |
| `test_app.py` | **GLM / z.ai** | unit test untuk storage |

## Jalankan

```bash
python3 test_app.py          # unit test
python3 cli.py add "Beli kopi"
python3 cli.py add "Tulis laporan"
python3 cli.py done 1
python3 cli.py list
```

Output `list`:
```
[x] #1 Beli kopi
[ ] #2 Tulis laporan
```

Karena `cli.py` (GLM) dan `storage.py` (DeepSeek) sama-sama patuh pada
`CONTRACT.md`, keduanya langsung kompatibel tanpa pernah saling melihat kode.
