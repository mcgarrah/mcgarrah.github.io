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

## Understanding Wav2Vec 2.0

Before diving into the code, it's helpful to understand how Wav2Vec 2.0 works:

Wav2Vec 2.0 is a self-supervised learning framework for speech recognition developed by Facebook AI. It works in two main stages:

1. **Pre-training**: The model learns speech representations from unlabeled audio data by solving a contrastive task that requires identifying the true future audio sample from a set of distractors.

2. **Fine-tuning**: The pre-trained model is then fine-tuned on labeled data using Connectionist Temporal Classification (CTC) loss for speech recognition tasks.

The architecture consists of:
- A CNN feature encoder that converts raw audio into latent speech representations
- A Transformer network that builds contextual representations
- A quantization module that discretizes the latent representations

This design allows Wav2Vec 2.0 to capture both phonetic and linguistic information from speech, making it ideal for our phoneme extraction task.

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
pip install torch torchaudio transformers matplotlib numpy soundfile librosa
```

### Obtaining Sample Audio

For this example, we'll download a sample audio file from LibriSpeech:

```python
# Download and extract a sample audio file from LibriSpeech
import os
import tarfile
import tempfile
from urllib.request import urlretrieve
import shutil

sample_dir = "sample_data"
os.makedirs(sample_dir, exist_ok=True)

# Target audio file paths - we'll create both FLAC and WAV versions
flac_path = os.path.join(sample_dir, "sample_audio.flac")
wav_path = os.path.join(sample_dir, "sample_audio.wav")

# Check which files exist and set the audio path accordingly
flac_exists = os.path.exists(flac_path)
wav_exists = os.path.exists(wav_path)

# Prefer WAV if it exists, otherwise use FLAC if it exists
if wav_exists:
    audio_path = wav_path
    print(f"Using existing WAV file: {wav_path}")
elif flac_exists:
    audio_path = flac_path
    print(f"Using existing FLAC file: {flac_path}")
else:
    # Neither file exists, need to download
    print("Sample audio not found. Downloading from LibriSpeech...")
    
    # Download a specific file from LibriSpeech
    audio_url = "https://www.openslr.org/resources/12/dev-clean/84/121123/84-121123-0001.flac"
    print(f"Downloading from {audio_url}...")
    urlretrieve(audio_url, flac_path)
    print(f"Sample audio downloaded to {flac_path}")
    audio_path = flac_path
    
    # Convert FLAC to WAV for better compatibility
    try:
        import librosa
        import soundfile as sf
        
        print("Converting FLAC to WAV format...")
        audio_data, sample_rate = librosa.load(flac_path, sr=None)
        sf.write(wav_path, audio_data, sample_rate)
        print(f"Converted audio saved to {wav_path}")
        audio_path = wav_path  # Use the WAV file
    except Exception as e:
        print(f"Error converting audio: {e}")
        print("Using original FLAC file instead.")

print(f"Using audio file: {audio_path}")
```

### Loading and Processing Audio

```python
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import matplotlib.pyplot as plt
import numpy as np
import os
import IPython.display as ipd

# Check if CUDA is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Function to load and process audio
def process_audio(file_path):
    # Load audio using alternative method if torchaudio fails
    try:
        # Try torchaudio first
        waveform, sample_rate = torchaudio.load(file_path)
    except RuntimeError:
        # Fall back to using librosa
        print(f"torchaudio failed to load {file_path}, trying librosa instead...")
        import librosa
        import numpy as np
        
        # Load with librosa (automatically handles various formats including FLAC)
        audio_data, sample_rate = librosa.load(file_path, sr=None)
        waveform = torch.from_numpy(audio_data).unsqueeze(0).float()
        print("Successfully loaded audio with librosa")
    
    # Resample if needed
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
        waveform = resampler(waveform)
        sample_rate = 16000
    
    # Convert to mono if needed
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)
    
    return waveform.squeeze(), sample_rate

# Load and process the audio
waveform, sample_rate = process_audio(audio_path)

# Display audio information
print(f"Sample rate: {sample_rate} Hz")
print(f"Waveform shape: {waveform.shape}")
print(f"Audio duration: {waveform.shape[0]/sample_rate:.2f} seconds")

# In a Jupyter notebook, you can play the audio with:
# ipd.Audio(waveform.numpy(), rate=sample_rate)
```

### Extracting Phoneme Probabilities

To extract phoneme-level information, we need to access the logits from the model before they're converted to text:

```python
# Load pre-trained model and processor
model_name = "facebook/wav2vec2-base-960h"
print(f"Loading model: {model_name}")

processor = Wav2Vec2Processor.from_pretrained(model_name)
model = Wav2Vec2ForCTC.from_pretrained(model_name).to(device)
print("Model loaded successfully!")

def extract_phoneme_probs(waveform, sample_rate=16000):
    # Process audio for model input
    input_values = processor(waveform, sampling_rate=sample_rate, return_tensors="pt").input_values
    input_values = input_values.to(device)
    
    # Get model outputs (without gradient calculation)
    with torch.no_grad():
        outputs = model(input_values)
        logits = outputs.logits
    
    # Convert logits to probabilities
    probs = torch.nn.functional.softmax(logits, dim=-1)
    
    return probs.cpu().squeeze(), processor.tokenizer.decoder

# Get phoneme probabilities
phoneme_probs, decoder = extract_phoneme_probs(waveform)
print(f"Shape of phoneme probabilities: {phoneme_probs.shape}")
print(f"Number of time steps: {phoneme_probs.shape[0]}")
print(f"Number of phoneme classes: {phoneme_probs.shape[1]}")
```

### Visualizing Phoneme Activations

We can visualize the phoneme activations over time:

```python
def plot_phoneme_activations(probs, decoder, top_k=5):
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
    
    # Plot for a subset of time steps for clarity
    start_idx = 0
    end_idx = min(200, len(time_steps))  # Show first 4 seconds or less
    
    for i in range(top_k):
        plt.plot(time_steps[start_idx:end_idx], 
                 top_probs[start_idx:end_idx, i], 
                 label=f"Class {top_indices[0, i]} ({phoneme_map.get(top_indices[0, i], '')})")
    
    plt.xlabel("Time (seconds)")
    plt.ylabel("Probability")
    plt.title("Top Phoneme Activations Over Time")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # For a blog post, save the figure instead of displaying it
    plt.savefig('phoneme_activations.png')
    # plt.show()  # This works in interactive environments like Jupyter
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

print("Full phoneme sequence (first 50 frames):")
print(phoneme_sequence[:50])
print("\nCollapsed phoneme sequence:")
print(collapsed_phonemes)
print("\nDecoded text:")
print(text)
```

## Exploring Phoneme-Based ASR with Wav2Vec-CTC

For a more direct approach to phoneme recognition, we can use a model specifically fine-tuned for phoneme recognition:

```python
# Load a model fine-tuned for phoneme recognition
phoneme_model_name = "facebook/wav2vec2-lv-60-espeak-cv-ft"
print(f"Loading phoneme model: {phoneme_model_name}")

try:
    # Import specific processor class for this model
    from transformers import Wav2Vec2ProcessorWithLM, Wav2Vec2CTCTokenizer, Wav2Vec2FeatureExtractor
    
    # Load the model components separately
    feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(phoneme_model_name)
    tokenizer = Wav2Vec2CTCTokenizer.from_pretrained(phoneme_model_name)
    phoneme_processor = Wav2Vec2Processor(feature_extractor=feature_extractor, tokenizer=tokenizer)
    phoneme_model = Wav2Vec2ForCTC.from_pretrained(phoneme_model_name).to(device)
    print("Phoneme model loaded successfully!")
    
    def transcribe_to_phonemes(waveform, sample_rate=16000):
        # Process audio for model input
        input_values = phoneme_processor(waveform, sampling_rate=sample_rate, return_tensors="pt").input_values
        input_values = input_values.to(device)
        
        # Get model predictions
        with torch.no_grad():
            logits = phoneme_model(input_values).logits
        
        # Decode phonemes
        predicted_ids = torch.argmax(logits, dim=-1)
        phoneme_string = phoneme_processor.batch_decode(predicted_ids)[0]
        
        return phoneme_string

    # Get phoneme transcription
    phoneme_transcription = transcribe_to_phonemes(waveform)
    print("\nPhoneme transcription:")
    print(phoneme_transcription)
    
except Exception as e:
    print(f"Error loading phoneme model: {e}")
    print("Skipping phoneme-specific model demonstration.")
```

## Analyzing Phoneme Distributions

We can analyze the distribution of phonemes in our sample:

```python
# Count phoneme occurrences
from collections import Counter

# Count non-blank phonemes
phoneme_counts = Counter([p for p in collapsed_phonemes if p != ''])

# Plot top 15 phonemes
top_phonemes = phoneme_counts.most_common(15)
phonemes, counts = zip(*top_phonemes)

# For visualization in a blog post
plt.figure(figsize=(12, 6))
plt.bar(phonemes, counts)
plt.title('Top 15 Phonemes in Sample')
plt.xlabel('Phoneme')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('phoneme_distribution.png')
# plt.show()  # For interactive environments

# For text-based output:
print("\nTop 15 phonemes and their counts:")
for phoneme, count in top_phonemes:
    print(f"{phoneme}: {count}")
```

## Comparing Phoneme Transcriptions

Let's compare the different phoneme transcriptions side by side:

```python
# Create a comparison of the different phoneme transcriptions
print("\nPhoneme Transcription Comparison:")
print("-" * 50)
print("Wav2Vec2 Base with CTC Decoding:")
print(text[:100] + "..." if len(text) > 100 else text)
print("-" * 50)

try:
    print("Specialized Phoneme Model:")
    print(phoneme_transcription[:100] + "..." if len(phoneme_transcription) > 100 else phoneme_transcription)
except NameError:
    print("Specialized model transcription not available")
print("-" * 50)
```

## Saving and Loading Models

For practical use, you might want to save and reuse models:

```python
# Save the model and processor for later use
output_dir = "saved_model"
os.makedirs(output_dir, exist_ok=True)

# Save the model
model.save_pretrained(output_dir)
processor.save_pretrained(output_dir)
print(f"Model and processor saved to {output_dir}")

# Later, you can load them back:
# loaded_processor = Wav2Vec2Processor.from_pretrained(output_dir)
# loaded_model = Wav2Vec2ForCTC.from_pretrained(output_dir)
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

## Code with Outputs

You can review the complete code for the Jupyter Notebook used for this post [PyTorch ASR Example](https://github.com/mcgarrah/pytorch-asr-phonemes){:target="_blank"} on Github. You can also see an example of a successful execution with the **Notebook Outputs** here at [PyTorch Notebook Code & Outputs](/assets/pdfs/pytorch_asr_phonemes.html){:target="_blank"}. That will let you see the results with the graphics.

## Resources

For further exploration:

- [PyTorch Audio Documentation](https://pytorch.org/audio/stable/tutorials/speech_recognition_pipeline_tutorial.html)
- [Wav2Vec 2.0 Paper](https://arxiv.org/abs/2006.11477)
- [ASR with CTC Decoder Tutorial](https://pytorch.org/audio/main/tutorials/asr_inference_with_ctc_decoder_tutorial.html)
- [Online ASR Tutorial](https://pytorch.org/audio/main/tutorials/online_asr_tutorial.html)
- [ASR from Scratch Implementation](https://github.com/alifarrokh/asr-from-scratch)
- [Building an ASR System with PyTorch & Hugging Face](https://www.kdnuggets.com/building-an-automatic-speech-recognition-system-with-pytorch-hugging-face)