# v0.95 r2 技术资料与接入索引

面向维护者、接入者和需要核验文件的使用者。普通安装及问题反馈见[仓库首页](../README.md)，详细玩家恢复步骤见[已测包原始说明](v0.95-installation.txt)。

## 发布文件与校验

适用 Steam AppID **1025600**、build **25733254**。当前安装器修订为 **r2**，仍是测试版。以下 ZIP 均已在上传后下载核对，与本地文件字节一致。

| 文件 | 字节数 | SHA256 |
| --- | ---: | --- |
| [玩家 r2 ZIP](https://github.com/Katafractoi/Battle-Realms-ZH/releases/download/v0.95/BRZH-v0.95-Steam-build25733254-r2.zip) | 6,732,946 | `3B4461D032D4410B0B62C06FB66C6D0EE41A283D76F783E2015C74C825045F25` |


[本次 SHA256 校验文件](https://github.com/Katafractoi/Battle-Realms-ZH/releases/download/v0.95/SHA256SUMS-v0.95-r2.txt) 列出玩家 r2 和[官方接入材料 ZIP](https://github.com/Katafractoi/Battle-Realms-ZH/releases/download/v0.95/BRZH-v0.95-r2-integration-sources.zip)。材料包内另有完整文件清单、逐文件校验和 Python 标准库核验入口。

玩家 r2 ZIP 为原始发布字节，未重新编译、未修改 EXE。相较旧 A415 包，40 个成员不变，安装器 EXE、源码和 README 改变，新增兼容清单及构建信息；37 项汉化资源增量及目标哈希保持一致。ZIP 内构建时“未发布”字段保留原样，当前发布状态以 Release 为准。

旧 `BRZH-v0.95-Steam-build25733254.zip` 与旧 `SHA256SUMS.txt` 仅作历史保留，请勿用于本次安装。旧包为 6,718,648 字节，SHA256 `A4159125588CB9278AB0336092A9EC14FBC34D86892211F1BAD6688ECC19CD13`。

## 源码与官方接入

官方材料在包内 `PROVENANCE.json` 绑定完整来源提交，包含 6,583 条完整文本、37 项资源增量、r2 安装器源码、认证兼容清单、UI/字体参数、工具及原始许可。后续首页文案整理不改变此材料快照。

- [完整来源入口与中英文接入说明](../source/v0.95/README.md)
- [安装器源码及组装要求](../source/v0.95/installer/README.md)
- [旧包与 r2 逐成员对应报告](../source/v0.95/docs/r2-package-comparison.json)
- [本次重建与文本读回核验](../source/v0.95/docs/r2-source-verification.json)

`v0.95` tag 保持在 `f3c6594359736c6de69295a6a4b6cb08ca8a28b8`。GitHub 自动生成的“Source code”跟随该旧 tag，不含新增的接入来源目录；接入请使用独立材料附件或上述固定提交。

## 字体与许可

中文采用字体圈欣意吉祥宋。原始作者证书、使用声明，以及 blast/Pillow 必要通知均保留，见[第三方许可索引](../source/v0.95/licenses/README.md)。原始 TTF 不随材料分发，须依作者条款另行取得；本项目不扩大字体软件或游戏资源的转分发权。

完整初始字体构建输入尚未齐备，精确重建仍依赖指定英文原版与随附种子增量，不能仅凭 CSV 和 TTF 从零重建所有图集。接入者须合法取得并提供哈希匹配的原版资源。材料不含游戏原版全量资源、原始 TTF、凭证或私人聊天。

未实测的 +1500 字候选构建产物或增量未纳入 r2。来源中的可选扩字工具及字符清单仅作独立参考，不改变已测 r2 配置。

## 验证范围

37 项资源的重建结果与目标哈希一致，6,583 条文本已逐条读回核对。安装器回归和来源检查的技术记录见上述核验文件。未测试“学习版”，剧情没有完整通关测试，仍可能有漏译和显示问题。
