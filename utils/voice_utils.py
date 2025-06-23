def voice_input_html():
    """
    Returns HTML and JavaScript to render a simple mic button for voice input.
    This gets embedded using streamlit.components.v1.html().
    """
    return """
        <input type="text" id="voiceInput" placeholder="Click mic 🔈 to speak..." style="width:90%; padding:8px;" />
        <button onclick="startRecognition()">🎤</button>
        <script>
            function startRecognition() {
                var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = 'en-IN';
                recognition.onresult = function(event) {
                    document.getElementById('voiceInput').value = event.results[0][0].transcript;
                    alert("You said: " + event.results[0][0].transcript);
                };
                recognition.start();
            }
        </script>
    """
