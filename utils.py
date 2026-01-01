
#gets image from api
def get_image(tag: str, caption: str, seq_id: int):
    """
    Generate a cat image from CATAAS, place it centered on a 9:16 black canvas,
    and save as PNG. If the image is a GIF, the LAST frame is used.

    Image is NEVER cropped.
    Image can scale UP (up to a limit) or DOWN to fit canvas.
    """

    import requests
    from io import BytesIO
    from PIL import Image, ImageSequence, ImageDraw, ImageFont

    # --- download image ---
    url = f"https://cataas.com/cat/{tag}"
    resp = requests.get(url)
    resp.raise_for_status()

    img_bytes = BytesIO(resp.content)

    # --- load with PIL ---
    img = Image.open(img_bytes)

    # --- handle GIF: take LAST frame ---
    if getattr(img, "is_animated", False):
        frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
        img = frames[-1]

    img = img.convert("RGB")

    iw, ih = img.size

    # --- canvas ---
    CANVAS_W, CANVAS_H = 1080, 1920
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (0, 0, 0))

    # --- scaling logic ---
    fit_scale = min(CANVAS_W / iw, CANVAS_H / ih)

    MAX_SCALE_UP = 2.0   # 👈 tweak this (1.5–2.5 are reasonable)

    scale = min(fit_scale, MAX_SCALE_UP)

    # resize if needed
    if scale != 1.0:
        new_w = int(iw * scale)
        new_h = int(ih * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        iw, ih = img.size

    # --- center ---
    x = (CANVAS_W - iw) // 2
    y = (CANVAS_H - ih) // 2

    canvas.paste(img, (x, y))

    # --- draw caption ---
    if caption:
        draw = ImageDraw.Draw(canvas)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 60)
        except IOError:
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except IOError:
                font = ImageFont.load_default()

        # Wrap text logic
        margin = 40
        max_width = CANVAS_W - 2 * margin
        lines = []
        words = caption.split()
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            
            if hasattr(draw, "textbbox"):
                bbox = draw.textbbox((0, 0), test_line, font=font)
                w = bbox[2] - bbox[0]
            else:
                w, _ = draw.textsize(test_line, font=font)
            
            if w > max_width:
                if len(current_line) == 1:
                    lines.append(current_line[0])
                    current_line = []
                else:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))

        # Calculate heights
        if hasattr(draw, "textbbox"):
            bbox_sample = draw.textbbox((0, 0), "Ag", font=font)
            line_height = (bbox_sample[3] - bbox_sample[1]) * 1.2
        else:
            _, h = draw.textsize("Ag", font=font)
            line_height = h * 1.2

        total_height = len(lines) * line_height
        y_text = CANVAS_H - total_height - 150 

        for line in lines:
            if hasattr(draw, "textbbox"):
                bbox = draw.textbbox((0, 0), line, font=font)
                w_line = bbox[2] - bbox[0]
            else:
                w_line, _ = draw.textsize(line, font=font)
                
            x_text = (CANVAS_W - w_line) // 2
            
            # Draw outline/shadow
            shadow_color = (0, 0, 0)
            fill_color = (255, 255, 255)
            offset = 3
            
            for off_x in range(-offset, offset+1, offset):
                for off_y in range(-offset, offset+1, offset):
                    if off_x == 0 and off_y == 0: continue
                    draw.text((x_text + off_x, y_text + off_y), line, font=font, fill=shadow_color)
            
            draw.text((x_text, y_text), line, font=font, fill=fill_color)
            y_text += line_height

    # --- save ---
    canvas.save(f"{seq_id}.png", format="PNG")

def get_tags():
    import requests
    tags = requests.get("https://cataas.com/api/tags")
    return tags.text

#transcribes the audio 
def get_transcript(audio="assets/demo.mp3"):
    import whisper
    model = whisper.load_model("medium")
    result = model.transcribe(audio)
    transcript = ""
    for segment in result['segments']:
        transcript += str(segment['start']) + " : " + str(segment['end']) + " " + str(segment['text']) + " \n"

    return transcript

def get_audio(video_path, audio_ext="mp3"):
    import os
    from moviepy import VideoFileClip

    base, _ = os.path.splitext(video_path)
    audio_path = f"{base}.{audio_ext}"

    with VideoFileClip(video_path) as video:
        audio = video.audio
        if audio is None:
            raise ValueError("Video has no audio track")

        audio.write_audiofile(audio_path)

    return audio_path



def make_vid(datas, frames_path, audio, output="output.mp4"):
    from moviepy import ImageClip, CompositeVideoClip, AudioFileClip
    import os
    clips = []

    for i, item in enumerate(datas, start=1):
        print(item)
        start = float(item["start"])
        end = float(item["end"]) if i == len(datas) else float(datas[i]['start']) 
        duration = end - start

        img_path = os.path.join(frames_path, f"{i}.png")
        if not os.path.isfile(img_path):
            raise FileNotFoundError(f"Image not found: {img_path}")

        # Create an ImageClip with the right duration
        clip = (
            ImageClip(img_path)
            .with_duration(duration)   # duration of this clip
            .with_start(start)          # when it begins on the timeline
        )

        clips.append(clip)

    # Create a composite clip that places each clip on the timeline
    video = CompositeVideoClip(clips)

    # Attach audio
    audio_clip = AudioFileClip(audio)
    video = video.with_audio(audio_clip)

    # Export
    video.write_videofile(
        output,
        fps=30,
        codec="libx264",
        audio_codec="aac"
    )













