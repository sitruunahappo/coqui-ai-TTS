# https://github.com/ogunlao/glowtts_stdp/blob/main/modules/glow_tts_with_pitch.py#L833
import torch
import torch.nn.functional as F
from torch import nn


class ConvReLUNorm(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=1, dropout=0.0):
        super(ConvReLUNorm, self).__init__()
        self.conv = nn.Conv1d(in_channels, out_channels, kernel_size=kernel_size, padding=(kernel_size // 2))
        self.norm = nn.LayerNorm(out_channels)
        self.dropout = nn.Dropout(dropout)

    def forward(self, signal):
        out = F.relu(self.conv(signal))
        out = self.norm(out.transpose(1, 2)).transpose(1, 2)
        return self.dropout(out)

class PitchPredictor(nn.Module):
    """Predicts a single float per each temporal location. Borrowed from fastpitch"""

    def __init__(self, input_size, filter_size, kernel_size, dropout, n_layers=2, gin_channels=0):
        super(PitchPredictor, self).__init__()
        self.gin_channels = gin_channels
        if gin_channels != 0:
            self.cond = nn.Conv1d(gin_channels, input_size, 1)
        self.layers = nn.Sequential(
            *[
                ConvReLUNorm(
                    input_size if i == 0 else filter_size, filter_size, kernel_size=kernel_size, dropout=dropout
                )
                for i in range(n_layers)
            ]
        )
        self.fc = nn.Linear(filter_size, 1, bias=True)

    def forward(self, enc, enc_mask, g=None):
        enc = torch.detach(enc)
        if g is not None:
            g = torch.detach(g)
            enc = enc + self.cond(g)
        out = enc * enc_mask
        # out = self.layers(out.transpose(1, 2)).transpose(1, 2)
        out = self.layers(out).transpose(1, 2)
        out = self.fc(out) 
        out = out * enc_mask.transpose(1, 2)
        return out.squeeze(-1)
