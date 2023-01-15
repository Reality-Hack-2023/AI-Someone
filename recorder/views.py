import os
import wave
from pathlib import Path

from django.shortcuts import render
import speech_recognition as sr
from django.views.decorators.csrf import csrf_exempt

from DPT.run_monodepth import run
from Scripts.point_cloud_generation import create_scene_mesh
from Scripts.speech_text import find_background, find_points, create_scene
from .models import Scene


# Create your views here.

def homepage(request):
    if request.method == 'POST':
        print(request.POST)
        title = request.POST.get('title')
        if title:
            scene = Scene(name=title)
            scene.save()

    scenes = Scene.objects.all()
    print(scenes)
    context = {
        "scenes": scenes
    }
    return render(request, 'base.html', context)


def edit(request, title):
    scenes = Scene.objects.get(name=title)
    if request.method == 'POST':
        speech = request.POST.get('speech')
        back_text = find_background(speech)
        action_prompts = find_points(speech)
        create_scene(back_text, action_prompts, scenes.name)
        print(back_text, action_prompts)
        scenes.speech = speech
        scenes.scene_prompts = ".".join(action_prompts)
        scenes.save()

    IMG_PATH = Path.cwd() / 'static/images' / scenes.name
    IMG_PATH.mkdir(exist_ok=True)
    images = os.listdir(IMG_PATH)
    context = {
        "scene": scenes,
        "images": images
    }
    return render(request, 'edit.html', context)


def generate_depth(request, title):
    model_weights = 'DPT/weights/dpt_hybrid-midas-501f0c75.pt'
    model_type = 'dpt_hybrid'
    scenes = Scene.objects.get(name=title)
    IMAGE_DIR = Path.cwd() / 'static/images' / scenes.name
    OUT_DIR = Path.cwd() / 'static/output' / scenes.name
    IMAGE_DIR.mkdir(exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)
    if request.method == "POST":
        run(str(IMAGE_DIR), str(OUT_DIR), model_weights, model_type, True)

    images = os.listdir(IMAGE_DIR)
    context = {
        "scene": scenes,
        "images": images
    }
    return render(request, 'edit.html', context)


def generate_model(request, title):
    scenes = Scene.objects.get(name=title)
    IMAGE_DIR = Path.cwd() / 'static/images' / scenes.name
    OUT_DIR = Path.cwd() / 'static/output' / scenes.name
    RESP_DIR = Path.cwd() / 'static/responses' / scenes.name
    IMAGE_DIR.mkdir(exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)
    RESP_DIR.mkdir(exist_ok=True)
    images = os.listdir(IMAGE_DIR)
    scenes = Scene.objects.get(name=title)
    context = {
        "scene": scenes,
        "images": images
    }
    if request.method == 'POST':
        create_scene_mesh(IMAGE_DIR, OUT_DIR, RESP_DIR)
    return render(request, 'edit.html', context)


def view_model(request, title):
    print('he;;p', title)
    scenes = Scene.objects.get(name=title)
    context = {
        "scene": scenes,
    }
    return render(request, 'view_gltf.html', context)


def handle_uploaded_file(f, filename):
    destination = wave.open(str(filename), 'wb')
    destination.setnchannels(1)
    destination.setsampwidth(1)
    destination.setframerate(8000)
    destination.setnframes(1)
    destination.writeframes(f.read())


@csrf_exempt
def get_audio(request, title):
    scenes = Scene.objects.get(name=title)
    if request.method == 'POST':
        AUDIO_DIR = Path.cwd() / 'static/audio' / scenes.name
        AUDIO_DIR.mkdir(exist_ok=True)
        print(request.FILES['audio'])
        handle_uploaded_file(request.FILES['audio'], AUDIO_DIR / "audio.wav")
        # r = sr.Recognizer()
        # audio_file = sr.AudioFile(str(AUDIO_DIR / "audio.wav"))
        # with audio_file as source:
        #     audio = r.record(source)
        #     text = r.recognize_google(audio)
        #     scenes.speech = text
        #     scenes.save()

    context = {
        "scene": scenes,
    }
    return render(request, 'edit.html', context)
