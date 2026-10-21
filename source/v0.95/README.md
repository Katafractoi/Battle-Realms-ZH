# Battle Realms ZH v0.95 r2 — integration sources

- [中文接入说明](docs/official-integration.zh-CN.md)
- [English integration guide](docs/official-integration.en.md)
- [r2 package comparison and file hashes](docs/r2-package-comparison.json)
- [Installer source and staging requirements](installer/README.md)

This snapshot is aligned with **v0.95 installer r2**, Steam AppID **1025600**, build **25733254**. Player ZIP: **6,732,946 bytes**, SHA256 `3B4461D032D4410B0B62C06FB66C6D0EE41A283D76F783E2015C74C825045F25`. The 37 resource deltas, manifest, 6,583 text rows, accepted UI/font data and original license notices are unchanged from the older A415 package. Installer source, player instructions, compatibility manifest and build metadata are synchronized from the r2 ZIP, without recompiling its EXE.

The integration update starts from repository commit `5cbfbd5fd9ca65fd3afc2450a517f570615c6e8f`. The unchanged resource snapshot was originally prepared against `8d024ba98b6f573fd8608b9cf7028b319d045db9`. `package-status.json` binds the current r2 package; `source-files.json` lists every other file in this directory with exact size and SHA256.

The complete initial font build inputs have not all been recovered. Exact reconstruction requires the specified English originals **and seed deltas**; CSV and TTF alone do not rebuild every atlas. Original game archives, font software, generated candidate archives and the untested **+1500-character font candidate build** are not included. Existing optional extension tools/list remain separate, disabled source references and have no effect on the r2 resource profile. Complete campaign, device and expanded-font runtime coverage is not claimed.

本目录对应 v0.95 r2，保留重建依赖与授权边界。接入前请阅读中英文说明与原始许可证。
