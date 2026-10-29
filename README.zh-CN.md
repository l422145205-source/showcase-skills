# 日常生活 Agent Skills

把现实中的零散任务交给 Agent。当前主打 **PetLife｜铲屎官生活管家**：读宠物食品标签、小票和照顾说明，算账、查库存、做交接。

[English](README.md) · [Skill 本体](skills/pet-life/SKILL.md) · [完整调用示例](examples/pet-life/agent-example.md)

## 直接装进你的 Agent

```sh
npx skills add l422145205-source/showcase-skills --skill pet-life
```

然后对 Agent 说：

> 用 `$pet-life` 整理这些猫粮标签、小票和我的日常说明。两只猫共用一袋粮，算一下还够吃多久、本月记了多少钱，再准备3天托管交接单。看不清的价格别猜。

Skill 提供任务流程、记录结构、单位规则和确定性计算脚本；Agent 负责理解资料、读图（宿主支持时）、核对事实和完成回答。**使用入口就在 Agent 里。**

## 三件实际能帮忙的事

| 场景 | 得到什么 |
| --- | --- |
| 粮袋标签 + 购物小票 + 剩余库存 | 每100g/标签热量单位的价格、两只宠物共用库存还能撑多久 |
| 一个月的小票与日常记录 | 不重复记账的消费汇总，以及可用“猫老板审计”口吻写的生活月报 |
| 我要出门几天，朋友来照顾 | 每只宠物分别列用量、喂食位置、习惯、打包量；缺联系人就标草稿 |

### 合成资料包跑出来的结果

- 本期已记录 **209元**，同一张重复小票只算一次。
- 干粮账面约够 **25.7天**，罐头约够 **7天**；会显示最近盘点日期和漏记的影响。
- 按最近小票和现有用量估算 **13.22元/天**，与实际购买支出分开。
- 三天托管按两只猫各自的既定用量整理；没有紧急联系安排，交接单保留为草稿。

[看原始资料、调用方式与结果 →](examples/pet-life/agent-example.md)  
[实际生成的生活账本](examples/pet-life/brief.md) · [托管交接单](examples/pet-life/care-card.md)

### 怎么复现

Python 3.10+，PetLife 的计算脚本只用标准库，不需要额外部署模型、数据库或网页。宿主 Agent 自身需要相应的语言/图像理解能力；脚本不自带 OCR。

```sh
python skills/pet-life/scripts/petlife.py build --input skills/pet-life/assets/household.example.json --as-of 2026-10-03 --trip-days 3 --out work/pet-life-demo
```

记录保存在选定的本地工作区。脚本不联网、不改输入账本、不自动把交接单发给别人。模糊价格不当成零、毫升不当成克、账面库存不当成传感器实测值。用量采用主人提供的现有安排，不替宠物开饮食或用药方案。[记录格式](skills/pet-life/references/record-format.md)

有想让 Agent 帮忙的真实养宠杂事，可以用脱敏或合成资料提 Issue。喜欢这个 Skill，点个 Star 可以帮其他养宠人找到它。

## 保留的旧项目

之前的 RepoPet 仓库吉祥物 Skill 和展示页仍保留，展开可查看。

<details>
<summary>RepoPet：早期的仓库像素宠物项目</summary>

# RepoPet · 给你的仓库养一只小龙

![RepoPet：测试状态决定小龙的心情](examples/repopet-hero.gif)

**绿灯就撒欢，红灯就炸毛，没事就睡觉。** 把真实测试结果变成 README 里的像素宠物。

[在线试玩](https://l422145205-source.github.io/showcase-skills/) · [English](README.md) · [Skill 指令](skills/repo-pet/SKILL.md)

## 领养 Patch

```sh
npx skills add l422145205-source/showcase-skills --skill repo-pet
```

安装后对你的 Agent 说：

> 用 `$repo-pet` 给这个仓库养一只薄荷绿的小龙，名字叫 Patch。读取已有的 JUnit 测试报告，把动图放进 README。

生成图片不需要模型或 API Key。只需要 Python 3.10+ 和 Pillow 10.1+；安装 Skill 的命令另外需要 Node.js。也可以直接克隆仓库运行，不安装 Skill：

```sh
git clone https://github.com/l422145205-source/showcase-skills.git
cd showcase-skills
python -m venv .venv
# 按你的终端类型激活 .venv 后执行：
python -m pip install -r requirements.txt
python skills/repo-pet/scripts/repopet.py demo --out repopet-demo
```

打开 `repopet-demo/passing/pet.gif` 就能看到效果。下面这条命令给你的真实项目生成动图，并只替换 README 中属于 RepoPet 的标记区：

```sh
python skills/repo-pet/scripts/repopet.py render --repo ../your-project --junit ../your-project/junit.xml --out ../your-project/assets/repopet --readme ../your-project/README.md
```

## 它会怎么“闹情绪”？

| 状态 | 表现 | 数据依据 |
| --- | --- | --- |
| 通过 | 开心晃尾巴、冒星星 | 存在实际执行通过的用例，且无失败/错误；或 CI 成功 |
| 失败 | 炸毛、冒小火花 | 有失败/错误用例，或工作流失败 |
| 运行中 | 等待动画 | 工作流排队或执行中 |
| 跳过 | 闭眼打盹 | 全部用例跳过，或工作流明确跳过 |
| 未知 | 一脸问号 | 缺报告、报告损坏、无用例或 CI 取消/结果中立 |

![开心小龙示例](examples/gallery/passing/pet.gif)

首页与试玩页使用**明确标注的合成示例**。生成图片是某一时刻的快照，重新运行才会刷新。CI 成功不等于“测试全部通过”，因此不编造用例数量；报告缺失也不会假装通过。[详细依据与 CI 接入方法](skills/repo-pet/references/evidence.md)

## 从蛋到小龙

![蛋、幼龙、成龙](examples/evolution.png)

读取本地可达提交数：**0–2 次为蛋、3–24 次为幼龙、25 次以上为成龙**。这只是外观彩蛋，不是贡献质量评分。浅克隆只能统计已获取的历史；非 Git 目录默认幼龙。

还可以自选薄荷绿、淡紫或蜜桃色，手动指定外形：

```sh
python skills/repo-pet/scripts/repopet.py render --repo . --theme peach --name Mochi --stage dragon
```

## 公开时不用交出个人资料

渲染器仅使用测试汇总、工作流状态和提交总数，不读取作者、邮箱、提交说明、远程仓库地址，不把源文件路径写进图片/JSON。不会自动运行测试、推送代码或给工作流添加写权限。宠物名字由你指定，公开时建议使用昵称。

想要别的表情、配色或原创小生物？欢迎在 [Issues](https://github.com/l422145205-source/showcase-skills/issues) 留下想法。喜欢它的话，点个 Star 可以帮下一位养龙人找到这里。

MIT 开源；像素龙由代码原创绘制。测试：`python -m unittest discover -s tests -v`。

</details>
