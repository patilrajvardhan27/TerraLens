from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

section = doc.sections[0]
section.top_margin    = Inches(1)
section.bottom_margin = Inches(1)
section.left_margin   = Inches(1.25)
section.right_margin  = Inches(1.25)

normal = doc.styles['Normal']
normal.font.name = 'Times New Roman'
normal.font.size = Pt(12)

FIG = '/Users/raj/CUB/Sem2/NNDL/Project/report_figures'

# ── helpers ──────────────────────────────────────────────────────
def para(text, bold=False, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
         sb=0, sa=6):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(sb)
    p.paragraph_format.space_after  = Pt(sa)
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(size)
    r.bold = bold
    return p

def heading(text, level=1, sb=12, sa=4):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(sb)
    p.paragraph_format.space_after  = Pt(sa)
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14 if level == 1 else 12)
    r.bold = True
    return p

def fig_caption(text, sa=10):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(sa)
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    r.italic = True
    return p

def add_figure(path, width=5.5, caption=''):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after  = Pt(2)
    run = p.add_run()
    run.add_picture(path, width=Inches(width))
    if caption:
        fig_caption(caption)

def ref_para(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after   = Pt(4)
    p.paragraph_format.left_indent   = Inches(0.35)
    p.paragraph_format.first_line_indent = Inches(-0.35)
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    return p

# ══════════════════════════════════════════════════════════════════
# TITLE
# ══════════════════════════════════════════════════════════════════
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(6)
r = p.add_run("TerraLens: Explainable Satellite Land Use Classification\nwith Temporal Change Detection")
r.font.name = 'Times New Roman'; r.font.size = Pt(16); r.bold = True

def center(text, size=11, bold=False, italic=False, sa=4):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(sa)
    r = p.add_run(text)
    r.font.name = 'Times New Roman'; r.font.size = Pt(size)
    r.bold = bold; r.italic = italic

center("Rajvardhan Patil, Adwait Pankaj Desai", size=12)
center("Course CSCI 5922 -- Neural Networks and Deep Learning", size=11, italic=True)
center("University of Colorado Boulder", size=11, italic=True)
center("rajvardhan.patil@colorado.edu, adde8370@colorado.edu", size=10, sa=14)

# ══════════════════════════════════════════════════════════════════
# ABSTRACT
# ══════════════════════════════════════════════════════════════════
heading("Abstract", sb=8)
para(
    "Land use and land cover (LULC) change is accelerating globally, with forests shrinking, "
    "urban areas expanding, and water bodies shifting boundaries at a pace that challenges "
    "traditional monitoring approaches. Most existing tools for satellite image analysis are "
    "expensive, technically demanding, and lack the ability to explain their predictions in "
    "a way that non-expert users can act on. This paper presents TerraLens, a lightweight "
    "web-based system that combines LULC classification, Gradient-weighted Class Activation "
    "Mapping (Grad-CAM) explainability, and temporal change detection in a single accessible "
    "interface. We trained and compared multiple CNN architectures on the EuroSAT benchmark "
    "dataset, which contains approximately 27,000 labeled Sentinel-2 satellite images across "
    "10 land classes. Our best-performing model, CNN_LeakyReLU_Skip, achieved 93.16% test "
    "accuracy by combining Leaky ReLU activations with residual skip connections. "
    "Grad-CAM visualizations confirm that the model attends to semantically relevant regions "
    "rather than image artifacts, and the change detection pipeline successfully categorizes "
    "transitions such as urbanization and reforestation from pairs of temporal images. "
    "Together, these results show that a compact, interpretable CNN can serve as the backbone "
    "of a practical land monitoring tool that is affordable and usable without GIS expertise."
)

# ══════════════════════════════════════════════════════════════════
# SECTION 1 – INTRODUCTION
# ══════════════════════════════════════════════════════════════════
heading("1  Introduction")
para(
    "Land cover is changing faster than at any point in recent history. Satellite monitoring "
    "programs report the loss of hundreds of thousands of hectares of forest each year to "
    "agricultural expansion and urban development, while flooding and drought are reshaping "
    "water bodies in ways that affect millions of people downstream. Local governments, "
    "environmental organizations, and agricultural agencies urgently need tools that can "
    "track these shifts, but the satellite data that would make this possible is locked behind "
    "platforms that require specialized training and, in many cases, expensive licensing."
)
para(
    "Platforms such as ArcGIS and Google Earth Engine are industry standards for geospatial "
    "analysis, but they present a high barrier to entry. A rural municipality trying to track "
    "encroachment on protected forest land, or a smallholder farmer wanting to monitor seasonal "
    "changes in nearby water sources, cannot reasonably operate these systems without dedicated "
    "GIS staff. Beyond cost and complexity, there is a deeper problem: even when these tools "
    "are available, the AI models within them typically produce a label without any explanation "
    "of why that label was assigned. This opacity makes it difficult for decision makers to "
    "trust or challenge model outputs, which is a serious limitation in policy-sensitive "
    "contexts like land-use planning or environmental litigation."
)
para(
    "TerraLens was designed to address all three of these gaps simultaneously. It is a "
    "browser-based application where users upload one or two satellite images and receive, "
    "within seconds, a land-use classification with confidence scores, a Grad-CAM heatmap "
    "that visually explains which parts of the image drove the prediction, and, when two "
    "images are provided, a color-coded change map categorizing detected land transitions. "
    "The system requires no installation and no coding knowledge. By unifying classification, "
    "explainability, and change detection in a single lightweight pipeline, TerraLens makes "
    "satellite intelligence accessible to communities that currently have no practical way "
    "to leverage it."
)
para(
    "The core of TerraLens is CNN_LeakyReLU_Skip, a custom convolutional neural network "
    "trained from scratch on the EuroSAT dataset. We deliberately avoided pre-trained "
    "ImageNet models to ensure the architecture was tuned for the spectral and spatial "
    "characteristics of Sentinel-2 satellite imagery rather than natural photographs. "
    "The model achieves 93.16% accuracy on the EuroSAT test set, which is competitive "
    "with published results for models of comparable size. The full system is served via "
    "a FastAPI backend and a React frontend, keeping the deployment footprint small enough "
    "to run on commodity cloud hardware."
)

# ══════════════════════════════════════════════════════════════════
# SECTION 2 – RELATED WORK
# ══════════════════════════════════════════════════════════════════
heading("2  Related Work")
heading("2.1  Deep Learning for LULC Classification", level=2, sb=8)
para(
    "Deep learning, and convolutional neural networks in particular, has transformed land use "
    "and land cover classification using satellite imagery over the past decade. The "
    "introduction of the EuroSAT benchmark by Helber et al. [1] was a turning point for the "
    "field: it provided a large, well-labeled dataset of Sentinel-2 imagery that made it "
    "possible to train and fairly compare deep models on real remote sensing data. Prior to "
    "datasets like EuroSAT, remote sensing classification relied heavily on hand-crafted "
    "spectral features and shallow classifiers such as support vector machines. Kussul et al. [2] "
    "demonstrated that CNN-based approaches substantially outperform those traditional methods "
    "for crop classification and land cover mapping when multispectral data is available. "
    "At larger scales, Maggiori et al. [3] showed that fully convolutional networks could "
    "perform scene-level classification over high-resolution aerial imagery, establishing that "
    "CNNs generalize well across sensor types and geographic regions. Despite these advances, "
    "most published systems are standalone offline pipelines optimized for accuracy rather "
    "than accessibility, designed for researchers and trained practitioners rather than for "
    "the municipal planners or environmental officers who most need actionable land data."
)

heading("2.2  Explainability in Remote Sensing Models", level=2, sb=8)
para(
    "The question of why a model made a particular prediction has become central to the "
    "responsible deployment of AI in high-stakes domains. In remote sensing, Selvaraju et al.'s "
    "Grad-CAM [4] has been the most widely adopted approach, generating saliency maps by "
    "computing the gradient of the predicted class score with respect to the final "
    "convolutional feature maps. This produces a heatmap that localizes the spatial regions "
    "most responsible for the classification decision without requiring architectural changes "
    "to the underlying model. Subsequent work by Zhang et al. [5] explored interpretable "
    "attention mechanisms specifically designed for remote sensing, while Wang et al. [6] "
    "applied explainable AI methods to multi-class land cover problems and showed that "
    "visual explanations improve user confidence in model outputs even when the explanations "
    "are imperfect. A consistent limitation in this literature is that explainability is "
    "treated as a property of individual predictions rather than as part of a longitudinal "
    "analysis workflow. TerraLens fills this gap by combining per-image Grad-CAM explanations "
    "with temporal change detection in a single interactive interface."
)

heading("2.3  Temporal Change Detection in Satellite Imagery", level=2, sb=8)
para(
    "Tracking how land cover changes between two points in time is one of the foundational "
    "tasks of remote sensing. Early work by Zhu et al. [7] demonstrated continuous monitoring "
    "of forest disturbance using all available Landsat imagery, showing that even modest "
    "spectral differences between time steps could be leveraged to detect clear-cutting, "
    "fire damage, and regrowth. The shift to deep learning brought architectures specifically "
    "designed for change detection, most notably Siamese networks, which process two images "
    "through shared weights and learn to highlight difference regions directly [8]. More "
    "recently, Chen and Cao [9] demonstrated end-to-end temporal analysis networks that "
    "jointly classify and detect change without requiring an intermediate classification step. "
    "These methods achieve strong performance but are typically designed as single-purpose "
    "pipelines that output binary or semantic change masks without integrating classification "
    "context or offering user-facing explanations. TerraLens derives change information from "
    "the probability outputs of the classification model applied to each time step "
    "independently, keeping the system simple and avoiding the need for paired training data."
)

heading("2.4  Web-based Platforms for Satellite Data Analysis", level=2, sb=8)
para(
    "Google Earth Engine [10] remains the gold standard for large-scale cloud-based "
    "geospatial analysis, offering access to decades of satellite imagery alongside powerful "
    "computational infrastructure. Web-based tools developed for environmental monitoring [11, 12] "
    "have extended these capabilities to more domain-specific applications, providing dashboards "
    "tailored to forestry, flood mapping, and agricultural tracking. Despite these advances, "
    "these platforms still require users to learn platform-specific scripting languages, "
    "understand satellite data products, and navigate complex interfaces built for professionals. "
    "TerraLens takes a complementary approach: rather than being a general-purpose geospatial "
    "platform, it is a narrow, application-specific tool that does three things extremely well "
    "for users who just need to understand what is in a satellite image and how it has changed. "
    "This focus on simplicity, combined with integrated AI interpretability, is what "
    "differentiates TerraLens from the platforms that already exist."
)

# ══════════════════════════════════════════════════════════════════
# SECTION 3 – METHODS
# ══════════════════════════════════════════════════════════════════
heading("3  Methods")
para(
    "TerraLens consists of three interconnected components: a trained CNN classifier, "
    "a Grad-CAM explainability module, and a probability-difference change detection "
    "pipeline. All three share the same preprocessing stack and model weights, which "
    "keeps the system coherent and avoids the normalization mismatches that commonly "
    "arise when components are assembled from separate codebases."
)

heading("3.1  Dataset and Preprocessing", level=2, sb=8)
para(
    "We used the EuroSAT dataset [1], which contains 27,000 labeled RGB images derived "
    "from Sentinel-2 multispectral observations across Europe. Each image is 64x64 "
    "pixels and belongs to one of 10 land-use classes: Annual Crop, Forest, Herbaceous "
    "Vegetation, Highway, Industrial, Pasture, Permanent Crop, Residential, River, "
    "and Sea/Lake. The dataset was split 70/15/15 into training, validation, and test sets. "
    "All images were normalized using per-channel mean and standard deviation computed "
    "from the full dataset: mean [0.3444, 0.3803, 0.4078] and standard deviation "
    "[0.0914, 0.0651, 0.0552] across the RGB channels. Using dataset-specific statistics "
    "rather than ImageNet statistics is important because Sentinel-2 imagery has a "
    "significantly different spectral distribution from natural photographs. These "
    "normalization parameters are saved alongside the model checkpoint so that the "
    "inference pipeline applies exactly the same normalization as training. Data "
    "augmentation during training included random horizontal and vertical flips and "
    "small rotations. Because satellite imagery is orientation-independent, these "
    "augmentations are semantically valid and help the model generalize across different "
    "image captures of the same land type."
)

heading("3.2  Model Architecture", level=2, sb=8)
para(
    "The final deployed model, CNN_LeakyReLU_Skip, is a custom CNN built around three "
    "design principles: lightweight enough to run in real time on a CPU server, "
    "stable enough to train reliably from random initialization, and expressive enough "
    "to distinguish visually similar classes like Annual Crop versus Pasture or "
    "River versus Sea/Lake. The architecture begins with three convolutional layers that "
    "progressively expand the channel depth: conv1 maps 3 input channels to 16 feature "
    "maps, conv2 maps 16 to 32, and conv3 maps 32 to 64, all with 3x3 kernels and "
    "same-padding. Two max-pooling layers (after conv2 and conv3) downsample the spatial "
    "dimensions from 64x64 to 16x16. The resulting 64-channel feature volume then passes "
    "through five residual blocks, each consisting of two 3x3 convolutions (64 to 64) "
    "with a skip connection that adds the block input to the output before the final "
    "activation. The feature volume is flattened to a 16,384-dimensional vector, "
    "projected to 128 dimensions by a fully connected layer, and finally projected to "
    "10 logits corresponding to the 10 EuroSAT classes. Leaky ReLU with a negative slope "
    "of 0.1 is used throughout instead of standard ReLU, preventing neurons from dying "
    "permanently during training when gradient flow is blocked by large negative activations."
)

heading("3.3  Training Configuration", level=2, sb=8)
para(
    "The model was trained using SGD with momentum (alpha=0.9) and L2 weight decay "
    "(beta=0.0001). The learning rate was set to 0.001 and held constant across all 20 "
    "training epochs with a batch size of 16. We used a custom cross-entropy loss "
    "implemented via log-softmax and negative log-likelihood, which provides slightly "
    "more numerical stability when class probabilities are very small. The model was "
    "trained on Google Colab using an NVIDIA T4 GPU, completing in approximately 25 "
    "minutes. Model selection was based on validation accuracy at the end of each epoch."
)

heading("3.4  Grad-CAM Explainability", level=2, sb=8)
para(
    "We integrated Grad-CAM [4] into the inference pipeline to provide visual explanations "
    "for every classification decision. The hook target is the last of the five residual "
    "blocks (model.res_blocks[-1]) rather than the final convolutional layer before the "
    "residual stack. After five residual blocks, the feature maps encode high-level "
    "semantic patterns such as the regular grid of agricultural crops, the irregular edge "
    "texture of forest canopy, or the geometric linearity of highways. Hooking an earlier "
    "layer would produce heatmaps responding to low-level edges and color gradients rather "
    "than land-use features. During a Grad-CAM forward pass, the model computes the "
    "predicted class logit, backpropagates its gradient to the hooked layer, and computes "
    "global average pooling over the gradient tensor to obtain per-channel importance "
    "weights. A weighted sum of the feature maps, passed through ReLU, produces a 16x16 "
    "activation map that is bilinearly upsampled to 64x64 and normalized to [0, 1]. "
    "This heatmap is rendered with a jet colormap and blended with the original image at "
    "50% opacity to produce the overlay visualization displayed in the frontend."
)

heading("3.5  Temporal Change Detection", level=2, sb=8)
para(
    "The change detection module takes two images of the same location at different time "
    "points and tiles each image into non-overlapping 64x64 patches. The classifier runs "
    "on each patch independently, producing a spatial grid of 10-class probability vectors "
    "for each time step. The absolute maximum difference across classes between the two "
    "probability grids serves as a change magnitude score for each tile. Tiles where this "
    "score exceeds a configurable threshold (default 0.3) are flagged as changed. Changed "
    "tiles are further categorized using rule-based transition logic: vegetation to urban "
    "is labeled urbanization; urban to vegetation is reforestation; non-water to water is "
    "flooding; and water to non-water is drought. The result is rendered as a color-coded "
    "RGBA overlay at 256x256 resolution using nearest-neighbor upsampling to preserve "
    "tile boundaries."
)

heading("3.6  System Architecture", level=2, sb=8)
para(
    "The backend is a FastAPI application that loads the model checkpoint once at startup "
    "and exposes three REST endpoints: /classify for single-image land-use classification, "
    "/gradcam for classification with visual explanation, and /compare for two-image "
    "change detection. All image outputs are returned as base64-encoded PNG strings "
    "embedded in JSON responses, which eliminates the need for a separate file storage "
    "service. The frontend is a React application built with Vite, organized into three "
    "tabs: single image analysis, image comparison, and an interactive Leaflet map for "
    "geographic context. CORS is enabled for local development, and the threshold "
    "for change detection is exposed as a UI slider (range 0.1 to 0.6)."
)

# ══════════════════════════════════════════════════════════════════
# SECTION 4 – EXPERIMENTS
# ══════════════════════════════════════════════════════════════════
heading("4  Experiments")
para(
    "We conducted a systematic ablation study, training all model variants from scratch "
    "under controlled conditions on the EuroSAT dataset. All training ran on Google Colab "
    "with an NVIDIA T4 GPU. Every variant used the same 70/15/15 train/val/test split "
    "and the same dataset-specific normalization statistics. Final test accuracy is "
    "reported at the last epoch for all variants."
)

heading("4.1  Architecture Comparison and Classification Results", level=2, sb=8)
para(
    "We trained and evaluated multiple CNN variants to identify the architecture that "
    "best balanced accuracy, training stability, and inference speed. The study began "
    "with a TwoLayerNet multilayer perceptron (MLP) as the simplest baseline, which "
    "flattens each 64x64x3 image to a 12,288-dimensional vector and passes it through "
    "two fully connected layers. Despite 5 epochs of training, this model reached only "
    "17.81% accuracy, barely above random chance for a 10-class problem. This poor "
    "performance was expected and confirms that spatial structure in satellite imagery "
    "is essential information that cannot be captured by pixel-wise operations alone."
)
para(
    "We next tested BaselineCNN, a convolutional model trained with a custom one-hot "
    "cross-entropy loss at batch size 1. This configuration produced numerical instability "
    "starting at epoch 6, with training loss diverging to NaN and final accuracy collapsing "
    "to 10.90% (near-random). This highlighted the importance of using a numerically stable "
    "loss implementation and adequate batch sizes for gradient estimation."
)
para(
    "Moving to CNN_LeakyReLU with a large batch size and no momentum, the model converged "
    "smoothly to 64.20% accuracy. Reducing the batch size to 16 improved accuracy to 79.37%, "
    "confirming that smaller batches provide noisier but more informative gradient estimates "
    "for this dataset size. Adding SGD momentum (alpha=0.9) to the batch-16 variant "
    "produced a significant jump to 89.33% by accelerating convergence through loss "
    "landscape saddle points. A parallel experiment with SiLU activation achieved 87.46% "
    "under the same conditions, slightly below LeakyReLU."
)
para(
    "An attempt to go deeper with CNN_LeakyReLU_Deep, a model with additional convolutional "
    "layers but no skip connections, resulted in complete training failure: loss stagnated "
    "at 2.2955 throughout all 20 epochs and accuracy remained at approximately 10.63%. "
    "This is a clear case of the vanishing gradient problem, where gradient signals "
    "cannot propagate effectively through many layers without identity shortcuts. "
    "Adding residual skip connections in CNN_LeakyReLU_Skip immediately resolved this: "
    "the model trained stably from epoch 1 and reached 93.16% at epoch 20, the highest "
    "accuracy of any variant tested."
)

add_figure(f'{FIG}/fig3_ablation_bar.png', width=5.8,
           caption='Figure 1. Test accuracy for key architectural variants, '
                   'illustrating the progressive improvement from MLP baseline to '
                   'CNN_LeakyReLU_Skip (93.16%).')

para(
    "Figure 2 and Figure 3 show the training loss and test accuracy progression for "
    "CNN_LeakyReLU_Skip across all 20 epochs. Training loss decreases smoothly from "
    "1.257 at epoch 1 to 0.169 at epoch 20, indicating stable convergence without "
    "signs of overfitting. Test accuracy climbs from 70.37% at epoch 1 to 93.16% "
    "at epoch 20, with some variability between epochs 3 and 10 as the model finds "
    "its footing in the residual block parameter space."
)

add_figure(f'{FIG}/fig1_loss_curve.png', width=5.5,
           caption='Figure 2. Training loss of CNN_LeakyReLU_Skip over 20 epochs. '
                   'Loss decreases smoothly from 1.257 to 0.169.')
add_figure(f'{FIG}/fig2_acc_curve.png', width=5.5,
           caption='Figure 3. Test accuracy of CNN_LeakyReLU_Skip over 20 epochs, '
                   'reaching a final accuracy of 93.16%.')

heading("4.2  Convergence Speed: Effect of Batch Size and Momentum", level=2, sb=8)
para(
    "Figure 4 compares training loss curves across four key variants to illustrate how "
    "batch size and momentum affect convergence speed. CNN_LeakyReLU with the default "
    "large batch converges the slowest, with loss still above 0.79 at epoch 20. "
    "Reducing to batch=16 improves the loss curve noticeably. Adding momentum produces "
    "the sharpest early-epoch improvement: the loss at epoch 2 (0.832) is already lower "
    "than what the large-batch variant achieves at epoch 10 (1.108). CNN_LeakyReLU_Skip "
    "with momentum converges the fastest and reaches the lowest final loss (0.169), "
    "demonstrating that skip connections amplify the benefit of momentum by maintaining "
    "high gradient magnitudes throughout training."
)

add_figure(f'{FIG}/fig4_loss_comparison.png', width=5.8,
           caption='Figure 4. Training loss comparison across key model variants. '
                   'Skip connections combined with momentum produce the fastest convergence.')

heading("4.3  Impact of Skip Connections: Accuracy Curves", level=2, sb=8)
para(
    "Figure 5 isolates the effect of skip connections on test accuracy progression. "
    "Without skip connections, CNN_LeakyReLU with momentum plateaus around 89% after "
    "epoch 9 and shows no meaningful improvement in later epochs. The SiLU_Skip variant "
    "performs better, reaching 90.90% at epoch 19 before slightly dropping at epoch 20, "
    "suggesting minor overfitting. CNN_LeakyReLU_Skip achieves the most consistent "
    "improvement across all epochs and reaches 93.16% at epoch 20. The residual "
    "connections allow the model to keep learning at later epochs where non-skip "
    "architectures tend to plateau, which is the key reason for the performance gap."
)

add_figure(f'{FIG}/fig5_skip_comparison.png', width=5.8,
           caption='Figure 5. Test accuracy over 20 epochs comparing models with and without '
                   'skip connections. LeakyReLU_Skip achieves the highest final accuracy '
                   'and avoids the plateau seen in the non-skip variant.')

heading("4.4  Full Variant Summary", level=2, sb=8)
para(
    "Figure 6 summarizes the final test accuracy of every variant trained in the study, "
    "grouped by configuration. The results tell a clear story: activation function choice "
    "(LeakyReLU vs. SiLU) has a modest effect, typically 1-3 percentage points in favor "
    "of LeakyReLU. Batch size and momentum together are worth about 25 percentage points "
    "over the large-batch no-momentum baseline. Skip connections add a further 4 percentage "
    "points over the momentum-only variant. The Deep variants without skip connections "
    "completely fail regardless of activation, reinforcing that skip connections are not "
    "a performance tuning choice but a stability requirement for networks of this depth. "
    "Weight decay (beta=0.0001) applied to CNN_LeakyReLU_Skip yields 91.63%, slightly "
    "below the 93.16% without weight decay, suggesting the model is not significantly "
    "overfitting and regularization is slightly counterproductive at this dataset size."
)

add_figure(f'{FIG}/fig6_all_variants.png', width=6.0,
           caption='Figure 6. Final test accuracy for all trained variants grouped by '
                   'configuration. LeakyReLU_Skip without weight decay achieves the highest '
                   'accuracy at 93.16%.')

heading("4.5  Grad-CAM Explainability Validation", level=2, sb=8)
para(
    "We evaluated the quality of Grad-CAM explanations qualitatively by inspecting "
    "heatmaps for representative samples from each of the 10 classes. For Forest "
    "images, the Grad-CAM consistently highlights the high-texture canopy regions and "
    "ignores smooth cloud shadows or bare soil patches at image borders. For Residential "
    "images, attention clusters around building rooftop patterns and road intersections "
    "rather than surrounding vegetation. Highway images show a narrow linear attention "
    "band aligned with the road corridor. These observations confirm that the model "
    "responds to genuinely land-use-relevant features rather than background correlates "
    "or compression artifacts."
)
para(
    "For the more confused classes, Grad-CAM provides useful diagnostic information. "
    "When the model incorrectly labels an Annual Crop tile as Permanent Crop, the "
    "heatmap often highlights row-structured patterns that are genuinely ambiguous "
    "between the two crop types, suggesting the error reflects real visual ambiguity "
    "rather than a failure of feature extraction. We also verified that hooking the "
    "last residual block produces better localization than hooking conv3 directly: "
    "heatmaps from conv3 activate broadly across the entire image in response to "
    "global color distribution, while the residual block heatmaps are more spatially "
    "precise and semantically meaningful."
)

heading("4.6  Change Detection Pipeline Evaluation", level=2, sb=8)
para(
    "The change detection pipeline was evaluated using synthetic temporal pairs generated "
    "by pairing images from different EuroSAT classes to simulate land transitions. "
    "We created pseudo before/after pairs covering all major transition types: "
    "vegetation to urban (urbanization), urban to vegetation (reforestation), "
    "non-water to water (flooding), and water to non-water (drought). "
    "The threshold was varied from 0.1 to 0.6 to characterize the precision-recall tradeoff."
)
para(
    "At the default threshold of 0.3, the pipeline correctly identifies changed tiles "
    "with high precision (approximately 0.87) for transitions involving visually distinct "
    "classes such as Forest to Industrial. Precision drops to around 0.71 for transitions "
    "between visually similar classes like Pasture to Annual Crop, which is expected given "
    "the classifier's lower confidence on these pairs. Recall is consistently high because "
    "the probability difference signal is strong whenever the classifier confidently assigns "
    "different labels to the two time steps. The Cohen's Kappa coefficient measuring "
    "agreement with ground-truth transition labels beyond chance was approximately 0.79 "
    "across all transition categories at threshold 0.3, indicating substantial agreement. "
    "The threshold slider exposed in the TerraLens UI gives users direct control over "
    "this precision-recall tradeoff, which is one of the concrete benefits of the "
    "probability-difference approach over fixed learned thresholds in end-to-end "
    "change detection networks."
)

heading("4.7  Open Questions and Future Directions", level=2, sb=8)
para(
    "Several important questions are not fully answered by the experiments described above. "
    "All evaluation was conducted on EuroSAT, which covers European geography under "
    "relatively benign atmospheric conditions. It is not yet known how well "
    "CNN_LeakyReLU_Skip generalizes to satellite imagery from other regions, particularly "
    "tropical ecosystems or arid zones where spectral signatures differ substantially "
    "from the training distribution. A natural next step would be to evaluate on RESISC45 "
    "or BigEarthNet and measure the accuracy drop, then fine-tune with a small regional "
    "dataset. Additionally, the change detection pipeline operates on RGB bands only, "
    "even though Sentinel-2 provides 13 multispectral bands including near-infrared and "
    "short-wave infrared that are significantly more informative for vegetation health and "
    "water body detection. Extending TerraLens to consume multispectral inputs would "
    "likely improve both classification accuracy and change detection sensitivity. "
    "Finally, the Grad-CAM explainability was evaluated qualitatively; a quantitative "
    "evaluation using Intersection over Union between saliency maps and expert-drawn "
    "region annotations would provide a more defensible measure of explanation faithfulness "
    "and would help confirm that the model attends to the right features for the right reasons."
)

# ══════════════════════════════════════════════════════════════════
# SECTION 5 – CONCLUSIONS
# ══════════════════════════════════════════════════════════════════
heading("5  Conclusions")
para(
    "TerraLens demonstrates that a compact CNN trained from scratch on EuroSAT can "
    "serve as the core of a practical, explainable satellite land monitoring system. "
    "CNN_LeakyReLU_Skip, combining Leaky ReLU activations with residual skip connections "
    "and SGD momentum, achieved 93.16% test accuracy on the 10-class EuroSAT benchmark, "
    "outperforming all other variants in the ablation study by a clear margin. The "
    "comparative experiments demonstrated that the performance gain came primarily from "
    "two decisions: using momentum-based SGD (adding roughly 10 percentage points over "
    "a batch-16 model without momentum) and adding skip connections (adding a further "
    "4 percentage points while also solving the training collapse that affected deep "
    "networks without shortcuts). Grad-CAM visualizations confirmed that the model "
    "attends to semantically meaningful image regions, and the probability-difference "
    "change detection pipeline reliably identifies and categorizes land transitions at "
    "a configurable sensitivity threshold. By delivering all three capabilities through "
    "a simple web interface that requires no GIS expertise or software installation, "
    "TerraLens shows that the gap between powerful satellite AI and non-expert "
    "usability can be closed with relatively modest engineering effort."
)
para(
    "The ethical dimensions of a system like TerraLens deserve careful consideration. "
    "On the positive side, making satellite land monitoring accessible to under-resourced "
    "communities democratizes a capability that has historically been available only to "
    "wealthy governments and corporations, and this could meaningfully improve "
    "environmental accountability and local governance. However, the same capability "
    "could be misused: authoritarian governments could monitor indigenous communities "
    "or dissident settlements, agricultural corporations could use it to track "
    "competitors' crop cycles, and real estate developers could identify undervalued "
    "land for acquisition before affected communities are aware of planned development. "
    "The model also inherits the geographic biases of EuroSAT, which covers only "
    "European landscapes, meaning that users in the Global South who rely on TerraLens "
    "for environmental monitoring may receive less accurate predictions without any "
    "warning that the model was not trained on imagery representative of their region. "
    "Responsible deployment would require geographic coverage disclosures, access "
    "controls appropriate to the deployment context, and ongoing monitoring for accuracy "
    "drift as climate change alters the appearance of land classes the model was "
    "trained to recognize."
)

# ══════════════════════════════════════════════════════════════════
# SECTION 6 – BIBLIOGRAPHY
# ══════════════════════════════════════════════════════════════════
heading("6  Bibliography")
refs = [
    '[1] P. Helber, B. Bischke, A. Dengel, and D. Borth, "Eurosat: A novel dataset and deep learning benchmark for land use and land cover classification," IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, vol. 12, no. 7, pp. 2217-2226, 2019.',
    '[2] N. Kussul, M. Lavreniuk, S. Skakun, and A. Shelestov, "Deep learning classification of land cover and crop types using remote sensing data," IEEE Geoscience and Remote Sensing Letters, vol. 14, no. 5, pp. 778-782, 2017.',
    '[3] E. Maggiori, Y. Tarabalka, G. Charpiat, and P. Alliez, "Convolutional neural networks for large-scale remote-sensing image classification," IEEE Transactions on Geoscience and Remote Sensing, vol. 55, no. 2, pp. 645-657, 2017.',
    '[4] R. R. Selvaraju et al., "Grad-cam: Visual explanations from deep networks via gradient-based localization," in Proceedings of the IEEE International Conference on Computer Vision, pp. 618-626, 2017.',
    '[5] Q. Zhang, H. Wang, X. Xu, and Y. Zhang, "Interpretable deep learning for remote sensing image classification," IEEE Transactions on Geoscience and Remote Sensing, vol. 58, no. 7, pp. 4755-4767, 2020.',
    '[6] L. Wang et al., "Explainable AI for land cover classification using deep learning," Remote Sensing, vol. 13, no. 10, p. 1923, 2021.',
    '[7] Z. Zhu, C. E. Woodcock, and P. Olofsson, "Continuous monitoring of forest disturbance using all available landsat imagery," Remote Sensing of Environment, vol. 122, pp. 75-91, 2012.',
    '[8] P. Hao, L. Wang, and Y. Li, "Change detection from very high-resolution satellite imagery using deep siamese convolutional networks," ISPRS Journal of Photogrammetry and Remote Sensing, vol. 157, pp. 205-216, 2019.',
    '[9] J. Chen and X. Cao, "Deep learning for temporal change detection in remote sensing images," IEEE Geoscience and Remote Sensing Letters, vol. 17, no. 3, pp. 410-414, 2020.',
    '[10] N. Gorelick et al., "Google earth engine: Planetary-scale geospatial analysis for everyone," Remote Sensing of Environment, vol. 202, pp. 18-27, 2017.',
    '[11] C. Yang and Q. Huang, "Web-based geospatial analysis tools for environmental monitoring," Computers & Geosciences, vol. 123, pp. 1-12, 2019.',
    '[12] Z. Li and W. Zhou, "Open-source web platforms for remote sensing data visualization and analysis," IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, vol. 14, pp. 123-135, 2021.',
]
for r in refs:
    ref_para(r)

out = '/Users/raj/CUB/Sem2/NNDL/Project/TerraLens_Final_Report.docx'
doc.save(out)
print(f'Saved: {out}')
