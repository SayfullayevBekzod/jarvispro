import asyncio
import edge_tts
import pygame
import os
import tempfile

async def test_edge_tts():
    print("Testing Edge TTS...")
    voice = "uz-UZ-SardorNeural"
    text = "Salom, bu ovoz tekshiruvi."
    output = "test_audio.mp3"
    
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output)
        print(f"Audio saved to {output}")
        
        pygame.mixer.init()
        pygame.mixer.music.load(output)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        print("Playback finished.")
        pygame.mixer.quit()
        os.remove(output)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_edge_tts())
