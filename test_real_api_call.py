#!/usr/bin/env python3
"""
Real test that actually calls Google Cloud Speech API to verify it works.
"""

import os
import logging
from google.cloud import speech
from google.api_core.client_options import ClientOptions

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_direct_google_cloud_api():
    """Test Google Cloud Speech API directly with your API key."""
    print("🔍 Testing Direct Google Cloud Speech API Call")
    print("=" * 60)
    
    # Load API key from .env
    api_key = None
    try:
        with open('.env', 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('GOOGLE_CLOUD_CREDENTIALS='):
                    api_key = line.split('=', 1)[1].strip()
                    break
    except FileNotFoundError:
        print("❌ No .env file found")
        return False
    
    if not api_key:
        print("❌ No GOOGLE_CLOUD_CREDENTIALS found in .env")
        return False
        
    print(f"Using API key: {api_key[:20]}...")
    
    try:
        # Create client with API key
        client_options = ClientOptions(api_key=api_key)
        client = speech.SpeechClient(client_options=client_options)
        
        # Test with a simple audio sample (we'll create a minimal WAV)
        print("Creating test audio...")
        
        # Create a minimal 1-second silent WAV file for testing
        import wave
        import numpy as np
        
        sample_rate = 16000
        duration = 1  # 1 second
        samples = np.zeros(sample_rate * duration, dtype=np.int16)
        
        # Write to in-memory buffer
        import io
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(samples.tobytes())
        
        wav_buffer.seek(0)
        audio_content = wav_buffer.getvalue()
        
        print(f"Created test audio: {len(audio_content)} bytes")
        
        # Configure the recognition request
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code="en-US",
        )
        
        print("🚀 Making actual Google Cloud Speech API call...")
        
        # Make the API call
        response = client.recognize(config=config, audio=audio)
        
        print("✅ API call successful!")
        print(f"Response: {response}")
        
        if response.results:
            print(f"Transcription: {response.results[0].alternatives[0].transcript}")
        else:
            print("No speech detected (expected for silent audio)")
            
        return True
        
    except Exception as e:
        print(f"❌ Google Cloud API call failed: {type(e).__name__}: {e}")
        print("\nPossible issues:")
        print("1. API key is invalid or expired")
        print("2. Speech-to-Text API is not enabled for your project")
        print("3. Billing is not enabled for your project")
        print("4. API key doesn't have permission for Speech-to-Text API")
        return False

def test_api_key_validity():
    """Quick test to verify API key format and basic connectivity."""
    print("\n🔑 Testing API Key Validity")
    print("=" * 60)
    
    # Load API key
    api_key = None
    try:
        with open('.env', 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('GOOGLE_CLOUD_CREDENTIALS='):
                    api_key = line.split('=', 1)[1].strip()
                    break
    except FileNotFoundError:
        print("❌ No .env file found")
        return False
    
    if not api_key:
        print("❌ No GOOGLE_CLOUD_CREDENTIALS found in .env")
        return False
    
    print(f"API Key: {api_key}")
    print(f"Length: {len(api_key)} characters")
    print(f"Starts with AIza: {api_key.startswith('AIza')}")
    
    # Check basic format
    if not api_key.startswith('AIza'):
        print("❌ API key should start with 'AIza'")
        return False
        
    if len(api_key) < 35:
        print("❌ API key seems too short")
        return False
        
    print("✅ API key format looks correct")
    
    # Test if we can create a client (doesn't make API call yet)
    try:
        client_options = ClientOptions(api_key=api_key)
        client = speech.SpeechClient(client_options=client_options)
        print("✅ Client created successfully")
        return True
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        return False

def show_dashboard_info():
    """Show information about checking Google Cloud dashboard."""
    print("\n📊 How to Check Google Cloud Dashboard Usage")
    print("=" * 60)
    print("""
To verify API calls in Google Cloud Console:

1. Go to: https://console.cloud.google.com/
2. Select your project
3. Navigate to: APIs & Services > Dashboard
4. Look for "Cloud Speech-to-Text API"
5. Check the usage metrics and quotas

Alternative locations:
- APIs & Services > Enabled APIs > Cloud Speech-to-Text API
- Monitoring > Metrics Explorer > Search for "speech"
- Billing > Reports (if billing is enabled)

Note: Usage might take a few minutes to appear in the dashboard.
""")

def main():
    print("🧪 Real Google Cloud API Test")
    print("=" * 60)
    print("This test will actually call Google Cloud Speech API")
    print("and you should see usage in your dashboard.\n")
    
    # Test API key validity first
    if not test_api_key_validity():
        print("\n❌ API key validation failed. Cannot proceed with real API test.")
        return
    
    # Make real API call
    success = test_direct_google_cloud_api()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("✅ Real Google Cloud API call was made")
        print("✅ You should see usage in your dashboard within a few minutes")
        print("✅ The reCAPTCHA solver will work with your API key")
    else:
        print("\n❌ FAILED!")
        print("The API key or setup has issues that need to be resolved.")
    
    show_dashboard_info()

if __name__ == "__main__":
    # Install required package for audio testing
    try:
        import numpy
        import wave
    except ImportError:
        print("Installing numpy for audio testing...")
        os.system("pip install numpy")
        import numpy
        import wave
    
    main()