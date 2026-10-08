import os
import streamlit as st

from config.settings import settings
from utils.file_utils import make_temp_path, make_output_path
from utils.cleanup import TempFileTracker

from services.video_service import validate_video_file, VideoValidationError, has_audio_stream
from services.audio_service import extract_audio, AudioExtractionError
from services.transcription_service import load_whisper_model, transcribe_audio, TranscriptionError
from services.nlp_service import process_segments
from services.subtitle_service import generate_srt, save_srt_file
from services.caption_video_service import burn_captions_into_video, CaptionBurnError


st.set_page_config(page_title=settings.APP_NAME, page_icon="🎬", layout="centered")


@st.cache_resource(show_spinner=False)
def get_whisper_model():
    return load_whisper_model()


def _reset_pipeline_state():
    for key in ("video_path", "srt_content", "transcript", "tracker"):
        st.session_state.pop(key, None)


def main():
    st.title("AI English Video Caption Generator")
    st.caption(
        "Upload an video."
    )

    st.divider()
   
    uploaded_file = st.file_uploader(
        "Choose Video",
        type=[ext.lstrip(".") for ext in settings.SUPPORTED_VIDEO_EXTENSIONS],
        help="Supported: MP4, MOV, MKV, AVI, WEBM",
    )

    if uploaded_file is None:
        _reset_pipeline_state()
        st.info("Upload a video to get started.")
        return

    st.subheader("Original Video")
    st.video(uploaded_file)

    # New upload -> clear any previous generated captions
    if st.session_state.get("uploaded_name") != uploaded_file.name:
        _reset_pipeline_state()
        st.session_state["uploaded_name"] = uploaded_file.name

    # ---------- STEP 1: Generate captions ----------
    if st.button("Generate English Captions", type="primary"):
        _run_generate_captions(uploaded_file)

    if "srt_content" not in st.session_state:
        return

    # ---------- STEP 2: Edit captions ----------
    st.divider()
    st.subheader("Transcript")
    st.text_area("Full transcript", st.session_state["transcript"], height=120, disabled=True)

    st.subheader("Edit Captions (SRT)")
    edited_srt = st.text_area(
        "SRT content — edit text as needed, keep the numbering and timestamp format",
        value=st.session_state["srt_content"],
        height=300,
        key="srt_editor",
    )

    # ---------- STEP 3: Burn captions ----------
    if st.button("Burn Captions Into Video", type="primary"):
        _run_burn_captions(edited_srt)


def _run_generate_captions(uploaded_file):
    tracker = TempFileTracker()
    status = st.empty()
    progress_lines = []

    def log(step: str):
        progress_lines.append(step)
        status.markdown("\n\n".join(progress_lines))

    try:
        file_bytes = uploaded_file.getvalue()
        validate_video_file(uploaded_file.name, len(file_bytes))

        ext = os.path.splitext(uploaded_file.name)[1].lower()
        video_path = make_temp_path(ext)  # kept, not tracked for cleanup — needed in step 2
        with open(video_path, "wb") as f:
            f.write(file_bytes)
        log("✓ Video uploaded")

        if not has_audio_stream(video_path):
            st.error("No usable audio track was found.")
            return

        log("⏳ Extracting audio...")
        audio_path = tracker.track(extract_audio(video_path))
        log("✓ Audio extracted")

        log("⏳ Transcribing speech...")
        model = get_whisper_model()
        transcription = transcribe_audio(model, audio_path)
        log("✓ Transcription completed")

        log("⏳ Processing captions...")
        captions = process_segments(transcription.segments)
        srt_content = generate_srt(captions)
        log("✓ Captions generated")

        st.session_state["video_path"] = video_path
        st.session_state["srt_content"] = srt_content
        st.session_state["transcript"] = transcription.full_text

        if len(transcription.full_text.split()) < 5:
            st.warning("The audio quality may affect caption accuracy.")

        st.success("Captions ready. Edit below if needed, then burn them into the video.")

    except VideoValidationError as exc:
        st.error(str(exc))
    except AudioExtractionError as exc:
        st.error(str(exc))
    except TranscriptionError as exc:
        st.error(str(exc))
    except Exception as exc:  # noqa: BLE001
        st.error("Something went wrong while generating captions.")
        st.exception(exc)
    finally:
        tracker.cleanup_all()


def _run_burn_captions(edited_srt: str):
    video_path = st.session_state.get("video_path")
    if not video_path or not os.path.exists(video_path):
        st.error("Original video is no longer available. Please re-upload and regenerate captions.")
        return

    status = st.empty()
    status.markdown("⏳ Burning captions into video...")

    srt_path = make_output_path(".srt", prefix="captions")
    output_path = make_output_path(".mp4", prefix="captioned_video")

    try:
        save_srt_file(edited_srt, srt_path)
        burn_captions_into_video(video_path, srt_path, output_path)
        status.markdown("✓ Final video generated")

        st.subheader("Final Output")
        with open(output_path, "rb") as f:
            video_bytes = f.read()
        st.video(video_bytes)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "⬇ Download Captioned Video",
                data=video_bytes,
                file_name="captioned_video.mp4",
                mime="video/mp4",
            )
        with col2:
            st.download_button(
                "⬇ Download SRT",
                data=edited_srt,
                file_name="captions.srt",
                mime="text/plain",
            )

    except CaptionBurnError as exc:
        st.error(str(exc))
    except Exception as exc:  # noqa: BLE001
        st.error("Something went wrong while burning captions into the video.")
        st.exception(exc)


if __name__ == "__main__":
    main()