import math
import torch
import torch.nn as nn

from kosr.model.attention import MultiHeadAttention
from kosr.model.transducer.sub_layer import FeedForwardNetwork
from kosr.model.mask import target_mask

class DecoderLayer(nn.Module):
    def __init__(self, hidden_dim, filter_dim, n_head, dropout_rate):
        super(DecoderLayer, self).__init__()
        self.att_norm = nn.LayerNorm(hidden_dim, eps=1e-6)
        self.att = MultiHeadAttention(hidden_dim, n_head, dropout_rate)

        self.memory_att_norm = nn.LayerNorm(hidden_dim, eps=1e-6)
        self.memory_att = MultiHeadAttention(hidden_dim, n_head, dropout_rate)

        self.ffn_norm = nn.LayerNorm(hidden_dim, eps=1e-6)
        self.ffn = FeedForwardNetwork(hidden_dim, filter_dim, dropout_rate)

    def forward(self, x, x_mask, memory, memory_mask):
        y = self.att_norm(x)
        y = self.att(y, y, y, x_mask)
        x = x + y

        if memory is not None:
            y = self.memory_att_norm(x)
            y = self.memory_att(y, memory, memory, memory_mask)
            x = x + y

        y = self.ffn_norm(x)
        y = self.ffn(y)
        x = x + y
        return x

class Decoder(nn.Module):
    def __init__(self, hidden_dim, filter_dim, n_head, dropout_rate, n_layers, pad_id):
        super(Decoder, self).__init__()
        self.pad_id = pad_id
        self.embed = nn.Embedding(out_dim, hidden_dim)
        self.pos_enc = PositionalEncoding(hidden_dim)
        self.scale = math.sqrt(hidden_dim)
        self.layers = nn.ModuleList([DecoderLayer(hidden_dim, filter_dim, n_head, dropout_rate)
                    for _ in range(n_layers)])

        self.last_norm = nn.LayerNorm(hidden_dim, eps=1e-6)

    def forward(self, tgt, memory=None, memory_mask=None):
        tgt_mask = target_mask(tgt, ignore_id=self.pad_id).to(tgt.device).unsqueeze(-3)
        
        decoder_output = self.embed(tgt)*self.scale + self.pos_enc(tgt)
        for i, dec_layer in enumerate(self.layers):
            decoder_output = dec_layer(decoder_output, tgt_mask, memory, memory_mask)
        decoder_output = self.last_norm(decoder_output)
        return decoder_output