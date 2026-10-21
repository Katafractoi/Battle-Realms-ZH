# v0.95 installer r2 source / 安装器 r2 源码

`BRZH-installer.cs`, `compatibility.json`, `build-info.json` and `player-README.txt` are copied byte for byte from the r2 distribution ZIP. The executable distributed on the Release is that original distribution executable.

以上四个文件逐字节来自 r2 发布 ZIP；Release 使用原始发布 EXE。

`build.ps1` is an optional source compilation entry point. Its output is a new local build, not a bit-identical replacement for the distribution binary. To stage that build, put the EXE, `compatibility.json`, `resources/patch-manifest.json` (named `patch-manifest.json`), and the complete `resources/patches/` directory together at one package root, alongside the original player instructions and third-party notices. Keep `build-info.json` as provenance, not proof that a new EXE was tested. The installer authenticates both manifests by fixed SHA256 values.

`build.ps1` 仅为可选编译入口；新编译 EXE 不等于原始发布文件。若自行组装，EXE、`compatibility.json`、由 `resources/` 复制的 `patch-manifest.json` 及完整 `patches/` 须位于同一包根目录，并保留玩家说明与第三方声明。`build-info.json` 是来源记录，不能作为新 EXE 经过验证的证明。安装器以内置 SHA256 验证两份清单。

The embedded `distributionStatus: local-test-candidate-not-published` records the original build-time state. It is retained unchanged to preserve the distribution package bytes; consult the current Release and `package-status.json` for the synchronized revision. / 内嵌“未发布”字段是原构建时状态，为保留发布包字节而保持原样；当前修订以 Release 和 `package-status.json` 为准。

See `player-README.txt` for supported installation, verified-original restoration, backup requirements, recovery and Steam file verification. r2 recognizes only its current resources and the exact certified legacy-r1 profile; unknown modifications remain blocked. Official integration can consume reconstructed resources without running the player installer.

安装、可信原版还原、备份前提、异常恢复及 Steam 验证路径见 `player-README.txt`。r2 只识别现行资源及精确认证的旧 r1 配置；未知修改仍被拒绝。官方可直接接入重建资源，无需运行玩家安装器。
