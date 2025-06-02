import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QHBoxLayout, QVBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QSplitter, QLabel)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QPalette, QColor
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mapa_matplotlib import GraphVisualizer
from deepseek import assistant
import json
import unicodedata
from difflib import SequenceMatcher

# Importar módulos personalizados
from ui_components import ChatWidget, StyleManager
from navigation_handler import NavigationHandler

class LLMWorker(QThread):
    """Worker thread para procesar LLM sin bloquear la UI"""
    response_ready = Signal(str, str)  # message, response
    
    def __init__(self, message):
        super().__init__()
        self.message = message
    
    def run(self):
        try:
            response = assistant(self.message)
            self.response_ready.emit(self.message, response)
        except Exception as e:
            self.response_ready.emit(self.message, f"ERROR: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Navegación Universitaria MAP UNAP")
        
        # Configurar ventana a pantalla completa
        self.showMaximized()
        
        # Aplicar estilos
        StyleManager.apply_main_window_style(self)
        
        # Variable para el worker del LLM
        self.llm_worker = None
        
        # Inicializar handler de navegación
        self.navigation_handler = NavigationHandler()
        
        # Widget central y layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Splitter para dividir chat y mapa
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(StyleManager.get_splitter_style())
        
        # Widget de chat con componentes mejorados
        self.chat_widget = ChatWidget(main_window=self)
        
        # Widget del mapa
        self.graph_widget = GraphVisualizer()
        self.graph_widget.load_data('graph_information.json')
        self.graph_widget.draw_base_graph()
        
        # Cargar información de escuelas disponibles
        self.load_available_schools()
        
        # Contenedor para el widget de matplotlib con estilo
        map_container = QWidget()
        map_container.setStyleSheet(StyleManager.get_map_container_style())
        map_layout = QVBoxLayout(map_container)
        map_layout.setContentsMargins(15, 15, 15, 15)
        
        # Título para el mapa
        map_title = QLabel("🗺️ Mapa Interactivo")
        map_title.setStyleSheet(StyleManager.get_section_title_style())
        map_title.setAlignment(Qt.AlignCenter)
        
        map_layout.addWidget(map_title)
        map_layout.addWidget(self.graph_widget)
        
        # Agregar widgets al splitter
        splitter.addWidget(self.chat_widget)
        splitter.addWidget(map_container)
        
        # Configurar proporción del splitter (30% chat, 70% mapa)
        splitter.setSizes([400, 900])
        main_layout.addWidget(splitter)

    def load_available_schools(self):
        """Carga las escuelas disponibles desde el JSON"""
        try:
            with open('graph_information.json', 'r') as file:
                data = json.load(file)
            
            # Extraer nombres de escuelas de los nodos
            self.available_schools = []
            for node in data['nodes']:
                if node.get('is_school', False) and 'school_name' in node:
                    self.available_schools.append(node['school_name'])
            
            # Pasar escuelas al navigation handler
            self.navigation_handler.set_available_schools(self.available_schools)
            self.navigation_handler.set_graph_widget(self.graph_widget)
            
            print(f"Escuelas disponibles: {self.available_schools}")
            
        except Exception as e:
            print(f"Error al cargar escuelas: {e}")
            self.available_schools = []

    def is_navigation_request(self, message):
        """Determina si el mensaje es una solicitud de navegación"""
        navigation_keywords = [
            'ruta', 'camino', 'llegar', 'ir', 'navegar', 'dirigir', 
            'desde', 'hasta', 'hacia', 'cómo llego', 'dónde está',
            'ubicación', 'encontrar', 'buscar', 'quiero ir'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in navigation_keywords)

    def process_message(self, message):
        """Procesa mensajes del usuario"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Comando tradicional
        if message.startswith("/ruta"):
            self.process_navigation_command(message)
            return
        
        # Verificar si es una consulta de navegación
        if self.is_navigation_request(message):
            # Mostrar mensaje de espera INMEDIATAMENTE
            self.chat_widget.add_bot_message("🤖 Procesando tu solicitud... ⏳")
            
            # Iniciar procesamiento en hilo separado
            self.start_llm_processing(message)
            
        else:
            # Respuesta genérica para mensajes que no son de navegación
            self.chat_widget.add_bot_message(
                "Hola! Soy tu asistente de navegación universitaria. "
                "Puedes pedirme rutas entre escuelas profesionales usando lenguaje natural."
            )

    def start_llm_processing(self, message):
        """Inicia el procesamiento del LLM en un hilo separado"""
        if self.llm_worker and self.llm_worker.isRunning():
            return  # Ya hay un proceso en curso
        
        self.llm_worker = LLMWorker(message)
        self.llm_worker.response_ready.connect(self.handle_llm_response)
        self.llm_worker.start()

    def handle_llm_response(self, original_message, llm_response):
        """Maneja la respuesta del LLM cuando está lista"""
        try:
            print(f"Respuesta del LLM: {llm_response}")
            
            # Procesar la respuesta del LLM
            if llm_response.startswith("ERROR:") or llm_response.upper() == 'NINGUNA' or not llm_response.strip():
                self.chat_widget.add_bot_message(
                    "❌ No pude identificar escuelas específicas en tu mensaje. "
                    "¿Podrías ser más específico? Por ejemplo: 'Quiero ir de Medicina a Ingeniería'"
                )
                return
            
            # Usar el navigation handler para procesar
            result = self.navigation_handler.handle_schools_navigation(llm_response)
            self.chat_widget.add_bot_message(result)
            
        except Exception as e:
            self.chat_widget.add_bot_message(
                f"❌ Error al procesar con IA: {str(e)}\n"
                "Puedes intentar usar comandos directos como '/ruta 1 10'"
            )

    def process_navigation_command(self, message):
        """Procesa comandos tradicionales /ruta"""
        result = self.navigation_handler.process_navigation_command(message)
        self.chat_widget.add_bot_message(result)

def main():
    app = QApplication(sys.argv)
    
    # Configurar tema oscuro para la aplicación
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(45, 45, 48))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(35, 35, 38))
    palette.setColor(QPalette.AlternateBase, QColor(55, 55, 58))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(60, 60, 63))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()