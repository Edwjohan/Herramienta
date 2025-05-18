import paramiko  # Librería para conexión SSH
import os  # Librería para operaciones del sistema operativo
import sys   # Librería para gestionar excepciones y salida del programa
import platform    # Librería para obtener información del sistema operativo


def main():
    """Solicita los datos al usuario para establecer
    la conexion ssh he inicia la auditoría."""

    print(f"Ejecutando en {platform.system()} ({platform.version()})\n")  # Muestra información del sistema local

    # Solicita los datos al usuario
    host = input("Introduce la dirección del servidor remoto: ")
    port = int(input("Introduce el puerto SSH (por defecto 22): ") or 22)
    user = input("Introduce el usuario SSH: ")
    password = input("Introduce la contraseña SSH: ")
    output = input("Introduce el nombre del archivo de salida (por defecto audit_report.txt): ") or "audit_report.txt"

    # Establece conexión SSH
    client = connect_ssh(host, port, user, password)

    # Ejecuta la auditoría y guarda el informe
    report = audit_system(client)
    save_report(report, output)

    # Cierra la conexión SSH
    client.close()


def connect_ssh(host, port, username, password):
    """Establece una conexión SSH con el servidor remoto."""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Acepta automáticamente claves desconocidas
        client.connect(hostname=host, port=port, username=username, password=password)  # Conecta al servidor
        return client
    except Exception as e:
        print(f"Error al conectar por SSH: {e}")  # Muestra errores de conexión
        sys.exit(1)  # Finaliza la ejecución en caso de error


def audit_system(client):
    """Realiza una auditoría del sistema remoto y genera un informe."""
    hostname = platform.node()  # Obtiene el nombre del equipo local
    system_info = f"Sistema local: {platform.system()} {platform.version()}"  # Información del sistema operativo local
    cpu_count = os.cpu_count()  # Obtiene el número de núcleos del procesador
    user_home = os.path.expanduser("~")  # Obtiene el directorio del usuario

    # Construye el informe con la información del sistema
    report = "=== AUDITORÍA DEL SISTEMA ===\n"
    report += f"Ejecutado desde: {hostname}\n"
    report += f"{system_info}\n"
    report += f"Número de núcleos CPU: {cpu_count}\n"
    report += f"Directorio del usuario: {user_home}\n\n"

    # Define los comandos de auditoría
    commands = {
        "Usuarios conectados": "w",  # Lista los usuarios activos
        "Procesos en ejecución": "ps aux",  # Lista los procesos del sistema
        "Estado de servicios": "systemctl list-units --type=service --state=running",  # Muestra servicios activos
        "Uso de disco": "df -h",  # Muestra el espacio en disco disponible
        "Uso de memoria": "free -m",  # Muestra el uso de memoria RAM
        "Últimos registros del sistema": "tail -n 20 /var/log/syslog || tail -n 20 /var/log/messages || journalctl --no-pager | tail -n 20"
        # Muestra los últimos registros del sistema
    }
    # Ejecuta los comandos y almacena la información en el informe
    for section, cmd in commands.items():
        report += f"\n**{section}**\n"
        report += execute_command(client, cmd) + "\n"

    return report


def execute_command(client, command):
    """Ejecuta un comando en el servidor remoto y devuelve la salida."""
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    return output if output else f"Error: {error}"


def save_report(report, output_file):
    """Guarda el informe de auditoría en un archivo de texto dentro de un directorio 'auditoria'."""
    audit_dir = os.path.join(os.getcwd(), "auditoria")  # Define el directorio de almacenamiento

    # Crea la carpeta de auditoría si no existe
    if not os.path.exists(audit_dir):
        os.makedirs(audit_dir)

    output_path = os.path.join(audit_dir, output_file)  # Define la ruta completa del archivo

    try:
        with open(output_path, "w", encoding="utf-8") as file:  # Abre el archivo para escritura con codificación UTF-8
            file.write(report)  # Escribe el informe en el archivo
        print(f"Informe guardado en {output_path}")  # Muestra la ruta de almacenamiento del informe
    except Exception as e:
        print(f"Error al guardar el informe: {e}")  # Muestra errores en la escritura del archivo


if __name__ == "__main__":
    main()