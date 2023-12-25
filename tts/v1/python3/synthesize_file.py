import argparse
import random
import grpc
import logging
import os

import tts_pb2
import tts_pb2_grpc

def load_config(file_name: str = "config.ini") -> dict:
    config = {}
    parser = ConfigParser()
    parser.read(file_name)
    config["api"] = {"server_address": parser.get("API", "server_address")}
    config["auth"] = {
        "sso_server_url": parser.get("Auth", "sso_server_url"),
        "realm_name": parser.get("Auth", "realm_name"),
        "client_id": parser.get("Auth", "client_id"),
        "client_secret": parser.get("Auth", "client_secret"),
    }
    return config

def get_grpc_stub(config: dict) -> tts_pb2_grpc.TTSStub:
    credentials = grpc.ssl_channel_credentials()
    options = [
        ("grpc.min_reconnect_backoff_ms", 1000),
        ("grpc.max_reconnect_backoff_ms", 1000),
        ("grpc.max_send_message_length", -1),
        ("grpc.max_receive_message_length", -1),
    ]
    with grpc.secure_channel(config["api"]["server_address"], credentials=credentials, options=options) as channel:
        return tts_pb2_grpc.TTSStub(channel)

def synthesize_speech(text: str, stub: tts_pb2_grpc.TTSStub) -> bytes:
    request = tts_pb2.SynthesizeSpeechRequest(
        text=text,
        encoding=tts_pb2.AudioEncoding.LINEAR_PCM,
        sample_rate_hertz=22050,
        voice_name="gandzhaev",
        synthesize_options=tts_pb2.SynthesizeOptions(
            postprocessing_mode=tts_pb2.SynthesizeOptions.PostprocessingMode.POST_PROCESSING_DISABLE,
            model_type="default",
            voice_style=tts_pb2.VoiceStyle.VOICE_STYLE_NEUTRAL,
        ),
    )
    response = stub.Synthesize(request)
    return response.audio

def save_audio_to_file(audio: bytes, file_path: str):
    with open(file_path, "wb") as f:
        f.write(audio)

def synthesize_and_save_audio(text: str, config: dict):
    stub = get_grpc_stub(config)
    audio = synthesize_speech(text, stub)
    save_audio_to_file(audio, "synthesized_audio.wav")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("text", type=str, help="text for speech synthesis")

    args = parser.parse_args()

    config = load_config()

    synthesize_and_save_audio(args.text, config)
