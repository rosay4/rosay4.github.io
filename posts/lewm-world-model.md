---
title: LEWM 世界模型分析解读
date: May 29, 2026
author: GPT 5.5
math: true
description: 用克制极简的动画结构解释 LeWM 如何避免表征崩溃、使用 SIGReg 约束潜在空间，并通过世界模型完成规划。
summary: 用动画拆解 LeWM：表征崩溃、SIGReg、潜在空间规划与复现要点。
---

## 一句话看懂 LeWM

LeWM 想解决一个朴素但致命的问题：世界模型训练时，编码器可能把所有画面都映射成同一个向量，预测误差看起来很小，但表示已经失效。

<section class="lewm-stage lewm-stage-overview" aria-label="LeWM overview animation">
  <div class="lewm-copy">
    <span class="lewm-label">Core idea</span>
    <p>不靠老师模型，不冻结编码器，只用预测损失和 SIGReg，把潜在表示推向稳定的高维正态分布。</p>
  </div>
  <div class="lewm-pipeline" aria-hidden="true">
    <div class="lewm-frame">o<sub>t</sub></div>
    <div class="lewm-arrow"></div>
    <div class="lewm-chip">Encoder</div>
    <div class="lewm-arrow"></div>
    <div class="lewm-latent-cloud">
      <span></span><span></span><span></span><span></span><span></span><span></span>
    </div>
    <div class="lewm-arrow"></div>
    <div class="lewm-chip">Predictor</div>
    <div class="lewm-arrow"></div>
    <div class="lewm-frame">z<sub>t+1</sub></div>
  </div>
</section>

## 表征崩溃

如果只优化预测误差，模型会发现一条捷径：所有输入都编码成 0。预测值和目标值都变成 0，loss 很低，但特征没有任何辨别力。

<section class="lewm-stage lewm-collapse" aria-label="Representation collapse animation">
  <div class="lewm-copy">
    <span class="lewm-label">Failure mode</span>
    <p>输入很多，表示只剩一个点。训练看似成功，下游任务直接失明。</p>
  </div>
  <div class="collapse-board" aria-hidden="true">
    <div class="collapse-inputs">
      <span>car</span><span>wall</span><span>goal</span><span>robot</span>
    </div>
    <div class="collapse-funnel"></div>
    <div class="collapse-zero">0</div>
    <div class="collapse-loss">loss ↓</div>
  </div>
</section>

## SIGReg 的直觉

SIGReg 不让特征挤成一个点。它随机抽很多方向，把高维特征投影成一维，再检查每条投影是否像正态分布。

<section class="lewm-stage lewm-sigreg" aria-label="SIGReg projection animation">
  <div class="lewm-copy">
    <span class="lewm-label">SIGReg</span>
    <p>像用多束光照一个云团：每个影子都正常，整体形状才更可信。</p>
  </div>
  <div class="sigreg-visual" aria-hidden="true">
    <div class="sigreg-cloud">
      <span></span><span></span><span></span><span></span><span></span>
      <span></span><span></span><span></span><span></span><span></span>
    </div>
    <div class="beam beam-a"></div>
    <div class="beam beam-b"></div>
    <div class="beam beam-c"></div>
    <div class="projection projection-a"></div>
    <div class="projection projection-b"></div>
    <div class="projection projection-c"></div>
  </div>
</section>

## 训练目标

LeWM 的训练目标很干净：预测未来，同时约束当前 batch 的表示分布。

$$
\mathcal{L}_{\mathrm{LeWM}}
= \mathcal{L}_{\mathrm{pred}}
+ \lambda \,\mathcal{L}_{\mathrm{SIGReg}}
$$

<section class="lewm-stage lewm-loss" aria-label="LeWM loss animation">
  <div class="loss-term">
    <span>L<sub>pred</sub></span>
    <p>预测未来特征</p>
  </div>
  <div class="loss-plus">+</div>
  <div class="loss-term loss-term-active">
    <span>λ · SIGReg</span>
    <p>防止表示坍缩</p>
  </div>
  <div class="loss-equals">=</div>
  <div class="loss-term">
    <span>L<sub>LeWM</sub></span>
    <p>稳定端到端训练</p>
  </div>
</section>

## 用世界模型规划

训练完成后，LeWM 在潜在空间里“想象”未来：采样动作序列，滚动预测 H 步，选择最接近目标的那条轨迹。

<section class="lewm-stage lewm-planning" aria-label="Planning in latent space animation">
  <div class="lewm-copy">
    <span class="lewm-label">Planning</span>
    <p>不是一次执行完整计划，而是滚动规划：想很多步，只走第一步。</p>
  </div>
  <div class="planning-space" aria-hidden="true">
    <div class="state state-start">z<sub>1</sub></div>
    <div class="state state-goal">z<sub>g</sub></div>
    <div class="planning-horizon">
      <span>H=1</span><span>H=2</span><span>H=3</span><span>H=4</span>
    </div>
    <div class="path path-bad"><span></span><span></span><span></span></div>
    <div class="path path-mid"><span></span><span></span><span></span></div>
    <div class="path path-best"><span></span><span></span><span></span></div>
    <div class="planned-step"><span>execute a<sub>1</sub></span></div>
    <div class="planner-dot rollout-dot"></div>
    <div class="planner-dot execute-dot"></div>
  </div>
</section>

## 为什么值得看

- 理论动机更清楚：用分布约束切断崩溃捷径。
- 结构更简单：Encoder + Predictor，没有老师学生双网络。
- 超参数更少：主要关注投影数量 `M` 和权重 `lambda`。
- 更适合从零训练：不用把上限交给冻结的预训练视觉模型。

## 复现提示

先从简单环境开始，例如 `tworoom`。如果任务很简单，过高的潜在维度可能反而不自然；如果环境更复杂，可以优先观察 SIGReg 权重、投影数和训练曲线稳定性。
