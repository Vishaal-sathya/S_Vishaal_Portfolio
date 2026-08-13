---
title: "Implementing a GPT Model Part 1: Architecture and Layer Normalization"
description: "A step-by-step guide to assembling a GPT placeholder architecture and implementing layer normalization in PyTorch."
author: "PhD Author"
date: "2026-08-13"
---

Large Language Models, such as GPT (which stands for generative pretrained transformer), are large deep neural network architectures designed to generate new text one token at a time. Despite their considerable size, the model architecture is highly repetitive, as many of its components are duplicated throughout the network.

Previously, we used smaller embedding dimensions for simplicity to ensure that the concepts and examples could comfortably fit on a single page. Now, we are scaling up to the size of a small GPT-2 model, specifically the 124-million-parameter version.

In the context of deep learning and models like GPT, the term "parameters" refers to the trainable weights of the model. These weights are essentially the internal variables of the network that are adjusted and optimized during the training process to minimize a specific loss function. This optimization process allows the model to learn from the training data.

![[Pasted image 20260722173841.png]]
*A GPT model architecture. In addition to the embedding layers, it consists of one or more transformer blocks containing the masked multi-head attention module.*

> **Key Takeaways**
> - The final GPT architecture consists of token and positional embeddings, sequential transformer blocks, layer normalization, and a linear output head.
> - A placeholder model provides a structural overview of the data flow before implementing the full transformer block.
> - Layer normalization adjusts activations across the feature dimension to have a zero mean and unit variance, which improves training stability.

---

## Coding an LLM architecture

We specify the configuration of the small GPT-2 model via the following Python dictionary. We will use this configuration in the code examples that follow.

```python
GPT_CONFIG_124M = {
    "vocab_size": 50257,    # Vocabulary size
    "context_length": 1024, # Context length
    "emb_dim": 768,         # Embedding dimension
    "n_heads": 12,          # Number of attention heads
    "n_layers": 12,         # Number of transformer blocks
    "drop_rate": 0.1,       # Dropout rate
    "qkv_bias": False       # Query-Key-Value bias
}
```

Using this configuration, we will implement a GPT placeholder architecture named `DummyGPTModel`, as shown in the figure below. This placeholder provides a big-picture view of how everything fits together and clarifies what other components we need to assemble the full architecture. The numbered boxes in the figure illustrate the order in which we will tackle the individual concepts required to code the final model. We will start with step 1, a placeholder GPT backbone.

![[Pasted image 20260722174855.png]]
*Placeholder GPT architecture illustrating the sequence of implementation steps.*

```python
import torch
import torch.nn as nn

class DummyTransformerBlock(nn.Module):
    def __init__(self, cfg):
        super().__init__()

    def forward(self, x):
        return x

class DummyLayerNorm(nn.Module):
    def __init__(self, normalized_shape, eps=1e-5):
        super().__init__()

    def forward(self, x):
        return x

class DummyGPTModel(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.tok_emb = nn.Embedding(cfg['vocab_size'], cfg['emb_dim'])
        self.pos_emb = nn.Embedding(cfg['context_length'], cfg['emb_dim'])
        self.drop_emb = nn.Dropout(cfg['drop_rate'])
        
        # Placeholder transformer blocks
        self.trf_blocks = nn.Sequential(
            *[DummyTransformerBlock(cfg) for _ in range(cfg['n_layers'])]
        )

        # Placeholder layer normalization
        self.final_norm = DummyLayerNorm(cfg['emb_dim'])
        self.out_head = nn.Linear(cfg['emb_dim'], cfg['vocab_size'], bias=False)

    def forward(self, in_idx):
        batch_size, seq_len = in_idx.shape
        tok_embeds = self.tok_emb(in_idx)
        pos_embeds = self.pos_emb(torch.arange(seq_len, device=in_idx.device))
        x = tok_embeds + pos_embeds
        x = self.drop_emb(x)
        x = self.trf_blocks(x)
        x = self.final_norm(x)
        logits = self.out_head(x)
        return logits
```

The model architecture in the `DummyGPTModel` class consists of token and positional embeddings, dropout, a series of transformer blocks (`DummyTransformerBlock`), a final layer normalization (`DummyLayerNorm`), and a linear output layer (`out_head`).

The forward method describes the data flow through the model. It computes token and positional embeddings for the input indices, applies dropout, processes the data through the transformer blocks, applies normalization, and finally produces logits with the linear output layer.

Next, we will prepare the input data and initialize a new GPT model to illustrate its usage. To implement these steps, we tokenize a batch consisting of two text inputs for the GPT model using the `tiktoken` tokenizer.

```python
import tiktoken

tokenizer = tiktoken.get_encoding("gpt2")
batch = []
txt1 = "Every effort moves you"
txt2 = "Every day holds a"

batch.append(torch.tensor(tokenizer.encode(txt1)))
batch.append(torch.tensor(tokenizer.encode(txt2)))
batch = torch.stack(batch, dim=0)

print(batch)
```

```python
# Output
tensor([[6109, 3626, 6100,  345],
        [6109, 1110, 6622,  257]])
```

We initialize a new 124-million-parameter `DummyGPTModel` instance and feed it the tokenized batch.

```python
torch.manual_seed(123)
model = DummyGPTModel(GPT_CONFIG_124M)
logits = model(batch)

print("Output shape:", logits.shape)
print(logits)
```

```python
# Output
Output shape: torch.Size([2, 4, 50257])
tensor([[[-1.2034,  0.3201, -0.7130,  ..., -1.5548, -0.2390, -0.4667],
         [-0.1192,  0.4539, -0.4432,  ...,  0.2392,  1.3469,  1.2430],
         [ 0.5307,  1.6720, -0.4695,  ...,  1.1966,  0.0111,  0.5835],
         [ 0.0139,  1.6754, -0.3388,  ...,  1.1586, -0.0435, -1.0400]],

        [[-1.0908,  0.1798, -0.9484,  ..., -1.6047,  0.2439, -0.4530],
         [-0.7860,  0.5581, -0.0610,  ...,  0.4835, -0.0077,  1.6621],
         [ 0.3567,  1.2698, -0.6398,  ..., -0.0162, -0.1296,  0.3717],
         [-0.2407, -0.7349, -0.5102,  ...,  2.0057, -0.3694,  0.1814]]],
       grad_fn=<UnsafeViewBackward0>)
```

---

## Normalizing activations with layer normalization

Training deep neural networks with many layers can sometimes prove challenging due to problems like vanishing or exploding gradients. This makes it difficult for the network to find the right weights that minimize the loss function.

We will now implement layer normalization to improve the stability and efficiency of neural network training. The main idea behind layer normalization is to adjust the activations (outputs) of a neural network layer to have a mean of zero and a variance of one, also known as unit variance.

![[Pasted image 20260722185540.png]]
*An illustration of layer normalization where the six outputs of the layer, also called activations, are normalized such that they have a zero mean and a unit variance.*

To apply normalization, we subtract the mean and divide by the square root of the variance, which is also known as the standard deviation.

```python
class LayerNorm(nn.Module):
    def __init__(self, emb_dim):
        super().__init__()
        self.eps = 1e-5
        self.scale = nn.Parameter(torch.ones(emb_dim))
        self.shift = nn.Parameter(torch.zeros(emb_dim))

    def forward(self, x):
        mean = x.mean(dim=-1, keepdim=True)
        var = x.var(dim=-1, keepdim=True, unbiased=False)
        norm_x = (x - mean) / torch.sqrt(var + self.eps)
        return self.scale * norm_x + self.shift
```

This specific implementation of layer normalization operates on the last dimension of the input tensor `x`, which represents the embedding dimension (`emb_dim`). The variable `eps` is a small constant (epsilon) added to the variance to prevent division by zero during normalization. The scale and shift are two trainable parameters, of the same dimension as the input, that the model automatically adjusts during training if it determines that doing so improves performance on its training task. This allows the model to learn the appropriate scaling and shifting that best suit the data it processes.

Let us try the `LayerNorm` module in practice and apply it to a batch input.

```python
ln = LayerNorm(emb_dim=5)
batch_example = torch.randn(2, 5)
out_ln = ln(batch_example)
mean = out_ln.mean(dim=-1, keepdim=True)
var = out_ln.var(dim=-1, unbiased=False, keepdim=True)

print("Mean:\n", mean)
print("Variance:\n", var)
```

```python
# Output
Mean:
 tensor([[ 0.0000e+00],
        [-2.3842e-08]], grad_fn=<MeanBackward1>)
Variance:
 tensor([[1.0000],
        [1.0000]], grad_fn=<VarBackward0>)
```

> **Layer normalization vs. batch normalization**
> If you are familiar with batch normalization, a common and traditional normalization method for neural networks, you may wonder how it compares to layer normalization. Unlike batch normalization, which normalizes across the batch dimension, layer normalization normalizes across the feature dimension. LLMs often require significant computational resources, and the available hardware or the specific use case can dictate the batch size during training or inference. Since layer normalization normalizes each input independently of the batch size, it offers more flexibility and stability in these scenarios. This is particularly beneficial for distributed training or when deploying models in environments where resources are constrained.

We have now covered two of the building blocks we will need to implement the full GPT architecture. In the next section, we will look at the GELU activation function, which is one of the activation functions commonly used in modern LLMs.
