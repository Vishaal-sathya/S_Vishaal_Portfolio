---
title: "Coding Attention Mechanisms Part 3: Implementing Causal Self-Attention and Dropout"
description: "A step-by-step implementation of causal attention (masked self-attention) and dropout weights in PyTorch."
author: "PhD Author"
date: "2026-07-22"
---

Causal attention, also known as masked attention, is a specialized form of self-attention. It restricts a model to only consider previous and current inputs in a sequence when processing any given token during the computation of attention scores. This is in contrast to the standard self-attention mechanism, which allows access to the entire input sequence at once.

> **Key Takeaways**
> - Causal attention restricts a model from accessing future tokens by masking attention weights above the diagonal.
> - Masking is implemented efficiently by setting attention scores of future tokens to negative infinity prior to softmax.
> - Attention dropout randomly zeros out weights during training, scaling the remaining values to prevent overfitting.

---

## Hiding future words with causal attention

In causal attention, we mask out the attention weights above the diagonal such that for a given input, the LLM cannot access future tokens when computing the context vectors using the attention weights. For example, for the word “journey” in the second row, we only keep the attention weights for the words before (“Your”) and in the current position (“journey”).

![[Pasted image 20260721174649.png]]

Our next step is to implement the causal attention mask in code. For that, we compute the attention weights using the softmax function as we have done previously. We initialize the input embeddings and import the `SelfAttentionV2` module from the previous chapter to compute the initial weights:

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

class SelfAttentionV2(nn.Module):
    def __init__(self, d_in, d_out, qkv_bias=False):
        super().__init__()
        self.W_query = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_key = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_value = nn.Linear(d_in, d_out, bias=qkv_bias)

    def forward(self, x):
        keys = self.W_key(x)
        queries = self.W_query(x)
        values = self.W_value(x)

        attn_scores = queries @ keys.T
        attn_weights = torch.softmax(attn_scores / keys.shape[-1]**0.5, dim=-1)
        context_vec = attn_weights @ values

        return context_vec

d_in = 3
d_out = 2

torch.manual_seed(789)
sa_v2 = SelfAttentionV2(d_in, d_out)

queries = sa_v2.W_query(inputs)
keys = sa_v2.W_key(inputs)
attn_scores = queries @ keys.T
attn_weights = torch.softmax(attn_scores / keys.shape[-1]**0.5, dim=-1)
print(attn_weights)
```
```python
# Output
tensor([[0.1921, 0.1646, 0.1652, 0.1550, 0.1721, 0.1510],
        [0.2041, 0.1659, 0.1662, 0.1496, 0.1665, 0.1477],
        [0.2036, 0.1659, 0.1662, 0.1498, 0.1664, 0.1480],
        [0.1869, 0.1667, 0.1668, 0.1571, 0.1661, 0.1564],
        [0.1830, 0.1669, 0.1670, 0.1588, 0.1658, 0.1585],
        [0.1935, 0.1663, 0.1666, 0.1542, 0.1666, 0.1529]],
       grad_fn=<SoftmaxBackward0>)
```

![[Pasted image 20260721175401.png]]
*One way to obtain the masked attention weight matrix in causal attention is to apply the softmax function to the attention scores, zeroing out the elements above the diagonal and normalizing the resulting matrix*

We can implement the second step using PyTorch's `tril` function to create a mask where the values above the diagonal are zero:

```python
context_length = attn_scores.shape[0]
mask_simple = torch.tril(torch.ones(context_length, context_length))
print(mask_simple)
```
```python
# Output
tensor([[1., 0., 0., 0., 0., 0.],
        [1., 1., 0., 0., 0., 0.],
        [1., 1., 1., 0., 0., 0.],
        [1., 1., 1., 1., 0., 0.],
        [1., 1., 1., 1., 1., 0.],
        [1., 1., 1., 1., 1., 1.]])
```

Now, we can multiply this mask with the attention weights to zero-out the values above the diagonal:

```python
masked_simple = attn_weights * mask_simple
print(masked_simple)
```
```python
# Output
tensor([[0.1921, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
        [0.2041, 0.1659, 0.0000, 0.0000, 0.0000, 0.0000],
        [0.2036, 0.1659, 0.1662, 0.0000, 0.0000, 0.0000],
        [0.1869, 0.1667, 0.1668, 0.1571, 0.0000, 0.0000],
        [0.1830, 0.1669, 0.1670, 0.1588, 0.1658, 0.0000],
        [0.1935, 0.1663, 0.1666, 0.1542, 0.1666, 0.1529]],
       grad_fn=<MulBackward0>)
```

The third step is to renormalize the attention weights to sum up to 1 again in each row. We can achieve this by dividing each element in each row by the sum in each row:

```python
row_sums = masked_simple.sum(dim=-1, keepdim=True)
masked_simple_norm = masked_simple / row_sums
print(masked_simple_norm)
```
```python
# Output
tensor([[1.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
        [0.5517, 0.4483, 0.0000, 0.0000, 0.0000, 0.0000],
        [0.3800, 0.3097, 0.3103, 0.0000, 0.0000, 0.0000],
        [0.2758, 0.2460, 0.2462, 0.2319, 0.0000, 0.0000],
        [0.2175, 0.1983, 0.1984, 0.1888, 0.1971, 0.0000],
        [0.1935, 0.1663, 0.1666, 0.1542, 0.1666, 0.1529]],
       grad_fn=<DivBackward0>)
```

The result is an attention weight matrix where the attention weights above the diagonal are zeroed-out, and the rows sum to 1.

While we could wrap up our implementation of causal attention at this point, we can still improve it. The softmax function converts its inputs into a probability distribution. When negative infinity values ($-\infty$) are present in a row, the softmax function treats them as zero probability.

![[Pasted image 20260721180005.png]]
*A more efficient way to obtain the masked attention weight matrix in causal attention is to mask the attention scores with negative infinity values before applying the softmax function*

```python
mask = torch.triu(torch.ones(context_length, context_length), diagonal=1)
masked = attn_scores.masked_fill(mask.bool(), -torch.inf)
attn_weights = torch.softmax(masked / keys.shape[-1]**0.5, dim=-1)
print(attn_weights)
```
```python
# Output
tensor([[1.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
        [0.5517, 0.4483, 0.0000, 0.0000, 0.0000, 0.0000],
        [0.3800, 0.3097, 0.3103, 0.0000, 0.0000, 0.0000],
        [0.2758, 0.2460, 0.2462, 0.2319, 0.0000, 0.0000],
        [0.2175, 0.1983, 0.1984, 0.1888, 0.1971, 0.0000],
        [0.1935, 0.1663, 0.1666, 0.1542, 0.1666, 0.1529]],
       grad_fn=<SoftmaxBackward0>)
```

---

## Masking additional attention weights with dropout

In the transformer architecture, including models like GPT, dropout in the attention mechanism is typically applied at two specific times: after calculating the attention weights or after applying the attention weights to the value vectors. Here we will apply the dropout mask after computing the attention weights:

```python
torch.manual_seed(123)
dropout = torch.nn.Dropout(.3) # 30% dropout rate
print(dropout(attn_weights))
```
```python
# Output
tensor([[1.4286, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
        [0.7881, 0.6405, 0.0000, 0.0000, 0.0000, 0.0000],
        [0.5428, 0.4424, 0.4433, 0.0000, 0.0000, 0.0000],
        [0.3941, 0.3515, 0.3518, 0.3313, 0.0000, 0.0000],
        [0.3107, 0.2833, 0.0000, 0.2696, 0.2815, 0.0000],
        [0.2764, 0.2376, 0.2380, 0.2203, 0.2379, 0.2184]],
       grad_fn=<MulBackward0>)
```

When applying dropout to an attention weight matrix with a rate of 30%, about a third of the elements in the matrix are randomly set to zero. To compensate for the reduction in active elements, the values of the remaining elements in the matrix are scaled up by a factor of 1/0.7 = 1.42. This scaling is crucial to maintain the overall balance of the attention weights, ensuring that the average influence of the attention mechanism remains consistent during both the training and inference phases.

---

## Implementing the Causal Attention Class

We will now incorporate the causal attention and dropout modifications into the `CausalAttention` Python class:

```python
import torch
import torch.nn as nn

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
```

> **Note on Dimension Transposition**: We transpose dimensions 1 and 2 of the keys, keeping the batch dimension at the first position (0).

While all added code lines should be familiar at this point, we now added a `self.register_buffer()` call in the `__init__` method. The use of `register_buffer` in PyTorch is not strictly necessary for all use cases but offers several advantages here. For instance, when we use the `CausalAttention` class in our LLM, buffers are automatically moved to the appropriate device (CPU or GPU) along with our model, which will be relevant when training our LLM. This means we do not need to manually ensure these tensors are on the same device as the model parameters, avoiding device mismatch errors.

We can use the `CausalAttention` class as follows:

```python
batch = torch.stack((inputs, inputs), dim=0)

context_length = batch.shape[1]
ca = CausalAttention(d_in, d_out, context_length, 0.0)
context_vecs = ca(batch)
print("context_vecs.shape:", context_vecs.shape)
```
```python
# Output
context_vecs.shape: torch.Size([2, 6, 2])
```

---

## Conclusion

So far we have focused on the concept and implementation of causal attention in neural networks. Next, we will expand on this concept and implement a multi-head attention module that implements several causal attention mechanisms in parallel.
