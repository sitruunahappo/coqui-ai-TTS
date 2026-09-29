import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch.optim import Adam

import TTS
from TTS.tts.configs.glow_tts_test_config import GlowTTSConfig
from TTS.tts.configs.shared_configs import CharactersConfig
from TTS.tts.datasets.dataset import TTSDataset
from TTS.tts.utils.text.tokenizer import TTSTokenizer
from TTS.tts.configs.shared_configs import BaseDatasetConfig
from TTS.tts.datasets import load_tts_samples
from TTS.config.shared_configs import BaseAudioConfig
from TTS.utils.audio import AudioProcessor
from TTS.tts.layers.glow_tts.encoder import Encoder

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

class ConvReLUNorm(torch.nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=1, dropout=0.0):
        super(ConvReLUNorm, self).__init__()
        self.conv = torch.nn.Conv1d(in_channels, out_channels,
                                    kernel_size=kernel_size,
                                    padding=(kernel_size // 2))
        self.norm = torch.nn.LayerNorm(out_channels)
        self.dropout = torch.nn.Dropout(dropout)

    def forward(self, signal):
        out = F.relu(self.conv(signal))
        out = self.norm(out.transpose(1, 2)).transpose(1, 2).to(signal.dtype)
        return self.dropout(out)

class TemporalPredictor(nn.Module):
    '''Modified From FastPitch 
    
    From the paper:
        [...] a 1-D conv with kernel size 3 and 384/256 channels, and a 1-D conv 
        with 256/256 channels, each followed by ReLU, Layer Norm and Dropout layers. 
        The last layer projects every 256-channel vector to a scalar. Dropout rate is 0.1, [...]

    New:
        - Adam optimiser
        - Loss fn output
        - emb for phonemes input
    '''
    
    def __init__(self, 
                 vocab_size, 
                 hidden_channels,
                 enc_channels, 
                 text_size,
                 pitch_size,
                 filter_size, 
                 kernel_size=3, 
                 dropout=0.1, 
                 hidden_channels_dp=None, 
                 n_layers=2, 
                 lr=1e-3, 
                 epochs=10):
        '''
        vocab_size
        hidden_channels: emb dimesion
        enc_channels: out_channels in encoder
        input_size: for ph_id -> frame projection
        
        filter_size: out_channels for predictor

        hidden_channels_dp: in encoder, hidden_channels*4 as other file recommended
        '''
        super(TemporalPredictor, self).__init__()

        self.layers = nn.Sequential(*[
            ConvReLUNorm(enc_channels if i == 0 else filter_size, filter_size,
                         kernel_size=kernel_size, dropout=dropout)
            for i in range(n_layers)]
        )
        self.text_size = text_size
        self.pitch_size = pitch_size
        self.epochs = epochs
        self.loss = 0.0
        self.training_loss = []

        self.proj = nn.Linear(text_size, pitch_size)
        self.fc = nn.Linear(filter_size, 1, bias=True)
        self.loss_fn = nn.MSELoss()

        self.enc = Encoder(
            num_chars=vocab_size,
            out_channels=enc_channels,
            hidden_channels=hidden_channels,
            hidden_channels_dp=hidden_channels_dp if hidden_channels_dp else enc_channels*4,
            encoder_type='gated_conv',
            encoder_params={
                'kernel_size':5,
                'dropout_p': 0.1,
                'num_layers': 9,
            })
        
        self.optimiser = Adam(self.parameters(), lr=lr)

        if torch.cuda.is_available():
            self.cuda()

    def forward(self, enc_out, enc_out_mask):
        out = enc_out * enc_out_mask
        
        out = self.proj(out)
        enc_out_mask = nn.ConstantPad1d((0, self.pitch_size - self.text_size), 0)(enc_out_mask)
        
        out = self.layers(out).transpose(1, 2)
        out = self.fc(out) 
        out = out.transpose(1, 2) * enc_out_mask
        
        return out.squeeze()

    def fit(self, token_id, token_id_lengths, pitch):
        token_id = token_id.to(device)
        token_id_lengths = token_id_lengths.to(device)
        pitch = pitch.to(device)

        self.zero_grad()
        
        x_m, x_logs, logw, x_mask = self.enc(token_id, token_id_lengths)
        x_m = x_m.to(device)
        x_mask = x_mask.to(device)
        
        out = self.forward(x_m, x_mask)
        
        self.loss = self.loss_fn(out, pitch) 
        self.loss.backward()
        self.optimiser.step()

        return out

    def preprocess(self, batch, inf_mode=False):        
        token_id = batch['token_id']
        _, T_id = token_id.size()
        token_id_lengths = batch['token_id_lengths']
        token_id = nn.ConstantPad1d((0, self.text_size - T_id), 0)(token_id)

        if inf_mode:
            pitch = None
        else:
            pitch = batch['pitch'].squeeze(1)
            _, T_pitch = pitch.size()
            pitch = nn.ConstantPad1d((0, self.pitch_size - T_pitch), 0)(pitch)
        
        return token_id, token_id_lengths, pitch

    @torch.inference_mode()
    def inference(self, token_id, token_id_lengths):  
        token_id = token_id.to(device)
        token_id_lengths = token_id_lengths.to(device)
        
        _, T_id = token_id.size()
        token_id = nn.ConstantPad1d((0, self.text_size - T_id), 0)(token_id)
        
        x_m, x_logs, logw, x_mask = self.enc(token_id, token_id_lengths)
        x_m = x_m.to(device)
        x_mask = x_mask.to(device)
        
        raw_out = self.forward(x_m, x_mask)

        return raw_out.unsqueeze(1)
        
    @torch.inference_mode()
    def batch_inference(self, dataloader):  
        outs = []
        for batch in dataloader:
            token_id, token_id_lengths, _ = self.preprocess(batch, inf_mode=True)
            out = self.inference(token_id, token_id_lengths)
            outs.append(out)

        return outs
        