<p align="center">
  <img src="assets/library-mark.svg" width="76" height="76" alt="Codex Skills Library 标志">
</p>

<h1 align="center">Codex Skills Library</h1>

<p align="center">
  面向研究、论文、产品开发、视觉表达和项目发布的可复用 Codex 工作流。
</p>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="docs/SKILL_CATALOG.md">Skills 目录</a> ·
  <a href="docs/INSTALL.md">安装指南</a> ·
  <a href="CONTRIBUTING.md">贡献指南</a>
</p>

<p align="center">
  <a href="https://github.com/sidiangongyuan/codex-skills-library/actions/workflows/quality.yml"><img alt="Quality" src="https://github.com/sidiangongyuan/codex-skills-library/actions/workflows/quality.yml/badge.svg"></a> <img alt="17 skills" src="https://img.shields.io/badge/skills-17-0f766e"> <img alt="Python 标准库安装器" src="https://img.shields.io/badge/installer-Python%20stdlib-2563eb"> <a href="NOTICE.md"><img alt="来源可追溯" src="https://img.shields.io/badge/provenance-tracked-b45309"></a>
</p>

Codex Skills Library 是一个公开的可复用工作流集合，涵盖产品开发、研究、
学术写作、视觉表达和项目运维。每个 skill 都是可以独立安装的目录，其中包含
聚焦的操作说明、可选辅助工具、依赖声明和可追溯的来源信息。

这是由社区维护的独立项目，不是 OpenAI 官方项目，也不隶属于 OpenAI 或获得其
背书。仓库本身就是发布载体，不另建网站、GitHub Pages 或插件市场。

<table>
  <tr>
    <td width="33%">
      <strong>找一个 skill</strong><br>
      从目标导航中选择需要的工作流，只安装这一项。<br><br>
      <a href="#按目标浏览">按目标浏览</a>
    </td>
    <td width="33%">
      <strong>组合完整流程</strong><br>
      在研究、写作、评审、rebuttal 和发布阶段使用职责清晰的 skill。<br><br>
      <a href="#工作流导航">查看工作流</a>
    </td>
    <td width="33%">
      <strong>安装前先检查</strong><br>
      每个目录都保留依赖、许可证和可追溯来源。<br><br>
      <a href="docs/SKILL_CATALOG.md">打开完整目录</a>
    </td>
  </tr>
</table>

## 快速开始

Codex 自带 `$skill-installer` 系统 skill。把目标 skill 的 GitHub 目录链接交给它：

```text
$skill-installer 安装 https://github.com/sidiangongyuan/codex-skills-library/tree/main/skills/research-evidence
```

将 `research-evidence` 替换为目录中的任意 skill 名称。安装后，它会在下一轮对话中
可用。`$skill-installer` 会使用当前 Codex 环境配置的 skills 目录。

在敏感环境中安装前，请先检查目标目录中的 `SKILL.md`、`LICENSE`、依赖和来源。
私有 fork 与命令行安装方式见英文
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

</details>

## 工作流导航

<table>
  <tr>
    <td width="50%">
      <strong>研究构思</strong><br>
      <code>grill-me</code> &rarr; <code>experiment-planner</code> &rarr; <code>research-evidence</code><br><br>
      把模糊想法压实为可证伪实验计划，再核验文献和主张。
    </td>
    <td width="50%">
      <strong>论文生命周期</strong><br>
      <code>paper-section-playbook</code> &rarr; <code>paper-refinement-skills</code> &rarr; <code>paper-review-panel</code> &rarr; <code>rebuttal-response-skills</code><br><br>
      先组织和润色论文，投稿前做独立评审；收到正式 reviews 后再切换到 rebuttal 工作流。
    </td>
  </tr>
  <tr>
    <td width="50%">
      <strong>产品交付</strong><br>
      <code>app-feature-craft</code> &rarr; <code>app-bug-forensics</code> &rarr; <code>app-release-readiness</code><br><br>
      实现功能、基于证据定位故障，并验证最终发布面。
    </td>
    <td width="50%">
      <strong>论文表达</strong><br>
      <code>paper-framework-figure-studio-pro</code> &rarr; <code>paper-visual-craft</code> &rarr; <code>paper-share-html</code><br><br>
      规划视觉叙事、完善图表，并制作面向听众的论文分享。
    </td>
  </tr>
</table>

## 按目标浏览

下面提供 17 个 skills 的中文导航。英文 README 中的技能表和
[完整目录](docs/SKILL_CATALOG.md)由 [`skills.json`](skills.json) 自动生成，
其中包含完整依赖、示例 prompt、许可证以及固定的上游 revision。

| 目标 | Skill |
|---|---|
| 把产品需求做成可交付功能 | [`app-feature-craft`](skills/app-feature-craft) |
| 从现象和日志定位应用问题 | [`app-bug-forensics`](skills/app-bug-forensics) |
| 测试、打包并核验应用发布 | [`app-release-readiness`](skills/app-release-readiness) |
| 改进界面、交互和无障碍质量 | [`ui-ux-pro-max`](skills/ui-ux-pro-max) |
| 逐层追问并压实模糊方案 | [`grill-me`](skills/grill-me) |
| 把研究想法变成可证伪实验矩阵 | [`experiment-planner`](skills/experiment-planner) |
| 搜索论文并核验主张与引用 | [`research-evidence`](skills/research-evidence) |
| 开发前检索现成工具和方法 | [`search-first`](skills/search-first) |
| 规划论文各章节的论证结构 | [`paper-section-playbook`](skills/paper-section-playbook) |
| 在不扩大主张的前提下润色论文 | [`paper-refinement-skills`](skills/paper-refinement-skills) |
| 投稿前独立模拟顶会评审并评估接收风险 | [`paper-review-panel`](skills/paper-review-panel) |
| 收到正式 reviews 后组织证据、起草回复并执行盲审 | [`rebuttal-response-skills`](skills/rebuttal-response-skills) |
| 规划论文方法、架构和流程总览图 | [`paper-framework-figure-studio-pro`](skills/paper-framework-figure-studio-pro) |
| 设计并验证论文图表 | [`paper-visual-craft`](skills/paper-visual-craft) |
| 制作表格清晰、可按演讲节奏呈现的论文分享 HTML | [`paper-share-html`](skills/paper-share-html) |
| 审计并发布干净的 GitHub 项目仓库 | [`github-project-release`](skills/github-project-release) |
| 诊断并恢复 Codex Desktop 会话 | [`codex-session-restore`](skills/codex-session-restore) |

来源处理和版权归属统一记录在 [NOTICE.md](NOTICE.md)。

## 使用 skill

显式调用最清楚，也最便于复现和交接：

```text
$app-bug-forensics 从界面状态沿请求链路诊断这个间歇性 provider timeout；先报告根因，再修改代码。
```

```text
$experiment-planner 把这个想法整理成 pilot-first 实验矩阵，给出可证伪主张、基线、诊断项和 stop/go 门槛。
```

投稿前使用独立评审：

```text
$paper-review-panel 在投稿前按顶会评审组的方式审查这份论文，区分会改变接收判断的证据缺口和可通过写作修复的问题。
```

收到正式 reviews 后切换到 rebuttal 工作流：

```text
$rebuttal-response-skills 逐条映射这些正式 reviews，建立证据与决策记录，起草 reviewer-specific 回复，并执行最终盲审。
```

所有收录的 skills 也允许隐式调用：当用户请求与描述高度匹配时，Codex 可以自动
选择。需要固定工作流或可复现交接时，建议显式写出 `$skill-name`。

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
