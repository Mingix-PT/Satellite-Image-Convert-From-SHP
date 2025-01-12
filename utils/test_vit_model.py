import timm
import torch
import torch.nn as nn

class ViTForSegmentation(nn.Module):
    def __init__(self, num_classes, img_size=224):
        super(ViTForSegmentation, self).__init__()

        # Load ViT backbone from timm
        self.backbone = timm.create_model('vit_small_patch16_224', pretrained=True, num_classes=0)

        # Segmentation decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(384, 256, kernel_size=2, stride=2),  # Upsample by 2x
            nn.ReLU(),
            nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2),  # Upsample by 2x
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2),   # Upsample by 2x
            nn.ReLU(),
            nn.ConvTranspose2d(64, num_classes, kernel_size=2, stride=2)  # Final upsampling
        )

        self.img_size = img_size

    def forward(self, x):
        # Pass input through ViT backbone
        x = self.backbone.patch_embed(x)  # [B, C, H/16, W/16]
        x = self.backbone.forward_features(x)

        # Reshape to 2D feature maps
        x = x.permute(0, 2, 1).view(x.size(0), -1, self.img_size // 16, self.img_size // 16)

        # Pass through segmentation decoder
        x = self.decoder(x)

        return x

# Define the model
num_classes = 5  # Example: 10 segmentation classes
model = ViTForSegmentation(num_classes)

# Define input
input_tensor = torch.rand(8, 13, 224, 224)  # Batch size 8, 13 channels, 224x224 image
output = model(input_tensor)

print(output.shape)  # Expected output: [8, num_classes, 224, 224]
