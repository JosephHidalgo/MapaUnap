from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QLabel, QScrollArea, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor
from datetime import datetime

class StyleManager:
    """Gestiona todos los estilos de la aplicación"""
    
    @staticmethod
    def get_chat_container_style():
        return """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d30, stop:1 #1e1e1e);
                border-radius: 12px;
                border: 1px solid #404040;
            }
        """
    
    @staticmethod
    def get_title_style():
        return """
            QLabel {
                color: #ffffff;
                font-size: 20px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0078d4, stop:1 #005a9e);
                border: none;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 10px;
            }
        """
    
    @staticmethod
    def get_section_title_style():
        return """
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #404040, stop:1 #2d2d30);
                border: none;
                border-radius: 6px;
                padding: 8px;
                margin-bottom: 8px;
            }
        """
    
    @staticmethod
    def get_chat_display_style():
        return """
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border-color: #0078d4;
                background-color: #252526;
            }
            QScrollBar:vertical {
                background: #2d2d30;
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #404040;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4a4a4a;
            }
        """
    
    @staticmethod
    def get_input_style():
        return """
            QLineEdit {
                background-color: #2d2d30;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
                background-color: #37373d;
            }
            QLineEdit::placeholder {
                color: #888888;
                font-style: italic;
            }
        """
    
    @staticmethod
    def get_send_button_style():
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078d4, stop:1 #005a9e);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #106ebe, stop:1 #0e5a9e);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #005a9e, stop:1 #004578);
            }
            QPushButton:disabled {
                background: #404040;
                color: #888888;
            }
        """
    
    @staticmethod
    def get_splitter_style():
        return """
            QSplitter::handle {
                background-color: #404040;
                border: 1px solid #2d2d30;
            }
            QSplitter::handle:horizontal {
                width: 3px;
            }
            QSplitter::handle:pressed {
                background-color: #0078d4;
            }
        """
    
    @staticmethod
    def get_map_container_style():
        return """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d30, stop:1 #1e1e1e);
                border-radius: 12px;
                border: 1px solid #404040;
            }
        """
    
    @staticmethod
    def apply_main_window_style(window):
        window.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #252526);
            }
        """)

class ChatWidget(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        self.setup_connections()
        self.add_welcome_message()

    def setup_ui(self):
        """Configura la interfaz del chat"""
        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Aplicar estilo al contenedor
        self.setStyleSheet(StyleManager.get_chat_container_style())
        
        # Título del chat
        self.title_label = QLabel("🎓 Sistema de Navegación Universitaria MAP UNAP")
        self.title_label.setStyleSheet(StyleManager.get_title_style())
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Área de mensajes del chat
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(StyleManager.get_chat_display_style())
        layout.addWidget(self.chat_display)
        
        # Campo de entrada de texto
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("💬 Ejemplo: 'Quiero ir de Medicina Humana a Turismo'")
        self.message_input.setStyleSheet(StyleManager.get_input_style())
        
        # Botón de envío
        self.send_button = QPushButton("📤 Enviar")
        self.send_button.setStyleSheet(StyleManager.get_send_button_style())
        
        # Layout para entrada y botón
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        input_layout.addWidget(self.message_input, 1)  # El input ocupa más espacio
        input_layout.addWidget(self.send_button)
        
        # Agregar widgets al layout principal
        layout.addLayout(input_layout)
        self.setLayout(layout)

    def setup_connections(self):
        """Configura las conexiones de eventos"""
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)

    def add_welcome_message(self):
        """Añade el mensaje de bienvenida"""
        welcome_html = """
        <div style='background: linear-gradient(135deg, #0078d4, #005a9e); 
                   color: white; padding: 15px; border-radius: 10px; margin: 5px 0;'>
            <h3 style='margin: 0; color: white;'>¡Bienvenido al Sistema de Navegación! 🎓</h3>
        </div>
        """
        self.chat_display.append(welcome_html)

    def send_message(self):
        """Envía un mensaje"""
        message = self.message_input.text().strip()
        if message:
            # Mostrar mensaje del usuario INMEDIATAMENTE
            self.add_user_message(message)
            
            # Limpiar campo de entrada INMEDIATAMENTE
            self.message_input.clear()
            
            # Auto-scroll al final
            self.chat_display.ensureCursorVisible()
            
            # Procesar mensaje (esto ahora no bloquea la UI)
            if self.main_window:
                self.main_window.process_message(message)

    def add_user_message(self, message):
        """Añade un mensaje del usuario al chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        user_html = f"""
        <div style='background: linear-gradient(135deg, #404040, #2d2d30); 
                   color: white; padding: 12px; border-radius: 10px; 
                   margin: 8px 0; border-left: 4px solid #0078d4;'>
            <div style='font-weight: bold; color: #4cc2ff; margin-bottom: 4px;'>
                👤 Tú <span style='font-size: 10px; color: #888; font-weight: normal;'>({timestamp})</span>
            </div>
            <div style='color: #ffffff;'>{message}</div>
        </div>
        """
        self.chat_display.append(user_html)
        self.scroll_to_bottom()

    def add_bot_message(self, message):
        """Añade un mensaje del bot al chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Determinar el tipo de mensaje y aplicar color apropiado
        if "❌" in message or "ERROR" in message.upper():
            bg_color = "linear-gradient(135deg, #d13438, #a01e22)"
            icon = "🤖"
        elif "✅" in message or "encontrada" in message.lower():
            bg_color = "linear-gradient(135deg, #107c10, #0e6b0e)"
            icon = "🤖"
        elif "⏳" in message or "procesando" in message.lower():
            bg_color = "linear-gradient(135deg, #ff8c00, #e67700)"
            icon = "🤖"
        else:
            bg_color = "linear-gradient(135deg, #5d5d5d, #454545)"
            icon = "🤖"
        
        bot_html = f"""
        <div style='background: {bg_color}; 
                   color: white; padding: 12px; border-radius: 10px; 
                   margin: 8px 0; border-left: 4px solid #66ff66;'>
            <div style='font-weight: bold; color: #66ff66; margin-bottom: 4px;'>
                {icon} Asistente MAP <span style='font-size: 10px; color: #ccc; font-weight: normal;'>({timestamp})</span>
            </div>
            <div style='color: #ffffff; line-height: 1.4;'>{message}</div>
        </div>
        """
        self.chat_display.append(bot_html)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """Hace scroll hasta abajo en el chat"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()