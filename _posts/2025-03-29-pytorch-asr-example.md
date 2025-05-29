---
title:  "ASR with PyTorch"
layout: post
published: false
---

# ASR with PyTorch: Exploring Phoneme Representations

I have a fascination with the sounds of languages (phonemes) and how they are processed. This came about from a project I did a few years ago in grad school. How ASR (automatic speech recognition) used to work did not include breaking down the sounds of the language and present them as pieces of the solution. You typically just got a final text representation.

I'm interested in seeing if the phonetic or phoneme representations can be pulled from the modern machine learning ASR pipelines. This is just an interest of mine with no defined goals beyond learning.

## Understanding ASR and Phonemes

Automatic Speech Recognition (ASR) systems convert spoken language into text. Traditional ASR systems typically output only the final text, but modern deep learning approaches can provide intermediate representations, including phonemes.

**Phonemes** are the smallest units of sound that distinguish one word from another in a particular language. For example, the words "bat" and "pat" differ only in their initial phonemes /b/ and /p/.

## Why PyTorch for ASR?

After reviewing various frameworks, I've decided to focus on PyTorch for this exploration:

PyTorch is an open-source machine learning framework based on the Torch library, primarily used for applications such as computer vision and natural language processing. Developed by Meta AI and now part of the Linux Foundation, it's known for its flexibility, ease of use, and dynamic computational graph. PyTorch facilitates the building and training of deep learning models, offering strong GPU acceleration and an imperative programming style favored by many Python developers.

Key advantages for ASR work:

- **Dynamic computational graph**: Makes it easier to work with variable-length speech inputs
- **Torchaudio**: A dedicated library for audio processing built on PyTorch
- **Rich ecosystem**: Many pre-trained ASR models with phoneme-level outputs
- **Research-friendly**: Easier to modify models to extract intermediate representations

## Extracting Phonemes with PyTorch and Wav2Vec 2.0

Let's create a practical example using PyTorch and the Wav2Vec 2.0 model to extract phoneme representations from speech.

### Setup

First, we need to install the required libraries:

```python
# Install required packages
# pip install torch torchaudio transformers
```

### Loading and Processing Audio

```python
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import IPython.display as ipd

# Load pre-trained model and processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

# Function to load and process audio
def process_audio(file_path):
    # Load audio
    waveform, sample_rate = torchaudio.load(file_path)
    
    # Resample if needed
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
        waveform = resampler(waveform)
        sample_rate = 16000
    
    # Convert to mono if needed
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)
    
    return waveform.squeeze(), sample_rate

# Example usage
audio_path = "path/to/your/audio.wav"  # Replace with your audio file
waveform, sample_rate = process_audio(audio_path)

# Display audio for verification
ipd.Audio(waveform.numpy(), rate=sample_rate)
```

### Extracting Phoneme Probabilities

To extract phoneme-level information, we need to access the logits from the model before they're converted to text:

```python
def extract_phoneme_probs(waveform, sample_rate=16000):
    # Process audio for model input
    input_values = processor(waveform, sampling_rate=sample_rate, return_tensors="pt").input_values
    
    # Get model outputs (without gradient calculation)
    with torch.no_grad():
        outputs = model(input_values)
        logits = outputs.logits
    
    # Convert logits to probabilities
    probs = torch.nn.functional.softmax(logits, dim=-1)
    
    return probs.squeeze(), processor.tokenizer.decoder

# Get phoneme probabilities
phoneme_probs, decoder = extract_phoneme_probs(waveform)
print(f"Shape of phoneme probabilities: {phoneme_probs.shape}")
```

### Visualizing Phoneme Activations

We can visualize the phoneme activations over time:

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_phoneme_activations(probs, decoder, top_k=10):
    # Get top-k phonemes at each time step
    top_probs, top_indices = torch.topk(probs, k=top_k, dim=1)
    
    # Convert to numpy for plotting
    top_probs = top_probs.numpy()
    top_indices = top_indices.numpy()
    
    # Get phoneme labels
    phoneme_map = {v: k for k, v in decoder.items()}
    
    # Create a time axis (assuming 50 frames per second for Wav2Vec 2.0)
    time_steps = np.arange(top_probs.shape[0]) / 50
    
    # Plot
    plt.figure(figsize=(15, 8))
    for i in range(min(5, top_k)):  # Plot top 5 phonemes
        plt.plot(time_steps, top_probs[:, i], label=f"Phoneme {phoneme_map.get(top_indices[0, i], top_indices[0, i])}")
    
    plt.xlabel("Time (seconds)")
    plt.ylabel("Probability")
    plt.title("Top Phoneme Activations Over Time")
    plt.legend()
    plt.tight_layout()
    plt.show()

# Visualize phoneme activations
plot_phoneme_activations(phoneme_probs, decoder)
```

### Decoding to Phonemes and Text

We can decode the model outputs to both phonemes and text:

```python
def decode_outputs(probs, decoder):
    # Get the most likely phoneme at each time step
    pred_ids = torch.argmax(probs, dim=-1)
    
    # Decode to phonemes (keeping all predictions)
    phoneme_sequence = [decoder.get(id.item(), f"[{id.item()}]") for id in pred_ids]
    
    # Apply CTC decoding logic (collapse repeated tokens and remove blanks)
    collapsed_phonemes = []
    prev_id = -1
    for id in pred_ids:
        if id != prev_id and id != 0:  # 0 is usually the blank token in CTC
            collapsed_phonemes.append(decoder.get(id.item(), f"[{id.item()}]"))
        prev_id = id
    
    # Join phonemes to get the text
    text = ''.join(collapsed_phonemes).replace('|', ' ')
    
    return phoneme_sequence, collapsed_phonemes, text

# Decode outputs
phoneme_sequence, collapsed_phonemes, text = decode_outputs(phoneme_probs, decoder)

print("Full phoneme sequence (including repetitions):")
print(phoneme_sequence[:50])  # Show first 50 for brevity
print("\nCollapsed phoneme sequence:")
print(collapsed_phonemes)
print("\nDecoded text:")
print(text)
```

## Exploring Phoneme-Based ASR with Wav2Vec-CTC

For a more direct approach to phoneme recognition, we can use a model specifically fine-tuned for phoneme recognition:

```python
# Load a model fine-tuned for phoneme recognition
phoneme_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-lv-60-espeak-cv-ft")
phoneme_model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-lv-60-espeak-cv-ft")

def transcribe_to_phonemes(waveform, sample_rate=16000):
    # Process audio for model input
    input_values = phoneme_processor(waveform, sampling_rate=sample_rate, return_tensors="pt").input_values
    
    # Get model predictions
    with torch.no_grad():
        logits = phoneme_model(input_values).logits
    
    # Decode phonemes
    predicted_ids = torch.argmax(logits, dim=-1)
    phoneme_string = phoneme_processor.batch_decode(predicted_ids)[0]
    
    return phoneme_string

# Get phoneme transcription
phoneme_transcription = transcribe_to_phonemes(waveform)
print("Phoneme transcription:")
print(phoneme_transcription)
```

## Comparing Different ASR Models for Phoneme Extraction

Different ASR models have different approaches to handling phonemes:

1. **Wav2Vec 2.0**: Provides frame-level features that can be mapped to phonemes
2. **DeepSpeech**: Uses CTC loss and can be modified to output phonemes
3. **Whisper**: More focused on end-to-end transcription but internal representations contain phonetic information
4. **Conformer**: Combines convolutional and transformer architectures for better phoneme recognition

## Conclusion

Modern ASR systems built with PyTorch can indeed provide access to phoneme-level representations, not just final text output. This opens up interesting possibilities for:

- Studying pronunciation patterns
- Developing language learning tools
- Creating more interpretable ASR systems
- Analyzing speech disorders

By leveraging PyTorch's flexibility and the rich ecosystem of pre-trained models, we can extract and visualize phoneme representations from speech signals. This allows for a deeper understanding of how ASR systems process the sounds of language.

## Resources

For further exploration:

- [PyTorch Audio Documentation](https://pytorch.org/audio/stable/tutorials/speech_recognition_pipeline_tutorial.html)
- [Wav2Vec 2.0 Paper](https://arxiv.org/abs/2006.11477)
- [ASR with CTC Decoder Tutorial](https://pytorch.org/audio/main/tutorials/asr_inference_with_ctc_decoder_tutorial.html)
- [Online ASR Tutorial](https://pytorch.org/audio/main/tutorials/online_asr_tutorial.html)
- [ASR from Scratch Implementation](https://github.com/alifarrokh/asr-from-scratch)
- [Building an ASR System with PyTorch & Hugging Face](https://www.kdnuggets.com/building-an-automatic-speech-recognition-system-with-pytorch-hugging-face)