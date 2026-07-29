<p align="center">
  <img src="assets/library-mark.svg" width="76" height="76" alt="Codex Skills Library 标志">
</p>

<h1 align="center">Codex Skills Library</h1>

<p align="center">
  面向科研与论文，也覆盖应用开发、通用方法和日常技术运维的 Codex 工作流库。
</p>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="docs/FEISHU_PAPER_READING.zh-CN.md">重点工作流</a> ·
  <a href="docs/SKILL_CATALOG.md">Skills 目录</a> ·
  <a href="docs/INSTALL.md">安装指南</a> ·
  <a href="CONTRIBUTING.md">贡献指南</a>
</p>

<p align="center">
  <a href="https://github.com/sidiangongyuan/codex-skills-library/actions/workflows/quality.yml"><img alt="Quality" src="https://github.com/sidiangongyuan/codex-skills-library/actions/workflows/quality.yml/badge.svg"></a>
</p>

<p align="center">
  <a href="assets/readme-overview.svg"><img src="assets/readme-overview.svg" width="100%" alt="一个任务经过已安装的 skill 和 Codex 检查点，最终成为可检查的产物"></a>
</p>

Codex Skills Library 收录了 19 个从真实科研、软件开发和日常技术工作中反复打磨
出来的可安装工作流。这里的 skill 更像一份轻量 SOP，不是模型，也不是几句万能
提示词：它会告诉 Codex 先看什么、在哪些节点检查、最后留下什么产物，以及什么
时候必须停下来交给人判断。

可以只装一项解决眼前问题，也可以把几项串成完整流程。每个可安装目录都把说明、
依赖、许可证和来源放在一起，方便使用前检查。

目前仍以科研和论文为主，但不是纯科研工具箱：

- **科研与论文 · 10 项**：实验、证据、近期论文深读、写作、评审、rebuttal、
  图表和分享。
- **应用与 UI · 5 项**：产品设计、功能开发、故障定位和应用发布。
- **通用方法 · 2 项**：把模糊方案问清楚，以及动手前先检索现成方案。
- **GitHub 与 Codex 运维 · 2 项**：发布干净仓库，以及恢复 Codex Desktop 会话。

_这是由社区维护的独立项目，与 OpenAI 无隶属或背书关系。_

## 重点工作流 · 飞书论文深读

> **把一个研究问题变成有原文锚点、可跨论文比较、写入后回读核验的飞书阅读
> 报告，而不是论文链接堆。**

[`feishu-paper-reading`](docs/FEISHU_PAPER_READING.zh-CN.md) 覆盖完整链路：
扩展候选池、核验一手来源、阅读全文和附录、维护证据台账、跨论文综合、报告校验、
带写前检查点且禁止盲目重复创建的飞书发布，以及写入后的回读确认。若当前没有
可写连接，它可以逐步引导完成最小权限的官方接入，但不会把凭据打包进 skill，
也不会静默接管账号。

<p align="center">
  <a href="docs/FEISHU_PAPER_READING.zh-CN.md"><img src="assets/feishu-paper-reading/actual-summary.png" width="100%" alt="真实飞书论文阅读报告的匿名裁切，展示一篇论文的 30 秒结论"></a>
</p>

<p align="center"><sub>来自一次真实 connector 写入结果，仅保留文档内容区；账号和文档标识均未公开。</sub></p>

**[查看完整流程、真实结果节选、接入边界与调用示例
&rarr;](docs/FEISHU_PAPER_READING.zh-CN.md)**

## 先装一个试试

Codex 自带 `$skill-installer` 系统 skill。可以从最接近手头任务的一项开始。

**科研或课程实验**

```text
$skill-installer 安装 https://github.com/sidiangongyuan/codex-skills-library/tree/main/skills/experiment-planner
```

下一轮可以直接输入：

```text
$experiment-planner 把我的图像分类课程项目整理成一天内能完成的最小实验，给出基线、指标、资源假设和 stop/go 条件。
```

合格的结果至少应包含可证伪主张、对照、最小 pilot、预期信号和决策门槛，而不是
把原来的想法扩写得更长。
[完整示例](docs/EXAMPLE_EXPERIMENT_PLAN.md)展示了这种产物应有的形状，同时明确
区分实验计划和尚未产生的结果。

**应用故障排查**

```text
$skill-installer 安装 https://github.com/sidiangongyuan/codex-skills-library/tree/main/skills/app-bug-forensics
```

下一轮可以输入：

```text
$app-bug-forensics 从用户看到的现象、日志和请求链路追查这个间歇性超时；先确定根因，再修改代码。
```

合格的结果应区分已观察到的证据和待验证假设，找到真正失败的边界，并留下针对性的
回归检查。

不必一次装完 19 项。将 `experiment-planner` 换成[目标目录](#按目标浏览)中的任意
skill 名称即可；安装后会在下一轮对话中可用。在敏感环境中使用前，请检查目标
目录中的 `SKILL.md`、`LICENSE`、依赖和来源。私有 fork 与命令行安装方式见
[单项安装说明](docs/INSTALL.md#install-one-skill-with-codex)。

<details>
<summary><strong>安装多个 skills</strong></summary>

仓库自带的安装器支持选择安装和批量安装，运行时只依赖 Python 标准库，默认写入
用户级共享目录 `$HOME/.agents/skills`。

```bash
git clone https://github.com/sidiangongyuan/codex-skills-library.git
cd codex-skills-library
python scripts/install.py
python scripts/install.py --all --dry-run
python scripts/install.py --all
```

不带选择参数运行时只会显示目录和用法，不会写入文件。批量安装必须显式使用
`--all`。只安装部分 skills：

```bash
python scripts/install.py \
  --skill experiment-planner \
  --skill app-bug-forensics \
  --skill search-first \
  --dry-run

python scripts/install.py \
  --skill experiment-planner \
  --skill app-bug-forensics \
  --skill search-first
```

已有目录默认跳过。只有在检查 dry run 后，才应使用 `--replace` 覆盖同名 skill。
用 `--target <目录>` 可以指定其他安装位置。Windows 路径、手动复制、旧参数
`--codex-home` 的兼容行为和故障排查见英文[安装指南](docs/INSTALL.md)。

</details>

## 从手头任务开始

- **模糊方案或陌生任务**：
  `grill-me` &rarr; `search-first`，先问清真正影响决策的问题，再检查维护中的工具、
  开源实现或已有方法。
- **软件或应用类课程设计**：
  `grill-me` &rarr; `search-first` &rarr; `app-feature-craft`，先把需求边界问清楚，
  再检查现成工具，最后完成实现与验证。
- **一个深度学习研究想法**：
  `grill-me` &rarr; `search-first` / `research-evidence` &rarr;
  `experiment-planner`，把猜想和主张分开，核对相关工作，并留下 pilot-first
  实验矩阵。
- **近期论文深读与飞书整理**：
  [`feishu-paper-reading`](docs/FEISHU_PAPER_READING.zh-CN.md)，先扩展候选池，
  再阅读全文、保留带定位的原文短句、完成
  跨论文综合，最后写入并回读验证飞书文档。若尚无已验证的连接，它会先逐步引导
  完成官方、最小权限的飞书接入；只有用户拒绝、环境不兼容或接入仍失败时才降级为
  Markdown。
- **论文投稿前**：
  `paper-section-playbook` &rarr; `paper-refinement-skills` &rarr;
  `paper-review-panel`，组织论证、克制润色，并提前暴露可能改变接收判断的问题。
- **收到正式 reviews 后**：
  由 `rebuttal-response-skills` 接手，逐条映射意见、证据和 reviewer-specific
  回复，不与投稿前评审混在一起。
- **方法图、表格和组会分享**：
  `paper-framework-figure-studio-pro` &rarr; `paper-visual-craft` &rarr;
  `paper-share-html`，先规划视觉叙事，再完善证据表达和演示页面。
- **应用开发或开源发布**：
  `app-feature-craft` &rarr; `app-bug-forensics` &rarr;
  `app-release-readiness`，完成开发、定位根因，并核验真正发布出去的产物。
- **仓库发布或 Codex 恢复**：
  `github-project-release` 用于发布前的仓库审计；`codex-session-restore` 则专门处理
  切换服务商后 Codex Desktop 会话缺失的问题。

## 按目标浏览

下面提供 19 个 skills 的中文导航。英文 README 中的技能表和
[完整目录](docs/SKILL_CATALOG.md)由 [`skills.json`](skills.json) 自动生成，
其中包含完整依赖、示例 prompt、许可证以及固定的上游 revision。

| 目标 | Skill |
|---|---|
| 逐层追问并压实模糊方案 | [`grill-me`](skills/grill-me) |
| 开发前检索现成工具和方法 | [`search-first`](skills/search-first) |
| 搜索论文并核验主张与引用 | [`research-evidence`](skills/research-evidence) |
| 深读近期论文、按需引导接入飞书并发布阅读报告 | [`feishu-paper-reading`](skills/feishu-paper-reading) |
| 把研究想法变成可证伪实验矩阵 | [`experiment-planner`](skills/experiment-planner) |
| 规划论文各章节的论证结构 | [`paper-section-playbook`](skills/paper-section-playbook) |
| 在不扩大主张的前提下润色论文 | [`paper-refinement-skills`](skills/paper-refinement-skills) |
| 投稿前独立模拟顶会评审并评估接收风险 | [`paper-review-panel`](skills/paper-review-panel) |
| 收到正式 reviews 后组织证据、起草回复并执行盲审 | [`rebuttal-response-skills`](skills/rebuttal-response-skills) |
| 规划论文方法、架构和流程总览图 | [`paper-framework-figure-studio-pro`](skills/paper-framework-figure-studio-pro) |
| 设计并验证论文图表 | [`paper-visual-craft`](skills/paper-visual-craft) |
| 制作表格清晰、可按演讲节奏呈现的论文分享 HTML | [`paper-share-html`](skills/paper-share-html) |
| 把产品需求做成可交付功能 | [`app-feature-craft`](skills/app-feature-craft) |
| 从现象和日志定位应用问题 | [`app-bug-forensics`](skills/app-bug-forensics) |
| 测试、打包并核验应用发布 | [`app-release-readiness`](skills/app-release-readiness) |
| 改进界面、交互和无障碍质量 | [`ui-ux-pro-max`](skills/ui-ux-pro-max) |
| 构建有明确设计语言的前端与作品集 | [`design-taste-frontend`](skills/design-taste-frontend) |
| 审计并发布干净的 GitHub 项目仓库 | [`github-project-release`](skills/github-project-release) |
| 诊断并恢复 Codex Desktop 会话 | [`codex-session-restore`](skills/codex-session-restore) |

来源处理和版权归属统一记录在 [NOTICE.md](NOTICE.md)。

## 使用 skill

显式调用最清楚，也最便于复现和交接。任务本身还没想清楚时，可以先用通用方法：

```text
$search-first 在决定自己开发这个数据集工具前，先查找维护中的工具、库和现成方案。
```

遇到应用故障时：

```text
$app-bug-forensics 从界面状态沿请求链路诊断这个间歇性 provider timeout；先报告根因，再修改代码。
```

规划研究实验时：

```text
$experiment-planner 把这个想法整理成 pilot-first 实验矩阵，给出可证伪主张、基线、诊断项和 stop/go 门槛。
```

投稿前使用独立评审：

```text
$paper-review-panel 在投稿前按顶会评审组的方式审查这份论文，区分会改变接收判断的证据缺口和可通过写作修复的问题。
```

大多数 skills 允许在请求与描述高度匹配时隐式调用；默认会向外部系统发布内容的
skill 可以要求显式写出 `$skill-name`，具体策略记录在 `agents/openai.yaml`。
需要固定工作流或可复现交接时，也建议显式调用。

多个 skills 可以串联，但每个阶段应由一个职责明确的 skill 主导。完整示例和交接点
见英文[工作流手册](docs/USAGE.md)。

## 参与贡献

项目接受任何主题的实用 skill。可以先开 issue 讨论，但不是提交 pull request 的
前置条件。新 skill 必须包含：

- 名称与目录一致、使用小写 kebab-case 的聚焦 `SKILL.md`；
- `skills.json` 中的示例 prompt 和完整依赖；
- 放在可独立安装目录内的适用许可证；
- 原创声明或固定到 revision 的上游来源；
- 对删除、发布和其他外部可见操作的安全默认行为。

不要提交凭据、私人对话、未公开项目材料、本机专用路径、数据集、checkpoint，
也不要提交再分发权不明确的内容。模板、校验命令和评审标准见英文
[贡献指南](CONTRIBUTING.md)。

## 许可与安全

项目原创内容采用 [MIT License](LICENSE)。第三方内容继续遵循上游许可证和版权；
每个可独立安装的 skill 都携带适用于自身的许可证文本。来源标签和固定 revision
见 [NOTICE.md](NOTICE.md)。

Skills 会影响工具调用，也可能包含可执行的辅助脚本。仓库安装器只复制文件，
不会执行已安装 skill 的脚本；但在允许其访问敏感数据、凭据、发布渠道或破坏性
工具前，仍应检查具体内容。安全问题请按 [SECURITY.md](SECURITY.md) 中的流程私下报告。
