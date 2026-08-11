---
title: "Coding Attention Mechanisms Part 4: Implementing Multi-Head Attention"
description: "A step-by-step implementation of multi-head attention wrapper and a computationally efficient tensor-parallel multi-head attention module using PyTorch."
author: "PhD Author"
date: "2026-07-22"
---

The term “multi-head” refers to dividing the attention mechanism into multiple “heads,” each operating independently. In this context, a single causal attention module can be considered single-head attention, where there is only one set of attention weights processing the input sequentially.

> **Key Takeaways**
> - Multi-head attention routes inputs through multiple independent attention layers, each with distinct weight parameters.
> - Processing heads in parallel requires specific tensor reshaping and transposition to preserve token boundaries in memory.
> - Transitioning from a sequential module list wrapper to a unified tensor parallel implementation significantly improves computational efficiency.

---

## Stacking multiple single-head attention layers

In practical terms, implementing multi-head attention involves creating multiple instances of the self-attention mechanism, each with its own weights, and then combining their outputs.

![[Pasted image 20260721185453.png]]
*The multi-head attention module includes two single-head attention modules stacked on top of each other. So, instead of using a single matrix Wv for computing the value matrices, in a multi-head attention module with two heads, we now have two value weight matrices: Wv1 and Wv2. The same applies to the other weight matrices, WQ and Wk. We obtain two sets of context vectors Z1 and Z2 that we can combine into a single context vector matrix Z.*

In code, we can achieve this by implementing a simple `MultiHeadAttentionWrapper` class that stacks multiple instances of our previously implemented `CausalAttention` module. We define all prerequisites, including input tensors and the `CausalAttention` class, to ensure the code block is fully executable:

```python
import torch
import torch.nn as nn

inputs = torch.tensor(
 [[0.43, 0.15, 0.89], # Your (x^1)
  [0.55, 0.87, 0.66], # journey (x^2)
  [0.57, 0.85, 0.64], # starts (x^3)
  [0.22, 0.58, 0.33], # with (x^4)
  [0.77, 0.25, 0.10], # one (x^5)
  [0.05, 0.80, 0.55]] # step (x^6)
)
batch = torch.stack((inputs, inputs), dim=0)

class CausalAttention(nn.Module):
    def __init__(self, d_in, d_out, context_length, dropout, qkv_bias=False):
        super().__init__()
        self.d_out = d_out
        self.W_query = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_key = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_value = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.dropout = nn.Dropout(dropout)
        self.register_buffer(
            'mask',
            torch.triu(torch.ones(context_length, context_length), diagonal=1)
        )

    def forward(self, x):
        b, num_tokens, d_in = x.shape
        keys = self.W_key(x)
        queries = self.W_query(x)
        values = self.W_value(x)

        attn_scores = queries @ keys.transpose(1, 2)
        attn_scores.masked_fill_(self.mask.bool()[:num_tokens, :num_tokens], -torch.inf)
        attn_weights = torch.softmax(attn_scores / keys.shape[-1]**0.5, dim=-1)
        attn_weights = self.dropout(attn_weights)
        context_vec = attn_weights @ values

        return context_vec

class MultiHeadAttentionWrapper(nn.Module):
    def __init__(self, d_in, d_out, context_length, dropout, num_heads, qkv_bias=False):
        super().__init__()
        self.heads = nn.ModuleList(
            [CausalAttention(d_in, d_out, context_length, dropout, qkv_bias) 
                for _ in range(num_heads)]
        )

    def forward(self, x):
        return torch.cat([head(x) for head in self.heads], dim=-1)

torch.manual_seed(123)
context_length = batch.shape[1] # This is the number of tokens
d_in, d_out = 3, 2

mha = MultiHeadAttentionWrapper(
 d_in, d_out, context_length, 0.0, num_heads=2
)
context_vecs = mha(batch)
print(context_vecs)
```
```python
# Output
tensor([[[-0.4519,  0.2216,  0.4772,  0.1063],
         [-0.5874,  0.0058,  0.5891,  0.3257],
         [-0.6300, -0.0632,  0.6202,  0.3860],
         [-0.5675, -0.0843,  0.5478,  0.3589],
         [-0.5526, -0.0981,  0.5321,  0.3428],
         [-0.5299, -0.1081,  0.5077,  0.3493]],

        [[-0.4519,  0.2216,  0.4772,  0.1063],
         [-0.5874,  0.0058,  0.5891,  0.3257],
         [-0.6300, -0.0632,  0.6202,  0.3860],
         [-0.5675, -0.0843,  0.5478,  0.3589],
         [-0.5526, -0.0981,  0.5321,  0.3428],
         [-0.5299, -0.1081,  0.5077,  0.3493]]], grad_fn=<CatBackward0>)
```

Up to this point, we have implemented a `MultiHeadAttentionWrapper` that combined multiple single-head attention modules. However, these are processed sequentially via list comprehension inside the forward method.

In contrast, the following `MultiHeadAttention` class integrates the multi-head functionality within a single class. It splits the input into multiple heads by reshaping the projected query, key, and value tensors, and then combines the results from these heads after computing attention.

---

## Implementing the Efficient MultiHeadAttention Class

```python
import torch
import torch.nn as nn

class MultiHeadAttention(nn.Module):
    def __init__(self, d_in, d_out, context_length, dropout, num_heads, qkv_bias=False):
        super().__init__()
        assert (d_out % num_heads == 0), "d_out must be divisible by num_heads"

        self.d_out = d_out
        self.num_heads = num_heads
        self.head_dim = d_out // num_heads
        self.W_query = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_key = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_value = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.dropout = nn.Dropout(dropout)
        self.out_proj = nn.Linear(d_out, d_out)
        self.register_buffer('mask', torch.triu(torch.ones(context_length, context_length), diagonal=1))

    def forward(self, x):
        b, num_tokens, d_in = x.shape
        keys = self.W_key(x)
        queries = self.W_query(x)
        values = self.W_value(x)

        keys = keys.view(b, num_tokens, self.num_heads, self.head_dim)
        queries = queries.view(b, num_tokens, self.num_heads, self.head_dim)
        values = values.view(b, num_tokens, self.num_heads, self.head_dim)

        keys = keys.transpose(1, 2)
        queries = queries.transpose(1, 2)
        values = values.transpose(1, 2)

        attn_scores = queries @ keys.transpose(2, 3)
        mask_bool = self.mask.bool()[:num_tokens, :num_tokens]
        attn_scores.masked_fill_(mask_bool, -torch.inf)
        attn_weights = torch.softmax(attn_scores / keys.shape[-1]**0.5, dim=-1)
        attn_weights = self.dropout(attn_weights)

        context_vec = (attn_weights @ values).transpose(1, 2)
        context_vec = context_vec.contiguous().view(b, num_tokens, self.d_out)
        context_vec = self.out_proj(context_vec)

        return context_vec
```

---

## Tensor Reshaping and Memory Layout

What we are trying to do is to create weight parameters of size num_tokens x head_dim for each head. So if we have two heads, we will have two W_key operations of size num_tokens x head_dim for each batch.

Initially we have a single weight matrix of dimension batch x num_tokens x d_out and we convert it to batch x num_heads x num_tokens x head_dim, but if you notice we are not directly reshaping it to the final dimensions. We first reshape it to batch x num_tokens x num_heads x head_dim and then we transpose the second and third dimensions to get the result.

The reason is because the matrix is arranged in memory as follows:

```
Batch0

Token1
[embeddings]

Token2
[embeddings]

Token3
[embeddings]

Token4
[embeddings]
```

So we now split every token embedding across the number of heads we want:

```
Batch0

Token1
[head1_embeddings, head2_embeddings, head3_embeddings]

Token2
[head1_embeddings, head2_embeddings, head3_embeddings]

Token3
[head1_embeddings, head2_embeddings, head3_embeddings]

Token4
[head1_embeddings, head2_embeddings, head3_embeddings]
```

If we tried to reshape it directly to batch x num_heads x num_tokens x head_dim, PyTorch would interpret the matrix as:

```
Batch

Head0

Token1
Token2
...

Head1
...
```

But the memory is **not arranged that way**.

The first set of numbers belongs completely to token 1, not to head 1 across all tokens. So the heads would become garbage mixtures of different tokens.

---

## Merging Attention Heads and Output Projection

The final phase of the `MultiHeadAttention` forward pass merges the independent attention heads back into a single unified context tensor for each token. Initially, batched matrix multiplication computes context vectors for each head, resulting in a tensor of dimension `(batch, heads, tokens, head_dim)` (for example, `(2, 12, 4, 64)`). To group the outputs of different heads by token, we transpose the tensor dimensions to `(batch, tokens, heads, head_dim)` (yielding `(2, 4, 12, 64)`). Because this transposition only alters the logical layout indexing (strides) without copying data, we call `.contiguous()` to physically rearrange the data in memory. This contiguity is required before utilizing `.view()`, which flattens the last two dimensions to concatenate the heads into a unified embedding dimension of size `self.d_out` ($12 \times 64 = 768$), producing a shape of `(batch, tokens, d_out)` (yielding `(2, 4, 768)`).

For a single token, this flattening and concatenation process modifies the memory layout as follows:

```text
Before view() [Independent Attention Heads]:
Head 1:   [64 values]
Head 2:   [64 values]
...
Head 12:  [64 values]

After view() [Concatenated Context Vector]:
[ Head 1 (64) | Head 2 (64) | ... | Head 12 (64) ]  --->  768 dimensions
```

Once the heads are concatenated, the combined representation is passed through a linear projection layer `self.out_proj` of shape `(d_out, d_out)` (representing `nn.Linear(768, 768)`). This projection layer is critical because a direct concatenation simply groups the independent attention outputs adjacent to one another without interaction. The projection adds learnable weights to this step so if for example head one learns grammar, head 2 learns long-range dependencies etc, the projection matrix can learn things like 40% of head 1 + 20% of head 2...

---

## Verifying the Multi-Head Attention Output

The `MultiHeadAttention` class can be used similarly to the `SelfAttention` and `CausalAttention` classes we implemented earlier:

```python
# Assuming 'inputs' and 'batch' are defined as before:
torch.manual_seed(123)
batch_size, context_length, d_in = batch.shape
d_out = 2
mha = MultiHeadAttention(d_in, d_out, context_length, 0.0, num_heads=2)
context_vecs = mha(batch)
print(context_vecs)
print("context_vecs.shape:", context_vecs.shape)
```
```python
# Output
tensor([[[0.3190, 0.4858],
         [0.2943, 0.3897],
         [0.2856, 0.3593],
         [0.2693, 0.3873],
         [0.2639, 0.3928],
         [0.2575, 0.4028]],

        [[0.3190, 0.4858],
         [0.2943, 0.3897],
         [0.2856, 0.3593],
         [0.2693, 0.3873],
         [0.2639, 0.3928],
         [0.2575, 0.4028]]], grad_fn=<ViewBackward0>)
context_vecs.shape: torch.Size([2, 6, 2])
```

We have now implemented the `MultiHeadAttention` class that we will use when we implement and train the LLM. Note that while the code is fully functional, we used relatively small embedding sizes and numbers of attention heads to keep the outputs readable.

For comparison, the smallest GPT-2 model (117 million parameters) has 12 attention heads and a context vector embedding size of 768. The largest GPT-2 model (1.5 billion parameters) has 25 attention heads and a context vector embedding size of 1,600. The embedding sizes of the token inputs and context embeddings are the same in GPT models (d_in = d_out).
