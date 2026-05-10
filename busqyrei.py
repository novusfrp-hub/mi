import os
import sys
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QFrame, QLabel, QSizePolicy, QStatusBar,
                            QFileDialog, QListWidget, QListWidgetItem, QMessageBox)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QCursor, QFont, QPixmap, QPainter, QIcon

def get_adb_path():
    """Obtiene la ruta absoluta al ejecutable de adb en la misma carpeta que el programa"""
    if getattr(sys, 'frozen', False):
        # Si está congelado (ejecutable)
        base_path = sys.executable
    else:
        # Si está en desarrollo
        base_path = __file__
    
    dir_path = os.path.dirname(base_path)
    adb_path = os.path.join(dir_path, 'adb.exe')
    
    # Si no existe adb.exe, intentar con 'adb' (para Linux/Mac)
    if not os.path.exists(adb_path):
        adb_path = os.path.join(dir_path, 'adb')
    
    if not os.path.exists(adb_path):
        # Fallback a adb en PATH si no se encuentra localmente
        return 'adb'
    
    return adb_path

ADB_BINARY = get_adb_path()

def run_adb_command(command_args):
    """Ejecuta un comando ADB usando el binario localizado"""
    cmd = [ADB_BINARY] + command_args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout
    except subprocess.TimeoutExpired:
        print(f"Timeout ejecutando comando ADB: {' '.join(cmd)}")
        return ""
    except Exception as e:
        print(f"Error ejecutando comando ADB: {str(e)}")
        return ""

def run_adb_shell(command):
    """Ejecuta un comando shell de ADB usando el binario localizado"""
    cmd = f'"{ADB_BINARY}" {command}'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout
    except subprocess.TimeoutExpired:
        print(f"Timeout ejecutando comando ADB shell: {cmd}")
        return ""
    except Exception as e:
        print(f"Error ejecutando comando ADB shell: {str(e)}")
        return ""

class AppCard(QWidget):
    def __init__(self, package_name, parent=None):
        super().__init__(parent)
        self.package_name = package_name
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 2, 10, 2)
        layout.setSpacing(5)
        
        self.name_label = QLabel(self.package_name)
        self.name_label.setStyleSheet("font-weight: bold;")
        self.name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.name_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.name_label.mousePressEvent = self.copy_package_name
        
        self.btn_stop = QPushButton("⏹ Detener")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 2px 5px;
                font-weight: bold;                    
                border-radius: 4px;
                min-width: 60px;
            }
            QPushButton:hover { background-color: #e68a00; }
        """)
        self.btn_stop.clicked.connect(self.stop_app)
        
        self.btn_uninstall = QPushButton("🗑 Eliminar")
        self.btn_uninstall.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                font-weight: bold;                         
                padding: 2px 5px;
                border-radius: 4px;
                min-width: 60px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        self.btn_uninstall.clicked.connect(self.confirm_uninstall)
        
        layout.addWidget(self.name_label)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_uninstall)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            AppCard {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 5px;
                border: 1px solid #e0e0e0;
            }
            AppCard:hover {
                background-color: rgba(245, 245, 245, 200);
            }
        """)
    
    def confirm_uninstall(self):
        list_widget = self.parent().parent()
        if hasattr(list_widget, 'is_system_package') and list_widget.is_system_package(self.package_name):
            self.show_system_warning()
            return
        
        self.uninstall_app()
    
    def show_system_warning(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error crítico")
        msg.setText(f"No se puede eliminar aplicación del sistema:\n{self.package_name}")
        msg.setInformativeText("Esta es una aplicación crítica del sistema.")
        msg.exec_()
    
    def copy_package_name(self, event):
        if event.button() == Qt.LeftButton:
            try:
                clipboard = QApplication.clipboard()
                clipboard.setText(self.package_name)
                self.save_to_database(self.package_name)
                self.save_to_malware_list(self.package_name)
                
                self.msg = QMessageBox()
                self.msg.setWindowModality(Qt.NonModal)
                self.msg.setIcon(QMessageBox.Information)
                self.msg.setText(f"Paquete copiado:\n{self.package_name}")
                self.msg.setWindowTitle("Copiado")
                self.msg.setStandardButtons(QMessageBox.Ok)
                self.msg.show()
                
                QTimer.singleShot(1000, self.msg.close)
                
            except Exception as e:
                print(f"Error al copiar: {str(e)}")
        
        QLabel.mousePressEvent(self.name_label, event)
    
    def save_to_database(self, package_name):
        try:
            with open("base_de_datos.txt", "a+", encoding='utf-8') as file:
                file.seek(0)
                content = file.read()
                if package_name not in content:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    file.write(f"{timestamp} - {package_name}\n")
        except Exception as e:
            print(f"Error guardando en base de datos: {str(e)}")
    
    def save_to_malware_list(self, package_name):
        try:
            with open("malware_list.txt", "a+", encoding='utf-8') as file:
                file.seek(0)
                content = file.read()
                if package_name not in content:
                    file.write(f"{package_name}\n")
        except Exception as e:
            print(f"Error guardando en malware list: {str(e)}")
    
    def stop_app(self):
        run_adb_shell(f'shell am force-stop {self.package_name}')
    
    def uninstall_app(self):
        resultado = run_adb_shell(f'shell pm uninstall --user 0 {self.package_name}')
        if "Success" not in resultado:
            run_adb_shell(f'shell pm disable-user --user 0 {self.package_name}')
        self.save_to_database(f"ELIMINADO: {self.package_name}")
        list_widget = self.parent().parent()
        for i in range(list_widget.count()):
            if list_widget.itemWidget(list_widget.item(i)) == self:
                list_widget.takeItem(i)
                break

class AppsList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.background_image = None
        self.load_background_image()
        self.setup_ui()
        self.system_packages = set()
        self.malware_packages = set()
    
    def update_system_packages(self):
        try:
            result = run_adb_shell('shell pm list packages -s')
            self.system_packages = {line.split(':')[1].strip() for line in result.split('\n') if line}
        except Exception as e:
            print(f"Error actualizando paquetes del sistema: {str(e)}")
            self.system_packages = set()
    
    def update_malware_packages(self):
        try:
            if os.path.exists("malware_list.txt"):
                with open("malware_list.txt", "r", encoding='utf-8') as file:
                    self.malware_packages = {line.strip() for line in file.readlines() if line.strip()}
        except Exception as e:
            print(f"Error actualizando lista de malware: {str(e)}")
            self.malware_packages = set()
    
    def is_system_package(self, package_name):
        return package_name in self.system_packages
    
    def is_malware_package(self, package_name):
        return package_name in self.malware_packages
    
    def setup_ui(self):
        self.setViewMode(QListWidget.ListMode)
        self.setFlow(QListWidget.TopToBottom)
        self.setResizeMode(QListWidget.Adjust)
        self.setMovement(QListWidget.Static)
        self.setSpacing(3)
        self.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                padding: 3px;
            }
            QListWidget::item {
                border-bottom: 1px solid #e0e0e0;
                background-color: transparent;
            }
        """)
    
    def load_background_image(self):
        image_path = r"C:\Users\Marshall\Downloads\logosf.png"
        try:
            if os.path.exists(image_path):
                original_pixmap = QPixmap(image_path)
                self.background_image = original_pixmap.scaled(
                    original_pixmap.width() // 8,
                    original_pixmap.height() // 8,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
        except Exception as e:
            print(f"Error cargando imagen de fondo: {str(e)}")
    
    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        
        if self.background_image and not self.background_image.isNull():
            painter.setOpacity(0.9)
            x = self.viewport().width() - self.background_image.width() -10
            y = self.viewport().height() - self.background_image.height() -0.0
            painter.drawPixmap(int(x), int(y), self.background_image)
            painter.setOpacity(1.0)
        
        super().paintEvent(event)
    
    def add_card(self, package_name):
        item = QListWidgetItem()
        item.setSizeHint(QSize(400, 40))
        self.addItem(item)
        
        card = AppCard(package_name, self)
        
        if self.is_system_package(package_name):
            card.setStyleSheet("""
                AppCard {
                    background-color: #ffeeee;
                    border-radius: 5px;
                    font-weight: bold;           
                    border: 1px solid #ffcccc;
                }
            """)
            card.btn_uninstall.setEnabled(False)
            card.btn_uninstall.setStyleSheet("""
                QPushButton {
                    background-color: #cccccc;
                    color: #666666;
                    border: none;
                    padding: 2px 5px;
                    font-weight: bold;                         
                    border-radius: 4px;
                    min-width: 60px;
                }
            """)
            card.btn_uninstall.setToolTip("Aplicación del sistema - No se puede eliminar")
        elif self.is_malware_package(package_name):
            card.setStyleSheet("""
                AppCard {
                    background-color: #ffdddd;
                    border-radius: 5px;
                    font-weight: bold;
                    border: 1px solid #ff9999;
                }
                QLabel {
                    color: #cc0000;
                }
            """)
            card.btn_uninstall.setStyleSheet("""
                QPushButton {
                    background-color: #ff3333;
                    color: white;
                    border: none;
                    padding: 2px 5px;
                    font-weight: bold;
                    border-radius: 4px;
                    min-width: 60px;
                }
                QPushButton:hover { background-color: #cc0000; }
            """)
        
        self.setItemWidget(item, card)

class MarshallApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MC-BLOATWARE TOOL")
        self.setGeometry(400, 200, 600, 400)
        
        # Configuración mejorada del icono
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icono.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"No se encontró el icono en: {icon_path}")
        
        self.is_monitoring = False
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.monitorear)
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.verify_connection)
        self.create_database_file()
        self.create_malware_list_file()
        self.setup_ui()
        self.check_adb_connection()
        self.connection_timer.start(1000)
        self.found_malware = set()
    
    def create_database_file(self):
        if not os.path.exists("base_de_datos.txt"):
            with open("base_de_datos.txt", "w", encoding='utf-8') as file:
                file.write("=== PAQUETES SOSPECHOSOS ===\n")
                file.write(f"Creado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    def create_malware_list_file(self):
        if not os.path.exists("malware_list.txt"):
            with open("malware_list.txt", "w", encoding='utf-8') as file:
                file.write("# Lista de paquetes maliciosos\n")
                file.write(f"# Creado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Eliminé completamente el QLabel con el título duplicado

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f0f0f0;
                color: #333;
                font-size: 11px;
                font-weight: bold;                      
                padding: 5px;
            }
        """)
        self.setStatusBar(self.status_bar)
        
        control_frame = QFrame()
        control_frame.setFrameShape(QFrame.StyledPanel)
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(10, 5, 10, 5)
        
        self.btn_start = QPushButton("▶ Iniciar Monitoreo")
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 6px 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.btn_start.clicked.connect(self.iniciar_monitoreo)
        self.btn_start.setEnabled(False)
        
        self.btn_stop = QPushButton("■ Detener")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 6px 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #d32f2f; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.btn_stop.clicked.connect(self.detener_monitoreo)
        self.btn_stop.setEnabled(False)
        
        self.btn_search = QPushButton("🔍 Buscar Malware")
        self.btn_search.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #7B1FA2; }
        """)
        self.btn_search.clicked.connect(self.buscar_malware)
        self.btn_search.setEnabled(False)
        
        self.btn_view_db = QPushButton("📋 Ver Listas")
        self.btn_view_db.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #0b7dda; }
        """)
        self.btn_view_db.clicked.connect(self.ver_listas)
        
        self.btn_restart = QPushButton("🔄 Reiniciar")
        self.btn_restart.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #E64A19; }
        """)
        self.btn_restart.clicked.connect(self.reiniciar_dispositivo)
        self.btn_restart.setEnabled(False)

        self.btn_connect = QPushButton("🔌 Conectar")
        self.btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.btn_connect.clicked.connect(self.toggle_connection)
        
        control_layout.addWidget(self.btn_start)
        control_layout.addWidget(self.btn_stop)
        control_layout.addStretch()
        control_layout.addWidget(self.btn_connect)
        control_layout.addWidget(self.btn_restart)
        control_layout.addWidget(self.btn_search)
        control_layout.addWidget(self.btn_view_db)
        
        list_container = QFrame()
        list_container.setFrameShape(QFrame.StyledPanel)
        list_container.setStyleSheet("background-color: white; border-radius: 5px;")
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        self.apps_list = AppsList()
        list_layout.addWidget(self.apps_list)
        
        main_layout.addWidget(control_frame)
        main_layout.addWidget(list_container, 1)
        
        self.setStyleSheet("""
            QMainWindow { 
                background-color: #f5f5f5;
                font-size: 12px;
            }
        """)
    
    def reiniciar_dispositivo(self):
        """Reinicia el dispositivo conectado mediante ADB"""
        if not self.check_adb_connection():
            return
            
        confirm = QMessageBox.question(
            self, "Confirmar Reinicio",
            "¿Estás seguro que deseas reiniciar el dispositivo?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                run_adb_shell('shell reboot')
                self.update_status("Reiniciando dispositivo...", "orange")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo reiniciar el dispositivo:\n{str(e)}")
    
    def buscar_malware(self):
        """Busca paquetes maliciosos en todas las apps de usuario"""
        if not self.check_adb_connection():
            return
            
        try:
            # Obtener todos los paquetes de usuario (no del sistema)
            result = run_adb_shell('shell pm list packages -3')
            user_packages = {line.split(':')[1].strip() for line in result.split('\n') if line}
            
            # Actualizar lista de malware
            self.apps_list.update_malware_packages()
            malware_packages = self.apps_list.malware_packages
            
            # Encontrar coincidencias
            self.found_malware = user_packages & malware_packages
            
            # Mostrar resultados con botón de eliminar
            if self.found_malware:
                malware_list = "\n".join(self.found_malware)
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Malware Detectado")
                msg.setText(f"Malware(s) encontrado(s):\n\n{malware_list}")
                
                # Añadir botón de eliminar
                delete_button = msg.addButton("Eliminar", QMessageBox.ActionRole)
                delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: black;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #d32f2f; }
                """)
                delete_button.clicked.connect(self.eliminar_malware)
                
                msg.addButton(QMessageBox.Ok)
                msg.exec_()
            else:
                QMessageBox.information(self, "Búsqueda Completada", 
                                      "Sin Malware en Dispositivo")
            
            # Actualizar la vista
            self.monitorear()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar malware:\n{str(e)}")
    
    def eliminar_malware(self):
        """Elimina todos los paquetes maliciosos encontrados"""
        if not self.found_malware:
            return
            
        confirm = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Eliminar {len(self.found_malware)} paquete(s) malicioso(s)?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success_count = 0
            for package in self.found_malware:
                resultado = run_adb_shell(f'shell pm uninstall --user 0 {package}')
                if "Success" in resultado:
                    success_count += 1
                    self.save_to_database(f"ELIMINADO: {package}")
                else:
                    run_adb_shell(f'shell pm disable-user --user 0 {package}')
                    self.save_to_database(f"DESHABILITADO: {package}")
            
            # Mostrar resultados
            QMessageBox.information(
                self, "Eliminación completa",
                f"Se eliminó {success_count} de {len(self.found_malware)} Malware(s)"
            )
            
            # Actualizar la vista
            self.monitorear()
    
    def save_to_database(self, message):
        """Guarda un mensaje en la base de datos"""
        try:
            with open("base_de_datos.txt", "a", encoding='utf-8') as file:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"{timestamp} - {message}\n")
        except Exception as e:
            print(f"Error guardando en base de datos: {str(e)}")
    
    def ver_listas(self):
        """Abre ambos archivos de texto (base de datos y malware list)"""
        try:
            if sys.platform == "win32":
                os.startfile("base_de_datos.txt")
                os.startfile("malware_list.txt")
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                os.system(f'{opener} "base_de_datos.txt"')
                os.system(f'{opener} "malware_list.txt"')
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudieron abrir los archivos:\n{str(e)}")
    
    def verify_connection(self):
        """Verifica periódicamente si el dispositivo sigue conectado"""
        if "Conectado:" in self.status_bar.currentMessage():
            try:
                result = run_adb_command(['devices'])
                devices = [line for line in result.split('\n') 
                         if 'device' in line and not line.startswith('List of')]
                
                connected_devices = [d for d in devices if 'unauthorized' not in d]
                
                if not connected_devices:
                    self.reset_to_initial_state()
            except:
                self.reset_to_initial_state()
    
    def reset_to_initial_state(self):
        """Restaura la aplicación al estado inicial"""
        self.detener_monitoreo()
        self.update_status("No hay dispositivos conectados", "red")
        self.apps_list.clear()
        self.btn_connect.setText("🔌 Conectar")
        self.btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.disable_actions()
        self.clear_device_info()
    
    def toggle_connection(self):
        """Alterna entre conectar y desconectar el dispositivo"""
        if "Conectado:" in self.status_bar.currentMessage():
            self.reset_to_initial_state()
        else:
            self.check_adb_connection()
    
    def check_adb_connection(self):
        """Verifica la conexión ADB y actualiza la interfaz"""
        try:
            result = run_adb_command(['devices'])
            devices = [line for line in result.split('\n') 
                     if 'device' in line and not line.startswith('List of')]
            
            connected_devices = [d for d in devices if 'unauthorized' not in d]
            
            if not connected_devices:
                self.reset_to_initial_state()
                if any('unauthorized' in d for d in devices):
                    self.update_status("Dispositivo no autorizado", "red")
                else:
                    self.update_status("No hay dispositivos conectados", "red")
                return False
            
            device_name = self.get_device_name()
            if "desconocido" in device_name.lower():
                self.update_status("Dispositivo no reconocido", "orange")
                self.disable_actions()
                return False
                
            self.update_status(f"Conectado: {device_name}", "green")
            self.enable_actions()
            self.btn_connect.setText("🔓 Desconectar")
            self.btn_connect.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    font-weight: bold;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #d32f2f; }
            """)
            return True
            
        except Exception as e:
            self.update_status(f"Error ADB: {str(e)}", "red")
            self.disable_actions()
            self.clear_device_info()
            return False
    
    def clear_device_info(self):
        """Limpia la información del dispositivo almacenada"""
        if hasattr(self, 'last_device_name'):
            del self.last_device_name
    
    def get_device_name(self):
        """Obtiene información del dispositivo conectado"""
        if hasattr(self, 'last_device_name'):
            return self.last_device_name
            
        try:
            model = run_adb_shell('shell getprop ro.product.model').strip()
            android_version = run_adb_shell('shell getprop ro.build.version.release').strip()
            
            if not model or not android_version:
                return "Dispositivo desconocido"
                
            device_name = f"{model} (Android {android_version})"
            self.last_device_name = device_name
            return device_name
        except:
            return "Dispositivo desconocido"
    
    def update_status(self, message, color="black"):
        """Actualiza la barra de estado"""
        self.status_bar.showMessage(message)
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: #f0f0f0;
                color: {color};
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }}
        """)
    
    def disable_actions(self):
        """Deshabilita acciones que requieren ADB"""
        self.btn_start.setEnabled(False)
        self.btn_search.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_restart.setEnabled(False)
    
    def enable_actions(self):
        """Habilita acciones cuando hay conexión ADB"""
        self.btn_start.setEnabled(True)
        self.btn_search.setEnabled(True)
        self.btn_restart.setEnabled(True)
        if self.is_monitoring:
            self.btn_stop.setEnabled(True)
    
    def monitorear(self):
        if not self.is_monitoring:
            return
            
        if not self.check_adb_connection():
            self.detener_monitoreo()
            return
            
        try:
            self.apps_list.clear()
            self.apps_list.update_system_packages()
            self.apps_list.update_malware_packages()
            
            resultado_activity = run_adb_shell('shell dumpsys activity top | findstr ACTIVITY')
            paquetes_activity = self.extraer_paquetes_activity(resultado_activity)
            
            if paquetes_activity:
                for paquete in paquetes_activity[:5]:
                    self.apps_list.add_card(paquete)
            
        except Exception as e:
            print(f"Error en monitoreo: {str(e)}")
            self.check_adb_connection()
    
    def extraer_paquetes_activity(self, texto):
        paquetes = []
        for linea in texto.split('\n'):
            if "ACTIVITY" in linea and len(linea.split()) > 1:
                paquete = linea.split()[1].split('/')[0]
                if paquete not in paquetes:
                    paquetes.append(paquete)
        return paquetes if paquetes else None
    
    def iniciar_monitoreo(self):
        if not self.is_monitoring and self.check_adb_connection():
            self.is_monitoring = True
            self.btn_stop.setEnabled(True)
            self.btn_start.setEnabled(False)
            self.monitorear()
            self.refresh_timer.start(3000)
    
    def detener_monitoreo(self):
        if self.is_monitoring:
            self.is_monitoring = False
            self.refresh_timer.stop()
            self.btn_stop.setEnabled(False)
            self.btn_start.setEnabled(True)
    
    def closeEvent(self, event):
        """Maneja el cierre de la aplicación"""
        self.detener_monitoreo()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Configurar fuente global para el título
    font = QFont()
    font.setBold(True)
    app.setFont(font, "QMainWindow")
    
    window = MarshallApp()
    window.show()
    sys.exit(app.exec_())