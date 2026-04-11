# TerraLens — Detailed Implementation Plan

## What We're Building
A full-stack web app: upload one or two satellite images → get land use classification
(CNN_LeakyReLU_Skip, 93.16%), Grad-CAM heatmap explaining the prediction, and a
pixel-level change detection map comparing two time steps.

---

## Existing Code Summary

**Best model: `CNN_LeakyReLU_Skip`** (notebook Cell 49)
- Architecture: conv1 (3→16) → conv2 (16→32) → pool → conv3 (32→64) → pool → 5 residual blocks (64→64) → flatten → fc1 (64*16*16→128) → fc2 (128→10)
- Activation: LeakyReLU(0.1) throughout
- Input: 64×64 RGB images
- Training: SGD + Momentum (α=0.9), weight decay (β=0.0001), lr=0.001, batch=16, 20 epochs
- Custom cross-entropy loss (log-softmax based)

**EuroSAT Classes (10):**
```
0: AnnualCrop   1: Forest   2: HerbaceousVegetation   3: Highway
4: Industrial   5: Pasture  6: PermanentCrop           7: Residential
8: River        9: SeaLake
```

**Dataset normalization:** computed per-channel from EuroSAT (must be saved alongside model checkpoint)

---

## Project Structure

```
terralens/
├── backend/
│   ├── main.py                  # FastAPI app + all endpoints
│   ├── model.py                 # CNN_LeakyReLU_Skip class (copied from notebook)
│   ├── gradcam.py               # GradCAM class with hooks
│   ├── change_detection.py      # detect_change(), categorize_transition()
│   ├── inference.py             # preprocess_image(), run_inference(), tile_image()
│   ├── requirements.txt
│   └── checkpoints/
│       └── best_model.pth       # saved from Colab (includes mean/std/classes)
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── MapView.jsx          # Leaflet map
│   │   │   ├── ImageUpload.jsx      # Before/After drag-drop
│   │   │   ├── ResultPanel.jsx      # Classification results + probability bars
│   │   │   ├── GradCAMOverlay.jsx   # Toggle heatmap over image
│   │   │   └── ChangeMap.jsx        # Color-coded diff map + slider
│   │   ├── api/
│   │   │   └── terralens.js         # axios API calls
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── model_export/
    └── export_model.py          # Run in Colab to save checkpoint
```

---

## Phase 1 — Model Export (Run in Colab)

**File: `model_export/export_model.py`**

After training `CNN_LeakyReLU_Skip`, save everything needed for inference:

```python
checkpoint = {
    'model_state_dict': model.state_dict(),
    'classes': full_dataset.classes,   # ['AnnualCrop', 'Forest', ...]
    'mean': mean.tolist(),              # per-channel normalization mean
    'std': std.tolist(),                # per-channel normalization std
    'input_size': 64,
    'architecture': 'CNN_LeakyReLU_Skip'
}
torch.save(checkpoint, 'best_model.pth')
```

Download `best_model.pth` and place in `backend/checkpoints/`.

**Critical:** The mean/std computed in Cell 7 of the notebook must be saved here. Without them, inference normalization will be wrong.

---

## Phase 2 — Backend (FastAPI)

### 2.1 `backend/model.py` — Model Definition

Exact copy of `CNN_LeakyReLU_Skip` from notebook Cell 49. No changes.

```python
import torch
import torch.nn as nn

class CNN_LeakyReLU_Skip(nn.Module):
    def __init__(self):
        super().__init__()
        self.act = nn.LeakyReLU(0.1)
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.res_blocks = nn.ModuleList([
            nn.Sequential(
                nn.Conv2d(64, 64, 3, padding=1),
                nn.LeakyReLU(0.1),
                nn.Conv2d(64, 64, 3, padding=1)
            ) for _ in range(5)
        ])
        self.fc1 = nn.Linear(64 * 16 * 16, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.act(self.conv1(x))
        x = self.act(self.conv2(x))
        x = self.pool(x)
        x = self.act(self.conv3(x))
        x = self.pool(x)
        for block in self.res_blocks:
            identity = x
            out = block(x)
            x = self.act(out + identity)
        x = x.view(x.size(0), -1)
        x = self.act(self.fc1(x))
        x = self.fc2(x)
        return x
```

### 2.2 `backend/gradcam.py` — Grad-CAM

Hook target: **last residual block** (`model.res_blocks[-1]`), which is a `nn.Sequential`.
This gives the richest feature maps — better than hooking `conv3` because it's after all skip connections.

```python
import torch
import torch.nn.functional as F
import numpy as np
import cv2

class GradCAM:
    def __init__(self, model):
        self.model = model
        self.gradients = None
        self.activations = None

        # Hook the LAST residual block (index 4 of res_blocks)
        target_layer = model.res_blocks[-1]
        target_layer.register_forward_hook(self._save_activation)
        target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, input, output):
        self.activations = output.detach()

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate(self, input_tensor, class_idx=None):
        """
        input_tensor: (1, 3, 64, 64) normalized tensor
        class_idx: None → use predicted class
        Returns: numpy array (64, 64) in [0, 1]
        """
        self.model.eval()
        output = self.model(input_tensor)

        if class_idx is None:
            class_idx = output.argmax(dim=1).item()

        self.model.zero_grad()
        output[0, class_idx].backward()

        # Global average pooling of gradients
        weights = self.gradients.mean(dim=[2, 3], keepdim=True)  # (1, 64, 1, 1)
        cam = (weights * self.activations).sum(dim=1).squeeze()   # (16, 16)
        cam = torch.relu(cam)

        # Normalize to [0, 1]
        cam_min, cam_max = cam.min(), cam.max()
        if cam_max > cam_min:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = torch.zeros_like(cam)

        # Upsample to 64x64 to match input
        cam_np = cam.cpu().numpy()
        cam_resized = cv2.resize(cam_np, (64, 64), interpolation=cv2.INTER_LINEAR)
        return cam_resized  # shape (64, 64), values in [0, 1]

def overlay_heatmap(original_rgb_np, cam, alpha=0.5):
    """
    original_rgb_np: (64, 64, 3) uint8
    cam: (64, 64) float in [0, 1]
    Returns: (64, 64, 3) uint8 blended image
    """
    import matplotlib.cm as cm
    colormap = cm.get_cmap('jet')
    heatmap = colormap(cam)[:, :, :3]                    # (64, 64, 3) float
    heatmap = (heatmap * 255).astype(np.uint8)
    blended = (alpha * heatmap + (1 - alpha) * original_rgb_np).astype(np.uint8)
    return blended
```

### 2.3 `backend/change_detection.py` — Change Detection

```python
import numpy as np

# EuroSAT class indices
VEGETATION_CLASSES = {0, 1, 2, 5, 6}   # AnnualCrop, Forest, Herbaceous, Pasture, PermanentCrop
URBAN_CLASSES = {4, 7}                   # Industrial, Residential
WATER_CLASSES = {8, 9}                   # River, SeaLake
INFRASTRUCTURE_CLASSES = {3}             # Highway

def detect_change(probs_t1, probs_t2, threshold=0.3):
    """
    probs_t1, probs_t2: (H, W, 10) softmax probability arrays over a tiled image
    Returns:
        change_mask: (H, W) bool
        change_labels: (H, W) str — 'urbanization', 'deforestation', 'reforestation',
                                    'flooding', 'drought', 'other', 'no_change'
        diff_map: (H, W) float in [0, 1] — magnitude of change
    """
    diff = np.abs(probs_t2 - probs_t1).max(axis=-1)  # (H, W)
    change_mask = diff > threshold

    pred_t1 = probs_t1.argmax(axis=-1)  # (H, W)
    pred_t2 = probs_t2.argmax(axis=-1)

    change_labels = np.full(pred_t1.shape, 'no_change', dtype=object)

    changed = change_mask
    was_vegetation = np.isin(pred_t1, list(VEGETATION_CLASSES))
    now_urban      = np.isin(pred_t2, list(URBAN_CLASSES))
    was_urban      = np.isin(pred_t1, list(URBAN_CLASSES))
    now_vegetation = np.isin(pred_t2, list(VEGETATION_CLASSES))
    was_water      = np.isin(pred_t1, list(WATER_CLASSES))
    now_water      = np.isin(pred_t2, list(WATER_CLASSES))

    change_labels[changed & was_vegetation & now_urban]      = 'urbanization'
    change_labels[changed & was_urban & now_vegetation]      = 'reforestation'
    change_labels[changed & ~was_water & now_water]          = 'flooding'
    change_labels[changed & was_water & ~now_water]          = 'drought'
    change_labels[changed & ~np.isin(change_labels, [
        'urbanization', 'reforestation', 'flooding', 'drought'])] = 'other'

    return change_mask, change_labels, diff

# Color map for rendering: category → RGB
CHANGE_COLORS = {
    'urbanization':   [255,  60,  60],   # red
    'reforestation':  [ 60, 200,  60],   # green
    'flooding':       [ 60, 100, 255],   # blue
    'drought':        [200, 160,  40],   # orange-brown
    'other':          [180, 180, 180],   # gray
    'no_change':      [  0,   0,   0],   # black (transparent in UI)
}

def render_change_map(change_labels, change_mask):
    """Returns (H, W, 4) RGBA numpy array for the change map overlay."""
    H, W = change_labels.shape
    rgba = np.zeros((H, W, 4), dtype=np.uint8)
    for label, color in CHANGE_COLORS.items():
        mask = (change_labels == label) & change_mask
        rgba[mask, :3] = color
        rgba[mask, 3] = 200  # semi-transparent
    return rgba
```

### 2.4 `backend/inference.py` — Preprocessing + Inference

```python
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import io
import base64

def get_transform(mean, std):
    return transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])

def image_to_tensor(image_bytes, transform):
    """image_bytes: raw bytes from upload → (1, 3, 64, 64) tensor"""
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    tensor = transform(img).unsqueeze(0)  # add batch dim
    return tensor, img

def run_inference(model, tensor, classes):
    """Returns (class_name, confidence, all_probabilities_dict)"""
    model.eval()
    with torch.no_grad():
        logits = model(tensor)
        probs = F.softmax(logits, dim=1).squeeze()
    
    pred_idx = probs.argmax().item()
    return {
        'class': classes[pred_idx],
        'confidence': float(probs[pred_idx]),
        'probabilities': {classes[i]: float(probs[i]) for i in range(len(classes))}
    }

def tile_image_for_change_detection(image_bytes, transform, model, classes):
    """
    Divides a larger image into 64x64 patches and returns a (H_tiles, W_tiles, 10)
    probability map. Falls back to single patch if image is already 64x64.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    W, H = img.size
    tile_size = 64
    
    cols = max(1, W // tile_size)
    rows = max(1, H // tile_size)
    
    prob_map = np.zeros((rows, cols, 10))
    
    model.eval()
    with torch.no_grad():
        for r in range(rows):
            for c in range(cols):
                left   = c * tile_size
                top    = r * tile_size
                right  = min(left + tile_size, W)
                bottom = min(top + tile_size, H)
                patch = img.crop((left, top, right, bottom))
                tensor = transform(patch).unsqueeze(0)
                logits = model(tensor)
                probs = F.softmax(logits, dim=1).squeeze().numpy()
                prob_map[r, c] = probs
    
    return prob_map

def numpy_to_base64_png(arr_uint8):
    """arr_uint8: HxWx3 or HxWx4 numpy array → base64 string"""
    img = Image.fromarray(arr_uint8)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode()
```

### 2.5 `backend/main.py` — FastAPI App

**Endpoints:**

| Method | Path | Input | Output |
|--------|------|-------|--------|
| GET | `/` | — | health check |
| GET | `/classes` | — | list of 10 class names |
| POST | `/classify` | form: `image` (file) | `{class, confidence, probabilities}` |
| POST | `/gradcam` | form: `image` (file) | `{class, confidence, gradcam_b64, overlay_b64}` |
| POST | `/compare` | form: `image_t1`, `image_t2` (files) | `{t1_result, t2_result, change_map_b64, summary}` |

```python
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import torch
import numpy as np
import cv2
from model import CNN_LeakyReLU_Skip
from gradcam import GradCAM, overlay_heatmap
from change_detection import detect_change, render_change_map
from inference import (get_transform, image_to_tensor, run_inference,
                       tile_image_for_change_detection, numpy_to_base64_png)

app = FastAPI(title="TerraLens API")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# --- Load model once at startup ---
checkpoint = torch.load('checkpoints/best_model.pth', map_location='cpu')
model = CNN_LeakyReLU_Skip()
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

CLASSES = checkpoint['classes']
MEAN    = checkpoint['mean']
STD     = checkpoint['std']
transform = get_transform(MEAN, STD)
gradcam   = GradCAM(model)

@app.get("/classes")
def get_classes():
    return {"classes": CLASSES}

@app.post("/classify")
async def classify(image: UploadFile = File(...)):
    image_bytes = await image.read()
    tensor, _ = image_to_tensor(image_bytes, transform)
    result = run_inference(model, tensor, CLASSES)
    return result

@app.post("/gradcam")
async def get_gradcam(image: UploadFile = File(...)):
    image_bytes = await image.read()
    tensor, pil_img = image_to_tensor(image_bytes, transform)
    result = run_inference(model, tensor, CLASSES)
    
    # Clone tensor so backward doesn't interfere
    tensor_grad = tensor.clone().requires_grad_(True)
    cam = gradcam.generate(tensor_grad)

    # Build overlay on original (denormalized) image
    orig_np = np.array(pil_img.resize((64, 64))).astype(np.uint8)
    overlay = overlay_heatmap(orig_np, cam)

    # Heatmap alone (colored)
    import matplotlib.cm as cm
    heatmap_colored = (cm.get_cmap('jet')(cam)[:, :, :3] * 255).astype(np.uint8)

    return {
        **result,
        'gradcam_b64':  numpy_to_base64_png(heatmap_colored),
        'overlay_b64':  numpy_to_base64_png(overlay),
        'original_b64': numpy_to_base64_png(orig_np),
    }

@app.post("/compare")
async def compare(image_t1: UploadFile = File(...), image_t2: UploadFile = File(...)):
    bytes_t1 = await image_t1.read()
    bytes_t2 = await image_t2.read()

    # Single-patch classification for display
    tensor_t1, _ = image_to_tensor(bytes_t1, transform)
    tensor_t2, _ = image_to_tensor(bytes_t2, transform)
    result_t1 = run_inference(model, tensor_t1, CLASSES)
    result_t2 = run_inference(model, tensor_t2, CLASSES)

    # Tile-based probability maps for change detection
    prob_t1 = tile_image_for_change_detection(bytes_t1, transform, model, CLASSES)
    prob_t2 = tile_image_for_change_detection(bytes_t2, transform, model, CLASSES)

    change_mask, change_labels, diff_map = detect_change(prob_t1, prob_t2)
    change_rgba = render_change_map(change_labels, change_mask)

    # Upscale change map to 256x256 for display
    change_display = cv2.resize(change_rgba, (256, 256), interpolation=cv2.INTER_NEAREST)

    # Summary stats
    unique, counts = np.unique(change_labels[change_mask], return_counts=True)
    summary = {str(k): int(v) for k, v in zip(unique, counts)}

    return {
        't1': result_t1,
        't2': result_t2,
        'changed': bool(change_mask.any()),
        'change_map_b64': numpy_to_base64_png(change_display),
        'summary': summary,
    }
```

### 2.6 `backend/requirements.txt`

```
fastapi==0.110.0
uvicorn[standard]==0.29.0
torch>=2.0.0
torchvision>=0.15.0
pillow>=10.0.0
numpy>=1.24.0
opencv-python-headless>=4.8.0
matplotlib>=3.7.0
python-multipart>=0.0.9
```

---

## Phase 3 — Frontend (React + Vite)

### 3.1 Setup

```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install axios leaflet react-leaflet react-compare-slider
```

### 3.2 Component Breakdown

#### `App.jsx` — Main layout
Three tabs / sections:
1. **Single Image** — classify + Grad-CAM
2. **Compare Images** — before/after + change detection
3. **Map** — Leaflet map (optional Sentinel tile click)

State managed at App level, passed to children via props.

#### `ImageUpload.jsx`
- Drag-and-drop zone using native HTML5 file API
- Preview uploaded image (URL.createObjectURL)
- "Analyze" button → calls `/classify` or `/gradcam`
- Props: `onResult(result)`, `label` ("Before" / "After")

#### `ResultPanel.jsx`
- Shows top predicted class + confidence %
- Horizontal probability bars for all 10 classes (sorted by confidence)
- Color-coded by category (green=vegetation, red=urban, blue=water)

```jsx
const CLASS_COLORS = {
  Forest: '#2d7d2d', HerbaceousVegetation: '#5aad5a', Pasture: '#90c990',
  AnnualCrop: '#c8e6a0', PermanentCrop: '#a8d080',
  Residential: '#e05050', Industrial: '#c03030',
  Highway: '#d4a820',
  River: '#4090e0', SeaLake: '#2060c0',
};
```

#### `GradCAMOverlay.jsx`
- Displays original image
- Toggle button: "Show Explanation" / "Hide Explanation"
- When on: overlay the `overlay_b64` image on top with opacity slider
- Small legend: red = high attention, blue = low attention

#### `ChangeMap.jsx`
- Left panel: T1 image + classification
- Right panel: T2 image + classification
- Center: color-coded change map
- Legend box: urbanization=red, reforestation=green, flooding=blue, drought=orange
- Summary text: "3 patches urbanized, 1 patch reforested"

#### `MapView.jsx` (Optional / Stretch Goal)
- Leaflet map centered on Europe (EuroSAT origin)
- Click → show lat/lng
- Future: call Sentinel Hub API to fetch 64x64 tile at that location
- For now: show a prompt "Upload a satellite image of this location"

### 3.3 `api/terralens.js`

```js
import axios from 'axios';

const BASE = 'http://localhost:8000';

export async function classifyImage(file) {
  const form = new FormData();
  form.append('image', file);
  const { data } = await axios.post(`${BASE}/classify`, form);
  return data;
}

export async function getGradCAM(file) {
  const form = new FormData();
  form.append('image', file);
  const { data } = await axios.post(`${BASE}/gradcam`, form);
  return data;
}

export async function compareImages(fileT1, fileT2) {
  const form = new FormData();
  form.append('image_t1', fileT1);
  form.append('image_t2', fileT2);
  const { data } = await axios.post(`${BASE}/compare`, form);
  return data;
}
```

---

## Phase 4 — Integration & Running

### Running locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev   # runs on http://localhost:5173
```

### CORS
Backend already has `allow_origins=["*"]` for development. Tighten for production.

---

## Implementation Order (What to Build First)

1. **`model_export/export_model.py`** — Run in Colab, get `best_model.pth` ← Blocker for everything
2. **`backend/model.py`** — Copy CNN_LeakyReLU_Skip exactly
3. **`backend/inference.py`** — Preprocessing pipeline
4. **`backend/main.py`** — `/classify` endpoint only (test with curl/Postman)
5. **`backend/gradcam.py`** — Add `/gradcam` endpoint
6. **`backend/change_detection.py`** — Add `/compare` endpoint
7. **`frontend/`** — Single-image classify UI first, then Grad-CAM toggle, then compare tab
8. **Polish** — MapView, loading states, error handling, mobile layout

---

## Key Implementation Notes

### Grad-CAM Hook Target
Hook `model.res_blocks[-1]` (the last `nn.Sequential` residual block), NOT `conv3`.
Reason: after 5 residual blocks, the feature maps encode semantic land-use features,
not just low-level edges. Grad-CAM on `conv3` would show spatial structure only.

### Normalization Consistency
The transform in `inference.py` MUST use the same `mean`/`std` computed from EuroSAT
in notebook Cell 7. These are stored in the checkpoint. Do not use ImageNet stats.

### Tile Size
All model inputs must be exactly 64×64. For the change detection tiled analysis,
pad tiles at image borders with reflection padding to avoid black-edge artifacts.

### Change Detection Threshold
Default threshold=0.3 works well. Expose it as a UI slider (0.1–0.6) so users can
tune sensitivity. Lower threshold = more sensitive to subtle changes.

### Grad-CAM Backward Pass
The backward pass modifies the model's gradient buffers. After generating a Grad-CAM,
call `model.zero_grad()` before any subsequent inference to prevent gradient accumulation.
The hooks store the last backward pass values, so always re-run forward+backward
for each new image rather than caching.

---

## Optional Stretch Goals (After Core Works)

| Feature | Effort | Impact |
|---------|--------|--------|
| Sentinel Hub API (auto-fetch tiles) | High | Very high — live data |
| Before/After image slider (react-compare-slider) | Low | High — visual wow |
| Confidence calibration plot | Medium | Academic value |
| Batch upload (zip of images → bulk classification) | Medium | Practical |
| Export PDF report with results | High | Professional |
| Docker-compose for one-command deploy | Low | Demo readiness |

---

## Demo Script (For Presentation)

1. Open TerraLens in browser
2. Upload a Forest image from EuroSAT test set
3. Show classification: "Forest — 96.2% confidence"
4. Click "Show Explanation" → Grad-CAM lights up the tree canopy patterns
5. Go to Compare tab, upload Forest image as T1 and Residential image as T2
6. Show change map: large red area labeled "Urbanization"
7. Adjust threshold slider to show sensitivity
8. (Optional) Click on map of Amazon region → "Upload a satellite image of this location to analyze"
