---
title:  "ASR with PyTorch"
layout: post
published: false
---

I have a fascination with the sounds of languages (phonemes) and how they are processed. This came about from a project I did a few years ago in grad school. How ASR (automatic speech recognition) used to work did not include breaking down the sounds of the language and present them as pieces of the solution. You typically just got a final text representation.

I'm interested in seeing if the phonetic or phoneme representations can be pulled from the modern machine learning ASR pipelines. This is just an interest of mine with no defined goals beyond learning.

To do this I need to know te right things to use to do this work...

https://www.kdnuggets.com/building-an-automatic-speech-recognition-system-with-pytorch-hugging-face

https://pytorch.org/audio/stable/tutorials/speech_recognition_pipeline_tutorial.html

https://pytorch.org/audio/main/tutorials/asr_inference_with_ctc_decoder_tutorial.html

https://pytorch.org/audio/main/tutorials/online_asr_tutorial.html

https://github.com/alifarrokh/asr-from-scratch

PyTorch
TensorFlow
Scikit-Learn
Torch
PyTorch Lightning
Jax
NumPY

Torch is an open-source machine learning library, a scientific computing framework, and a scripting language based on Lua. It provides LuaJIT interfaces to deep learning algorithms implemented in C. It was created by the Idiap Research Institute at EPFL.

PyTorch is an open-source machine learning framework based on the Torch library, primarily used for applications such as computer vision and natural language processing. Developed by Meta AI and now part of the Linux Foundation, it's known for its flexibility, ease of use, and dynamic computational graph. PyTorch facilitates the building and training of deep learning models, offering strong GPU acceleration and an imperative programming style favored by many Python developers. It provides high-level features for tensor computation, similar to NumPy but with GPU support, and includes tools for building neural networks with automatic differentiation.

TensorFlow:
A widely-used framework, particularly strong in production environments and large-scale deployments. It offers tools like Keras for simplified model building.
TensorFlow is defined as an open-source platform and framework for machine learning, which includes libraries and tools based on Python and Java — designed with the objective of training machine learning and deep learning models on data.

Keras:
An API that can run on top of TensorFlow, Theano or CNTK. Keras focuses on user-friendliness, enabling quick prototyping and model development.
Keras is a high-level, user-friendly Python API for building and training deep learning models, simplifying the process and making it more accessible for developers, especially those new to the field. 

Scikit-learn:
A versatile library for classical machine learning algorithms, covering tasks like data preprocessing, model selection, and evaluation. It's known for its simplicity and extensive documentation.
Scikit-learn, also known as sklearn, is an open-source, machine learning and data modeling library for Python.
Scikit-learn (sklearn) is a free, open-source Python library for machine learning, offering a wide range of algorithms and tools for tasks like classification, regression, clustering, and data preprocessing, built on NumPy, SciPy, and Matplotlib. 

JAX:
A framework developed by Google, emphasizing high-performance numerical computation and is often favored for research and complex model development.
JAX is a Python library and machine learning framework developed by Google that provides a high-performance numerical computing platform, particularly for machine learning research, by combining NumPy-like APIs with automatic differentiation and XLA acceleration.
JAX is used in various machine learning tasks, including building and training neural networks, performing scientific simulations, and developing other numerical applications. 

Chainer:
A flexible framework with a dynamic computation graph, similar to PyTorch, making it suitable for research and experimentation.
Chainer is a flexible, Python-based deep learning framework that uses a "define-by-run" or dynamic computational graph approach, allowing for intuitive and easy-to-debug code, and supports various network architectures and CUDA/cuDNN for high-performance training and inference. 
Chainer's core concept is the "define-by-run" (Dynamic Computational Graphs) approach, where the network is defined dynamically during the forward computation, rather than being statically defined beforehand like in frameworks like TensorFlow or Theano.

Fastai:
A library built on top of PyTorch that provides higher-level abstractions and simplifies the training process, particularly useful for rapid prototyping.
fastai is a high-level, open-source deep learning library built on top of PyTorch, designed to simplify and accelerate the development of deep learning models, especially for practitioners and researchers who want to achieve state-of-the-art results efficiently.

Caffe:
An older framework known for its speed and efficiency, often used in production settings, but less flexible for research compared to PyTorch.
CAFFE is an open-source deep learning architecture design tool, originally developed at UC Berkeley and written in C++ with a Python interface.

PyTorch Geometric:
An extension library for PyTorch, specifically designed for implementing graph neural networks.
Theano:
A predecessor to TensorFlow and PyTorch, primarily focused on automatic differentiation, but less actively developed now.
Catalyst:
A high-level framework built on PyTorch, designed to streamline research and development by emphasizing reproducibility and efficient experimentation.
Google Cloud Platform and Vertex AI:
Cloud-based platforms offering tools and services for training and deploying machine learning models, including support for PyTorch.

spaCy · Industrial-strength Natural Language Processing in Python
spaCy is designed to help you do real work — to build real products, or gather real insights. The library respects your time, and tries to avoid wasting it.
