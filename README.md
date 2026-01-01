# Agentic Catify

**Agentic Catify** is an intelligent automated pipeline designed to transform standard short-form video content into high-retention videos featuring cat memes. By leveraging advanced AI models for audio transcription and semantic understanding, the system replaces original video visuals with contextually relevant cat images while preserving the original audio track.

| Demo 1 | Demo 2 |
|------|------|
| [![Demo 1](https://img.youtube.com/vi/asN08puC5sE/hqdefault.jpg)](https://www.youtube.com/shorts/asN08puC5sE) | [![Demo 2](https://img.youtube.com/vi/8sxKK_3d9Wc/hqdefault.jpg)](https://www.youtube.com/shorts/8sxKK_3d9Wc) |


## 🚀 How It Works

The pipeline executes a sophisticated multi-step process to generate the final video:

1.  **Audio Extraction**: Isolates the audio track from the input video file using `moviepy`.
2.  **Transcription**: Uses **OpenAI Whisper** to generate a precise timestamped transcript of the spoken content.
3.  **Semantic Mapping**: An Agentic LLM (powered by **GPT-3.5-turbo** and **LangChain**) analyzes the transcript segments and maps them to specific cat image tags available via the **CATAAS (Cat as a Service) API**. It determines the most appropriate visual for every segment of the video.
4.  **Image Generation & Processing**: 
    - Fetches relevant cat images/GIFs based on the selected tags.
    - Dynamically resizes and centers images onto a 9:16 vertical canvas (optimized for TikTok/Shorts/Reels).
    - Overlays the transcript text as captions directly onto the images.
5.  **Video Synthesis**: Reassembles the processed images into a video sequence synchronized perfectly with the original audio timestamps to create a seamless final output.

## 🛠️ Tech Stack

-   **LangChain**: Orchestrates the LLM workflow and prompt management.
-   **OpenAI GPT-3.5-turbo**: Drives the semantic understanding and image selection logic.
-   **OpenAI Whisper**: Provides state-of-the-art speech-to-text transcription.
-   **MoviePy**: Handles video and audio manipulation (extraction, composition, and writing).
-   **Pillow (PIL)**: Manages image processing, resizing, and caption drawing.
-   **CATAAS API**: Source for the diverse collection of cat images and GIFs.

## 📦 Usage

Ensure you have your environment variables set up (specifically `OPENAI_API_KEY`) and dependencies installed.

```python
from catify import CatfyPipeline

# Initialize the pipeline
pipeline = CatfyPipeline()

# Run the transformation on a video file
pipeline.forward("path/to/input_video.mp4", output_path="output_directory")
```

The system will output a final `catify_vid.mp4` in the specified output directory.
