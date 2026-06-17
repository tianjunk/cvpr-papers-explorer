import argparse
import json
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_YEAR = "2026"
SITE_TITLE = "CVPR Papers"


LEVEL1_META = {
    "Awards & Nominations": {
        "cn": "获奖与提名",
        "en": "Awards & Nominations",
        "desc": "CVPR 获奖与提名论文。",
        "accent": "#9a6a18",
        "soft": "#f6edd8",
        "deep": "#6b4a0e",
    },
    "2D Detection & Open-Vocabulary Recognition": {
        "cn": "2D 检测与开放词汇识别",
        "en": "2D Detection & Open-Vocabulary Recognition",
        "desc": "二维目标检测、开放词汇检测与目标计数。",
        "accent": "#b45a2f",
        "soft": "#fbe7dd",
        "deep": "#793c1f",
    },
    "Segmentation, Parsing & Matting": {
        "cn": "分割、解析与抠图",
        "en": "Segmentation, Parsing & Matting",
        "desc": "语义分割、实例分割、解析与 matting。",
        "accent": "#b66a2b",
        "soft": "#f8ead8",
        "deep": "#7c451a",
    },
    "Classification, Retrieval & Fine-grained Recognition": {
        "cn": "分类、检索与细粒度识别",
        "en": "Classification, Retrieval & Fine-grained Recognition",
        "desc": "分类、检索、re-id 与细粒度识别。",
        "accent": "#8b5a3b",
        "soft": "#f3e6de",
        "deep": "#5d3b26",
    },
    "3D Reconstruction, Representation & Rendering": {
        "cn": "三维重建、表示与渲染",
        "en": "3D Reconstruction, Representation & Rendering",
        "desc": "三维重建、场景表示、NeRF/3DGS 与几何建模。",
        "accent": "#3f698d",
        "soft": "#e4edf8",
        "deep": "#2a455d",
    },
    "3D Detection & Point Cloud Perception": {
        "cn": "3D 检测与点云感知",
        "en": "3D Detection & Point Cloud Perception",
        "desc": "点云、体素、激光雷达感知与三维目标检测。",
        "accent": "#55779b",
        "soft": "#e7eef7",
        "deep": "#36516d",
    },
    "Depth, Pose, SLAM & Localization": {
        "cn": "深度、位姿、SLAM 与定位",
        "en": "Depth, Pose, SLAM & Localization",
        "desc": "深度估计、位姿恢复、SLAM 与视觉定位。",
        "accent": "#4a6b88",
        "soft": "#e5edf4",
        "deep": "#314658",
    },
    "Video Understanding, Tracking & Action": {
        "cn": "视频理解、跟踪与动作",
        "en": "Video Understanding, Tracking & Action",
        "desc": "视频理解、时序推理、目标跟踪与动作分析。",
        "accent": "#156d74",
        "soft": "#dff3f1",
        "deep": "#0d4a4f",
    },
    "Generative Models": {
        "cn": "生成模型",
        "en": "Generative Models",
        "desc": "图像与视频生成、图像编辑、个性化生成以及场景生成。",
        "accent": "#c86a33",
        "soft": "#ffe9dc",
        "deep": "#87411d",
    },
    "Vision-Language & Multimodal": {
        "cn": "视觉语言与多模态",
        "en": "Vision-Language & Multimodal",
        "desc": "VLM/MLLM 推理、grounding、文档理解与跨模态建模。",
        "accent": "#1d7a8c",
        "soft": "#dff5f8",
        "deep": "#124f5b",
    },
    "Embodied AI, Driving & Robotics": {
        "cn": "自动驾驶、机器人与具身智能",
        "en": "Embodied AI, Driving & Robotics",
        "desc": "自动驾驶、机器人操作、导航与具身控制。",
        "accent": "#637e2f",
        "soft": "#edf4dc",
        "deep": "#44561f",
    },
    "Image Restoration & Computational Imaging": {
        "cn": "图像复原与计算成像",
        "en": "Image Restoration & Computational Imaging",
        "desc": "图像复原、增强、计算成像与质量评价。",
        "accent": "#4a6986",
        "soft": "#e4edf4",
        "deep": "#314658",
    },
    "Learning, Compression, Adaptation & Safety": {
        "cn": "学习、压缩、适配与安全",
        "en": "Learning, Compression, Adaptation & Safety",
        "desc": "学习范式、模型压缩、适配、鲁棒性与安全。",
        "accent": "#2d7a58",
        "soft": "#e2f5e9",
        "deep": "#1d563d",
    },
    "Medical, Remote Sensing & Domain Vision": {
        "cn": "医学、遥感与行业视觉",
        "en": "Medical, Remote Sensing & Domain Vision",
        "desc": "医学影像、遥感、工业与科学成像等领域任务。",
        "accent": "#8d5447",
        "soft": "#f4e6e1",
        "deep": "#5d382f",
    },
}


LEVEL2_META = {
    "Award Winners": {
        "cn": "获奖",
        "desc": "最佳论文、最佳学生论文及荣誉提名。",
        "order": 0,
    },
    "Award Candidates": {
        "cn": "提名",
        "desc": "官方 Award Candidates 名单。",
        "order": 1,
    },
    "Medical & Biomedical Vision": {
        "cn": "医学与生物视觉",
        "desc": "医学影像、病理、临床视觉建模与诊断分析。",
    },
    "Remote Sensing & Geospatial Vision": {
        "cn": "遥感与地理空间视觉",
        "desc": "卫星、航拍、遥感理解与地理空间建模。",
    },
    "Scientific, Industrial & Physical Vision": {
        "cn": "科学、工业与物理视觉",
        "desc": "工业检测、科学成像与物理过程建模。",
    },
    "Autonomous Driving, BEV & Mapping": {
        "cn": "自动驾驶、BEV 与地图",
        "desc": "驾驶感知、BEV 表征、轨迹预测与地图建模。",
    },
    "Robotics, Manipulation & Navigation": {
        "cn": "机器人、操作与导航",
        "desc": "抓取、操作、导航和机器人场景理解。",
    },
    "Embodied Agents, Policy & Control": {
        "cn": "具身智能体、策略与控制",
        "desc": "具身 agent、策略学习、决策与控制。",
    },
    "Neural Rendering & Gaussian Splatting": {
        "cn": "神经渲染与高斯泼溅",
        "desc": "NeRF、3DGS 与新视角渲染。",
    },
    "Reconstruction & 3D Scene Representation": {
        "cn": "重建与三维场景表示",
        "desc": "场景、形状、几何与三维表示学习。",
    },
    "Depth, Pose, SLAM & Localization": {
        "cn": "深度、位姿、SLAM 与定位",
        "desc": "深度估计、位姿、SLAM 与视觉定位。",
    },
    "Point Clouds & 3D Detection": {
        "cn": "点云表征与三维目标感知",
        "desc": "点云、体素表示、激光雷达感知与三维目标检测。",
    },
    "Image/Video Generation & Diffusion": {
        "cn": "图像与视频生成",
        "desc": "扩散模型、流匹配以及图像与视频生成。",
    },
    "Editing, Personalization & Inpainting": {
        "cn": "图像编辑、修补与个性化",
        "desc": "图像编辑、修补、主体定制和风格控制。",
    },
    "Human, Avatar & Motion Generation": {
        "cn": "人体、数字人与动作生成",
        "desc": "人体、avatar 与动作内容生成。",
    },
    "3D, Scene Generation & World Models": {
        "cn": "三维与场景生成",
        "desc": "三维内容生成、场景建模与世界模型。",
    },
    "VLM/MLLM Reasoning & Agents": {
        "cn": "VLM/MLLM 推理与智能体",
        "desc": "多模态推理、规划、agent 和 benchmark。",
    },
    "Grounding, Retrieval & Referring": {
        "cn": "定位、检索与指代",
        "desc": "grounding、跨模态检索与指代理解。",
    },
    "Documents, Charts & Structured Understanding": {
        "cn": "文档、图表与结构化理解",
        "desc": "文档、表格、图表与 structured parsing。",
    },
    "Cross-modal Alignment & Fusion": {
        "cn": "跨模态对齐与融合",
        "desc": "模态对齐、特征融合与通用 embedding。",
    },
    "Detection, Open-Vocabulary & Counting": {
        "cn": "检测、开放词汇与计数",
        "desc": "开放词汇检测、实例发现和目标计数。",
    },
    "Segmentation, Parsing & Matting": {
        "cn": "分割、解析与抠图",
        "desc": "语义/实例分割、解析和 matting。",
    },
    "Classification, Retrieval & Fine-grained Recognition": {
        "cn": "分类、检索与细粒度识别",
        "desc": "分类、检索、re-id 与细粒度识别。",
    },
    "Video Understanding & Temporal Reasoning": {
        "cn": "视频理解与时序推理",
        "desc": "视频理解、长时序 reasoning 与事件建模。",
    },
    "Tracking, Flow & Correspondence": {
        "cn": "跟踪、光流与对应",
        "desc": "目标跟踪、光流估计和 correspondence。",
    },
    "Pose, Motion & Action Analysis": {
        "cn": "姿态、动作与行为分析",
        "desc": "人体姿态、动作分析与行为理解。",
    },
    "Restoration, Enhancement & Super-Resolution": {
        "cn": "复原、增强与超分",
        "desc": "去噪、去模糊、增强和超分辨率。",
    },
    "Computational Imaging & Sensors": {
        "cn": "计算成像与传感器",
        "desc": "成像系统、传感器与物理反演。",
    },
    "Compression & Quality Assessment": {
        "cn": "压缩与质量评估",
        "desc": "图像视频压缩、码率优化和质量评估。",
    },
    "Self-/Weak-/Semi-Supervised Learning": {
        "cn": "自/弱/半监督学习",
        "desc": "自监督、弱监督与标签效率提升。",
    },
    "Adaptation, Continual & Federated Learning": {
        "cn": "适配、持续与联邦学习",
        "desc": "域适配、持续学习和联邦训练。",
    },
    "Efficiency, Distillation, Pruning & NAS": {
        "cn": "效率、蒸馏、剪枝与 NAS",
        "desc": "效率优化、蒸馏、剪枝和结构搜索。",
    },
    "Robustness, Safety, Privacy & Security": {
        "cn": "鲁棒性、安全、隐私与安全攻防",
        "desc": "鲁棒性、隐私保护、安全与攻防研究。",
    },
}


DISPLAY_LEVEL1_BY_LEVEL2 = {
    "Detection, Open-Vocabulary & Counting": "2D Detection & Open-Vocabulary Recognition",
    "Segmentation, Parsing & Matting": "Segmentation, Parsing & Matting",
    "Classification, Retrieval & Fine-grained Recognition": "Classification, Retrieval & Fine-grained Recognition",
    "Neural Rendering & Gaussian Splatting": "3D Reconstruction, Representation & Rendering",
    "Reconstruction & 3D Scene Representation": "3D Reconstruction, Representation & Rendering",
    "Point Clouds & 3D Detection": "3D Detection & Point Cloud Perception",
    "Depth, Pose, SLAM & Localization": "Depth, Pose, SLAM & Localization",
    "Video Understanding & Temporal Reasoning": "Video Understanding, Tracking & Action",
    "Tracking, Flow & Correspondence": "Video Understanding, Tracking & Action",
    "Pose, Motion & Action Analysis": "Video Understanding, Tracking & Action",
    "Image/Video Generation & Diffusion": "Generative Models",
    "Editing, Personalization & Inpainting": "Generative Models",
    "Human, Avatar & Motion Generation": "Generative Models",
    "3D, Scene Generation & World Models": "Generative Models",
    "VLM/MLLM Reasoning & Agents": "Vision-Language & Multimodal",
    "Grounding, Retrieval & Referring": "Vision-Language & Multimodal",
    "Documents, Charts & Structured Understanding": "Vision-Language & Multimodal",
    "Cross-modal Alignment & Fusion": "Vision-Language & Multimodal",
    "Autonomous Driving, BEV & Mapping": "Embodied AI, Driving & Robotics",
    "Robotics, Manipulation & Navigation": "Embodied AI, Driving & Robotics",
    "Embodied Agents, Policy & Control": "Embodied AI, Driving & Robotics",
    "Restoration, Enhancement & Super-Resolution": "Image Restoration & Computational Imaging",
    "Computational Imaging & Sensors": "Image Restoration & Computational Imaging",
    "Compression & Quality Assessment": "Image Restoration & Computational Imaging",
    "Self-/Weak-/Semi-Supervised Learning": "Learning, Compression, Adaptation & Safety",
    "Adaptation, Continual & Federated Learning": "Learning, Compression, Adaptation & Safety",
    "Efficiency, Distillation, Pruning & NAS": "Learning, Compression, Adaptation & Safety",
    "Robustness, Safety, Privacy & Security": "Learning, Compression, Adaptation & Safety",
    "Medical & Biomedical Vision": "Medical, Remote Sensing & Domain Vision",
    "Remote Sensing & Geospatial Vision": "Medical, Remote Sensing & Domain Vision",
    "Scientific, Industrial & Physical Vision": "Medical, Remote Sensing & Domain Vision",
}


AWARD_LABEL_CN = {
    "Best Paper": "最佳论文",
    "Best Student Paper": "最佳学生论文",
    "Best Paper Honorable Mention": "最佳论文荣誉提名",
    "Best Student Paper Honorable Mention": "最佳学生论文荣誉提名",
    "Award Candidate": "提名",
}

AWARD_LABEL_ORDER = {
    "Best Paper": 0,
    "Best Student Paper": 1,
    "Best Paper Honorable Mention": 2,
    "Best Student Paper Honorable Mention": 3,
    "Award Candidate": 9,
}


HTML_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>@@SITE_TITLE@@</title>
  <style>
    :root {
      --bg: #f4efe6;
      --panel: #fffaf2;
      --panel-soft: #fcf7ef;
      --line: rgba(76, 56, 34, 0.12);
      --ink: #1f2624;
      --muted: #64706b;
      --accent: #1d7a8c;
      --accent-soft: #dff5f8;
      --accent-deep: #124f5b;
      --shadow: 0 16px 40px rgba(53, 39, 21, 0.08);
      --radius-xl: 28px;
      --radius-lg: 20px;
      --radius-md: 14px;
      --sans: "Sora", "Avenir Next", "Segoe UI", sans-serif;
      --serif: "Fraunces", "Iowan Old Style", "Palatino Linotype", serif;
      --mono: "IBM Plex Mono", "SFMono-Regular", Consolas, monospace;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      font-family: var(--sans);
      overflow-x: hidden;
      background:
        radial-gradient(circle at top left, rgba(29, 122, 140, 0.08), transparent 26%),
        linear-gradient(180deg, #f7f3eb 0%, var(--bg) 100%);
    }

    a {
      color: inherit;
    }

    button,
    input,
    select {
      font: inherit;
    }

    .app {
      width: min(1420px, calc(100vw - 24px));
      margin: 14px auto 28px;
    }

    .panel {
      background: rgba(255, 250, 242, 0.9);
      border: 1px solid rgba(255, 255, 255, 0.7);
      border-radius: var(--radius-xl);
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }

    .home-hero {
      min-height: min(620px, calc(100vh - 54px));
      padding: clamp(30px, 5vw, 58px);
      overflow: hidden;
      position: relative;
      isolation: isolate;
      display: flex;
      align-items: center;
      background:
        linear-gradient(90deg, rgba(255, 250, 242, 0.99) 0%, rgba(255, 250, 242, 0.96) 46%, rgba(255, 250, 242, 0.76) 72%, rgba(255, 250, 242, 0.36) 100%),
        #fffaf2;
    }

    .home-hero::after {
      content: "";
      position: absolute;
      inset: clamp(24px, 4vw, 50px) clamp(18px, 4vw, 46px) clamp(24px, 4vw, 50px) auto;
      width: min(58vw, 720px);
      background: url("mycode.png") center / contain no-repeat;
      opacity: 0.22;
      pointer-events: none;
      z-index: 0;
    }

    .home-content {
      width: min(700px, 100%);
      position: relative;
      z-index: 1;
    }

    .home-kicker {
      color: var(--accent-deep);
      font-family: var(--mono);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .home-hero h1 {
      margin: 14px 0 0;
      font-family: var(--serif);
      font-size: clamp(42px, 7vw, 76px);
      line-height: 0.98;
      letter-spacing: -0.03em;
      max-width: 10ch;
    }

    .home-lead {
      margin: 20px 0 0;
      max-width: 60ch;
      color: #43504b;
      font-size: clamp(15px, 1.4vw, 18px);
      line-height: 1.8;
    }

    .home-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 24px;
    }

    .home-action {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 44px;
      padding: 0 18px;
      border-radius: 8px;
      border: 1px solid rgba(76, 56, 34, 0.12);
      background: #fff;
      color: var(--ink);
      text-decoration: none;
      font-weight: 700;
      cursor: pointer;
    }

    .home-action.primary {
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
    }

    .home-search {
      display: flex;
      gap: 10px;
      width: min(560px, 100%);
      margin-top: 22px;
    }

    .home-search input {
      min-width: 0;
      flex: 1 1 auto;
      border: 1px solid rgba(76, 56, 34, 0.14);
      background: rgba(255, 255, 255, 0.92);
      border-radius: 8px;
      padding: 13px 14px;
      color: var(--ink);
      outline: none;
    }

    .home-search input:focus {
      border-color: rgba(29, 122, 140, 0.36);
      box-shadow: 0 0 0 4px rgba(29, 122, 140, 0.08);
    }

    .home-stats {
      display: grid;
      grid-template-columns: repeat(4, minmax(92px, 1fr));
      gap: 10px;
      width: min(620px, 100%);
      margin-top: 28px;
    }

    .home-stat {
      padding: 12px;
      border-radius: 8px;
      border: 1px solid rgba(76, 56, 34, 0.1);
      background: rgba(255, 255, 255, 0.78);
    }

    .home-stat strong {
      display: block;
      color: var(--accent-deep);
      font-family: var(--mono);
      font-size: 20px;
      line-height: 1.2;
    }

    .home-stat span {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 12px;
    }

    .home-follow {
      margin-top: 18px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.6;
    }

    .home-quick {
      margin-top: 18px;
      padding: 20px;
    }

    .home-quick-head {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 14px;
    }

    .home-quick h2 {
      margin: 0;
      font-size: 20px;
      line-height: 1.3;
    }

    .home-quick p {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.6;
    }

    .home-category-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 10px;
    }

    .home-category-btn {
      border: 1px solid rgba(76, 56, 34, 0.09);
      border-radius: 8px;
      background: #fff;
      padding: 13px 14px;
      text-align: left;
      cursor: pointer;
      transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease;
    }

    .home-category-btn:hover {
      transform: translateY(-1px);
      border-color: rgba(29, 122, 140, 0.28);
      box-shadow: 0 10px 20px rgba(53, 39, 21, 0.08);
    }

    .home-category-btn strong {
      display: block;
      font-size: 14px;
      line-height: 1.4;
    }

    .home-category-btn span {
      display: block;
      margin-top: 8px;
      color: var(--accent);
      font-family: var(--mono);
      font-size: 12px;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 9px 12px;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.78);
      border: 1px solid rgba(76, 56, 34, 0.09);
      color: var(--muted);
      font-size: 12px;
    }

    .layout {
      display: grid;
      grid-template-columns: 300px minmax(0, 1fr);
      gap: 18px;
      margin-top: 18px;
      align-items: start;
    }

    .sidebar {
      position: sticky;
      top: 14px;
      padding: 20px;
      max-height: calc(100vh - 28px);
      overflow: auto;
    }

    .paper-authors,
    .paper-abstract {
      color: var(--muted);
    }

    .level1-list {
      display: grid;
      gap: 10px;
      margin-top: 18px;
    }

    .level1-btn {
      width: 100%;
      border: 1px solid rgba(76, 56, 34, 0.08);
      border-radius: 18px;
      background: #fff;
      padding: 14px 14px 14px 16px;
      text-align: left;
      cursor: pointer;
      transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease, opacity 140ms ease;
      position: relative;
      overflow: hidden;
    }

    .level1-btn::before {
      content: "";
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 4px;
      background: var(--accent);
      opacity: 0;
      transition: opacity 140ms ease;
    }

    .level1-btn:hover {
      transform: translateY(-1px);
      border-color: rgba(76, 56, 34, 0.14);
    }

    .level1-btn.active {
      border-color: var(--accent);
      box-shadow: inset 0 0 0 1px var(--accent);
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), var(--accent-soft));
    }

    .level1-btn.active::before {
      opacity: 1;
    }

    .level1-btn.is-muted {
      opacity: 0.45;
    }

    .level1-top {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
    }

    .level1-count,
    .count-pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 7px 10px;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.88);
      border: 1px solid rgba(76, 56, 34, 0.08);
      color: var(--accent);
      font-size: 12px;
      font-family: var(--mono);
      white-space: nowrap;
    }

    .level1-title {
      margin: 6px 0 0;
      font-size: 15px;
      line-height: 1.45;
      font-weight: 700;
    }

    .main {
      display: grid;
      gap: 18px;
    }

    .toolbar {
      padding: 20px;
      display: grid;
      gap: 16px;
    }

    .toolbar-row {
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
      justify-content: space-between;
    }

    .search-box {
      position: relative;
      flex: 1 1 320px;
    }

    .search-box input {
      width: 100%;
      border: 1px solid rgba(76, 56, 34, 0.14);
      background: #fff;
      border-radius: 16px;
      padding: 14px 16px 14px 42px;
      color: var(--ink);
      outline: none;
    }

    .search-box input:focus,
    .control select:focus {
      border-color: rgba(29, 122, 140, 0.35);
      box-shadow: 0 0 0 4px rgba(29, 122, 140, 0.08);
    }

    .search-icon {
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--muted);
      font-size: 15px;
    }

    .controls {
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }

    .control.mobile-level1-control {
      display: none;
    }

    .control {
      display: inline-flex;
      align-items: center;
      padding: 0 10px;
      border-radius: 14px;
      background: #fff;
      border: 1px solid rgba(76, 56, 34, 0.1);
    }

    .control select {
      border: 0;
      background: transparent;
      padding: 12px 2px;
      color: var(--ink);
      outline: none;
      min-width: 96px;
    }

    .code-toggle {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 12px;
      border-radius: 14px;
      background: #fff;
      border: 1px solid rgba(76, 56, 34, 0.1);
      color: var(--muted);
      font-size: 12px;
      font-family: var(--mono);
      cursor: pointer;
      user-select: none;
    }

    .code-toggle input {
      margin: 0;
      accent-color: var(--accent);
    }

    .button {
      border: 1px solid rgba(76, 56, 34, 0.12);
      background: #fff;
      color: var(--ink);
      border-radius: 14px;
      padding: 11px 14px;
      cursor: pointer;
      transition: transform 140ms ease, background 140ms ease;
    }

    .button:hover {
      transform: translateY(-1px);
      background: #fffdf9;
    }

    .button.small {
      padding: 9px 12px;
      font-size: 13px;
    }

    .button.icon {
      width: 42px;
      height: 42px;
      padding: 0;
      font-size: 18px;
      line-height: 1;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex: 0 0 auto;
    }

    .scope {
      border-top: 1px solid rgba(76, 56, 34, 0.08);
      padding-top: 16px;
    }

    .scope-row {
      display: flex;
      gap: 12px;
      align-items: center;
      min-height: 42px;
    }

    .scope-path {
      color: var(--muted);
      font-size: 12px;
      font-family: var(--mono);
    }

    .scope-path strong {
      color: var(--accent-deep);
    }

    .scope-title {
      margin: 0;
      font-size: clamp(24px, 2.8vw, 34px);
      line-height: 1.05;
      letter-spacing: -0.03em;
      font-family: var(--serif);
      flex: 1 1 auto;
    }

    .scope-path:empty,
    .scope-title:empty,
    .scope-desc:empty,
    .scope-meta:empty,
    .section-note:empty,
    h2:empty {
      display: none;
    }

    .scope-desc {
      margin: 12px 0 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.75;
      max-width: 64ch;
    }

    .scope-meta {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 12px;
    }

    .section {
      padding: 20px;
    }

    .level2-grid {
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      margin-top: 16px;
    }

    .level2-btn {
      border: 1px solid rgba(76, 56, 34, 0.08);
      border-radius: 18px;
      background: #fff;
      padding: 16px;
      text-align: left;
      cursor: pointer;
      transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease, opacity 140ms ease;
    }

    .level2-btn:hover {
      transform: translateY(-1px);
      border-color: rgba(76, 56, 34, 0.14);
    }

    .level2-btn.active {
      border-color: var(--accent);
      box-shadow: inset 0 0 0 1px var(--accent);
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), var(--accent-soft));
    }

    .level2-btn.is-muted {
      opacity: 0.45;
    }

    .level2-top {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
    }

    .level2-title {
      margin: 0;
      font-size: 15px;
      line-height: 1.5;
      font-weight: 700;
    }

    .level2-subline {
      margin-top: 12px;
      color: var(--muted);
      font-family: var(--mono);
      font-size: 12px;
    }

    .paper-list {
      display: grid;
      gap: 14px;
    }

    .paper-card {
      border: 1px solid rgba(76, 56, 34, 0.08);
      border-radius: 20px;
      background: #fff;
      padding: 18px;
    }

    .paper-meta {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 12px;
    }

    .meta-row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      font-size: 12px;
      line-height: 1.4;
    }

    .meta-item {
      display: inline-flex;
      align-items: center;
      padding: 6px 10px;
      border-radius: 999px;
      background: var(--panel-soft);
      border: 1px solid rgba(76, 56, 34, 0.08);
      color: var(--muted);
      font-family: var(--mono);
    }

    .paper-top {
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: start;
    }

    .paper-top > div {
      min-width: 0;
    }

    .paper-title {
      margin: 0;
      font-size: 20px;
      line-height: 1.4;
      letter-spacing: 0;
      overflow-wrap: anywhere;
    }

    .paper-title a {
      text-decoration: none;
    }

    .paper-title a:hover {
      text-decoration: underline;
      text-underline-offset: 3px;
    }

    .paper-authors {
      margin: 10px 0 0;
      font-size: 14px;
      line-height: 1.7;
      overflow-wrap: anywhere;
    }

    .paper-links {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }

    .link-chip {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 8px 12px;
      border-radius: 12px;
      border: 1px solid rgba(76, 56, 34, 0.09);
      background: #fff;
      color: var(--ink);
      font-size: 12px;
      font-family: var(--mono);
      font-weight: 700;
      letter-spacing: 0.04em;
      text-decoration: none;
      box-shadow: 0 8px 18px rgba(53, 39, 21, 0.08);
      transition: transform 140ms ease, box-shadow 140ms ease, border-color 140ms ease, filter 140ms ease;
    }

    .link-chip:hover {
      transform: translateY(-1px);
      filter: saturate(1.05);
      box-shadow: 0 12px 22px rgba(53, 39, 21, 0.12);
    }

    .link-chip.code {
      background: linear-gradient(180deg, #e6f8ee 0%, #cfeeda 100%);
      border-color: rgba(61, 138, 96, 0.28);
      color: #1b5a3b;
    }

    .link-chip.pdf {
      background: linear-gradient(180deg, #ffe9e2 0%, #ffd4c7 100%);
      border-color: rgba(196, 95, 60, 0.28);
      color: #8b351d;
    }

    .link-chip.supp {
      background: linear-gradient(180deg, #ebf1ff 0%, #dbe6ff 100%);
      border-color: rgba(76, 112, 194, 0.28);
      color: #294d97;
    }

    .link-chip.arxiv {
      background: linear-gradient(180deg, #f2efe9 0%, #e8e0d4 100%);
      border-color: rgba(112, 84, 52, 0.24);
      color: #5f4430;
    }

    .paper-abstract {
      margin-top: 14px;
      padding-top: 14px;
      border-top: 1px dashed rgba(76, 56, 34, 0.16);
      font-size: 14px;
      line-height: 1.8;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }

    .meta-item.award-tag {
      background: linear-gradient(180deg, #f7ecd0 0%, #f2dfb0 100%);
      border-color: rgba(154, 106, 24, 0.22);
      color: #714e10;
    }

    .meta-item.candidate-tag {
      background: linear-gradient(180deg, #f5eee1 0%, #ece1ce 100%);
      border-color: rgba(120, 96, 64, 0.18);
      color: #6e583d;
    }

    .is-hidden {
      display: none !important;
    }

    .paper-section.is-empty {
      display: none;
    }

    @media (max-width: 1080px) {
      .layout {
        grid-template-columns: 1fr;
      }

      .sidebar {
        position: static;
        max-height: none;
      }
    }

    @media (max-width: 760px) {
      .app {
        width: min(100vw - 16px, 100%);
        margin: 8px auto 18px;
      }

      .sidebar,
      .toolbar,
      .section {
        padding: 18px;
      }

      .home-hero {
        min-height: auto;
        padding: 28px 18px;
        background:
          linear-gradient(180deg, rgba(255, 250, 242, 0.99) 0%, rgba(255, 250, 242, 0.96) 54%, rgba(255, 250, 242, 0.88) 100%),
          #fffaf2;
      }

      .home-hero::after {
        inset: auto -46px 8px auto;
        width: min(78vw, 320px);
        height: min(42vw, 180px);
        opacity: 0.13;
      }

      .home-hero h1 {
        font-size: clamp(36px, 13vw, 52px);
        max-width: 9ch;
      }

      .home-lead {
        font-size: 14px;
        line-height: 1.7;
      }

      .home-actions {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .home-action {
        width: 100%;
        padding: 0 12px;
      }

      .home-search {
        flex-direction: column;
      }

      .home-search input,
      .home-search button {
        width: 100%;
      }

      .home-stats {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .home-category-grid {
        grid-template-columns: repeat(auto-fit, minmax(148px, 1fr));
      }

      .home-category-btn {
        min-height: 76px;
        padding: 12px;
      }

      .home-category-btn strong {
        font-size: 13px;
      }

      .home-quick-head {
        align-items: stretch;
        flex-direction: column;
      }

      .layout {
        min-height: 100vh;
      }

      .sidebar {
        display: none;
      }

      .toolbar-row,
      .paper-top {
        flex-direction: column;
        align-items: stretch;
      }

      .scope-row {
        align-items: flex-start;
      }

      .paper-links,
      .controls,
      .scope-row {
        justify-content: flex-start;
      }

      .controls {
        width: 100%;
      }

      .controls .mobile-level1-control {
        display: inline-flex;
        flex: 1 1 100%;
        width: 100%;
      }

      .control {
        flex: 1 1 130px;
      }

      .control select {
        width: 100%;
      }

      .code-toggle {
        flex: 1 1 96px;
        justify-content: center;
      }

      .button.small {
        flex: 0 0 42px;
      }

      .paper-card {
        padding: 14px;
        border-radius: 14px;
      }

      .paper-title {
        font-size: 17px;
      }

      .paper-links {
        margin-top: 4px;
      }

      .paper-abstract {
        font-size: 13px;
        line-height: 1.7;
      }
    }

    @media (max-width: 420px) {
      .app {
        width: min(100vw - 10px, 100%);
        margin-top: 5px;
      }

      .home-hero {
        padding: 22px 14px;
      }

      .home-hero::after {
        right: -64px;
        width: 290px;
        height: 150px;
      }

      .home-stats {
        gap: 8px;
      }

      .home-stat {
        padding: 10px;
      }

      .home-stat strong {
        font-size: 17px;
      }

      .toolbar,
      .section {
        padding: 14px;
      }

      .search-box {
        flex-basis: auto;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <section class="panel home-hero">
      <div class="home-content">
        <div class="home-kicker">CVPR 2026 Paper Explorer</div>
        <h1>@@SITE_HEADING@@</h1>
        <p class="home-lead">按研究方向整理 CVPR 2026 论文，支持标题、作者、摘要检索，也可以直接筛选代码、PDF、补充材料和 arXiv 链接。</p>
        <div class="home-actions">
          <a class="home-action primary" href="#paperBrowser">进入论文库</a>
          <button id="homeCodeBtn" class="home-action" type="button">只看代码</button>
        </div>
        <div class="home-search">
          <input id="homeSearchInput" type="text" placeholder="搜索论文、作者或关键词">
          <button id="homeSearchBtn" class="home-action primary" type="button">搜索</button>
        </div>
        <div class="home-stats">
          <div class="home-stat"><strong>@@PAPER_COUNT@@</strong><span>论文</span></div>
          <div class="home-stat"><strong>@@CATEGORY_COUNT@@</strong><span>方向</span></div>
          <div class="home-stat"><strong>@@CODE_COUNT@@</strong><span>代码链接</span></div>
          <div class="home-stat"><strong>@@AWARD_COUNT@@</strong><span>获奖/提名</span></div>
        </div>
        <p class="home-follow">关注 AI感知笔记，获取 CVPR 资讯、论文速览和学习分享。</p>
      </div>
    </section>

    <section class="panel home-quick">
      <div class="home-quick-head">
        <div>
          <h2>按方向进入</h2>
          <p>先选一个大方向，再在下方展开二级分类和论文列表。</p>
        </div>
        <a class="home-action" href="#paperBrowser">查看全部分类</a>
      </div>
      <div id="homeCategoryGrid" class="home-category-grid"></div>
    </section>

    <div id="paperBrowser" class="layout">
      <aside class="panel sidebar">
        <div id="level1List" class="level1-list"></div>
      </aside>

      <main class="main">
        <section class="panel toolbar">
          <div class="toolbar-row">
            <div class="search-box">
              <span class="search-icon">⌕</span>
              <input id="searchInput" type="text" placeholder="搜索">
            </div>
            <div class="controls">
              <div class="control mobile-level1-control">
                <select id="mobileLevel1Select" aria-label="选择方向"></select>
              </div>
              <div class="control">
                <select id="daySelect"></select>
              </div>
              <label class="code-toggle">
                <input id="codeOnlyToggle" type="checkbox">
                <span>code</span>
              </label>
              <button id="clearFiltersBtn" class="button small" aria-label="清空">×</button>
            </div>
          </div>
          <div class="scope">
            <div class="scope-row">
              <button id="clearLevel2Btn" class="button icon is-hidden" aria-label="返回">←</button>
              <div id="scopeTitle" class="scope-title"></div>
            </div>
          </div>
        </section>

        <section id="level2Section" class="panel section">
          <div id="level2Grid" class="level2-grid"></div>
        </section>

        <section id="paperSection" class="panel section paper-section">
          <div id="paperList" class="paper-list"></div>
        </section>
      </main>
    </div>
  </div>

  <script id="dataset" type="application/json">@@DATASET_JSON@@</script>
  <script>
    const DATA = JSON.parse(document.getElementById("dataset").textContent);
    const LEVEL1_META = @@LEVEL1_META_JSON@@;
    const LEVEL2_META = @@LEVEL2_META_JSON@@;
    const DEFAULT_THEME = { accent: "#1d7a8c", soft: "#dff5f8", deep: "#124f5b" };
    const collator = new Intl.Collator("en");

    const level1List = document.getElementById("level1List");
    const searchInput = document.getElementById("searchInput");
    const mobileLevel1Select = document.getElementById("mobileLevel1Select");
    const daySelect = document.getElementById("daySelect");
    const codeOnlyToggle = document.getElementById("codeOnlyToggle");
    const clearFiltersBtn = document.getElementById("clearFiltersBtn");
    const scopeTitle = document.getElementById("scopeTitle");
    const clearLevel2Btn = document.getElementById("clearLevel2Btn");
    const level2Section = document.getElementById("level2Section");
    const level2Grid = document.getElementById("level2Grid");
    const paperSection = document.getElementById("paperSection");
    const paperList = document.getElementById("paperList");
    const paperBrowser = document.getElementById("paperBrowser");
    const homeCategoryGrid = document.getElementById("homeCategoryGrid");
    const homeSearchInput = document.getElementById("homeSearchInput");
    const homeSearchBtn = document.getElementById("homeSearchBtn");
    const homeCodeBtn = document.getElementById("homeCodeBtn");
    const AWARD_RANK = {
      "Best Paper": 0,
      "Best Student Paper": 1,
      "Best Paper Honorable Mention": 2,
      "Best Student Paper Honorable Mention": 3,
      "Award Candidate": 9,
    };

    function countBy(list, field) {
      const map = new Map();
      for (const item of list) {
        const key = item[field];
        map.set(key, (map.get(key) || 0) + 1);
      }
      return map;
    }

    const LEVEL1_ORDER = Object.keys(LEVEL1_META);
    const LEVEL2_ORDER_BY_L1 = {};
    for (const level1 of LEVEL1_ORDER) {
      const subset = DATA.filter(item => item.category_level1 === level1);
      const counts = countBy(subset, "category_level2");
      LEVEL2_ORDER_BY_L1[level1] = [...new Set(subset.map(item => item.category_level2))]
        .sort((a, b) =>
          (Number(LEVEL2_META[a]?.order ?? 999) - Number(LEVEL2_META[b]?.order ?? 999))
          || (counts.get(b) || 0) - (counts.get(a) || 0)
          || collator.compare(a, b)
        );
    }
    const ALL_DAYS = [...new Set(DATA.map(item => item.day).filter(Boolean))].sort();
    const INITIAL_LEVEL1 = LEVEL1_ORDER.find(level1 => level1 !== "Awards & Nominations" && DATA.some(item => item.category_level1 === level1)) || LEVEL1_ORDER[0] || "";

    const state = {
      query: "",
      day: "",
      codeOnly: false,
      level1: INITIAL_LEVEL1,
      level2: "",
    };

    function normalize(text) {
      return String(text || "").normalize("NFKC").trim().toLowerCase();
    }

    function escapeHtml(text) {
      return String(text || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }

    function meta1(name) {
      return LEVEL1_META[name] || { cn: name, desc: "", accent: DEFAULT_THEME.accent, soft: DEFAULT_THEME.soft, deep: DEFAULT_THEME.deep };
    }

    function meta2(name) {
      return LEVEL2_META[name] || { cn: name, desc: "" };
    }

    function label1(name) {
      return meta1(name).cn || name;
    }

    function label2(name) {
      return meta2(name).cn || name;
    }

    function awardLabel(item) {
      return item.award_display || item.award_label || "";
    }

    function activeTheme() {
      if (!state.level1) {
        return DEFAULT_THEME;
      }
      return meta1(state.level1);
    }

    function applyTheme() {
      const theme = activeTheme();
      document.documentElement.style.setProperty("--accent", theme.accent || DEFAULT_THEME.accent);
      document.documentElement.style.setProperty("--accent-soft", theme.soft || DEFAULT_THEME.soft);
      document.documentElement.style.setProperty("--accent-deep", theme.deep || DEFAULT_THEME.deep);
    }

    function matchesBase(item) {
      if (state.day && item.day !== state.day) {
        return false;
      }
      if (state.codeOnly && !item.code_git) {
        return false;
      }
      const query = normalize(state.query);
      if (query && !item.search_blob.includes(query)) {
        return false;
      }
      return true;
    }

    function getBaseFiltered() {
      return DATA.filter(matchesBase);
    }

    function getLevel1Items(baseFiltered) {
      return baseFiltered.filter(item => item.category_level1 === state.level1);
    }

    function getLevel2Items(level1Items) {
      if (!state.level2) {
        return [];
      }
      return level1Items.filter(item => item.category_level2 === state.level2);
    }

    function scrollToBrowser() {
      paperBrowser.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function sortPapers(list) {
      return [...list].sort((a, b) => {
        const awardCmp = Number(AWARD_RANK[a.award_label] ?? 999) - Number(AWARD_RANK[b.award_label] ?? 999);
        if (awardCmp) {
          return awardCmp;
        }
        const dayCmp = String(b.day || "").localeCompare(String(a.day || ""));
        if (dayCmp) {
          return dayCmp;
        }
        const abstractCmp = Number(Boolean(b.abstract)) - Number(Boolean(a.abstract));
        if (abstractCmp) {
          return abstractCmp;
        }
        return collator.compare(a.title, b.title);
      });
    }

    function fillDaySelect() {
      const current = state.day;
      daySelect.innerHTML = "";
      const blank = document.createElement("option");
      blank.value = "";
      blank.textContent = "全部";
      daySelect.appendChild(blank);
      for (const day of ALL_DAYS) {
        const option = document.createElement("option");
        option.value = day;
        option.textContent = day;
        daySelect.appendChild(option);
      }
      daySelect.value = current;
    }

    function fillMobileLevel1Select(baseFiltered) {
      const counts = countBy(baseFiltered, "category_level1");
      mobileLevel1Select.innerHTML = "";
      for (const level1 of LEVEL1_ORDER) {
        const option = document.createElement("option");
        option.value = level1;
        option.textContent = `${label1(level1)} (${counts.get(level1) || 0})`;
        mobileLevel1Select.appendChild(option);
      }
      mobileLevel1Select.value = state.level1;
    }

    function renderLevel1(baseFiltered) {
      const counts = countBy(baseFiltered, "category_level1");
      level1List.innerHTML = LEVEL1_ORDER.map(level1 => {
        const meta = meta1(level1);
        const count = counts.get(level1) || 0;
        const cls = [
          "level1-btn",
          state.level1 === level1 ? "active" : "",
          count ? "" : "is-muted",
        ].filter(Boolean).join(" ");
        return `
          <button class="${cls}" data-level1="${escapeHtml(level1)}">
            <div class="level1-top">
              <div class="level1-title">${escapeHtml(meta.cn)}</div>
              <div class="level1-count">${count}</div>
            </div>
          </button>
        `;
      }).join("");
    }

    function renderHomeCategories() {
      const counts = countBy(DATA, "category_level1");
      homeCategoryGrid.innerHTML = LEVEL1_ORDER
        .filter(level1 => level1 !== "Awards & Nominations")
        .map(level1 => {
          const meta = meta1(level1);
          const count = counts.get(level1) || 0;
          return `
            <button class="home-category-btn" type="button" data-home-level1="${escapeHtml(level1)}">
              <strong>${escapeHtml(meta.cn)}</strong>
              <span>${count} papers</span>
            </button>
          `;
        }).join("");
    }

    function renderScope() {
      scopeTitle.textContent = state.level2 ? label2(state.level2) : label1(state.level1);
    }

    function renderLevel2(level1Items) {
      const order = LEVEL2_ORDER_BY_L1[state.level1] || [];
      const counts = countBy(level1Items, "category_level2");
      level2Section.classList.toggle("is-hidden", !!state.level2);

      if (!order.length) {
        level2Grid.innerHTML = "";
        return;
      }

      level2Grid.innerHTML = order.map(level2 => {
        const detail = meta2(level2);
        const count = counts.get(level2) || 0;
        const cls = [
          "level2-btn",
          state.level2 === level2 ? "active" : "",
          count ? "" : "is-muted",
        ].filter(Boolean).join(" ");
        return `
          <button class="${cls}" data-level2="${escapeHtml(level2)}">
            <div class="level2-top">
              <h3 class="level2-title">${escapeHtml(detail.cn)}</h3>
              <div class="count-pill">${count}</div>
            </div>
          </button>
        `;
      }).join("");
    }

    function paperLinks(item) {
      const links = [];
      if (item.code_git) {
        links.push(`<a class="link-chip code" target="_blank" rel="noopener noreferrer" href="${escapeHtml(item.code_git)}">code</a>`);
      }
      if (item.pdf_url) {
        links.push(`<a class="link-chip pdf" target="_blank" rel="noopener noreferrer" href="${escapeHtml(item.pdf_url)}">pdf</a>`);
      }
      if (item.supp_url) {
        links.push(`<a class="link-chip supp" target="_blank" rel="noopener noreferrer" href="${escapeHtml(item.supp_url)}">supp</a>`);
      }
      if (item.arxiv_url) {
        links.push(`<a class="link-chip arxiv" target="_blank" rel="noopener noreferrer" href="${escapeHtml(item.arxiv_url)}">arxiv</a>`);
      }
      return links.join("");
    }

    function renderPaperCards(items) {
      return items.map(item => {
        const abstract = String(item.abstract || "").trim();
        const titleUrl = item.paper_url || item.pdf_url || "";
        const metaItems = [];
        if (item.award_label) {
          const awardClass = item.award_status === "candidate" ? "candidate-tag" : "award-tag";
          metaItems.push(`<span class="meta-item award-tag ${awardClass}">${escapeHtml(awardLabel(item))}</span>`);
        }
        if (item.day) {
          metaItems.push(`<span class="meta-item">${escapeHtml(item.day)}</span>`);
        }
        const metaHtml = metaItems.length
          ? `
              <div class="paper-meta">
                <div class="meta-row">
                  ${metaItems.join("")}
                </div>
              </div>
            `
          : "";
        return `
          <article class="paper-card">
            ${metaHtml}
            <div class="paper-top">
              <div>
                <h3 class="paper-title">
                  ${titleUrl
                    ? `<a target="_blank" rel="noopener noreferrer" href="${escapeHtml(titleUrl)}">${escapeHtml(item.title)}</a>`
                    : escapeHtml(item.title)}
                </h3>
                ${item.authors ? `<p class="paper-authors">${escapeHtml(item.authors)}</p>` : ""}
              </div>
              <div class="paper-links">${paperLinks(item)}</div>
            </div>
            ${abstract ? `
              <div class="paper-abstract">${escapeHtml(abstract)}</div>
            ` : ""}
          </article>
        `;
      }).join("");
    }

    function renderPapers(level2Items) {
      paperSection.classList.toggle("is-empty", !state.level2);
      clearLevel2Btn.classList.toggle("is-hidden", !state.level2);

      if (!state.level2) {
        paperList.innerHTML = "";
        return;
      }

      const items = sortPapers(level2Items);
      paperSection.classList.remove("is-empty");

      if (!items.length) {
        paperList.innerHTML = "";
        return;
      }

      paperList.innerHTML = renderPaperCards(items);
    }

    function updateControls(baseFiltered) {
      searchInput.value = state.query;
      homeSearchInput.value = state.query;
      fillMobileLevel1Select(baseFiltered);
      fillDaySelect();
      codeOnlyToggle.checked = state.codeOnly;
    }

    function updateTitle() {
      if (state.level2) {
        document.title = `${label2(state.level2)} | @@SITE_TITLE@@`;
        return;
      }
      if (state.level1) {
        document.title = `${label1(state.level1)} | @@SITE_TITLE@@`;
        return;
      }
      document.title = "@@SITE_TITLE@@";
    }

    function render() {
      const baseFiltered = getBaseFiltered();
      if (!state.level1) {
        state.level1 = LEVEL1_ORDER[0] || "";
      }
      const level1Items = getLevel1Items(baseFiltered);
      if (state.level2 && !level1Items.some(item => item.category_level2 === state.level2)) {
        state.level2 = "";
      }

      applyTheme();
      updateControls(baseFiltered);
      updateTitle();
      renderLevel1(baseFiltered);
      renderScope();
      const level2Items = getLevel2Items(level1Items);
      renderLevel2(level1Items);
      renderPapers(level2Items);
    }

    searchInput.addEventListener("input", event => {
      state.query = event.target.value.trim();
      render();
    });

    mobileLevel1Select.addEventListener("change", event => {
      state.level1 = event.target.value;
      state.level2 = "";
      render();
    });

    daySelect.addEventListener("change", event => {
      state.day = event.target.value;
      render();
    });

    codeOnlyToggle.addEventListener("change", event => {
      state.codeOnly = event.target.checked;
      render();
    });

    clearFiltersBtn.addEventListener("click", () => {
      state.query = "";
      state.day = "";
      state.codeOnly = false;
      render();
    });

    clearLevel2Btn.addEventListener("click", () => {
      state.level2 = "";
      render();
    });

    homeSearchBtn.addEventListener("click", () => {
      state.query = homeSearchInput.value.trim();
      state.level2 = "";
      render();
      scrollToBrowser();
    });

    homeSearchInput.addEventListener("keydown", event => {
      if (event.key !== "Enter") {
        return;
      }
      state.query = homeSearchInput.value.trim();
      state.level2 = "";
      render();
      scrollToBrowser();
    });

    homeCodeBtn.addEventListener("click", () => {
      state.codeOnly = true;
      state.level2 = "";
      render();
      scrollToBrowser();
    });

    homeCategoryGrid.addEventListener("click", event => {
      const button = event.target.closest("[data-home-level1]");
      if (!button) {
        return;
      }
      state.level1 = button.dataset.homeLevel1;
      state.level2 = "";
      render();
      scrollToBrowser();
    });

    document.addEventListener("click", event => {
      const level1Btn = event.target.closest("[data-level1]");
      if (level1Btn) {
        const nextLevel1 = level1Btn.dataset.level1;
        if (nextLevel1 !== state.level1) {
          state.level1 = nextLevel1;
          state.level2 = "";
          render();
        }
        return;
      }

      const level2Btn = event.target.closest("[data-level2]");
      if (level2Btn) {
        const nextLevel2 = level2Btn.dataset.level2;
        state.level2 = state.level2 === nextLevel2 ? "" : nextLevel2;
        render();
        if (state.level2 && window.innerWidth <= 900) {
          paperSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }
        return;
      }
    });

    renderHomeCategories();
    render();
  </script>
</body>
</html>
"""


def build_dataset(rows):
    dataset = []
    for idx, row in enumerate(
        sorted(
            rows,
            key=lambda item: (
                AWARD_LABEL_ORDER.get(item.get("award_label", ""), 99),
                item.get("day", ""),
                DISPLAY_LEVEL1_BY_LEVEL2.get(item.get("category_level2", ""), item.get("category_level1", "")),
                item.get("category_level2", ""),
                item.get("title", ""),
            )
        )
    ):
        level2 = row.get("category_level2", "")
        level1 = DISPLAY_LEVEL1_BY_LEVEL2.get(level2, row.get("category_level1", ""))
        award_display = AWARD_LABEL_CN.get(row.get("award_label", ""), row.get("award_label", ""))
        dataset.append(
            {
                "id": idx,
                "day": row.get("day", ""),
                "title": row.get("title", ""),
                "authors": row.get("authors", ""),
                "abstract": row.get("abstract", ""),
                "paper_url": row.get("paper_url", ""),
                "pdf_url": row.get("pdf_url", ""),
                "supp_url": row.get("supp_url", ""),
                "arxiv_url": row.get("arxiv_url", ""),
                "code_git": row.get("code_git", ""),
                "award_status": row.get("award_status", ""),
                "award_label": row.get("award_label", ""),
                "award_display": award_display,
                "base_category_level1": row.get("base_category_level1", ""),
                "base_category_level2": row.get("base_category_level2", ""),
                "category_level1": level1,
                "category_level2": level2,
                "search_blob": " ".join(
                    [
                        row.get("title", ""),
                        row.get("authors", ""),
                        row.get("abstract", ""),
                        row.get("award_label", ""),
                        award_display,
                        row.get("base_category_level1", ""),
                        row.get("base_category_level2", ""),
                        level1,
                        level2,
                        LEVEL1_META.get(level1, {}).get("cn", ""),
                        LEVEL2_META.get(level2, {}).get("cn", ""),
                    ]
                ).lower(),
            }
        )
    return dataset


def render_html(rows):
    dataset = build_dataset(rows)
    paper_count = len(dataset)
    category_count = len({row["category_level1"] for row in dataset if row["category_level1"] != "Awards & Nominations"})
    code_count = sum(1 for row in dataset if row.get("code_git"))
    award_count = sum(1 for row in dataset if row.get("award_status"))
    public_level1_meta = {
        key: {
            "cn": value["cn"],
            "accent": value["accent"],
            "soft": value["soft"],
            "deep": value["deep"],
        }
        for key, value in LEVEL1_META.items()
    }
    public_level2_meta = {
        key: {
            "cn": value["cn"],
            "order": value.get("order", 999),
        }
        for key, value in LEVEL2_META.items()
    }

    replacements = {
        "@@SITE_TITLE@@": SITE_TITLE,
        "@@SITE_HEADING@@": SITE_TITLE,
        "@@PAPER_COUNT@@": str(paper_count),
        "@@CATEGORY_COUNT@@": str(category_count),
        "@@CODE_COUNT@@": str(code_count),
        "@@AWARD_COUNT@@": str(award_count),
        "@@LEVEL1_META_JSON@@": json.dumps(public_level1_meta, ensure_ascii=False, separators=(",", ":")),
        "@@LEVEL2_META_JSON@@": json.dumps(public_level2_meta, ensure_ascii=False, separators=(",", ":")),
        "@@DATASET_JSON@@": json.dumps(dataset, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
    }

    html = HTML_TEMPLATE
    for needle, value in replacements.items():
        html = html.replace(needle, value)
    return html


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", default=DEFAULT_YEAR)
    parser.add_argument("--input-json", type=Path)
    parser.add_argument("--output-html", type=Path)
    parser.add_argument("--site-title", default=SITE_TITLE)
    return parser.parse_args()


def main():
    global SITE_TITLE

    args = parse_args()
    SITE_TITLE = args.site_title
    data_dir = BASE_DIR / "data" / args.year
    input_json = args.input_json or (data_dir / "papers.hierarchy.json")
    output_html = args.output_html or (BASE_DIR / "index.html")

    rows = json.loads(input_json.read_text(encoding="utf-8"))
    dataset = build_dataset(rows)
    html = render_html(rows)
    output_html.write_text(html, encoding="utf-8")

    print(f"loaded {len(rows)} papers")
    print(f"saved {output_html}")
    print(f"top-level categories: {Counter(row['category_level1'] for row in dataset)}")


if __name__ == "__main__":
    main()
