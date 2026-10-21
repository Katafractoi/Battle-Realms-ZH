# v0.95 r2 官方接入说明

适用 Windows / Steam AppID **1025600**、build **25733254**、安装器修订 **r2**。已测玩家 ZIP 为 6,732,946 字节，SHA256 `3B4461D032D4410B0B62C06FB66C6D0EE41A283D76F783E2015C74C825045F25`。全量文本映射及全部 37 项增量/资源目标与旧 A415 包相同。本次来源更新以 `5cbfbd5fd9ca65fd3afc2450a517f570615c6e8f` 为起点；资源快照保留最初 `8d024ba98b6f573fd8608b9cf7028b319d045db9` 的来源记录。版本仍为 **v0.95**，Release 保持预发布。

## 材料入口

| 路径 | 用途 |
| --- | --- |
| `translations/text.csv` | 6,583 条完整原文/现行译文映射；可在 Excel 中编辑 |
| `translations/locations.json` | 稳定 ID、资源路径、条目序号、文本 ID、字段类型 |
| `translations/baseline.json` | 版本绑定、保护字段、格式基准、资源哈希 |
| `ui/byte-edits.json` | 三个科技树 LSR 的精确字段改动；包含原值、目标值和解码资源哈希 |
| `font/generator-config.json`、`font/layout.json` | 吉祥宋来源哈希、渲染参数、已接受的字号、字宽与图集位置 |
| `font/extension-common1500.json` | 单独字库升级的 1,500 个新增汉字及频率来源 |
| `resources/patch-manifest.json`、`resources/patches/` | 从指定英文原版精确重建 37 个最终资源所需的增量种子 |
| `tools/`、`native/` | 沿用现有 LTE/H2O 回填、字库渲染和 blast 解码实现的可移植工具 |
| `installer/` | r2 原始源码、认证的旧版兼容清单、未改写构建信息和玩家说明；可选编译及组装说明 |
| `licenses/` | 吉祥宋原始许可文件、blast 与 Pillow 必要许可 |

6,583 条包括：6,463 条 LTE 文本、97 个地图标题、23 个 AI 名称。空译文和原本为空的地图标题也保留。Dialogue 的部分逻辑资源以 `#entryN` 标识；该定位键与归档、条目、文本 ID 一起使用。英文原始标题为空时，保留对应的原名/文件名参考状态。

最终文本已同步“杖术师”“抡石工”“剑客”，旧称计数为零。除上述三项术语修订外，译文未作其他润色。

## 首次重建

准备一份独立的英文原版资源副本，保留 `AIProfiles/`、`Interface/`、`Levels/`、`Sound/` 等相对路径。工具不会自动查找 Steam 或写入真实游戏。

```powershell
python tools/build_resources.py --base-root <official-copy> --output <new-snapshot>
```

该步骤逐文件校验原版和增量哈希，并回读重建后的 37 个结果。原版资源由接入者提供，本目录不包含原版整包。

文本预览仅需 Python 标准库。实际回填和字库验证需要 blast 解码 DLL。在 Visual Studio x64 Native Tools 命令行运行 `native/build.ps1`，可从随附源码编译；编译器由接入者提供。字库生成另需 `pip install -r requirements-font.txt`，使用 Pillow 12.2.0。

## 后续文字热修

在 UTF-8 CSV 的 `new` 列填写新译文，`action` 使用 `AUTO` 或 `SET`。其余列保持原样；保留所有行。`AUTO` 的空 `new` 表示保持现状；确需清空时显式用 `CLEAR`。请保留 Excel 导出后的换行和 UTF-8 编码。

```powershell
python tools/text_hotfix.py preview --csv <edited.csv> --report <preview.json>
python tools/text_hotfix.py build --csv <edited.csv> --resource-root <snapshot-copy> --blast-dll <blast.dll> --hotfix-id <your-id> --output <new-hotfix>
python tools/text_hotfix.py apply-copy --package <new-hotfix> --resource-root <snapshot-copy> --output <new-applied>
python tools/text_hotfix.py restore-copy --applied <new-applied> --output <new-restored>
```

预览列出逐条前后差异、缺字和宽度风险。工具校验稳定 ID、保护字段、占位符和控制码，保留当前空白字符序列；不自动删空格、改换行或重新排版。未知/重复 ID、错误基版、缺字会拦截生成。宽度超预算与未标定控件会提示风险，仍需显示验收。

生成物是绑定完整基版资源哈希的增量包，只重写受影响的 LTE、地图标题或 AI 名称。未变字体、UI 和安装器不会重做。`apply-copy` 在新目录生成 `candidate/`、`backup/` 和恢复记录，原副本保持不变；`restore-copy` 校验前后哈希后导出恢复副本。把审核后的资源纳入官方自己的构建/部署流程即可，无需运行玩家安装器。

使用升级字库或接入下一次已接受基版后，应在相应来源副本中更新资源清单，再运行 `refresh_snapshot.py` 导出新的 CSV、基准和字体度量。旧热修只适用于其绑定的基版，不跨基版套用。

## UI 与字体

`replay_ui.py` 可对指定英文原版 UI 副本重放 LSR 字段改动。`verify_jixiang.py` 可用原始 TTF 回读核验 161 个有明确生成记录的补充字符，覆盖十组字号。`extend_common_font.py` 在独立目录生成 +1,500 字候选，并检查旧字形度量、位置、像素和所有非字体物理条目保持一致。

新增清单采用 [Jun Da / Middle Tennessee State University 现代汉字频率表](https://lingua.mtsu.edu/chinese-computing/statistics/char/list.php?Which=MO)，排除现有字，优先补充项目游戏用字，再按频率填足。清单只保留汉字和频率序号，不复制词典释义。该升级须单次安装并形成新基版，后续已覆盖字符的热修才可保持为纯文本增量。

单独字库候选可通过 `python tools/font_upgrade.py --package <font-upgrade> --resource-root <snapshot-copy> --output <new-font-stage>` 导出带备份的升级资源副本；随后可用前述 `restore-copy` 导出恢复文件。正式接入前先完成游戏加载与显示验收，再将升级资源哈希和对应增量纳入新的来源配置。

原始吉祥宋 TTF 由接入者另行提供，SHA-256 为 `2E81B7F7DF0B954789CF29C08D5654C4B785712CAA192EF725469BE9A6A0BA5C`。随附作者证书和使用声明保留原样；这些文件没有给出无限制转分发字体软件的授权，因此本目录不附 TTF。请按原作者条款取得和使用字体。

## 可重建范围与验收边界

指定英文原版加随附增量种子可以精确重建全部 37 个已接受资源。文本可按稳定 ID 再编辑、回填。必要 UI 字段有可重放改动，新增字形有渲染代码、参数和来源哈希。

初始完整字库的全部构建来源尚未整理齐备，完整图集仍依赖精确增量种子；材料不声称“仅凭 CSV 和 TTF 从零重建全部图集”。现有许可也不被重新表述为无限制字体软件再分发授权。

+1,500 字候选已完成结构、解码、像素和增量回读检查。实际游戏启动、各字号显示和设备显存占用仍需验收。这项升级独立于已发布的 v0.95 玩家包，不修改当前 Release。

## r2 同步及合法使用前提

`r2-package-comparison.json` 逐成员核对旧包与已测 r2：40 个文件不变，3 个文件改变（EXE、源码、README），新增 `compatibility.json`、`build-info.json`，无删除。已接受文本、字体、UI、资源清单和 37 项增量均未改变。r2 增加认证旧版/现行配置的可信备份筛选、经校验原版还原、中断恢复记录、清单认证和同一游戏目录操作互斥。未知修改及不可信/不完整备份仍被拒绝。准确操作与组装要求见 `../installer/player-README.txt`、`../installer/README.md`。

历史 25 项安装器回归记录与本次来源同步检查分别标注，不能据此声称新完成全游戏流程测试。本次不重编译 EXE、不修改已测 ZIP，原 ZIP 内构建时“未发布”字段也不重写。

请使用合法取得且哈希匹配的英文游戏副本，并遵守游戏权利人与字体作者条款。原始许可文档保留原样；本材料不授予游戏/字体的概括性再分发权，也不代表官方背书或新增授权。包内不含原始 TTF、完整游戏原版资源、凭证或私人聊天。+1500 字的可选代码/清单仅作独立来源参考；r2 配置不含其候选构建产物或增量。

私有 Release 的独立附件 `BRZH-v0.95-r2-official-integration.zip` 才是本次接入材料包。GitHub 自动生成的“Source code”压缩包仍跟随未改动的 `v0.95` tag，不含本次更新的来源目录；请使用独立附件或固定 main 提交。链接仍需原有仓库授权，本次不授予任何访问权限。
