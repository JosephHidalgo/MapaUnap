import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QHBoxLayout, QVBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QSplitter)
from PySide6.QtCore import Qt
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mapa_matplotlib import GraphVisualizer
from deepseek import assistant
import json

class MatplotlibWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

class ChatWidget(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        
        # Área de mensajes del chat
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        
        # Campo de entrada de texto
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ejemplo: 'Quiero ir de Medicina a Ingeniería Industrial'")
        
        # Botón de envío
        self.send_button = QPushButton("Enviar")
        
        # Layout para entrada y botón
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        # Agregar widgets al layout principal
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
        
        # Conectar eventos
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)
        
        # Agregar mensaje de bienvenida
        self.chat_display.append(
            "<b>🎓 Sistema de Navegación Universitaria</b><br>"
            "Puedes escribir en lenguaje natural, por ejemplo:<br>"
            "• 'Quiero ir de Medicina a Ingeniería Industrial'<br>"
            "• '¿Cómo llego desde Derecho hasta Psicología?'<br>"
            "• 'Necesito una ruta de Enfermería a Administración'<br>"
            "• O usar comandos: '/ruta 1 10'<br><br>"
        )
        
    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Mostrar mensaje del usuario
            self.chat_display.append(f"<b>[{timestamp}] Tú:</b> {message}")
            
            # Limpiar campo de entrada
            self.message_input.clear()
            
            # Procesar mensaje
            if self.main_window:
                self.main_window.process_message(message)
            
            # Auto-scroll al final
            self.chat_display.ensureCursorVisible()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Navegación Universitaria")
        self.setGeometry(100, 100, 1200, 600)
        
        # Widget central y layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter para dividir chat y mapa
        splitter = QSplitter(Qt.Horizontal)
        
        # Widget de chat
        self.chat_widget = ChatWidget(main_window=self)
        
        # Widget del mapa
        self.graph_widget = GraphVisualizer()
        self.graph_widget.load_data('graph_information.json')
        self.graph_widget.draw_base_graph()
        
        # Cargar información de escuelas disponibles
        self.load_available_schools()
        
        # Contenedor para el widget de matplotlib
        map_container = QWidget()
        map_layout = QVBoxLayout(map_container)
        map_layout.addWidget(self.graph_widget)
        
        # Agregar widgets al splitter
        splitter.addWidget(self.chat_widget)
        splitter.addWidget(map_container)
        
        # Configurar splitter
        splitter.setSizes([400, 800])
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
            self.chat_widget.chat_display.append(
                f"<b>[{timestamp}] Bot:</b> 🤖 Procesando tu solicitud con IA..."
            )
            
            try:
                # Usar el LLM para extraer escuelas
                schools_response = assistant(message)
                print(f"Respuesta del LLM: {schools_response}")
                
                # Procesar la respuesta del LLM
                if schools_response.upper() == 'NINGUNA' or not schools_response.strip():
                    self.chat_widget.chat_display.append(
                        f"<b>[{timestamp}] Bot:</b> ❌ No pude identificar escuelas específicas en tu mensaje. "
                        "¿Podrías ser más específico? Por ejemplo: 'Quiero ir de Medicina a Ingeniería'"
                    )
                    return
                
                # Extraer escuelas de la respuesta
                schools = [school.strip() for school in schools_response.split(',')]
                self.handle_schools_navigation(schools, timestamp)
                
            except Exception as e:
                self.chat_widget.chat_display.append(
                    f"<b>[{timestamp}] Bot:</b> ❌ Error al procesar con IA: {str(e)}<br>"
                    "Puedes intentar usar comandos directos como '/ruta 1 10'"
                )
        else:
            # Respuesta genérica para mensajes que no son de navegación
            self.chat_widget.chat_display.append(
                f"<b>[{timestamp}] Bot:</b> Hola! Soy tu asistente de navegación universitaria. "
                "Puedes pedirme rutas entre escuelas profesionales usando lenguaje natural."
            )

    def handle_schools_navigation(self, schools, timestamp):
        """Procesa la navegación basada en escuelas extraídas"""
        if not schools:
            return
        
        # Mostrar escuelas detectadas
        self.chat_widget.chat_display.append(
            f"<b>[{timestamp}] Bot:</b> 🎯 Escuelas detectadas: {', '.join(schools)}"
        )
        
        # Buscar IDs de nodos correspondientes
        school_nodes = self.find_school_nodes(schools)
        print(school_nodes)
        
        if len(school_nodes) < 2:
            missing_schools = [school for school in schools if school not in [node['school_name'] for node in school_nodes]]
            self.chat_widget.chat_display.append(
                f"<b>[{timestamp}] Bot:</b> ❌ No encontré algunas escuelas en el mapa: {', '.join(missing_schools)}<br>"
                f"Escuelas disponibles: {', '.join(self.available_schools)}"
            )
            return
        
        # Si hay exactamente 2 escuelas, usar A*
        if len(school_nodes) == 2:
            start_node = school_nodes[0]
            end_node = school_nodes[1]
            
            path = self.graph_widget.find_and_highlight_path(int(start_node['id']), int(end_node['id']))
            if path:
                distance = self.calculate_path_distance(path)
                self.chat_widget.chat_display.append(
                    f"<b>[{timestamp}] Bot:</b> ✅ Ruta óptima encontrada:<br>"
                    f"🏫 Desde: {start_node['school_name']}<br>"
                    f"🏫 Hasta: {end_node['school_name']}<br>"
                    f"📏 Distancia: {distance:.2f} unidades<br>"
                    f"🗺️ Nodos: {len(path)}"
                )
            else:
                self.chat_widget.chat_display.append(
                    f"<b>[{timestamp}] Bot:</b> ❌ No se encontró ruta entre {start_node['school_name']} y {end_node['school_name']}"
                )
        
        # Si hay más de 2 escuelas, crear ruta manual
        elif len(school_nodes) > 2:
            node_ids = [node['id'] for node in school_nodes]
            self.graph_widget.highlight_path(node_ids)
            distance = self.calculate_path_distance(node_ids)
            
            route_names = " → ".join([node['school_name'] for node in school_nodes])
            self.chat_widget.chat_display.append(
                f"<b>[{timestamp}] Bot:</b> ✅ Ruta personalizada creada:<br>"
                f"🗺️ {route_names}<br>"
                f"📏 Distancia total: {distance:.2f} unidades"
            )

    def find_school_nodes(self, school_names):
        """Encuentra los nodos correspondientes a las escuelas mencionadas"""
        school_nodes = []
        
        for school_name in school_names:
            for node in self.graph_widget.nodes:
                if (node.get('is_school', False) and 
                    'school_name' in node and 
                    school_name.lower() in node['school_name'].lower()):
                    school_nodes.append({
                        'id': node['id'],
                        'school_name': node['school_name']
                    })
                    break
        
        return school_nodes

    def process_navigation_command(self, message):
        """Procesa comandos tradicionales /ruta"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        try:
            parts = message.split()
            if len(parts) < 3:
                raise ValueError("Se requieren al menos 2 nodos")
                
            node_ids = [int(x) for x in parts[1:]]
            
            if len(node_ids) == 2:
                start, end = node_ids
                path = self.graph_widget.find_and_highlight_path(start, end)
                if path:
                    distance = self.calculate_path_distance(path)
                    self.chat_widget.chat_display.append(
                        f"<b>[{timestamp}] Bot:</b> ✅ Ruta óptima encontrada: {path}<br>"
                        f"📏 Distancia total: {distance:.2f} unidades<br>"
                        f"🗺️ Nodos: {len(path)}"
                    )
                else:
                    self.chat_widget.chat_display.append(
                        f"<b>[{timestamp}] Bot:</b> ❌ No se encontró ruta entre los nodos {start} y {end}"
                    )
            else:
                self.graph_widget.highlight_path(node_ids)
                distance = self.calculate_path_distance(node_ids)
                self.chat_widget.chat_display.append(
                    f"<b>[{timestamp}] Bot:</b> ✅ Ruta personalizada: {node_ids}<br>"
                    f"📏 Distancia total: {distance:.2f} unidades"
                )
                
        except ValueError as e:
            self.chat_widget.chat_display.append(
                f"<b>[{timestamp}] Bot:</b> ❌ Error: {str(e)}<br>"
                "Formato correcto:<br>"
                "• Ruta automática: /ruta inicio fin<br>"
                "• Ruta manual: /ruta 1 2 3 4"
            )

    def calculate_path_distance(self, path):
        """Calcula la distancia total de una ruta"""
        if len(path) < 2:
            return 0
        distance = 0
        for i in range(len(path)-1):
            for edge in self.graph_widget.edges:
                if (edge['source'] == path[i] and edge['target'] == path[i+1]) or \
                   (edge['source'] == path[i+1] and edge['target'] == path[i]):
                    distance += edge['weight']
                    break
        return distance

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()