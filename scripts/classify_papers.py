import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_YEAR = "2026"


TITLE_WEIGHT = 4
ABSTRACT_WEIGHT = 1
AWARD_LEVEL1 = "Awards & Nominations"
AWARD_LEVEL2_WINNERS = "Award Winners"
AWARD_LEVEL2_CANDIDATES = "Award Candidates"
REPO_URL_RE = re.compile(r"https?://[^\s)\]>\"']+")
REPO_HOSTS = (
    "github.com",
    "gitlab.com",
    "bitbucket.org",
    "gitee.com",
    "huggingface.co",
)


def normalize_text(text):
    text = unicodedata.normalize("NFKC", text or "")
    text = text.replace("\u00A0", " ")
    text = text.replace("\u2010", "-")
    text = text.replace("\u2011", "-")
    text = text.replace("\u2012", "-")
    text = text.replace("\u2013", "-")
    text = text.replace("\u2014", "-")
    text = text.replace("\u2015", "-")
    text = text.replace("\u2212", "-")
    text = text.replace("\u2043", "-")
    text = text.replace("\u2018", "'")
    text = text.replace("\u2019", "'")
    text = text.replace("\u201C", '"')
    text = text.replace("\u201D", '"')
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def patt(label, regex, title_w=1, abs_w=1):
    return {
        "label": label,
        "regex": re.compile(regex, re.I),
        "title_weight": title_w,
        "abstract_weight": abs_w,
    }


def top_candidate_text(candidate):
    signals = ", ".join(candidate["matches"][:4])
    return (
        f"{candidate['level1']} > {candidate['level2']} "
        f"({candidate['score']}: {signals})"
    )


TAXONOMY = [
    {
        "level1": "Specialized Domains",
        "level2": "Medical & Biomedical Vision",
        "priority": 10,
        "patterns": [
            patt("medical", r"\bmedical\b", 5, 1),
            patt("biomedical", r"\bbiomedical\b", 5, 1),
            patt("radiology", r"\bradiolog", 5, 1),
            patt("ct", r"\bct\b", 5, 1),
            patt("mri", r"\bmri\b", 5, 1),
            patt("xray", r"\bx[- ]?ray\b", 5, 1),
            patt("ultrasound", r"\bultrasound\b", 5, 1),
            patt("pathology", r"\bpatholog", 5, 1),
            patt("histopathology", r"\bhistopath", 5, 1),
            patt("wsi", r"\bwhole slide\b|\bwsi\b", 5, 1),
            patt("retina", r"\bretina\w*|\bfundus\b|\boct\b", 5, 1),
            patt("endoscopy", r"\bendoscop", 5, 1),
            patt("lesion", r"\blesion\b", 4, 1),
            patt("tumor", r"\btumou?r\b", 4, 1),
            patt("ecg", r"\becg\b", 5, 1),
            patt("eeg", r"\beeg\b|\bfmri\b", 5, 1),
            patt("clinical", r"\bclinical\b|\bpatient\b", 3, 1),
            patt("anatomy", r"\banatom", 3, 1),
            patt("brain disease", r"\bbrain disease\b|\balzheimer", 4, 1),
            patt("spatial transcriptomics", r"\bspatial transcriptomics\b", 4, 1),
        ],
    },
    {
        "level1": "Specialized Domains",
        "level2": "Remote Sensing & Geospatial Vision",
        "priority": 9,
        "patterns": [
            patt("remote sensing", r"\bremote sensing\b", 5, 1),
            patt("satellite", r"\bsatellite\b", 5, 1),
            patt("aerial", r"\baerial\b", 5, 1),
            patt("geospatial", r"\bgeospatial\b|\bgeo-localization\b|\bgeolocalization\b", 5, 1),
            patt("earth observation", r"\bearth observation\b", 5, 1),
            patt("overhead", r"\boverhead\b", 4, 1),
            patt("land cover", r"\bland[ -]cover\b", 4, 1),
            patt("pansharpening", r"\bpansharpen", 4, 1),
            patt("sar", r"\binsar\b|\bsar\b", 4, 1),
            patt("hyperspectral", r"\bhyperspectral\b", 2, 1),
            patt("change detection", r"\bchange detection\b", 2, 1),
        ],
    },
    {
        "level1": "Specialized Domains",
        "level2": "Scientific, Industrial & Physical Vision",
        "priority": 7,
        "patterns": [
            patt("materials", r"\bmaterial\w*\b|\bquantum\b", 3, 2),
            patt("molecule", r"\bmolecule\w*\b|\bmolecular\b|\bprotein\b", 3, 2),
            patt("microscopy", r"\bmicroscop", 3, 2),
            patt("electron microscopy", r"\belectron microscop|\bstem tomography\b", 4, 2),
            patt("manufacturing", r"\bmanufactur", 3, 2),
            patt("industrial", r"\bindustr", 3, 2),
            patt("weather", r"\bweather\b|\bmeteorolog", 3, 2),
            patt("aerodynamic", r"\baerodynamic\b|\baviation\b", 3, 2),
            patt("sonar", r"\bsonar\b", 3, 2),
            patt("radar", r"\bradar\b|\bmmwave\b", 2, 1),
            patt("construction", r"\bconstruction\b|\bblueprint", 2, 1),
            patt("electromagnetic", r"\belectromagnetic\b|\binverse scattering\b", 4, 2),
            patt("circuit", r"\bcircuit\w*\b", 3, 1),
        ],
    },
    {
        "level1": "Embodied, Driving & Robotics",
        "level2": "Autonomous Driving, BEV & Mapping",
        "priority": 8,
        "patterns": [
            patt("driving", r"\bdriving\b|\bautonomous driving\b", 4, 2),
            patt("bev", r"\bbev\b|\bbird'?s eye view\b|\bbird's-eye view\b", 4, 2),
            patt("trajectory", r"\btrajectory\b", 3, 2),
            patt("lane", r"\blane\b", 3, 2),
            patt(
                "map",
                r"\bhd map\b|\blane map\b|\bsemantic map\b|\broad map\b|\bmap generation\b|\bmapgpt\b|\bautonomous driving map",
                3,
                1,
            ),
            patt("traffic", r"\btraffic\b|\bvehicle\b|\bcar\b|\broad\b", 3, 2),
            patt("planner", r"\bplanner\b|\bplanning\b", 2, 1),
        ],
    },
    {
        "level1": "Embodied, Driving & Robotics",
        "level2": "Robotics, Manipulation & Navigation",
        "priority": 8,
        "patterns": [
            patt("robot", r"\brobot\w*\b", 4, 2),
            patt(
                "manipulation",
                r"\b(robot|robotic|object|dexterous|bimanual|hand|in-hand) manipulation\b|\bmanipulation (policy|task|skill)\b",
                4,
                2,
            ),
            patt("grasp", r"\bgrasp", 4, 2),
            patt("navigation", r"\bnavigation\b|\bnav\b", 4, 2),
            patt("uav", r"\buav\b|\bdrone\b", 3, 2),
            patt("bimanual", r"\bbimanual\b", 3, 2),
            patt("affordance", r"\baffordance\b", 3, 2),
            patt("locomotion", r"\blocomo", 3, 2),
        ],
    },
    {
        "level1": "Embodied, Driving & Robotics",
        "level2": "Embodied Agents, Policy & Control",
        "priority": 7,
        "patterns": [
            patt("embodied", r"\bembodied\b", 4, 2),
            patt("spatial intelligence", r"\b3d spatial intelligence\b|\bspatial intelligence\b", 3, 1),
            patt(
                "rl environment",
                r"\b(environment\w*|embodied|navigation|agent\w*)\b.{0,80}\breinforcement learning\b|\breinforcement learning\b.{0,80}\b(environment\w*|embodied|navigation|agent\w*)\b",
                3,
                1,
            ),
            patt("policy", r"\b(robot|navigation|manipulation|embodied|control) polic", 3, 2),
            patt("reward", r"\b(reward model|reward learning|reward attribution|visual reward)\b", 2, 1),
            patt("control", r"\b(control policy|visuomotor control|robot control|closed-loop control)\b", 3, 1),
            patt("vla", r"\bvision-language-action\b|\bvla\b", 3, 2),
            patt("agent", r"\bembodied agent\w*\b|\bvisual navigation agent\w*\b|\brobotic agent\w*\b", 2, 1),
            patt("decision", r"\bdecision[- ]making\b|\bvision[- ]physics[- ]decision\b", 2, 1),
        ],
    },
    {
        "level1": "3D Vision & Geometry",
        "level2": "Neural Rendering & Gaussian Splatting",
        "priority": 8,
        "patterns": [
            patt("gaussian splatting", r"\bgaussian splatting\b|\b3dgs\b|\bsplatting\b", 4, 2),
            patt("nerf", r"\bnerf\b|\bradiance field\b|\bneural rendering\b", 4, 2),
            patt("novel view", r"\bnovel view\b|\bview synthesis\b", 4, 2),
            patt("triplane", r"\btriplane\b", 3, 2),
            patt("4d generation", r"\b4d\b", 1, 0),
        ],
    },
    {
        "level1": "3D Vision & Geometry",
        "level2": "Reconstruction & 3D Scene Representation",
        "priority": 7,
        "patterns": [
            patt("3d reconstruction", r"\b3d reconstruction\b|\bscene reconstruction\b", 4, 2),
            patt("multiview", r"\bmulti-view\b|\bmultiview\b|\bcross-view\b", 3, 2),
            patt("point cloud", r"\bpoint cloud\b", 3, 2),
            patt("mesh", r"\bmesh\b|\bsurface reconstruction\b", 3, 2),
            patt("scene representation", r"\bscene representation\b|\b3d scene\b", 3, 2),
            patt("geometry", r"\bgeometry\b|\bgeometric\b", 2, 1),
            patt("reconstruction", r"\breconstruction\b", 2, 1),
            patt("inverse rendering", r"\binverse rendering\b|\bdifferentiable rendering\b|\blighting decomposition\b|\brelighting\b|\billumination\b", 4, 2),
            patt("shape", r"\bshape\b|\bshapes\b", 2, 1),
            patt("cad", r"\bcad\b|\bb-rep\b|\bbrep\b|\bsketch\b", 3, 1),
            patt("multi view geometry", r"\bviewing graph\b|\bfundamental matrix\b|\bquadrifocal\b|\btwo-view\b", 4, 2),
        ],
    },
    {
        "level1": "3D Vision & Geometry",
        "level2": "Depth, Pose, SLAM & Localization",
        "priority": 7,
        "patterns": [
            patt("depth", r"\bdepth\b|\bmonocular depth\b", 4, 2),
            patt("pose", r"\bpose estimation\b|\bcamera pose\b|\b6d pose\b|\b3d pose\b", 4, 2),
            patt("slam", r"\bslam\b|\bodometr", 4, 2),
            patt("localization", r"\blocalization\b|\bvisual localization\b|\bgeo-localization\b", 4, 2),
            patt("calibration", r"\bcalibration\b", 3, 2),
            patt("registration", r"\bregistration\b", 2, 1),
            patt("tof", r"\btof\b|\bi-tof\b", 3, 1),
        ],
    },
    {
        "level1": "3D Vision & Geometry",
        "level2": "Point Clouds & 3D Detection",
        "priority": 6,
        "patterns": [
            patt("3d detection", r"\b3d detection\b|\b3d object detection\b", 4, 2),
            patt("point cloud segmentation", r"\bpoint cloud segmentation\b", 4, 2),
            patt("lidar", r"\blidars?\b", 3, 2),
            patt("point cloud", r"\bpoint cloud\b", 2, 1),
            patt("voxel", r"\bvoxel\b", 2, 1),
        ],
    },
    {
        "level1": "Generation & Editing",
        "level2": "Image/Video Generation & Diffusion",
        "priority": 7,
        "patterns": [
            patt("diffusion", r"\bdiffusion\b|\bflow matching\b", 4, 2),
            patt("text to image", r"\btext[- ]to[- ]image\b", 4, 2),
            patt("text to video", r"\btext[- ]to[- ]video\b", 4, 2),
            patt("image generation", r"\bimage generation\b|\bvideo generation\b|\bgenerative\b", 3, 1),
            patt("autoregressive", r"\bautoregressive (image|video|visual|generation|diffusion|transformer)", 2, 1),
            patt("synthesis", r"\bimage synthesis\b|\bvideo synthesis\b|\bvisual synthesis\b", 2, 1),
        ],
    },
    {
        "level1": "Generation & Editing",
        "level2": "Editing, Personalization & Inpainting",
        "priority": 7,
        "patterns": [
            patt("editing", r"\bimage editing\b|\bvideo editing\b|\bediting\b", 4, 2),
            patt("inpainting", r"\binpaint", 4, 2),
            patt("personalization", r"\bpersonalization\b|\bpersonalized\b", 3, 2),
            patt("retouching", r"\bretouch", 3, 2),
            patt("style transfer", r"\bstyle transfer\b|\bstylization\b|\bstylized\b", 2, 1),
            patt("instruction guided", r"\binstruction[- ]guided\b|\binstruction based\b", 3, 1),
        ],
    },
    {
        "level1": "Generation & Editing",
        "level2": "Human, Avatar & Motion Generation",
        "priority": 6,
        "patterns": [
            patt("avatar", r"\bavatar\w*\b|\btalking (head|portrait|face)\b", 4, 2),
            patt("human motion generation", r"\bhuman motion\b|\bmotion generation\b|\bdance\b", 4, 2),
            patt("character", r"\bcharacter\b|\banimation\b", 3, 1),
            patt("pose controlled", r"\bpose-controlled\b|\bpose controlled\b", 3, 2),
            patt("sign language generation", r"\bsign language\b", 2, 1),
        ],
    },
    {
        "level1": "Generation & Editing",
        "level2": "3D, Scene Generation & World Models",
        "priority": 6,
        "patterns": [
            patt("world model", r"\bworld model\b|\bworld cognition\b", 4, 2),
            patt("3d generation", r"\b3d generation\b|\bscene generation\b|\b4d generation\b", 4, 2),
            patt("panorama generation", r"\bpanorama\b|\bimmersive scene\b", 3, 2),
            patt("simulation", r"\bsimulation\b", 2, 1),
        ],
    },
    {
        "level1": "Vision-Language & Multimodal",
        "level2": "VLM/MLLM Reasoning & Agents",
        "priority": 7,
        "patterns": [
            patt("vision language", r"\bvision[- ]language\b", 4, 2),
            patt("mllm vlm", r"\bmllms?\b|\bvlms?\b|\blvlms?\b", 4, 2),
            patt("llm", r"\bllms?\b|\blarge language model\b|\blarge multimodal\b", 3, 1),
            patt("multimodal", r"\bmultimodal\b|\bmulti-modal\b|\bmulti modal\b", 3, 1),
            patt("reasoning", r"\bvisual reasoning\b|\bmultimodal reasoning\b|\bvision[- ]language reasoning\b|\bchain[- ]of[- ]thought\b", 2, 1),
            patt("cot", r"\bcot\b", 3, 1),
            patt("agent", r"\b(mllm|vlm|multimodal|vision[- ]language) agent\w*\b|\bagent-wise\b", 2, 1),
            patt("instruction", r"\bvisual instruction\b|\bmultimodal instruction\b|\binstruction tuning\b|\binstruction following\b", 2, 1),
        ],
    },
    {
        "level1": "Vision-Language & Multimodal",
        "level2": "Grounding, Retrieval & Referring",
        "priority": 6,
        "patterns": [
            patt("grounding", r"\bgrounding\b|\bgrounded\b|\bphrase grounding\b", 4, 2),
            patt("referring", r"\breferring\b|\breferral\b", 4, 2),
            patt(
                "cross modal retrieval",
                r"\bcross-modal retrieval\b|\bimage-text retrieval\b|\bmultimodal retrieval\b|\bomni[- ]modality retrieval\b|\bomni modality retrieval\b",
                4,
                2,
            ),
            patt("retrieval", r"\bvisual retrieval\b|\bvideo retrieval\b|\bretrieval\b", 3, 1),
            patt("geo localization", r"\bgeo-localization\b|\bgeolocalization\b", 3, 2),
        ],
    },
    {
        "level1": "Vision-Language & Multimodal",
        "level2": "Documents, Charts & Structured Understanding",
        "priority": 6,
        "patterns": [
            patt("document", r"\bdocument\b|\bdoc\b", 4, 2),
            patt("chart", r"\bchart\b", 4, 2),
            patt("diagram", r"\bdiagram\b", 4, 2),
            patt("drawing", r"\bdrawing\b|\bblueprint", 4, 2),
            patt("gui", r"\bgui\b|\bandroid\b|\bscreen\b|\bweb\b", 4, 2),
            patt("ocr", r"\bocr\b|\btext recognition\b", 3, 2),
            patt("table", r"\btable\b", 3, 2),
        ],
    },
    {
        "level1": "Vision-Language & Multimodal",
        "level2": "Cross-modal Alignment & Fusion",
        "priority": 5,
        "patterns": [
            patt("cross modal", r"\bcross-modal\b|\bcross modal\b", 4, 2),
            patt("alignment", r"\balignment\b|\balign\b", 3, 1),
            patt("fusion", r"\bfusion\b", 3, 1),
            patt("modality gap", r"\bmodality gap\b", 3, 2),
            patt("image text", r"\bimage-text\b|\btext-image\b", 2, 1),
        ],
    },
    {
        "level1": "Recognition & Segmentation",
        "level2": "Detection, Open-Vocabulary & Counting",
        "priority": 6,
        "patterns": [
            patt("detection", r"\bdetection\b|\bdetector\b", 4, 2),
            patt("open vocabulary", r"\bopen[- ]vocabulary\b|\bopen set\b", 3, 2),
            patt("counting", r"\bcounting\b|\bcount\b", 3, 2),
            patt("localization", r"\blocalization\b", 2, 1),
            patt("hoi", r"\bhoi\b|\bhuman-object interaction\b", 2, 1),
        ],
    },
    {
        "level1": "Recognition & Segmentation",
        "level2": "Segmentation, Parsing & Matting",
        "priority": 6,
        "patterns": [
            patt("segmentation", r"\bsegmentation\b|\bsegment anything\b", 4, 2),
            patt("parsing", r"\bparsing\b", 4, 2),
            patt("matting", r"\bmatting\b", 4, 2),
            patt("saliency", r"\bsaliency\b|\bsalient\b", 3, 2),
            patt("camouflaged", r"\bcamoufl", 3, 2),
            patt("mask", r"\bmask\b", 1, 1),
        ],
    },
    {
        "level1": "Recognition & Segmentation",
        "level2": "Classification, Retrieval & Fine-grained Recognition",
        "priority": 5,
        "patterns": [
            patt("classification", r"\bclassification\b|\bclassifier\b", 4, 2),
            patt("fine grained", r"\bfine[- ]grained\b", 4, 2),
            patt("reid", r"\bre-id\b|\breidentification\b|\bre-identification\b", 4, 2),
            patt("recognition", r"\brecognition\b", 3, 1),
            patt("retrieval", r"\bretrieval\b", 2, 1),
            patt("anomaly", r"\banomaly detection\b|\b3d anomaly\b|\banomaly\b|\bdefect", 5, 2),
        ],
    },
    {
        "level1": "Video & Motion",
        "level2": "Video Understanding & Temporal Reasoning",
        "priority": 6,
        "patterns": [
            patt("video understanding", r"\bvideo understanding\b|\blong video\b|\bvideo qa\b", 4, 2),
            patt("temporal reasoning", r"\btemporal reasoning\b|\btemporal grounding\b|\bmoment retrieval\b", 4, 2),
            patt("video", r"\bvideo\b", 2, 1),
            patt("temporal", r"\btemporal\b|\blong[- ]term\b|\bstreaming\b", 2, 1),
            patt("action quality", r"\baction quality\b|\baction assessment\b", 3, 2),
        ],
    },
    {
        "level1": "Video & Motion",
        "level2": "Tracking, Flow & Correspondence",
        "priority": 6,
        "patterns": [
            patt("tracking", r"\btracking\b|\btracker\b", 4, 2),
            patt("optical flow", r"\boptical flow\b|\bscene flow\b|\bflow estimation\b", 4, 2),
            patt("correspondence", r"\bcorrespondence\b|\bmatching\b", 3, 2),
            patt("registration", r"\bregistration\b", 2, 1),
        ],
    },
    {
        "level1": "Video & Motion",
        "level2": "Pose, Motion & Action Analysis",
        "priority": 6,
        "patterns": [
            patt("pose", r"\bpose\b", 4, 2),
            patt("motion capture", r"\bmotion capture\b|\bmocap\b", 4, 2),
            patt("human motion tracking", r"\bhuman motion tracking\b|\bmotion tracking\b|\bdiffusion poser\b", 5, 2),
            patt("human motion", r"\bhuman motion\b|\bmotion analysis\b", 3, 2),
            patt("action recognition", r"\baction recognition\b|\baction\b", 3, 1),
            patt("gait", r"\bgait\b", 3, 2),
            patt("gesture", r"\bgesture\b", 3, 2),
            patt("sign language", r"\bsign language\b", 3, 2),
        ],
    },
    {
        "level1": "Low-Level Vision & Imaging",
        "level2": "Restoration, Enhancement & Super-Resolution",
        "priority": 6,
        "patterns": [
            patt("super resolution", r"\bsuper[- ]resolution\b", 4, 2),
            patt("restoration", r"\brestoration\b", 4, 2),
            patt("deblur", r"\bdeblur", 4, 2),
            patt("denoise", r"\bdenois", 4, 2),
            patt("low light", r"\blow[- ]light\b|\bnight\b", 4, 2),
            patt("enhancement", r"\benhanc", 3, 2),
            patt("dehaze", r"\bdehaze\b|\bhaze\b", 3, 2),
            patt("derain", r"\bderain\b|\brain\b", 3, 2),
            patt("image fusion", r"\bimage fusion\b|\bfusion\b", 2, 1),
            patt("color", r"\bcolor constancy\b|\bwhite[- ]balance\b|\bcolor correction\b|\bcolor enhancement\b", 5, 2),
            patt("reflection removal", r"\breflection removal\b|\bshadow removal\b", 4, 2),
            patt("intrinsic image", r"\bintrinsic\b|\breflectance\b|\bshading\b", 3, 2),
        ],
    },
    {
        "level1": "Low-Level Vision & Imaging",
        "level2": "Computational Imaging & Sensors",
        "priority": 6,
        "patterns": [
            patt("raw", r"\braw\b", 4, 2),
            patt("hdr", r"\bhdr\b", 4, 2),
            patt("burst", r"\bburst\b", 3, 2),
            patt("event camera", r"\bevent camera\b|\bevent-based\b|\bevent based\b", 4, 2),
            patt("spike camera", r"\bspike\b", 4, 2),
            patt("fisheye", r"\bfisheye\b", 4, 2),
            patt("polarization", r"\bpolariz", 4, 2),
            patt("compressive imaging", r"\bcompressive imaging\b|\bsnapshot\b", 3, 2),
            patt("non uniform sampling", r"\bnon-uniform sampling\b", 3, 2),
            patt("imaging", r"\bcomputational imaging\b|\bimaging\b", 2, 1),
            patt("event stream", r"\bevent stream\b", 4, 2),
            patt("optics", r"\blens\b|\boptics\b|\bray tracing\b", 3, 2),
            patt("tof", r"\btof\b|\bi-tof\b", 4, 2),
        ],
    },
    {
        "level1": "Low-Level Vision & Imaging",
        "level2": "Compression & Quality Assessment",
        "priority": 5,
        "patterns": [
            patt("compression", r"\bcompression\b|\bcompressed\b|\bcodec\b", 4, 2),
            patt("quality assessment", r"\bquality assessment\b|\bimage quality\b|\bvideo quality\b", 4, 2),
            patt("jpeg", r"\bjpeg\b", 3, 2),
            patt("rate distortion", r"\brate-distortion\b|\bbitrate\b", 3, 2),
        ],
    },
    {
        "level1": "Learning, Efficiency & Trustworthiness",
        "level2": "Self-/Weak-/Semi-Supervised Learning",
        "priority": 5,
        "patterns": [
            patt("self supervised", r"\bself-supervised\b|\bself supervised\b", 4, 2),
            patt("semi supervised", r"\bsemi-supervised\b|\bsemi supervised\b", 4, 2),
            patt("weakly supervised", r"\bweakly-supervised\b|\bweakly supervised\b", 4, 2),
            patt("unsupervised", r"\bunsupervised\b", 4, 2),
            patt("few shot", r"\bfew-shot\b|\bfew shot\b", 3, 2),
            patt("zero shot", r"\bzero-shot\b|\bzero shot\b", 3, 2),
            patt("representation learning", r"\brepresentation learning\b|\brepresentation\b", 2, 1),
            patt("pretraining", r"\bpretraining\b|\bpre-training\b", 3, 2),
            patt("foundation model", r"\bfoundation model\b|\bfoundation vision\b", 3, 1),
        ],
    },
    {
        "level1": "Learning, Efficiency & Trustworthiness",
        "level2": "Adaptation, Continual & Federated Learning",
        "priority": 5,
        "patterns": [
            patt("domain adaptation", r"\bdomain adaptation\b|\bsource-free\b", 4, 2),
            patt("test time adaptation", r"\btest-time\b|\btest time\b", 4, 2),
            patt("continual learning", r"\bcontinual\b|\bincremental learning\b|\bclass incremental\b", 4, 2),
            patt("federated learning", r"\bfederated\b", 4, 2),
            patt("transfer learning", r"\btransfer\b|\badaptation\b", 2, 1),
            patt("generalization", r"\bgeneralization\b|\bdomain generalization\b", 3, 2),
            patt("model merging", r"\bmodel merging\b|\bmerging\b", 3, 2),
        ],
    },
    {
        "level1": "Learning, Efficiency & Trustworthiness",
        "level2": "Efficiency, Distillation, Pruning & NAS",
        "priority": 5,
        "patterns": [
            patt("efficient", r"\befficient\b|\befficiency\b|\breal-time\b|\breal time\b", 1, 1),
            patt("distillation", r"\bdistillation\b|\bdistill\b", 4, 2),
            patt("pruning", r"\bpruning\b|\bprune\b|\btoken pruning\b", 4, 2),
            patt("quantization", r"\bquantization\b|\bquantized\b", 4, 2),
            patt("compression", r"\bcompression\b|\bsparsification\b|\bsparse\b", 3, 1),
            patt("nas", r"\bneural architecture search\b|\bnas\b", 4, 2),
            patt("lora", r"\blora\b|\badapter\b|\blow-rank\b", 3, 2),
            patt("acceleration", r"\baccelerat", 3, 1),
            patt("decoding", r"\bdecoding\b|\bspeculative\b", 2, 1),
        ],
    },
    {
        "level1": "Learning, Efficiency & Trustworthiness",
        "level2": "Robustness, Safety, Privacy & Security",
        "priority": 6,
        "patterns": [
            patt("ood", r"\bood\b|\bout-of-distribution\b", 4, 2),
            patt("adversarial", r"\badversarial\b|\bevasion attack\b", 4, 2),
            patt("backdoor", r"\bbackdoor\b", 4, 2),
            patt("privacy", r"\bprivacy\b", 4, 2),
            patt("fairness", r"\bfairness\b|\bbias\b|\bdebias", 4, 2),
            patt("safety", r"\bsafety\b|\btrustworthy\b", 4, 2),
            patt("hallucination", r"\bhallucination\b", 4, 2),
            patt("watermark", r"\bwatermark\b", 4, 2),
            patt("deepfake", r"\bdeepfake\b|\bforensic\b|\bai-generated\b", 4, 2),
            patt("concept erasure", r"\bconcept erasure\b|\berasure\b", 3, 2),
            patt("robustness", r"\brobust\b|\brobustness\b", 2, 1),
            patt("unlearning", r"\bunlearning\b", 3, 2),
        ],
    },
]


def score_rule(rule, title_text, abstract_text):
    score = 0
    matched = []
    title_hits = 0
    abstract_hits = 0
    for pattern in rule["patterns"]:
        title_hit = pattern["regex"].search(title_text)
        abs_hit = pattern["regex"].search(abstract_text)
        if title_hit and pattern["title_weight"]:
            score += pattern["title_weight"] * TITLE_WEIGHT
            title_hits += 1
            matched.append(f"title:{pattern['label']}")
        elif abs_hit and pattern["abstract_weight"]:
            score += pattern["abstract_weight"] * ABSTRACT_WEIGHT
            abstract_hits += 1
            matched.append(f"abstract:{pattern['label']}")
    return score, matched, title_hits, abstract_hits


def confidence_for(best, runner_up):
    margin = best["score"] - (runner_up["score"] if runner_up else 0)
    if best["score"] >= 24 and margin >= 6:
        return "high"
    if best["score"] >= 16 and margin >= 8:
        return "high"
    if best["score"] >= 12 and margin >= 3:
        return "medium"
    return "low"


def fallback_rule(title_text, abstract_text):
    text = f"{title_text} {abstract_text}"
    if "video" in title_text or "temporal" in title_text:
        return (
            "Video & Motion",
            "Video Understanding & Temporal Reasoning",
            ["fallback:video"],
        )
    if "diffusion" in text or "generation" in title_text or "editing" in title_text:
        return (
            "Generation & Editing",
            "Image/Video Generation & Diffusion",
            ["fallback:generation"],
        )
    if "gaussian splatting" in text or "3d" in title_text or "reconstruction" in title_text:
        return (
            "3D Vision & Geometry",
            "Reconstruction & 3D Scene Representation",
            ["fallback:3d"],
        )
    if "vision-language" in text or "multimodal" in text or "mllm" in text or "vlm" in text:
        return (
            "Vision-Language & Multimodal",
            "VLM/MLLM Reasoning & Agents",
            ["fallback:multimodal"],
        )
    if "restoration" in text or "super-resolution" in text or "low-light" in text:
        return (
            "Low-Level Vision & Imaging",
            "Restoration, Enhancement & Super-Resolution",
            ["fallback:low-level"],
        )
    if "driving" in text or "robot" in text or "navigation" in text:
        return (
            "Embodied, Driving & Robotics",
            "Robotics, Manipulation & Navigation",
            ["fallback:robotics"],
        )
    if "self-supervised" in text or "adaptation" in text or "efficient" in text:
        return (
            "Learning, Efficiency & Trustworthiness",
            "Self-/Weak-/Semi-Supervised Learning",
            ["fallback:learning"],
        )
    return (
        "Recognition & Segmentation",
        "Classification, Retrieval & Fine-grained Recognition",
        ["fallback:recognition"],
    )


def classify_row(row):
    title_text = normalize_text(row.get("title", ""))
    abstract_text = normalize_text(row.get("abstract", ""))

    candidates = []

    for rule in TAXONOMY:
        score, matches, title_hits, abstract_hits = score_rule(rule, title_text, abstract_text)
        if matches:
            candidates.append(
                {
                    "level1": rule["level1"],
                    "level2": rule["level2"],
                    "priority": rule["priority"],
                    "score": score,
                    "matches": matches,
                    "title_hits": title_hits,
                    "abstract_hits": abstract_hits,
                }
            )

    candidates.sort(
        key=lambda item: (
            item["score"],
            item["priority"],
            item["title_hits"],
            len(item["matches"]),
        ),
        reverse=True,
    )

    if not candidates:
        level1, level2, matches = fallback_rule(title_text, abstract_text)
        return {
            "level1": level1,
            "level2": level2,
            "score": 0,
            "matches": matches,
            "confidence": "low",
            "margin": 0,
            "alternatives": "",
        }

    best = candidates[0]
    runner_up = candidates[1] if len(candidates) > 1 else None
    return {
        "level1": best["level1"],
        "level2": best["level2"],
        "score": best["score"],
        "matches": best["matches"],
        "confidence": confidence_for(best, runner_up),
        "margin": best["score"] - (runner_up["score"] if runner_up else 0),
        "alternatives": " | ".join(top_candidate_text(item) for item in candidates[1:4]),
    }


def extract_code_git(text):
    for url in REPO_URL_RE.findall(text or ""):
        clean = url.rstrip(".,;:!?)\\]\"'")
        low = clean.lower()
        if any(host in low for host in REPO_HOSTS):
            return clean
    return ""


def load_awards(awards_json):
    data = json.loads(awards_json.read_text(encoding="utf-8"))
    winner_map = {
        row["title"]: row["award_label"]
        for row in data.get("winner_entries", [])
    }
    candidate_titles = set(data.get("candidate_titles", []))
    return winner_map, candidate_titles


def taxonomy_level2_map():
    return {rule["level2"]: rule["level1"] for rule in TAXONOMY}


def load_category_overrides(overrides_json):
    if not overrides_json or not overrides_json.exists():
        return {}

    data = json.loads(overrides_json.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        entries = data.get("overrides", data)
    else:
        entries = data

    level2_to_level1 = taxonomy_level2_map()
    overrides = {}
    invalid = []

    if isinstance(entries, dict):
        iterable = []
        for title, value in entries.items():
            if isinstance(value, str):
                iterable.append({"title": title, "category_level2": value})
            else:
                row = dict(value)
                row.setdefault("title", title)
                iterable.append(row)
    else:
        iterable = entries

    for entry in iterable:
        title = str(entry.get("title", "")).strip()
        level2 = str(entry.get("category_level2", "")).strip()
        level1 = str(entry.get("category_level1", "")).strip() or level2_to_level1.get(level2, "")
        if not title or level2 not in level2_to_level1 or level1 != level2_to_level1[level2]:
            invalid.append(title or level2 or "<blank>")
            continue
        overrides[title] = {
            "category_level1": level1,
            "category_level2": level2,
            "source": entry.get("source", "override"),
            "reason": entry.get("reason", ""),
        }

    if invalid:
        print(f"ignored {len(invalid)} invalid category overrides")
    return overrides


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", default=DEFAULT_YEAR)
    parser.add_argument("--input-json", type=Path)
    parser.add_argument("--awards-json", type=Path)
    parser.add_argument("--overrides-json", type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-csv", type=Path)
    parser.add_argument("--out-summary-csv", type=Path)
    return parser.parse_args()


def main():
    args = parse_args()
    data_dir = BASE_DIR / "data" / args.year
    input_json = args.input_json or (data_dir / "papers.json")
    awards_json = args.awards_json or (data_dir / "awards.json")
    overrides_json = args.overrides_json or (data_dir / "category_overrides.json")
    out_json = args.out_json or (data_dir / "papers.hierarchy.json")
    out_csv = args.out_csv or (data_dir / "papers.hierarchy.csv")
    out_summary_csv = args.out_summary_csv or (data_dir / "papers.hierarchy.summary.csv")

    rows = json.loads(input_json.read_text(encoding="utf-8"))
    winner_map, candidate_titles = load_awards(awards_json)
    category_overrides = load_category_overrides(overrides_json)

    classified_rows = []
    summary = Counter()
    summary_l1 = Counter()
    samples = defaultdict(list)

    for row in rows:
        category = classify_row(row)
        base_level1 = category["level1"]
        base_level2 = category["level2"]
        score = category["score"]
        matches = category["matches"]
        title = row.get("title", "")
        override = category_overrides.get(title)
        if override:
            base_level1 = override["category_level1"]
            base_level2 = override["category_level2"]
            score = category["score"]
            matches = [f"{override['source']}:category"]
        award_label = ""
        award_status = ""
        level1 = base_level1
        level2 = base_level2
        if title in winner_map:
            award_label = winner_map[title]
            award_status = "winner"
            level1 = AWARD_LEVEL1
            level2 = AWARD_LEVEL2_WINNERS
        elif title in candidate_titles:
            award_label = "Award Candidate"
            award_status = "candidate"
            level1 = AWARD_LEVEL1
            level2 = AWARD_LEVEL2_CANDIDATES
        out_row = dict(row)
        out_row["code_git"] = extract_code_git(row.get("abstract", ""))
        out_row["award_status"] = award_status
        out_row["award_label"] = award_label
        out_row["base_category_level1"] = base_level1
        out_row["base_category_level2"] = base_level2
        out_row["category_level1"] = level1
        out_row["category_level2"] = level2
        out_row["category_score"] = score
        out_row["category_confidence"] = category["confidence"]
        out_row["category_margin"] = category["margin"]
        out_row["category_signals"] = "; ".join(matches[:8])
        out_row["category_alternatives"] = category["alternatives"]
        classified_rows.append(out_row)
        summary[(level1, level2)] += 1
        summary_l1[level1] += 1
        if len(samples[(level1, level2)]) < 3:
            samples[(level1, level2)].append(row.get("title", ""))

    out_json.parent.mkdir(parents=True, exist_ok=True)

    with out_json.open("w", encoding="utf-8") as f:
        json.dump(classified_rows, f, ensure_ascii=False, indent=2)

    fieldnames = [
        "day",
        "title",
        "authors",
        "abstract",
        "abstract_source",
        "paper_url",
        "pdf_url",
        "supp_url",
        "arxiv_url",
        "code_git",
        "bibtex",
        "award_status",
        "award_label",
        "base_category_level1",
        "base_category_level2",
        "category_level1",
        "category_level2",
        "category_score",
        "category_confidence",
        "category_margin",
        "category_signals",
        "category_alternatives",
    ]
    with out_csv.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(classified_rows)

    with out_summary_csv.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "category_level1",
                "category_level2",
                "paper_count",
                "sample_titles",
            ],
        )
        writer.writeheader()
        for (level1, level2), count in sorted(
            summary.items(),
            key=lambda item: (-item[1], item[0][0], item[0][1]),
        ):
            writer.writerow(
                {
                    "category_level1": level1,
                    "category_level2": level2,
                    "paper_count": count,
                    "sample_titles": " | ".join(samples[(level1, level2)]),
                }
            )

    print(f"classified {len(classified_rows)} papers")
    print("top-level summary:")
    for level1, count in summary_l1.most_common():
        print(f"  {level1}: {count}")
    print(f"saved {out_csv}")
    print(f"saved {out_summary_csv}")
    print(f"saved {out_json}")


if __name__ == "__main__":
    main()
