# Required pip packages:
# pip install PyQt6 PyQt6-WebEngine pytube

import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout,
    QVBoxLayout, QSlider, QLabel, QInputDialog
)
from PyQt6.QtGui import QIcon, QPixmap, QPalette, QBrush
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QObject, pyqtSlot, QUrl
from PyQt6.QtWebChannel import QWebChannel
from pytube import Search

class WebEngineBridge(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    @pyqtSlot()
    def onPlayerError(self):
        print("Player error detected, loading next video...")
        self.parent.shuffle_video()

class RandomYouTubePlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.static_filter = None  # Initialize the static filter before init_ui
        self.current_genre = None  # Track the current genre for Courageous Shuffle

        # Set the application window icon
        self.setWindowIcon(QIcon("icon.png"))  # Ensure icon.png is in the project directory

        # Genres for Courageous Shuffle
        self.genres = ['Music', 'Gaming', 'News', 'Sports', 'Comedy', 'Education', 'Film', 'Technology', 'Travel']

        # Load word list from dict.txt
        try:
            with open('dict.txt', 'r', encoding='utf-8') as f:
                self.word_list = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("Dictionary file 'dict.txt' not found. Please ensure it exists in the script directory.")
            self.word_list = ['random']  # Fallback word list

        self.init_ui()

    def set_background_image(self, widget):
        # Load the background image and set it as a window background
        crt_image = QPixmap("crt.png")

        # Create a palette for the widget to set the background
        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(crt_image.scaled(self.size(), aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding)))
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)

    def init_ui(self):
        self.setWindowTitle('IndimensionalTube')
        self.resize(800, 775)
        # set resizable false
        self.setFixedSize(800, 775)
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)

        self.set_background_image(central_widget)

        # Horizontal layout for centering
        video_layout = QHBoxLayout()

        # Spacer for horizontal centering
        video_layout.addStretch()  # Left Spacer

        # Web view to display YouTube videos
        self.web_view = QWebEngineView()

        # Adjust size and position of the video player to fit within the CRT screen area
        self.web_view.setFixedSize(625, 475)  # Adjust this size to fit the CRT screen
        video_layout.addWidget(self.web_view)

        # Spacer for horizontal centering
        video_layout.addStretch()  # Right Spacer

        main_layout.addLayout(video_layout)

        # Set up the WebChannel for communication between JavaScript and Python
        self.bridge = WebEngineBridge(self)
        self.channel = QWebChannel()
        self.channel.registerObject('bridge', self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        # Horizontal layout for buttons and slider at the bottom center
        control_layout = QHBoxLayout()
        main_layout.addLayout(control_layout)

        # Spacer to center the controls
        control_layout.addStretch()

        # Shuffle button
        self.shuffle_button = QPushButton('Shuffle')
        self.shuffle_button.clicked.connect(self.shuffle_video)
        control_layout.addWidget(self.shuffle_button)

        # Courageous Shuffle button
        self.courageous_button = QPushButton('Courageous Shuffle')
        self.courageous_button.clicked.connect(self.courageous_shuffle_video)
        control_layout.addWidget(self.courageous_button)

        # Static Filter button
        self.filter_button = QPushButton('Search Keyword')
        self.filter_button.clicked.connect(self.set_static_filter)
        control_layout.addWidget(self.filter_button)

        # Toggle CRT Effect button
        self.toggle_crt_button = QPushButton('Toggle CRT Effect')
        self.toggle_crt_button.clicked.connect(self.toggle_crt_effect)
        control_layout.addWidget(self.toggle_crt_button)

        # CRT Intensity Slider
        self.crt_slider_label = QLabel('CRT Intensity')
        control_layout.addWidget(self.crt_slider_label)

        self.crt_slider = QSlider(Qt.Orientation.Horizontal)
        self.crt_slider.setMinimum(0)
        self.crt_slider.setMaximum(100)
        self.crt_slider.setValue(50)  # Starting value
        self.crt_slider.setFixedWidth(150)
        self.crt_slider.valueChanged.connect(self.update_crt_intensity)
        control_layout.addWidget(self.crt_slider)

        # Spacer to center the controls
        control_layout.addStretch()

        # Load the first video
        self.shuffle_video()

    def shuffle_video(self):
        if self.static_filter:
            query = self.static_filter
        else:
            # Source the dictionary instead of static terms
            query = random.choice(self.word_list)

        # Simulate random genre selection for the video
        self.current_genre = random.choice(self.genres)
        print(f"Current genre: {self.current_genre}")

        # Search YouTube using pytube
        search = Search(query)
        results = search.results

        if results:
            # Randomly select a video from search results
            video = random.choice(results)
            video_id = video.video_id

            # Embed YouTube video using IFrame API
            html_content = f'''
            <!DOCTYPE html>
            <html>
                <head>
                    <style>
                        :root {{
                            --crt-opacity: 0.5;
                            --crt-filter-contrast: 1.2;
                            --crt-filter-brightness: 0.9;
                            --crt-filter-saturate: 1.2;
                        }}
                        html, body {{
                            margin: 0;
                            padding: 0;
                            height: 100%;
                            width: 100%;
                            background: black;
                            overflow: hidden;
                        }}
                        #player {{
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            width: 100%;
                            height: 100%;
                        }}
                        /* CRT Monitor Effect */
                        body.crt-on #crt {{
                            position: absolute;
                            top: 0;
                            left: 0;
                            width: 100%;
                            height: 100%;
                            pointer-events: none;
                            background:
                                repeating-linear-gradient(
                                    transparent,
                                    transparent 2px,
                                    rgba(0, 0, 0, 0.1) 2px,
                                    rgba(0, 0, 0, 0.1) 4px
                                ),
                                linear-gradient(
                                    rgba(0, 255, 0, 0.1),
                                    rgba(0, 255, 0, 0.15)
                                );
                            background-blend-mode: overlay;
                            mix-blend-mode: screen;
                            border-radius: 15px;
                            opacity: var(--crt-opacity);
                        }}
                        body.crt-on #player iframe {{
                            filter: contrast(var(--crt-filter-contrast))
                                    brightness(var(--crt-filter-brightness))
                                    saturate(var(--crt-filter-saturate));
                            border-radius: 15px;
                        }}
                    </style>
                    <!-- YouTube IFrame API -->
                    <script src="https://www.youtube.com/iframe_api"></script>
                    <!-- Qt WebChannel script -->
                    <script type="text/javascript" src="qrc:///qtwebchannel/qwebchannel.js"></script>
                    <script type="text/javascript">
                        var bridge = null;
                        new QWebChannel(qt.webChannelTransport, function(channel) {{
                            bridge = channel.objects.bridge;
                        }});

                        var player;
                        function onYouTubeIframeAPIReady() {{
                            player = new YT.Player('player', {{
                                videoId: '{video_id}',
                                events: {{
                                    'onReady': onPlayerReady,
                                    'onError': onPlayerError
                                }},
                                playerVars: {{
                                    'autoplay': 1,
                                    'controls': 1
                                }}
                            }});
                        }}

                        function onPlayerReady(event) {{
                            console.log("Player is ready");
                        }}

                        function onPlayerError(event) {{
                            console.log('Player error occurred:', event.data);
                            if (bridge && bridge.onPlayerError) {{
                                bridge.onPlayerError();
                            }}
                        }}

                        // Function to toggle CRT effect
                        function toggleCRT() {{
                            var body = document.body;
                            if (body.classList.contains('crt-on')) {{
                                body.classList.remove('crt-on');
                            }} else {{
                                body.classList.add('crt-on');
                            }}
                        }}

                        // Function to set CRT intensity
                        function setCRTIntensity(intensity) {{
                            var normalizedIntensity = intensity / 100;
                            document.documentElement.style.setProperty('--crt-opacity', normalizedIntensity);

                            // Adjust filter values based on intensity
                            var contrast = 1 + (normalizedIntensity * 0.5); // from 1 to 1.5
                            var brightness = 1 - (normalizedIntensity * 0.3); // from 1 to 0.7
                            var saturate = 1 + (normalizedIntensity * 0.5); // from 1 to 1.5

                            document.documentElement.style.setProperty('--crt-filter-contrast', contrast);
                            document.documentElement.style.setProperty('--crt-filter-brightness', brightness);
                            document.documentElement.style.setProperty('--crt-filter-saturate', saturate);
                        }}
                    </script>
                </head>
                <body class="crt-on">
                    <div id="player"></div>
                    <div id="crt"></div>
                </body>
            </html>
            '''

            # Load HTML content into the web view
            self.web_view.setHtml(html_content, QUrl(''))  # Empty base URL

            # Set initial CRT intensity based on slider value
            self.update_crt_intensity(self.crt_slider.value())
        else:
            # Handle case when no results are found
            self.web_view.setHtml(
                '<h1 style="color: green; text-align: center; margin-top: 50%;">No videos found.</h1>'
            )

    def courageous_shuffle_video(self):
        """Select a video from a different genre than the current one."""
        available_genres = [genre for genre in self.genres if genre != self.current_genre]
        new_genre = random.choice(available_genres)
        print(f"Courageous Shuffle! Switching from {self.current_genre} to {new_genre}")
        self.current_genre = new_genre

        # Simulate the search by genre
        query = new_genre  # We can make the query based on the selected genre
        search = Search(query)
        results = search.results

        if results:
            video = random.choice(results)
            video_id = video.video_id

            html_content = f'''
            <!DOCTYPE html>
            <html>
                <head>
                    <style>
                        :root {{
                            --crt-opacity: 0.5;
                            --crt-filter-contrast: 1.2;
                            --crt-filter-brightness: 0.9;
                            --crt-filter-saturate: 1.2;
                        }}
                        html, body {{
                            margin: 0;
                            padding: 0;
                            height: 100%;
                            width: 100%;
                            background: black;
                            overflow: hidden;
                        }}
                        #player {{
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            width: 100%;
                            height: 100%;
                        }}
                    </style>
                    <!-- YouTube IFrame API -->
                    <script src="https://www.youtube.com/iframe_api"></script>
                    <!-- Qt WebChannel script -->
                    <script type="text/javascript" src="qrc:///qtwebchannel/qwebchannel.js"></script>
                    <script type="text/javascript">
                        var bridge = null;
                        new QWebChannel(qt.webChannelTransport, function(channel) {{
                            bridge = channel.objects.bridge;
                        }});

                        var player;
                        function onYouTubeIframeAPIReady() {{
                            player = new YT.Player('player', {{
                                videoId: '{video_id}',
                                events: {{
                                    'onReady': onPlayerReady,
                                    'onError': onPlayerError
                                }},
                                playerVars: {{
                                    'autoplay': 1,
                                    'controls': 1
                                }}
                            }});
                        }}

                        function onPlayerReady(event) {{
                            console.log("Player is ready");
                        }}

                        function onPlayerError(event) {{
                            console.log('Player error occurred:', event.data);
                            if (bridge && bridge.onPlayerError) {{
                                bridge.onPlayerError();
                            }}
                        }}

                        // Function to set CRT intensity
                        function setCRTIntensity(intensity) {{
                            var normalizedIntensity = intensity / 100;
                            document.documentElement.style.setProperty('--crt-opacity', normalizedIntensity);

                            // Adjust filter values based on intensity
                            var contrast = 1 + (normalizedIntensity * 0.5); // from 1 to 1.5
                            var brightness = 1 - (normalizedIntensity * 0.3); // from 1 to 0.7
                            var saturate = 1 + (normalizedIntensity * 0.5); // from 1 to 1.5

                            document.documentElement.style.setProperty('--crt-filter-contrast', contrast);
                            document.documentElement.style.setProperty('--crt-filter-brightness', brightness);
                            document.documentElement.style.setProperty('--crt-filter-saturate', saturate);
                        }}
                    </script>
                </head>
                <body>
                    <div id="player"></div>
                </body>
            </html>
            '''

            self.web_view.setHtml(html_content, QUrl(''))  # Empty base URL

            self.update_crt_intensity(self.crt_slider.value())

    def set_static_filter(self):
        # Open a dialog to set the static filter
        text, ok = QInputDialog.getText(self, 'Search Keyword', 'Enter search term:')
        if ok and text:
            self.static_filter = text
        else:
            self.static_filter = None  # Reset the filter if no input is provided
        # Shuffle video with the new filter
        self.shuffle_video()

    def toggle_crt_effect(self):
        # Call the JavaScript function to toggle CRT effect
        self.web_view.page().runJavaScript('toggleCRT();')

    def update_crt_intensity(self, value):
        # Adjust the CRT intensity based on the slider value
        intensity = int(value)
        js_code = f'setCRTIntensity({intensity});'
        self.web_view.page().runJavaScript(js_code)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = RandomYouTubePlayer()
    player.show()
    sys.exit(app.exec())
