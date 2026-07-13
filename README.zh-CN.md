<p align="center">
  <img src="assets/library-mark.svg" width="76" height="76" alt="Codex Skills Library 标志">
</p>

<h1 align="center">Codex Skills Library</h1>

<p align="center">
  从真实工作流中沉淀的实用 Codex Skills，明确记录依赖与来源，并向社区开放贡献。
</p>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="docs/SKILL_CATALOG.md">Skills 目录</a> ·
  <a href="docs/INSTALL.md">安装指南</a> ·
  <a href="CONTRIBUTING.md">贡献指南</a>
</p>

Codex Skills Library 是一个公开的可复用工作流集合，涵盖产品开发、研究、
学术写作、视觉表达和项目运维。每个 skill 都是可以独立安装的目录，其中包含
聚焦的操作说明、可选辅助工具、依赖声明和可追溯的来源信息。

这是由社区维护的独立项目，不是 OpenAI 官方项目，也不隶属于 OpenAI 或获得其
背书。仓库本身就是发布载体，不另建网站、GitHub Pages 或插件市场。

## 安装单个 skill

Codex 自带 `$skill-installer` 系统 skill。把目标 skill 的 GitHub 目录链接交给它：

```text
$skill-installer 安装 https://github.com/sidiangongyuan/codex-skills-library/tree/main/skills/research-evidence
```

将 `research-evidence` 替换为目录中的任意 skill 名称。安装后，它会在下一轮对话中
可用。`$skill-installer` 会使用当前 Codex 环境配置的 skills 目录。

在敏感环境中安装前，请先检查目标目录中的 `SKILL.md`、`LICENSE`、依赖和来源。
私有 fork 与命令行安装方式见英文
[单项安装说明](docs/INSTALL.md#install-one-skill-with-codex)。

## 安装多个 skills

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
  --skill research-evidence \
  --skill paper-section-playbook \
  --dry-run

python scripts/install.py \
  --skill experiment-planner \
  --skill research-evidence \
  --skill paper-section-playbook
```

已有目录默认跳过。只有在检查 dry run 后，才应使用 `--replace` 覆盖同名 skill。
用 `--target <目录>` 可以指定其他安装位置。Windows 路径、手动复制、旧参数
`--codex-home` 的兼容行为和故障排查见英文[安装指南](docs/INSTALL.md)。

## 按目标浏览

下面提供 17 个 skills 的中文导航。英文 README 中的技能表和
[完整目录](docs/SKILL_CATALOG.md)由 [`skills.json`](skills.json) 自动生成，
其中包含完整依赖、示例 prompt、许可证以及固定的上游 revision。

| 目标 | Skill | 来源类型 |
|---|---|---|
| 把产品需求做成可交付功能 | [`app-feature-craft`](skills/app-feature-craft) | `original` |
| 从现象和日志定位应用问题 | [`app-bug-forensics`](skills/app-bug-forensics) | `original` |
| 测试、打包并核验应用发布 | [`app-release-readiness`](skills/app-release-readiness) | `original` |
| 改进界面、交互和无障碍质量 | [`ui-ux-pro-max`](skills/ui-ux-pro-max) | `third-party-adapted` |
| 逐层追问并压实模糊方案 | [`grill-me`](skills/grill-me) | `third-party-exact` |
| 把研究想法变成可证伪实验矩阵 | [`experiment-planner`](skills/experiment-planner) | `adapter` |
| 搜索论文并核验主张与引用 | [`research-evidence`](skills/research-evidence) | `original` |
| 开发前检索现成工具和方法 | [`search-first`](skills/search-first) | `third-party-adapted` |
| 规划论文各章节的论证结构 | [`paper-section-playbook`](skills/paper-section-playbook) | `original` |
| 在不扩大主张的前提下润色论文 | [`paper-refinement-skills`](skills/paper-refinement-skills) | `original` |
| 模拟顶会评审并评估接收风险 | [`paper-review-panel`](skills/paper-review-panel) | `original` |
| 起草有证据边界的审稿回复 | [`rebuttal-response-skills`](skills/rebuttal-response-skills) | `third-party-adapted` |
| 规划论文方法、架构和流程总览图 | [`paper-framework-figure-studio-pro`](skills/paper-framework-figure-studio-pro) | `adapter` |
| 设计并验证论文图表 | [`paper-visual-craft`](skills/paper-visual-craft) | `original` |
| 制作表格清晰、叙事流畅的论文分享 HTML | [`paper-share-html`](skills/paper-share-html) | `original` |
| 审计并发布干净的 GitHub 项目仓库 | [`github-project-release`](skills/github-project-release) | `original` |
| 诊断并恢复 Codex Desktop 会话 | [`codex-session-restore`](skills/codex-session-restore) | `original` |

来源处理和版权归属统一记录在 [NOTICE.md](NOTICE.md)。

## 使用 skill

显式调用最清楚，也最便于复现和交接：

```text
$app-bug-forensics 从界面状态沿请求链路诊断这个间歇性 provider timeout；先报告根因，再修改代码。
```

```text
$experiment-planner 把这个想法整理成 pilot-first 实验矩阵，给出可证伪主张、基线、诊断项和 stop/go 门槛。
```

```text
$paper-review-panel 按顶会评审组的方式审查这份论文，区分致命证据缺口和可通过写作修复的问题。
```

所有收录的 skills 也允许隐式调用：当用户请求与描述高度匹配时，Codex 可以自动
选择。需要固定工作流或可复现交接时，建议显式写出 `$skill-name`。

多个 skills 可以串联。例如，研究构思可以依次使用 `$grill-me`、
`$experiment-planner` 和 `$research-evidence`；产品发布可以依次使用
`$app-feature-craft`、`$app-bug-forensics` 和 `$app-release-readiness`。
完整示例见英文[工作流手册](docs/USAGE.md)。

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
