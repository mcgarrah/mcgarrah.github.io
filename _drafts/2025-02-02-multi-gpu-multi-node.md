---
title:  "Multiple GPUs on Multiple Nodes in the Homelab"
layout: post
published: false
---

How can I get my multiple CPUs with RAM and GPUs with vRAM all running my machine learning models?

I've got a pile of Nvidia Quadro P400s and P620s that are useful for video codex processing for my video library. I also have two laptops with MX150 GP107 mobile GPUs. But when they are not doing that, I would like them to do some AI/ML work.

<!-- excerpt-end -->

[Scaling your LLM inference workloads: multi-node deployment with TensorRT-LLM and Triton on Amazon EKS](https://aws.amazon.com/blogs/hpc/scaling-your-llm-inference-workloads-multi-node-deployment-with-tensorrt-llm-and-triton-on-amazon-eks/) talks about Nvidia Triton for distributing LLM workload across nodes using MPI transport.

[Ollama, how can I use all the GPUs I have?](https://stackoverflow.com/questions/78481760/ollama-how-can-i-use-all-the-gpus-i-have) just brute forces this with multiple instances of Ollama on different IP address and ports. We should be able to make them aware of each other.

[Multiple Ollama instances](https://github.com/open-webui/open-webui/issues/278)

[LiteLLM](https://github.com/BerriAI/litellm) Call all LLM APIs using the OpenAI format [Bedrock, Huggingface, VertexAI, TogetherAI, Azure, OpenAI, Groq etc.]

[Llama.cpp now supports distributed inference across multiple machines](https://github.com/ollama/ollama/issues/4643) with [Feature: Add Support for Distributed Inferencing](https://github.com/ollama/ollama/pull/6729) to support this.

[Exo](https://github.com/exo-explore/exo) Forget expensive NVIDIA GPUs, unify your existing devices into one powerful GPU: iPhone, iPad, Android, Mac, Linux, pretty much any device!

Comparing GPUs...
https://technical.city/en/video/Quadro-P620-vs-GeForce-MX150-GP107
https://technical.city/en/video/Quadro-P400-vs-Quadro-P620

## GPU comparisons

[Nvidia Tesla K80](https://www.nvidia.com/en-gb/data-center/tesla-k80/) that are just two 12gb vram gpu cards plastered together which are all over the place for pricing between $50 - $250 on [ebay](https://www.ebay.com/itm/285269093876).

Here is a list of GPUs to review:

* Nvidia Tesla P40
* Nvidia Tesla K40m
* Nvidia Tesla M40
* Nvidia Tesla M60
* NVIDIA GeForce GTX TITAN XP
* Nvidia GeForce RTX 3060 12GB on [ebay](https://www.ebay.com/itm/126046122624)
