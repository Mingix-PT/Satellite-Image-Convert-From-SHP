import timm
from torchgeo.models import ViTSmall16_Weights
import torch

# Load the segmentation model weight
weights = ViTSmall16_Weights.SENTINEL2_ALL_MOCO

# Load the model
model = timm.create_model('vit_small_patch16_224', in_chans=weights.meta['in_chans'], num_classes=5)
model.load_state_dict(weights.get_state_dict(progress=True), strict=False)

dummy_input = torch.randn(8, 13, 224, 224)
output = model(dummy_input)
print(model)
for name, layer in model.named_children():
    print(f"Layer: {name}")
    # print(layer)

print(output.shape)
